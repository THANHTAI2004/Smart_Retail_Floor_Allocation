"""Exhaustive finite search with the nonnegative-objective lower bound zero."""

import hashlib
import itertools
import json
import time
from fractions import Fraction

from smart_retail.domain.models import EngineError
from smart_retail.engines.joint_exact.formulation import assemble, compile_space


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def leaf(decision, state=None, error=None):
    return {
        "decision_sha256": digest(decision),
        "status": "FEASIBLE" if state else "INVALID_DECISION",
        "score_fraction": state["score_fraction"] if state else None,
        "witness_sha256": digest(
            {
                "decisions": state["decisions"],
                "score": state["score_fraction"],
                "simulation": [r["stages"]["T4"] for r in state["scenarios"]],
            }
        )
        if state
        else None,
        "error": error,
    }


def solve(
    raw,
    evaluate,
    *,
    identity,
    deadline,
    max_evaluations=20000,
    cancelled=lambda: False,
    incumbent=None,
    progress=lambda _: None,
):
    space, domains, count = compile_space(raw)
    leaves: list[dict] = []
    best = incumbent
    termination = "COMPLETED"
    began = time.monotonic()
    for values in itertools.product(*(v for _, _, v in domains)):
        if cancelled():
            termination = "CANCELLED"
            break
        if time.monotonic() >= deadline:
            termination = "TIMEOUT"
            break
        if len(leaves) >= max_evaluations:
            termination = "EVALUATION_LIMIT"
            break
        decision = assemble(domains, values)
        try:
            state = evaluate(decision)
            record = leaf(decision, state)
            if best is None or Fraction(*state["score_fraction"]) < Fraction(
                *best["score_fraction"]
            ):
                best = state
        except EngineError as exc:
            if exc.code in ("CANCELLED", "TIMEOUT"):
                termination = exc.code
                break
            if exc.code not in (
                "INVALID_DECISION",
                "INVALID_LAYOUT",
                "INVALID_LOCKED_LAYOUT",
                "INVALID_TOPOLOGY",
                "NO_PATH",
                "ROUTING_FAILED",
                "DISCONNECTED_LAYOUT",
                "UNREACHABLE",
                "DISCONNECTED_AISLES",
            ):
                raise
            record = leaf(decision, error=exc.code)
        leaves.append(record)
        progress({"evaluated": len(leaves), "total": count})
    complete = len(leaves) == count
    ub = best["score_fraction"] if best else None
    if complete:
        status = "GLOBAL_OPTIMAL_CERTIFIED" if best else "INFEASIBLE_PROVEN"
    elif termination == "TIMEOUT":
        status = "TIMEOUT"
    else:
        status = "BOUNDED_GAP" if best else "SEARCH_EXHAUSTED"
    lb = ub if complete and ub is not None else [0, 1]
    gap = float(Fraction(*ub) - Fraction(*lb)) if ub else None
    certificate: dict = {
        "model_version": "joint-finite-1",
        "solver": "exhaustive-cartesian-v1",
        "identity": identity,
        "finite_space": space.model_dump(mode="json"),
        "status": status,
        "termination": termination,
        "complete": complete,
        "total_states": count,
        "evaluated_states": len(leaves),
        "pruned_states": 0,
        "leaves": leaves,
        "incumbent": best["decisions"] if best else None,
        "upper_bound_fraction": ub,
        "lower_bound_fraction": lb,
        "absolute_gap": gap,
        "relative_gap": (gap or 0) / max(1e-15, abs(float(Fraction(*ub)))) if ub else None,
        "bound_justification": "Every weighted normalized component is nonnegative; complete enumeration attains minimum",
        "arithmetic_scope": "Exact rational comparison of serialized deterministic IEEE-754 simulator observations; not exact real arithmetic",
        "scope": "Only the declared finite Cartesian domain and fixed scenario sample-average objective",
        "feasibility_validation": "official validators + independent application replay",
    }
    certificate["artifact_sha256"] = digest(certificate)
    return best, certificate, {"wall_s": time.monotonic() - began}
