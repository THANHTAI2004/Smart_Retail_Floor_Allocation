"""Steady-state genetic baseline over shelf poses (paper-v5)."""

import random
from collections.abc import Callable

from smart_retail.application.feedback.evaluator import exact_score
from smart_retail.application.feedback.neighborhood import geometry_valid
from smart_retail.application.feedback.restarts import DUPLICATE_LIMIT, restart
from smart_retail.application.stage_workflow import canonical_hash
from smart_retail.contracts.feedback import JointConfig
from smart_retail.contracts.inputs import to_domain
from smart_retail.domain.models import EngineError

DEFAULT_POPULATION = 8
DEFAULT_MUTATION_EDITS = 2
CROSSOVER_TRIES = 50
# Keeps the mutation stream distinct from the initial random walks (same job seed).
MUTATION_SEED_OFFSET = 104729
# Selection draws Random(seed * 1000003 + offset), beyond every restart walk variant number.
SELECTION_SEED_OFFSET = 7_340_033


def evolve(
    initial: dict,
    sections: dict,
    config: JointConfig,
    seed: int,
    assess: Callable,
    seen: set,
    archive: list,
    event: Callable[[dict], None],
    exhausted: Callable[[], bool],
    max_step: int,
) -> tuple[dict, str]:
    """Evolve shelf poses from the evaluated initial plan; return (best plan, termination).

    The population is the initial plan plus random walks (as in random_search). Each
    offspring is a uniform per-shelf crossover of two size-2 tournament winners, always
    followed by a mutation walk of `mutation_edits` shelves, and replaces the worst member
    when strictly better. T2/T3 are re-solved when a decision is evaluated. Already
    evaluated decisions cost no budget. Termination is EVALUATION_LIMIT,
    NEIGHBORHOOD_EXHAUSTED, TIMEOUT or CANCELLED.
    """
    domain = to_domain(sections)
    rng = random.Random(seed * 1000003 + SELECTION_SEED_OFFSET)
    size = config.population or DEFAULT_POPULATION
    edits = config.mutation_edits or DEFAULT_MUTATION_EDITS
    population = [initial]
    best = initial
    # A child that restores the initial layout is a duplicate although its id is not a pose hash.
    seen.add(canonical_hash({k: initial["decisions"][k] for k in ("poses", "routing_policy")}))

    def attempt(decision, action, variant, changed, parents=None):
        """Evaluate one decision: (candidate or None, TIMEOUT/CANCELLED or None)."""
        seen.add(canonical_hash(decision))
        try:
            # Population members are fully evaluated; offspring may be screened against the best.
            candidate = assess(decision, reference=None if parents is None else best)
        except EngineError as exc:
            if exc.code in ("TIMEOUT", "CANCELLED"):
                return None, exc.code
            if exc.code in ("CACHE_CORRUPT", "SOURCE_DRIFT"):
                raise
            event({"status": "FAILED", "action": action, "variant": variant, "reason": exc.code})
            return None, None
        archive.append(candidate)
        event(
            {
                "status": "EVALUATING",
                "action": action,
                "layer": "T1",
                "variant": variant,
                **({} if parents is None else {"parent_ids": parents}),
                "candidate_id": candidate["id"],
                "after": candidate["score"],
                "changed": changed,
            }
        )
        return candidate, None

    def skip(action, variant, reason):
        event({"status": "FAILED", "action": action, "variant": variant, "reason": reason})

    def tournament():
        pair = rng.sample(population, 2) if len(population) > 1 else [population[0]] * 2
        return min(pair, key=exact_score)

    def crossover(a, b):
        poses_a, poses_b = a["decisions"]["poses"], b["decisions"]["poses"]
        for _ in range(CROSSOVER_TRIES):
            child = {
                sid: list(poses_a[sid] if rng.random() < 0.5 else poses_b[sid])
                for sid in sorted(poses_a)
            }
            if geometry_valid(domain, child):
                return child
        better = min((a, b), key=exact_score)
        return {sid: list(pose) for sid, pose in better["decisions"]["poses"].items()}

    variant = skipped = 0
    while len(population) < size and not exhausted():
        variant += 1
        decision, changed = restart(initial, sections, seed, variant, max_step=max_step)
        if decision is None or canonical_hash(decision) in seen:
            skip("GA_INIT", variant, "RESTART_UNAVAILABLE" if decision is None else "DUPLICATE")
            skipped += 1
            if skipped >= DUPLICATE_LIMIT:
                return best, "NEIGHBORHOOD_EXHAUSTED"
            continue
        skipped = 0
        member, stopped = attempt(decision, "GA_INIT", variant, changed)
        if stopped:
            return best, stopped
        if member is not None:
            population.append(member)
            if exact_score(member) < exact_score(best):
                best = member
    variant = skipped = 0
    while not exhausted():
        variant += 1
        parent, mate = tournament(), tournament()
        poses = crossover(parent, mate)
        policy = parent["decisions"]["routing_policy"]
        decision, changed = restart(
            {"decisions": {"poses": poses, "routing_policy": policy}},
            sections,
            seed + MUTATION_SEED_OFFSET,
            variant,
            max_step=max_step,
            edits=edits,
        )
        if decision is None:
            decision, changed = {"poses": poses, "routing_policy": policy}, []
        if canonical_hash(decision) in seen:
            skip("GA_OFFSPRING", variant, "DUPLICATE")
            skipped += 1
            if skipped >= DUPLICATE_LIMIT:
                return best, "NEIGHBORHOOD_EXHAUSTED"
            continue
        skipped = 0
        child, stopped = attempt(
            decision, "GA_OFFSPRING", variant, changed, [parent["id"], mate["id"]]
        )
        if stopped:
            return best, stopped
        if child is None:
            continue
        worst = max(range(len(population)), key=lambda i: exact_score(population[i]))
        if exact_score(child) < exact_score(population[worst]):
            population[worst] = child
        if exact_score(child) < exact_score(best):
            best = child
    return best, "EVALUATION_LIMIT"
