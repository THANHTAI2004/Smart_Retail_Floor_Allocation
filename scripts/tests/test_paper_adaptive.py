# Vai trò: Kiểm thử ngưỡng RAM và hysteresis của điều phối thích nghi.
# Các assertion mô tả hành vi mong đợi; kết quả chỉ được xác nhận sau khi chạy test.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_paper_adaptive import desired_slots  # noqa: E402


# Hàm test_ram_hysteresis_and_strict_thresholds: kiểm tra kịch bản ram hysteresis and strict thresholds bằng các assertion trong thân hàm.
def test_ram_hysteresis_and_strict_thresholds():
    slots = 3
    observed = []
    for ram in [79, 90, 91, 85, 80, 79, 81, 95]:
        slots = desired_slots(slots, ram)
        observed.append(slots)
    assert observed == [3, 3, 2, 2, 2, 3, 3, 2]
