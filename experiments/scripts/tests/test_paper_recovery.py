"""Derived shards preserve the original per-job settings and bound campaign size."""

import unittest
from pathlib import Path

from smart_retail.application.experiments.campaign import job_sections, split_plans
from smart_retail.application.experiments.storage import read
from smart_retail.application.workflow import canonical_hash
from smart_retail.contracts.experiments import planned_jobs

from scripts.paper_recovery import shard_specs

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "backend").is_dir() and (p / "frontend").is_dir())


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT / "experiments/results/20261023-paper-v2/paper-x2b-small"
        self.config = read(self.root / "configuration.json")
        self.jobs = read(self.root / "plan.json")["jobs"]

    def test_shards_keep_exact_original_job_inputs(self):
        for spec, targets in shard_specs(self.config, self.jobs[:13]):
            for job in targets:
                data = read(self.root / "datasets" / job["dataset"] / "input.json")
                rebuilt = job_sections(
                    spec, data, job, split_plans(self.root, job["dataset"])
                )
                self.assertEqual(canonical_hash(rebuilt), job["input_sha256"])
            self.assertEqual(spec.job_time_limit_s, self.config["job_time_limit_s"])
            self.assertEqual(spec.memory_limit_mb, self.config["memory_limit_mb"])
            self.assertLessEqual(planned_jobs(spec), 10)

    def test_one_fold_request_keeps_its_paired_fold_explicit(self):
        shards = shard_specs(self.config, self.jobs[:1])
        self.assertEqual(len(shards), 1)
        spec, targets = shards[0]
        self.assertEqual(len(targets), 1)
        self.assertEqual(planned_jobs(spec), 2)

    def test_names_are_deterministic_and_distinct_for_distinct_requests(self):
        first = shard_specs(self.config, self.jobs[:1])[0][0].name
        self.assertEqual(first, shard_specs(self.config, self.jobs[:1])[0][0].name)
        self.assertNotEqual(first, shard_specs(self.config, self.jobs[:2])[0][0].name)


if __name__ == "__main__":
    unittest.main()
