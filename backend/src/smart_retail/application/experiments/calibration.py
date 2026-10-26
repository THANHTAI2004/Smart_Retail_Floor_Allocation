"""Order-load calibration: choose the order inter-arrival time for a target picker utilization.

The sequential plan of a reference instance is simulated at light load to measure the
mean picker service time S (travel + picking + shelf queueing). The first interval is
S / (c * target); further rounds rescale it by measured/target utilization. The
simulation assumption is explicit: utilization is measured on the sequential plan,
optimized plans change S and therefore the realized utilization.
"""

import copy
import statistics

from smart_retail.application.experiments.generators import SIZES, generate, merge
from smart_retail.application.workflow import execute
from smart_retail.contracts.experiments import DatasetSpec

LIGHT_INTERVAL_S = 3600.0
LIGHT_SPAN_S = 50000.0


def measure(spec: DatasetSpec, overrides: dict) -> dict:
    data, _ = generate(spec)
    data = merge(data, copy.deepcopy(overrides))
    data["optimization"]["joint"] = None
    metrics = execute(data)["stages"]["T4"]["metrics"]
    pickers = [j for j in metrics["journeys"] if j["kind"] == "picker"]
    return {
        "order_interval_s": spec.order_interval_s,
        "picker_utilization": metrics["picker_utilization"],
        "mean_service_s": statistics.mean(j["elapsed_s"] - j["picker_wait_s"] for j in pickers),
        "mean_picker_wait_s": statistics.mean(j["picker_wait_s"] for j in pickers),
        "late_orders": metrics["late_orders"],
    }


def calibrate(
    spec: DatasetSpec,
    overrides: dict,
    *,
    target: float = 0.75,
    tolerance: float = 0.05,
    max_rounds: int = 4,
) -> tuple[DatasetSpec, dict]:
    pickers = spec.picker_count or 2
    orders = spec.orders or SIZES[spec.scale][3]
    # Light load, kept inside the 86,400 s demand horizon contract.
    light_interval = round(min(LIGHT_INTERVAL_S, LIGHT_SPAN_S / orders), 2)
    light = measure(
        spec.model_copy(update={"order_interval_s": light_interval, "picker_count": pickers}),
        overrides,
    )
    interval = round(light["mean_service_s"] / (pickers * target), 2)
    rounds = [light]
    for _ in range(max_rounds):
        current = spec.model_copy(update={"order_interval_s": interval, "picker_count": pickers})
        observed = measure(current, overrides)
        rounds.append(observed)
        if abs(observed["picker_utilization"] - target) <= tolerance:
            break
        interval = round(interval * observed["picker_utilization"] / target, 2)
    best = min(rounds[1:], key=lambda r: abs(r["picker_utilization"] - target))
    chosen = spec.model_copy(
        update={"order_interval_s": best["order_interval_s"], "picker_count": pickers}
    )
    evidence = {
        "dataset": spec.id,
        "target_utilization": target,
        "tolerance": tolerance,
        "picker_count": pickers,
        "order_interval_s": best["order_interval_s"],
        "achieved_utilization": best["picker_utilization"],
        "within_tolerance": abs(best["picker_utilization"] - target) <= tolerance,
        "rounds": rounds,
        "assumption": "Measured on the sequential plan of this instance; optimized plans change service time",
    }
    return chosen, evidence
