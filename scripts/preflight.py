import shutil
import subprocess
import sys

import requests


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT, timeout=20).strip()


def main() -> None:
    errors = []
    for executable in ("kubectl",):
        if shutil.which(executable) is None:
            errors.append(f"{executable} is not installed or not on PATH")
    if not errors:
        try:
            command("kubectl", "cluster-info")
            command("kubectl", "get", "deployment", "hybrid-demo-app", "-n", "autoscaler-demo")
            command("kubectl", "get", "hpa", "hybrid-demo-hpa", "-n", "autoscaler-demo")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
            errors.append(f"Kubernetes check failed: {error}")
    for label, url in (
        ("application", "http://localhost:8000/health"),
        ("Prometheus", "http://localhost:9090/-/ready"),
    ):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as error:
            errors.append(f"{label} check failed at {url}: {error}")
    if errors:
        print("Preflight failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("Preflight passed: cluster, workload, HPA, application, and Prometheus are reachable")


if __name__ == "__main__":
    main()
