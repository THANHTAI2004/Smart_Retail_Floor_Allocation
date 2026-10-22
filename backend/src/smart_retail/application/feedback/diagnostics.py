"""Operational evidence from simulated journeys and shelf queues, never crowd inference."""

from collections import Counter
from itertools import combinations


def analyze(state, sections):
    shelves: Counter = Counter()
    skus: Counter = Counter()
    distances: Counter = Counter()
    waits: Counter = Counter()
    pairs: Counter = Counter()
    cats = {p["sku"]: p["category_id"] for p in sections["products"]["items"]}
    totals: Counter = Counter()
    scenario_kpis = []
    for scenario in state["scenarios"]:
        m = scenario["stages"]["T4"]["metrics"]
        scenario_kpis.append(
            {
                k: m[k]
                for k in (
                    "mean_distance_m",
                    "mean_wait_s",
                    "mean_completion_s",
                    "picker_utilization",
                    "late_orders",
                    "completed",
                )
            }
        )
        routes = {(r["kind"], r["id"]): r for r in m["routes"]}
        for j in m["journeys"]:
            totals[j["kind"] + "_distance_m"] += j["distance_m"]
            totals["picker_wait_s"] += j["picker_wait_s"]
            totals["shelf_wait_s"] += j["shelf_wait_s"]
            route = routes[j["kind"], j["id"]]
            for sid in route["shelves"]:
                shelves[sid] += 1
                waits[sid] += j["shelf_wait_s"] / max(1, len(route["shelves"]))
            for p in j["picks"]:
                skus[p["sku"]] += p["quantity"]
                distances[p["sku"]] += j["distance_m"] / max(1, len(j["picks"]))
            for a, b in combinations(sorted({cats[p["sku"]] for p in j["picks"]}), 2):
                pairs[a + "/" + b] += 1
    return {
        "hot_shelves": shelves.most_common(),
        "high_travel_skus": distances.most_common(),
        "high_wait_locations": waits.most_common(),
        "sku_pick_counts": dict(skus),
        "frequently_co_picked_categories": pairs.most_common(),
        "candidate_bottlenecks": [k for k, _ in waits.most_common(3)],
        "objective_components": state["components"],
        "recommended_action_types": ["T1_MOVE", "T2_REASSIGN", "T3_FACE"],
        "diagnostic_evidence": {
            "totals": dict(totals),
            "scenario_kpis": scenario_kpis,
            "wait_attribution": "Journey shelf wait divided across visited shelves; diagnostic proxy only",
            "travel_attribution": "Journey distance divided across picked SKU types; diagnostic proxy only",
            "scope": "Simulated shelf queues and finite picker pool; no corridor congestion inference",
        },
    }
