"""Deterministic routing policies over valid shortest-path distances."""

from collections.abc import Callable

from smart_retail.domain.models import EngineError


def order(policy: str, targets: dict[str, tuple], start: tuple, distance: Callable) -> list[str]:
    if policy == "return":
        return sorted(targets)
    if policy == "nearest":
        remaining, node, result = set(targets), start, []
        while remaining:
            sid = min(remaining, key=lambda k: (distance(node, targets[k]), k))
            result.append(sid)
            remaining.remove(sid)
            node = targets[sid]
        return result
    if policy != "exact":
        raise EngineError("INVALID_INPUT", "Unknown routing policy")
    keys = sorted(targets)
    if len(keys) > 10:
        raise EngineError(
            "PROBLEM_LIMIT",
            "Exact routing supports at most 10 distinct service locations per journey",
        )
    if not keys:
        return []
    dp: dict[tuple[int, int], tuple[float, tuple[int, ...]]] = {
        (1 << i, i): (distance(start, targets[k]), (i,)) for i, k in enumerate(keys)
    }
    for mask in range(1, 1 << len(keys)):
        for end in range(len(keys)):
            if (mask, end) not in dp:
                continue
            cost, path = dp[mask, end]
            for nxt in range(len(keys)):
                if mask & (1 << nxt):
                    continue
                key = (mask | (1 << nxt), nxt)
                option = (cost + distance(targets[keys[end]], targets[keys[nxt]]), path + (nxt,))
                if key not in dp or option < dp[key]:
                    dp[key] = option
    mask = (1 << len(keys)) - 1
    _, best = min(
        (dp[mask, i][0] + distance(targets[keys[i]], start), dp[mask, i][1])
        for i in range(len(keys))
    )
    return [keys[i] for i in best]
