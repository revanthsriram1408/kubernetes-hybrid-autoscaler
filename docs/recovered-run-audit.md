# Recovered Run Audit

The recovered April 17, 2026 artifacts were reviewed before preparing this public portfolio version.

## Findings

- Baseline Locust output: 61,664 requests and 61,664 failures (100% failed).
- Hybrid Locust output: 1,305 requests and 1,305 failures (100% failed).
- Both modes reported approximately 4.09 seconds average response time, reflecting failed requests rather than application performance.
- Both replica logs contained only one replica; neither run demonstrated a scale-up event.
- Baseline and hybrid test durations differed substantially, so failure counts were not comparable.
- The original presentation showed expected figures rather than measurements from these CSVs.

## Decision

The old CSVs and charts are excluded from the public repository. The rebuilt experiment harness adds connectivity checks, identical configurations, failure-rate validation, ready-replica logging, and automatic refusal of unsupported performance claims.
