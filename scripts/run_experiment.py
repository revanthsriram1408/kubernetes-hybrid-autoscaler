import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def kubectl(*args: str) -> None:
    subprocess.run(["kubectl", *args], check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["baseline", "hybrid"])
    parser.add_argument("--host", default="http://localhost:8000")
    parser.add_argument("--users", type=int, default=40)
    parser.add_argument("--spawn-rate", type=int, default=20)
    parser.add_argument("--duration", default="3m")
    args = parser.parse_args()
    subprocess.run([sys.executable, str(ROOT / "scripts" / "preflight.py")], check=True)
    RESULTS.mkdir(exist_ok=True)

    kubectl("patch", "hpa", "hybrid-demo-hpa", "-n", "autoscaler-demo", "--type=merge", "-p", '{"spec":{"minReplicas":1}}')
    kubectl("scale", "deployment", "hybrid-demo-app", "-n", "autoscaler-demo", "--replicas=1")
    kubectl("rollout", "restart", "deployment/hybrid-demo-app", "-n", "autoscaler-demo")
    kubectl("rollout", "status", "deployment/hybrid-demo-app", "-n", "autoscaler-demo", "--timeout=180s")
    time.sleep(20)

    controller = None
    if args.mode == "hybrid":
        controller = subprocess.Popen([sys.executable, str(ROOT / "controller" / "hybrid_controller.py")])
        time.sleep(5)
    logger = subprocess.Popen([
        sys.executable, str(ROOT / "scripts" / "replica_logger.py"),
        str(RESULTS / f"{args.mode}_replicas.csv"),
    ])

    config = {
        "mode": args.mode, "host": args.host, "users": args.users,
        "spawn_rate": args.spawn_rate, "duration": args.duration,
    }
    (RESULTS / f"{args.mode}_config.json").write_text(json.dumps(config, indent=2) + "\n")
    try:
        subprocess.run([
            "locust", "-f", str(ROOT / "loadtest" / "locustfile.py"), "--headless",
            "--host", args.host, "-u", str(args.users), "-r", str(args.spawn_rate),
            "-t", args.duration, "--csv", str(RESULTS / args.mode), "--only-summary",
        ], check=True)
    finally:
        for process in (controller, logger):
            if process is not None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
        kubectl("patch", "hpa", "hybrid-demo-hpa", "-n", "autoscaler-demo", "--type=merge", "-p", '{"spec":{"minReplicas":1}}')
    print(f"Completed {args.mode} run. Review files under {RESULTS}")


if __name__ == "__main__":
    main()
