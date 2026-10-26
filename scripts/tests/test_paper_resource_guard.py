"""Admission policy checks: sustained pressure, recovery, and failure classification."""

import unittest

from scripts.paper_resource_guard import Guard, Sampler, resource_failure


def measurement(ram=60, cpu=40, free=8):
    return {"ram_percent": ram, "cpu_percent": cpu, "available_bytes": free * 1024**3}


class ResourceGuardTests(unittest.TestCase):
    def test_memory_pressure_requires_sustained_interval(self):
        guard = Guard()
        self.assertIsNone(guard.reason(measurement(ram=91), timestamp=0))
        self.assertIsNone(guard.reason(measurement(ram=91), timestamp=14))
        self.assertEqual(
            guard.reason(measurement(ram=91), timestamp=15), "RAM_PRESSURE_15S"
        )

    def test_available_memory_also_triggers(self):
        guard = Guard()
        guard.reason(measurement(free=1), timestamp=10)
        self.assertEqual(
            guard.reason(measurement(free=1), timestamp=25), "RAM_PRESSURE_15S"
        )

    def test_transient_pressure_is_reset(self):
        guard = Guard()
        guard.reason(measurement(ram=92, cpu=99), timestamp=0)
        guard.reason(measurement(), timestamp=10)
        self.assertIsNone(guard.reason(measurement(ram=92, cpu=99), timestamp=121))

    def test_cpu_saturation_needs_two_minutes(self):
        guard = Guard()
        guard.reason(measurement(cpu=98), timestamp=0)
        self.assertIsNone(guard.reason(measurement(cpu=98), timestamp=119))
        self.assertEqual(
            guard.reason(measurement(cpu=98), timestamp=120), "CPU_SATURATION_120S"
        )

    def test_new_failure_triggers_immediately(self):
        self.assertEqual(
            Guard().reason(measurement(), failure=True),
            "NEW_RESOURCE_FAILURE_OR_WORKER_CRASH",
        )

    def test_normal_budget_timeout_does_not_imply_cpu_contention(self):
        record = {"status": "FAILED", "error": {"code": "TIMEOUT"}}
        self.assertFalse(resource_failure(record, 35))
        self.assertTrue(resource_failure(record, 96))
        self.assertFalse(resource_failure({"status": "SUCCEEDED"}, 99))

    def test_out_of_memory_and_crash_but_not_disk_or_search_failure(self):
        for error in (
            {"message": "MemoryError"},
            {"message": "Unable to allocate 4 GiB"},
            {"code": "WORKER_CRASH"},
        ):
            self.assertTrue(resource_failure({"status": "FAILED", "error": error}, 30))
        for error in (
            {"message": "No space left on device"},
            {"code": "SEARCH_EXHAUSTED"},
        ):
            self.assertFalse(resource_failure({"status": "FAILED", "error": error}, 30))

    def test_windows_sampler_returns_real_measurements(self):
        sampler = Sampler()
        first, second = sampler.sample(), sampler.sample()
        self.assertGreater(first["available_bytes"], 0)
        self.assertGreaterEqual(first["ram_percent"], 0)
        self.assertLessEqual(first["ram_percent"], 100)
        if second["cpu_percent"] is not None:
            self.assertGreaterEqual(second["cpu_percent"], 0)
            self.assertLessEqual(second["cpu_percent"], 100)


if __name__ == "__main__":
    unittest.main()
