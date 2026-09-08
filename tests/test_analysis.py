import json
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_results import aggregate_stats, reaction_time, validate_configs  # noqa: E402


class AnalysisTests(unittest.TestCase):
    def test_reaction_time_uses_first_ready_scale_event(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "replicas.csv"
            pd.DataFrame({
                "elapsed_seconds": [0.0, 2.0, 4.0, 6.0],
                "desired_replicas": [1, 2, 2, 3],
                "ready_replicas": [1, 1, 2, 3],
            }).to_csv(path, index=False)
            value, _ = reaction_time(path)
            self.assertEqual(value, 4.0)

    def test_no_scale_event_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "replicas.csv"
            pd.DataFrame({
                "elapsed_seconds": [0.0, 2.0], "desired_replicas": [1, 1], "ready_replicas": [1, 1]
            }).to_csv(path, index=False)
            with self.assertRaises(ValueError):
                reaction_time(path)

    def test_different_workloads_are_rejected(self):
        left = {"host": "x", "users": 40, "spawn_rate": 20, "duration": "3m"}
        right = {**left, "users": 20}
        with self.assertRaises(ValueError):
            validate_configs(left, right)


if __name__ == "__main__":
    unittest.main()
