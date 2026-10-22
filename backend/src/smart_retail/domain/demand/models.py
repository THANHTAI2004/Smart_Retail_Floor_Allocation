"""Business models for demand. No HTTP or ORM dependencies."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CustomerBehavior:
    model: str = "synthetic_basket"
    speed_m_s: float = 1.2
    dwell_s: float = 5


@dataclass(frozen=True)
class ArrivalPeriod:
    start_s: float
    end_s: float
    arrivals_per_hour: float


@dataclass(frozen=True)
class DemandProfile:
    arrivals_per_hour: float = 20
    horizon_s: float = 3600
    customers: int = 20
    baskets: tuple[tuple[str, ...], ...] = ()
    behavior: CustomerBehavior = field(default_factory=CustomerBehavior)
    periods: tuple[ArrivalPeriod, ...] = ()
    picker_count: int = 1
    routing_policy: str = "nearest"


@dataclass(frozen=True)
class SimulationResult:
    metrics: dict
    assumptions: tuple[str, ...]
