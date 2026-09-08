# Results

This directory is intentionally empty until a valid baseline and hybrid benchmark is run.

Generated files are ignored by Git until they are reviewed. After `scripts/analyze_results.py` reports `validation: passed`, explicitly add these evidence files:

- `baseline_config.json` and `hybrid_config.json`
- `baseline_stats.csv` and `hybrid_stats.csv`
- `baseline_replicas.csv` and `hybrid_replicas.csv`
- `validated_metrics.json`
- `validated_scaling_comparison.png`

Do not publish charts from failed or incomparable runs.

The `simulated_examples/` subfolder is safe to publish for design explanation because its filenames, columns, and README explicitly identify the values as unmeasured examples. It is not a substitute for the files above.
