"""Tests of workflow behavior using only synthetic records."""

import json
import tempfile
import unittest
from pathlib import Path

from ai4s_rsi.pipeline import load_config, run, save


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.config, self.task = load_config(Path(__file__).parents[1] / "configs/demo.json")

    def test_repeatable_run_and_feedback(self):
        first = run(self.config, self.task)
        self.assertEqual(first, run(self.config, self.task))
        qualities = [item["feedback"]["leading_quality"] for item in first["rounds"]]
        self.assertEqual(qualities, sorted(qualities))
        for item in first["rounds"]:
            scores = {e["candidate_id"]: e["metrics"] for e in item["evaluations"]}
            expected = sorted(scores, key=lambda cid: (
                -scores[cid]["quality"], scores[cid]["cost"], cid
            ))[:self.config["select"]]
            self.assertEqual(expected, item["selected"])
            for candidate in item["proposals"]:
                for key, value in candidate["parameters"].items():
                    low, high = self.task["parameter_bounds"][key]
                    self.assertLessEqual(low, value)
                    self.assertLessEqual(value, high)
        self.assertEqual(first["mode"], "synthetic")

    def test_saved_record_roundtrip(self):
        record = run(self.config, self.task)
        with tempfile.TemporaryDirectory() as directory:
            save(record, Path(directory))
            stored = json.loads((Path(directory) / "run.json").read_text())
            self.assertEqual(stored, record)
            self.assertIn("Demonstration data", (Path(directory) / "summary.md").read_text())
            self.assertNotIn("task_file", stored["config"])


if __name__ == "__main__":
    unittest.main()
