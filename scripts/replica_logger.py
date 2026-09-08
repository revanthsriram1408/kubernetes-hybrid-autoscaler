import argparse
import csv
import subprocess
import time
from pathlib import Path


def replica_state(namespace: str, deployment: str) -> tuple[int, int]:
    output = subprocess.check_output(
        ["kubectl", "get", "deployment", deployment, "-n", namespace,
         "-o", "jsonpath={.spec.replicas},{.status.readyReplicas}"],
        text=True,
        stderr=subprocess.STDOUT,
    ).strip()
    desired, ready = (output.split(",") + [""])[:2]
    return int(desired or 0), int(ready or 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--namespace", default="autoscaler-demo")
    parser.add_argument("--deployment", default="hybrid-demo-app")
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    with args.output.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["elapsed_seconds", "desired_replicas", "ready_replicas"])
        while True:
            try:
                desired, ready = replica_state(args.namespace, args.deployment)
                writer.writerow([round(time.monotonic() - start, 3), desired, ready])
                stream.flush()
                time.sleep(args.interval)
            except KeyboardInterrupt:
                break
            except (subprocess.CalledProcessError, ValueError) as error:
                print(f"Replica sample skipped: {error}", flush=True)
                time.sleep(args.interval)


if __name__ == "__main__":
    main()
