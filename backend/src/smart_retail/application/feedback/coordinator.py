"""Bounded strict-descent closed loop and certified finite-model orchestration."""

import copy
import time
from fractions import Fraction

from smart_retail.application.feedback.bootstrap import initialize
from smart_retail.application.feedback.diagnostics import analyze
from smart_retail.application.feedback.evaluator import evaluate, exact_score
from smart_retail.application.feedback.neighborhood import actions
from smart_retail.application.feedback.state import FeedbackSnapshot
from smart_retail.application.stage_workflow import canonical_hash
from smart_retail.contracts.feedback import JointConfig
from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import EngineError
from smart_retail.engines.joint_exact.formulation import compile_space
from smart_retail.engines.joint_exact.solver import digest, solve
from smart_retail.engines.joint_exact.verifier import verify as verify_certificate


def identity(sections, config):
    clean = copy.deepcopy(sections)
    clean["optimization"]["joint"] = None
    return {
        "problem_id": canonical_hash(clean),
        "runtime": sections.get("_runtime"),
        "scenario_sha256": digest(config.scenario_seeds),
        "objective": config.objective.model_dump(mode="json"),
        "model_version": "joint-finite-1",
        "finite_space_sha256": digest(compile_space(config.finite_space)[0].model_dump(mode="json"))
        if config.finite_space is not None
        else None,
    }


def validate_space(config, sections):
    space, domains, count = compile_space(config.finite_space)
    required = [
        (space.poses, {s["id"] for s in sections["shelves"]["items"]}),
        (space.assignments, {c["id"] for c in sections["categories"]["items"]}),
        (space.placements, {p["sku"] for p in sections["products"]["items"]}),
    ]
    if any(set(values) != keys for values, keys in required):
        raise EngineError(
            "INVALID_MODEL", "Finite domains must cover exactly every shelf/category/SKU"
        )
    for sku, rows in space.placements.items():
        if any(row.get("sku") != sku for row in rows):
            raise EngineError("INVALID_MODEL", "SKU domain contains another SKU")
    return space


def member(decision, space):
    return (
        all(list(v) in [list(p) for p in space.poses[k]] for k, v in decision["poses"].items())
        and all(v in space.assignments[k] for k, v in decision["assignment"].items())
        and all(p in space.placements[p["sku"]] for p in decision["placements"])
        and decision["routing_policy"] in space.routing_policies
    )


def resolved_config(sections):
    data = to_domain(sections)
    assert data.config.joint is not None
    config = JointConfig.model_validate_json(data.config.joint)
    if config.scenario_seed_policy == "job_seed_offsets":
        config = config.model_copy(
            update={
                "scenario_seeds": [
                    (data.config.seed + s) % 2147483648 for s in config.scenario_seeds
                ],
                "holdout_seeds": [
                    (data.config.seed + s) % 2147483648 for s in config.holdout_seeds
                ],
            }
        )
    return config


def optimize(
    sections,
    cancelled=lambda: False,
    progress=lambda _: None,
    *,
    stage_cache=None,
    observer=lambda *args: None,
):
    data = to_domain(sections)
    config = resolved_config(sections)
    if data.config.stop_after_stage != "T4":
        raise EngineError("INVALID_MODEL", "Joint optimization requires all four stages")
    cache = stage_cache if stage_cache is not None else {}
    began = time.monotonic()
    deadline = began + data.config.time_limit_s
    trace: list[dict] = []
    snapshots: list[FeedbackSnapshot] = []
    archive = []
    seen = set()
    evaluations = 0
    best = None
    termination = "INITIALIZED"
    space = validate_space(config, sections) if config.finite_space is not None else None

    def event(value):
        entry = {
            **copy.deepcopy(value),
            "event": len(trace),
            "telemetry": {**value.get("telemetry", {}), "elapsed_s": time.monotonic() - began},
        }
        trace.append(entry)
        observer(
            "JOINT_EVENT",
            canonical_hash({k: v for k, v in entry.items() if k != "telemetry"}),
            {"scenario_seeds": config.scenario_seeds},
            entry,
            False,
            time.monotonic() - began,
        )

    def assess(decision, variant=0):
        nonlocal evaluations
        if cancelled():
            raise EngineError("CANCELLED", "Joint search cancelled")
        if time.monotonic() >= deadline:
            raise EngineError("TIMEOUT", "Joint time budget")
        evaluations += 1
        state = evaluate(
            sections,
            config,
            decision,
            deadline,
            cancelled,
            progress,
            cache,
            observer,
            variant=variant,
        )
        snapshot = FeedbackSnapshot.capture(state)
        snapshots.append(snapshot)
        observer(
            "JOINT_STATE",
            snapshot.sha256,
            {"runtime": sections.get("_runtime"), "scenario_seeds": config.scenario_seeds},
            snapshot.read(),
            False,
            time.monotonic() - began,
        )
        return snapshot.read()

    event(
        {
            "status": "INITIALIZED",
            "mode": config.mode,
            "objective": config.objective.model_dump(mode="json"),
            "scenario_seeds": config.scenario_seeds,
            "evaluation_budget": config.max_evaluations,
        }
    )
    if config.mode != "exact":
        best = (
            initialize(
                sections,
                config,
                assess,
                event,
                deadline,
                cancelled,
                progress,
                cache,
                observer,
                lambda: evaluations,
            )
            if config.mode in ("feedback", "hybrid")
            else assess(None)
        )
        archive.append(best)
        seen.add(best["id"])
        event(
            {
                "status": "EVALUATING",
                "iteration": 0,
                "candidate_id": best["id"],
                "score": best["score"],
            }
        )
        if config.mode == "multistart":
            for variant in range(1, min(data.config.candidate_count, config.max_evaluations)):
                try:
                    candidate = assess(None, variant)
                except EngineError as exc:
                    if exc.code in ("TIMEOUT", "CANCELLED"):
                        termination = exc.code
                        break
                    event({"status": "FAILED", "action": "MULTISTART", "reason": exc.code})
                    continue
                archive.append(candidate)
                if exact_score(candidate) < exact_score(best):
                    best = candidate
            else:
                termination = "COMPLETED"
        elif config.mode == "sequential":
            termination = "COMPLETED"
        else:
            no_improvement = 0
            for iteration in range(1, config.max_iterations + 1):
                feedback = analyze(best, sections)
                proposals = actions(best, feedback, sections, config)
                event(
                    {
                        "status": "IMPROVING",
                        "iteration": iteration,
                        "feedback": feedback,
                        "candidate_id": best["id"],
                        "action_count": len(proposals),
                    }
                )
                current = best
                next_state = best
                limited = False
                for action in proposals:
                    if evaluations >= config.max_evaluations:
                        termination = "EVALUATION_LIMIT"
                        limited = True
                        break
                    proposal_hash = canonical_hash(action["decisions"])
                    if proposal_hash in seen:
                        event(
                            {
                                "status": "NO_IMPROVEMENT",
                                "iteration": iteration,
                                "action": action["type"],
                                "layer": action["layer"],
                                "accepted": False,
                                "reason": "DUPLICATE",
                            }
                        )
                        continue
                    seen.add(proposal_hash)
                    try:
                        candidate = assess(action["decisions"])
                    except EngineError as exc:
                        event(
                            {
                                "status": "FAILED"
                                if exc.code not in ("TIMEOUT", "CANCELLED")
                                else exc.code,
                                "iteration": iteration,
                                "action": action["type"],
                                "layer": action["layer"],
                                "accepted": False,
                                "reason": exc.code,
                                "before": current["score"],
                            }
                        )
                        if exc.code in ("TIMEOUT", "CANCELLED"):
                            termination = exc.code
                            limited = True
                            break
                        if exc.code in ("CACHE_CORRUPT", "SOURCE_DRIFT"):
                            raise
                        continue
                    archive.append(candidate)
                    accepted = exact_score(candidate) < exact_score(next_state) - Fraction(
                        str(config.tolerance)
                    )
                    event(
                        {
                            "status": "EVALUATING",
                            "iteration": iteration,
                            "action": action["type"],
                            "layer": action["layer"],
                            "parent_id": current["id"],
                            "candidate_id": candidate["id"],
                            "before": current["score"],
                            "after": candidate["score"],
                            "accepted": accepted,
                            "reason": "STRICT_DESCENT" if accepted else "NO_STRICT_IMPROVEMENT",
                            "changed": action["changed"],
                            "decisions": candidate["decisions"],
                            "cache_keys": candidate["result"]["stage_cache"],
                            "components": candidate["components"],
                            "scenario_seeds": config.scenario_seeds,
                            "validation": "PASS",
                        }
                    )
                    if accepted:
                        next_state = candidate
                    if accepted and config.policy == "first_improvement":
                        break
                if next_state is current:
                    no_improvement += 1
                else:
                    no_improvement = 0
                    best = next_state
                event(
                    {
                        "status": "NO_IMPROVEMENT" if best is current else "IMPROVING",
                        "iteration": iteration,
                        "best_id": best["id"],
                        "best_score": best["score"],
                    }
                )
                if limited:
                    break
                if config.target is not None and best["score"] <= config.target:
                    termination = "TARGET_REACHED"
                    break
                if no_improvement >= config.patience:
                    termination = "CONVERGED_LOCAL"
                    break
            else:
                termination = "ITERATION_LIMIT"
    certificate: dict | None = None
    proof: dict = {}
    if config.mode in ("exact", "hybrid"):
        warm = best if best and member(best["decisions"], space) else None
        best, certificate, timing = solve(
            config.finite_space,
            assess,
            identity=identity(sections, config),
            deadline=deadline,
            max_evaluations=max(0, config.max_evaluations - evaluations),
            cancelled=cancelled,
            incumbent=warm,
            progress=lambda p: progress("JOINT_EXACT_" + str(p["evaluated"])),
        )
        proof = {"status": "NOT_REQUESTED"}
        if config.verify_certificate:
            # Fresh cache forces independent numerical evaluation of the proof.
            proof_cache: dict = {}
            proof = verify_certificate(
                certificate,
                lambda d: evaluate(
                    sections, config, d, deadline, cancelled, progress, proof_cache, observer
                ),
                identity=identity(sections, config),
                deadline=deadline,
                cancelled=cancelled,
            )
        termination = certificate["termination"]
        if (
            certificate["status"] in ("GLOBAL_OPTIMAL_CERTIFIED", "INFEASIBLE_PROVEN")
            and proof["status"] != "PASS"
        ):
            # Keep complete-search claim separate from independently verified certification.
            event({"status": "PROOF_VERIFICATION_FAILED", "reason": proof["status"]})
        event(
            {
                "status": certificate["status"],
                "certificate": certificate,
                "verification": proof,
                "telemetry": timing,
            }
        )
        if best:
            archive.append(best)
    if best is None:
        result: dict = {
            "input_sha256": canonical_hash(sections),
            "stages": {},
            "status": "NO_SOLUTION",
        }
    else:
        result = copy.deepcopy(best["result"])
        result["input_sha256"] = canonical_hash(sections)
    feasible = [
        {
            "candidate": i,
            "status": "FEASIBLE",
            "score": s["score"],
            "components": s["components"],
            "stages": s["result"]["stages"],
            "stage_cache": s["result"]["stage_cache"],
        }
        for i, s in enumerate(archive)
    ]
    pareto = [
        i
        for i, s in enumerate(archive)
        if not any(
            all(a <= b for a, b in zip(o["components"], s["components"]))
            and any(a < b for a, b in zip(o["components"], s["components"]))
            for o in archive
        )
    ]
    certified = bool(
        certificate
        and certificate["status"] == "GLOBAL_OPTIMAL_CERTIFIED"
        and proof["status"] == "PASS"
    )
    result["integrated"] = {
        "algorithm": "joint-" + config.mode,
        "candidates": feasible,
        "pareto_candidates": pareto,
        "global_optimality_proven": certified,
        "termination": termination,
        "selected_candidate": next(
            (i for i, s in enumerate(archive) if best and s["id"] == best["id"]), None
        ),
    }
    result["joint"] = {
        "mode": config.mode,
        "status": termination,
        "best": None
        if best is None
        else {
            k: best[k]
            for k in ("id", "score", "score_fraction", "components", "decisions", "scenario_seeds")
        },
        "initial_score": archive[0]["score"] if archive else None,
        "evaluations": evaluations,
        "state_snapshots": [
            {"sha256": s.sha256, "candidate_id": s.read()["id"]} for s in snapshots
        ],
        "trace": trace,
        "certificate": certificate,
        "verification": proof,
        "proof_status": certificate["status"]
        if certificate and proof.get("status") == "PASS"
        else "PROOF_VERIFICATION_FAILED"
        if proof.get("status") == "PROOF_VERIFICATION_FAILED"
        else "FEASIBLE_NOT_PROVEN"
        if best
        else "SEARCH_EXHAUSTED",
        "general_optimality": "JOINT_GENERAL_OPTIMALITY_NOT_PROVEN",
        "normalization": config.objective.model_dump(mode="json"),
        "pareto_scope": "Evaluated candidates only",
    }
    if best and config.holdout_seeds and time.monotonic() < deadline:
        try:
            held = evaluate(
                sections,
                config,
                best["decisions"],
                deadline,
                cancelled,
                progress,
                cache,
                observer,
                seeds=config.holdout_seeds,
            )
            result["joint"]["holdout"] = {
                k: held[k] for k in ("score", "components", "scenario_seeds")
            }
            result["joint"]["holdout"]["status"] = "COMPLETED"
        except EngineError as exc:
            if exc.code not in ("TIMEOUT", "CANCELLED"):
                raise
            result["joint"]["holdout"] = {
                "status": exc.code,
                "scenario_seeds": config.holdout_seeds,
            }
    elif config.holdout_seeds:
        result["joint"]["holdout"] = {
            "status": "NOT_EXECUTED_BUDGET",
            "scenario_seeds": config.holdout_seeds,
        }
    event({"status": termination, "best_id": best["id"] if best else None})
    return result
