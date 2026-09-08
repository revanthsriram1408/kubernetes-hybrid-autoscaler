from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyConfig:
    base_min: int = 1
    warm_min: int = 2
    max_replicas: int = 5
    slo_latency_seconds: float = 1.5
    trend_threshold_rps: float = 0.30
    high_request_rate: float = 2.0
    low_request_rate: float = 0.20


def choose_minimum(
    request_rate: float,
    latency_seconds: float,
    trend_rps: float,
    moving_average_rps: float,
    current_ready: int,
    config: PolicyConfig = PolicyConfig(),
) -> int:
    """Return the HPA floor; HPA still owns CPU-based scaling above this value."""
    proactive = trend_rps > config.trend_threshold_rps and moving_average_rps > 0.5
    overloaded = latency_seconds > config.slo_latency_seconds or request_rate > config.high_request_rate
    if proactive or overloaded:
        return min(config.max_replicas, max(config.warm_min, current_ready + 1))
    if request_rate > 0.5:
        return config.warm_min
    if request_rate < config.low_request_rate and latency_seconds < config.slo_latency_seconds / 2:
        return config.base_min
    return max(config.base_min, min(current_ready, config.max_replicas))
