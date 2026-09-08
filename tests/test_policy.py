import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "controller"))

from policy import PolicyConfig, choose_minimum  # noqa: E402


class PolicyTests(unittest.TestCase):
    def test_idle_traffic_returns_to_base(self):
        result = choose_minimum(0.05, 0.1, -0.2, 0.1, 2)
        self.assertEqual(result, 1)

    def test_rising_traffic_scales_proactively(self):
        result = choose_minimum(1.0, 0.4, 0.8, 0.7, 1)
        self.assertEqual(result, 2)

    def test_high_latency_increases_floor(self):
        result = choose_minimum(1.0, 2.2, 0.0, 1.0, 2)
        self.assertEqual(result, 3)

    def test_floor_never_exceeds_limit(self):
        config = PolicyConfig(max_replicas=5)
        result = choose_minimum(8.0, 4.0, 2.0, 5.0, 5, config)
        self.assertEqual(result, 5)


if __name__ == "__main__":
    unittest.main()
