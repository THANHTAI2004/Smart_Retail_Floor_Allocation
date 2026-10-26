"""Independent mixed-radix proof replay; never calls the search/selection solver."""

import time
from fractions import Fraction

from smart_retail.domain.models import EngineError
from smart_retail.engines.joint_exact.formulation import compile_space
from smart_retail.engines.joint_exact.solver import digest, leaf


def inside(decision, space) -> bool:
    """Membership of a decision in per-key and/or bundled finite domains."""
    poses = {k: list(v) for k, v in decision["poses"].items()}
    if space.layouts is not None:
        layout_ok = any(poses == {k: list(v) for k, v in o.items()} for o in space.layouts)
    else:
        layout_ok = set(poses) == set(space.poses) and all(
            v in [list(p) for p in space.poses[k]] for k, v in poses.items()
        )
    rows = sorted(decision["placements"], key=lambda r: r["sku"])
    if space.allocations is not None:
        allocation_ok = any(
            decision["assignment"] == o["assignment"]
            and rows == sorted(o["placements"], key=lambda r: r["sku"])
            for o in space.allocations
        )
    else:
        allocation_ok = (
            set(decision["assignment"]) == set(space.assignments)
            and {r["sku"] for r in rows} == set(space.placements)
            and len(rows) == len(space.placements)
            and all(v in space.assignments[k] for k, v in decision["assignment"].items())
            and all(row in space.placements[row["sku"]] for row in rows)
        )
    return layout_ok and allocation_ok and decision["routing_policy"] in space.routing_policies


def verify(certificate, evaluate, *, identity, deadline=float("inf"), cancelled=lambda: False):
    try:
        payload = {k: v for k, v in certificate.items() if k != "artifact_sha256"}
        if digest(payload) != certificate["artifact_sha256"] or certificate["identity"] != identity:
            raise ValueError("Certificate seal or problem identity differs")
        space, domains, count = compile_space(certificate["finite_space"])
        if (
            certificate["model_version"] != space.model_version
            or certificate["model_version"] != identity["model_version"]
        ):
            raise ValueError("Proof model version differs")
        if digest(space.model_dump(mode="json")) != identity["finite_space_sha256"]:
            raise ValueError("Certificate decision space differs from the declared problem")
        if len(certificate["leaves"]) > count:
            raise ValueError("More leaves than decision states")
        if count != certificate["total_states"] or certificate["evaluated_states"] != len(
            certificate["leaves"]
        ):
            raise ValueError("Completeness count differs")
        if certificate["pruned_states"] != 0 or certificate["solver"] != "exhaustive-cartesian-v1":
            raise ValueError("Unsupported proof method")
        best = None
        for number, expected in enumerate(certificate["leaves"]):
            if time.monotonic() >= deadline or cancelled():
                return {"status": "NOT_VERIFIED_BUDGET", "checked": number}
            # Separate enumeration: decode a mixed-radix ordinal, no solver generator.
            index = number
            chosen = []
            for _, _, options in reversed(domains):
                chosen.append(options[index % len(options)])
                index //= len(options)
            decision: dict = {"poses": {}, "assignment": {}, "placements": []}
            for (kind, key, _), value in zip(domains, reversed(chosen)):
                if kind == "routing_policy":
                    decision[kind] = value
                elif kind == "placements":
                    decision[kind].append(dict(value))
                elif kind == "layout":
                    decision["poses"] = dict(value)
                elif kind == "allocation":
                    decision["assignment"] = dict(value["assignment"])
                    decision["placements"].extend(dict(row) for row in value["placements"])
                else:
                    decision[kind][key] = value
            try:
                state = evaluate(decision)
                actual = leaf(decision, state)
                value = Fraction(*state["score_fraction"])
                if best is None or value < best:
                    best = value
            except EngineError as exc:
                if exc.code in ("TIMEOUT", "CANCELLED"):
                    return {"status": "NOT_VERIFIED_BUDGET", "checked": number}
                actual = leaf(decision, error=exc.code)
            if expected != actual:
                raise ValueError("Leaf decision, feasibility, simulation or objective differs")
        complete = len(certificate["leaves"]) == count
        if certificate["complete"] != complete:
            raise ValueError("False completeness assertion")
        ub = certificate["upper_bound_fraction"]
        if ub is not None:
            decision = certificate["incumbent"]
            if not inside(decision, space):
                raise ValueError("Incumbent is outside the finite model")
            witness = evaluate(certificate["incumbent"])
            if witness["score_fraction"] != ub:
                raise ValueError("Incumbent objective differs")
            incumbent_value = Fraction(*ub)
            if best is not None and incumbent_value > best:
                raise ValueError("Incumbent worse than an enumerated witness")
        else:
            incumbent_value = None
        lb = Fraction(*certificate["lower_bound_fraction"])
        if complete:
            if best is None:
                if certificate["status"] != "INFEASIBLE_PROVEN" or ub is not None:
                    raise ValueError("False infeasibility/optimality status")
            elif (
                best != lb
                or incumbent_value != best
                or certificate["status"] != "GLOBAL_OPTIMAL_CERTIFIED"
            ):
                raise ValueError("Complete minimum and bounds differ")
        elif lb != 0 or certificate["status"] in ("GLOBAL_OPTIMAL_CERTIFIED", "INFEASIBLE_PROVEN"):
            raise ValueError("Incomplete search has unsupported bound/status")
        expected_gap = float(incumbent_value - lb) if incumbent_value is not None else None
        if certificate["absolute_gap"] != expected_gap:
            raise ValueError("Gap differs")
        expected_relative = (
            (expected_gap or 0) / max(1e-15, abs(float(incumbent_value)))
            if incumbent_value is not None
            else None
        )
        if certificate["relative_gap"] != expected_relative:
            raise ValueError("Relative gap differs")
        return {
            "status": "PASS",
            "checked": len(certificate["leaves"]),
            "trust": "Independent exhaustive re-evaluation using official model/validators; no solver-reported MIP proof",
        }
    except (ValueError, KeyError, TypeError, ArithmeticError, IndexError, EngineError) as exc:
        return {"status": "PROOF_VERIFICATION_FAILED", "reason": str(exc)}
