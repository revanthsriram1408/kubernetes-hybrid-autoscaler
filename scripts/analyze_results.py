import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def aggregate_stats(path: Path) -> dict:
    frame = pd.read_csv(path)
    row = frame[frame["Name"] == "Aggregated"]
    if row.empty:
        raise ValueError(f"Aggregated Locust row missing from {path.name}")
    item = row.iloc[0]
    requests = int(item["Request Count"])
    failures = int(item["Failure Count"])
    return {
        "requests": requests,
        "failures": failures,
        "failure_rate": failures / requests if requests else 1.0,
        "average_response_ms": float(item["Average Response Time"]),
        "p95_response_ms": float(item["95%"]),
        "requests_per_second": float(item["Requests/s"]),
    }


def reaction_time(path: Path) -> tuple[float, pd.DataFrame]:
    frame = pd.read_csv(path)
    scaled = frame[frame["ready_replicas"] > 1]
    if scaled.empty:
        raise ValueError(f"No ready scale-up event found in {path.name}")
    return float(scaled.iloc[0]["elapsed_seconds"]), frame


def validate_configs(left: dict, right: dict) -> None:
    compared = ("host", "users", "spawn_rate", "duration")
    differences = [key for key in compared if left.get(key) != right.get(key)]
    if differences:
        raise ValueError(f"Experiment settings differ: {', '.join(differences)}")


def main() -> None:
    baseline_config = json.loads((RESULTS / "baseline_config.json").read_text())
    hybrid_config = json.loads((RESULTS / "hybrid_config.json").read_text())
    validate_configs(baseline_config, hybrid_config)
    baseline_stats = aggregate_stats(RESULTS / "baseline_stats.csv")
    hybrid_stats = aggregate_stats(RESULTS / "hybrid_stats.csv")
    for name, stats in (("baseline", baseline_stats), ("hybrid", hybrid_stats)):
        if stats["failure_rate"] > 0.01:
            raise ValueError(f"{name} failure rate is {stats['failure_rate']:.2%}; results are invalid")
    baseline_reaction, baseline_replicas = reaction_time(RESULTS / "baseline_replicas.csv")
    hybrid_reaction, hybrid_replicas = reaction_time(RESULTS / "hybrid_replicas.csv")
    metrics = {
        "validation": "passed",
        "workload": {key: baseline_config[key] for key in ("host", "users", "spawn_rate", "duration")},
        "baseline": {**baseline_stats, "scale_reaction_seconds": baseline_reaction},
        "hybrid": {**hybrid_stats, "scale_reaction_seconds": hybrid_reaction},
        "scaling_reaction_improvement_ratio": round(baseline_reaction / hybrid_reaction, 3),
        "scaling_reaction_reduction_percent": round(100 * (baseline_reaction - hybrid_reaction) / baseline_reaction, 2),
    }
    (RESULTS / "validated_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].bar(["HPA baseline", "Hybrid"], [baseline_reaction, hybrid_reaction], color=["#2563eb", "#f97316"])
    axes[0].set_title("Ready-Replica Scale Reaction")
    axes[0].set_ylabel("Seconds from load start")
    axes[1].plot(baseline_replicas["elapsed_seconds"], baseline_replicas["ready_replicas"], label="HPA baseline")
    axes[1].plot(hybrid_replicas["elapsed_seconds"], hybrid_replicas["ready_replicas"], label="Hybrid")
    axes[1].set_title("Ready Replicas Over Time")
    axes[1].set_xlabel("Elapsed seconds")
    axes[1].set_ylabel("Ready replicas")
    axes[1].legend()
    plt.tight_layout()
    plt.savefig(RESULTS / "validated_scaling_comparison.png", dpi=180)
    plt.close()
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
