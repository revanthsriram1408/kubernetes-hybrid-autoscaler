import os
import sys
import unittest
from pathlib import Path

os.environ["WORK_ITERATIONS"] = "1000"
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


class ApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy"})

    def test_work_and_metrics(self):
        self.assertEqual(self.client.get("/work").status_code, 200)
        metrics = self.client.get("/metrics")
        self.assertEqual(metrics.status_code, 200)
        self.assertIn("demo_requests_total", metrics.text)
        self.assertIn("demo_request_latency_seconds", metrics.text)


if __name__ == "__main__":
    unittest.main()
