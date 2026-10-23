"""Deterministic order partitions for repeated stratified k-fold and temporal holdout."""

import copy
import math
import random
from collections import defaultdict
from datetime import datetime

from smart_retail.application.evaluation import estimate_demand
from smart_retail.application.workflow import canonical_hash
from smart_retail.contracts.experiments import EvaluationSpec


def dominant_category(lines: list[dict], category_of: dict[str, str]) -> str:
    units: dict[str, int] = defaultdict(int)
    for line in lines:
        units[category_of[line["sku"]]] += line["quantity"]
    return min(units, key=lambda key: (-units[key], key))


def split_orders(sections: dict, spec: EvaluationSpec, seed: int) -> dict:
    """Partition order IDs; the same (orders, spec, seed) always yields the same folds."""
    orders = sections["orders"]["orders"]
    lines: dict[str, list[dict]] = defaultdict(list)
    for line in sections["orders"]["order_lines"]:
        lines[line["order_id"]].append(line)
    if spec.split == "temporal_holdout":
        ordered = [
            o["id"]
            for o in sorted(orders, key=lambda o: (datetime.fromisoformat(o["placed_at"]), o["id"]))
        ]
        test = math.ceil(len(ordered) * spec.test_size)
        if not 0 < test < len(ordered):
            raise ValueError("Temporal holdout needs at least one training and one test order")
        folds = [{"fold": 0, "train": ordered[:-test], "test": ordered[-test:]}]
        strata = None
    else:
        if spec.n_folds > len(orders):
            raise ValueError("k-fold requires at least as many orders as folds")
        category_of = {p["sku"]: p["category_id"] for p in sections["products"]["items"]}
        strata = defaultdict(list)
        for order in orders:
            strata[dominant_category(lines[order["id"]], category_of)].append(order["id"])
        rng = random.Random(seed)
        members: list[list[str]] = [[] for _ in range(spec.n_folds)]
        offset = 0
        # Round-robin across concatenated shuffled strata keeps fold sizes within one order.
        for key in sorted(strata):
            identifiers = sorted(strata[key])
            rng.shuffle(identifiers)
            for i, identifier in enumerate(identifiers):
                members[(offset + i) % spec.n_folds].append(identifier)
            offset += len(identifiers)
        everyone = sorted(o["id"] for o in orders)
        folds = [
            {
                "fold": k,
                "train": sorted(set(everyone) - set(members[k])),
                "test": sorted(members[k]),
            }
            for k in range(spec.n_folds)
        ]
    plan = {
        "seed": seed,
        "split": spec.split,
        "n_folds": spec.folds,
        "test_size": spec.test_size if spec.split == "temporal_holdout" else None,
        "stratification": None if strata is None else spec.stratify,
        "strata_sizes": None if strata is None else {k: len(v) for k, v in sorted(strata.items())},
        "population_orders": len(orders),
        "orders_sha256": canonical_hash(sections["orders"]),
        "folds": folds,
    }
    plan["sha256"] = canonical_hash(plan)
    return plan


def apply_split(sections: dict, plan: dict, fold: int, spec: EvaluationSpec) -> dict:
    """Training sections with demand re-estimated from training orders plus held-out orders."""
    if canonical_hash(sections["orders"]) != plan["orders_sha256"]:
        raise ValueError("Treatment overrides changed the orders that the split was planned on")
    entry = plan["folds"][fold]

    def subset(identifiers: list[str]) -> dict:
        chosen = set(identifiers)
        section = copy.deepcopy(sections["orders"])
        section["orders"] = [o for o in section["orders"] if o["id"] in chosen]
        section["order_lines"] = [x for x in section["order_lines"] if x["order_id"] in chosen]
        return section

    data = estimate_demand(sections, subset(entry["train"]), plan["population_orders"])
    data["optimization"]["evaluation"] = {
        "split": spec.split,
        "fold": fold,
        "budget_fraction": spec.budget_fraction,
        "population_orders": plan["population_orders"],
        "orders": subset(entry["test"]),
    }
    return data
