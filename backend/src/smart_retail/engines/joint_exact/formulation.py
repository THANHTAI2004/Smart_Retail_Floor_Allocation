"""Compile explicit Cartesian domains; no undocumented heuristic pruning."""

import math

from smart_retail.contracts.optimality import FiniteSpace
from smart_retail.domain.models import EngineError


def compile_space(raw):
    space = FiniteSpace.model_validate(raw)
    domains: list[tuple[str, str, list]] = []
    groups: list[tuple[str, dict]] = [
        ("poses", space.poses),
        ("assignment", space.assignments),
        ("placements", space.placements),
    ]
    for kind, values in groups:
        for key, options in sorted(values.items()):
            if not options:
                raise EngineError("INVALID_MODEL", "Empty decision domain")
            domains.append((kind, key, options))
    domains.append(("routing_policy", "policy", space.routing_policies))
    count = math.prod(len(options) for _, _, options in domains)
    if count > space.max_states:
        raise EngineError(
            "INVALID_MODEL", f"Explicit space has {count} states, cap {space.max_states}"
        )
    return space, domains, count


def assemble(domains, values):
    decision: dict = {"poses": {}, "assignment": {}, "placements": []}
    for (kind, key, _), value in zip(domains, values):
        if kind == "routing_policy":
            decision[kind] = value
        elif kind == "placements":
            decision[kind].append(dict(value))
        else:
            decision[kind][key] = value
    return decision
