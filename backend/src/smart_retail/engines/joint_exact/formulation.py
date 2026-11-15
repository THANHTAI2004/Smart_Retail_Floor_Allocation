# Vai trò: Biên dịch miền Cartesian được khai báo thành quyết định có thể liệt kê.
# Giới hạn miền phải được phản ánh trong kết luận tối ưu.
"""Compile explicit Cartesian domains; no undocumented heuristic pruning."""

import math

from smart_retail.contracts.optimality import FiniteSpace
from smart_retail.domain.models import EngineError


# Đếm và biên dịch đúng miền được khai báo; các giới hạn miền quyết định phạm vi kết luận.
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
    # Bundles are single domains whose option fixes a whole layer.
    if space.layouts is not None:
        domains.append(("layout", "layouts", space.layouts))
    if space.allocations is not None:
        domains.append(("allocation", "allocations", space.allocations))
    domains.append(("routing_policy", "policy", space.routing_policies))
    count = math.prod(len(options) for _, _, options in domains)
    if count > space.max_states:
        raise EngineError(
            "INVALID_MODEL", f"Explicit space has {count} states, cap {space.max_states}"
        )
    return space, domains, count


# Chuyển chỉ số một trạng thái trong tích miền thành bộ quyết định vật lý.
def assemble(domains, values):
    decision: dict = {"poses": {}, "assignment": {}, "placements": []}
    for (kind, key, _), value in zip(domains, values):
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
    return decision
