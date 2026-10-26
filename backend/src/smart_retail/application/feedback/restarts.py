"""Seeded feasible shelf-pose restarts for the multistart baseline."""

import random
from dataclasses import replace

from smart_retail.contracts.inputs import to_domain
from smart_retail.engines.t1_layout.geometry import violations


def restart(state, sections, seed, variant, *, max_attempts=200):
    """Random walk of geometry-valid T1 edits from the sequential plan.

    Only poses and the routing policy are fixed; T2/T3 are re-optimized for the new
    layout. Topology is still validated when the decision is evaluated. Returns
    (None, []) when no unlocked shelf can move within the attempt budget.
    """
    data = to_domain(sections)
    shelves = {s.id: s for s in data.shelves}
    movable = sorted(k for k, s in shelves.items() if not s.locked)
    poses = {k: list(v) for k, v in state["decisions"]["poses"].items()}
    rng = random.Random(seed * 1000003 + variant)
    step = data.floorplan.grid_m
    target = len(movable)
    accepted = 0
    changed: set[str] = set()
    for _ in range(max_attempts if movable else 0):
        if accepted >= target:
            break
        trial = {k: list(v) for k, v in poses.items()}
        kind = rng.choice(("move", "rotate", "swap") if len(movable) > 1 else ("move", "rotate"))
        if kind == "swap":
            a, b = rng.sample(movable, 2)
            trial[a], trial[b] = trial[b], trial[a]
            edited = [a, b]
        else:
            sid = rng.choice(movable)
            x, y, angle = trial[sid]
            if kind == "rotate":
                trial[sid] = [x, y, 90 - angle]
            else:
                dx, dy = (0, 0)
                while (dx, dy) == (0, 0):
                    dx, dy = rng.randint(-3, 3), rng.randint(-3, 3)
                trial[sid] = [round(x + dx * step, 8), round(y + dy * step, 8), angle]
            edited = [sid]
        layout = tuple(
            replace(shelves[k], x=v[0], y=v[1], rotation=v[2]) for k, v in sorted(trial.items())
        )
        if violations(data.floorplan, layout):
            continue
        poses = trial
        accepted += 1
        changed.update(edited)
    if not changed:
        return None, []
    decision = {"poses": poses, "routing_policy": state["decisions"]["routing_policy"]}
    return decision, sorted(changed)
