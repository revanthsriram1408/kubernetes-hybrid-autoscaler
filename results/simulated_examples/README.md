# Simulated and Presentation-Expected Examples

These files are included only to explain the experiment and preserve the values shown as **expected results** in the thesis presentation.

They are not recovered Locust exports, not measured Kubernetes output, and not proof that the autoscaler achieved these values. Do not rename them to `baseline_stats.csv`, `hybrid_stats.csv`, `baseline_replicas.csv`, or `hybrid_replicas.csv`, because those names are reserved for a real rerun.

- `presentation_expected_metrics.csv` records the expected values shown in the presentation.
- `illustrative_hpa_replica_profile.csv` demonstrates a possible HPA timeline consistent with a 35-second ready-replica reaction.
- `illustrative_hybrid_replica_profile.csv` demonstrates a possible hybrid timeline consistent with a 12-second ready-replica reaction.

The two replica profiles are teaching illustrations. The intermediate replica values were not recovered from the original experiment.

For verified evidence, run both modes with identical settings and use only files generated directly under `results/` after `scripts/analyze_results.py` reports `validation: passed`.
