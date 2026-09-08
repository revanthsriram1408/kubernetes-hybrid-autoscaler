import argparse
import subprocess
import time
from collections import deque

import requests

from policy import PolicyConfig, choose_minimum


def prometheus_value(base_url: str, query: str) -> float:
    response = requests.get(f"{base_url}/api/v1/query", params={"query": query}, timeout=5)
    response.raise_for_status()
    result = response.json().get("data", {}).get("result", [])
    if not result:
        raise RuntimeError(f"Prometheus returned no series for: {query}")
    return float(result[0]["value"][1])


def kubectl(*args: str) -> str:
    return subprocess.check_output(["kubectl", *args], text=True, stderr=subprocess.STDOUT).strip()


def ready_replicas(namespace: str, deployment: str) -> int:
    value = kubectl("get", "deployment", deployment, "-n", namespace, "-o", "jsonpath={.status.readyReplicas}")
    return int(value or 0)


def patch_hpa_min(namespace: str, hpa: str, replicas: int) -> None:
    patch = f'{{"spec":{{"minReplicas":{replicas}}}}}'
    kubectl("patch", "hpa", hpa, "-n", namespace, "--type=merge", "-p", patch)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prometheus", default="http://localhost:9090")
    parser.add_argument("--namespace", default="autoscaler-demo")
    parser.add_argument("--deployment", default="hybrid-demo-app")
    parser.add_argument("--hpa", default="hybrid-demo-hpa")
    parser.add_argument("--interval", type=int, default=10)
    args = parser.parse_args()

    history: deque[float] = deque(maxlen=5)
    last_floor = None
    config = PolicyConfig()
    request_query = 'sum(rate(demo_requests_total{endpoint="/work"}[30s]))'
    latency_query = (
        'sum(rate(demo_request_latency_seconds_sum{endpoint="/work"}[30s])) / '
        'clamp_min(sum(rate(demo_request_latency_seconds_count{endpoint="/work"}[30s])), 0.000001)'
    )
    print("Hybrid controller started")
    while True:
        try:
            request_rate = prometheus_value(args.prometheus, request_query)
            latency = prometheus_value(args.prometheus, latency_query)
            history.append(request_rate)
            trend = history[-1] - history[0] if len(history) > 1 else 0.0
            moving_average = sum(history) / len(history)
            current = ready_replicas(args.namespace, args.deployment)
            floor = choose_minimum(request_rate, latency, trend, moving_average, current, config)
            if floor != last_floor:
                patch_hpa_min(args.namespace, args.hpa, floor)
                last_floor = floor
            print(
                f"rps={request_rate:.2f} latency={latency:.3f}s trend={trend:.2f} "
                f"moving_avg={moving_average:.2f} ready={current} hpa_min={floor}",
                flush=True,
            )
        except (requests.RequestException, RuntimeError, subprocess.CalledProcessError, ValueError) as error:
            print(f"[WARN] iteration skipped: {error}", flush=True)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
