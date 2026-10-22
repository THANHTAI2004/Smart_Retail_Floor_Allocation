import time
from dataclasses import replace

import pytest

from smart_retail.contracts.inputs import to_domain
from smart_retail.engines.t1_layout.engine import solve as layout
from smart_retail.engines.t1_layout.engine import violations


@pytest.mark.parametrize("count", [2, 10, 20])
def test_t1_bounded_sizes(sample, count, record_property):
    d = to_domain(sample)
    floor = replace(d.floorplan, boundary=((0, 0), (30, 0), (30, 30), (0, 30)), obstacles=())
    shelves = tuple(replace(d.shelves[0], id=f"S{i}") for i in range(count))
    start = time.monotonic()
    result = layout(floor, shelves, "optimizable", max_iterations=100000, deadline=start + 10)
    elapsed = time.monotonic() - start
    record_property("shelf_count", count)
    record_property("elapsed_s", elapsed)
    assert len(result.shelves) == count
    assert not violations(floor, result.shelves)
    assert elapsed < 10
