"""Reference solution for the canary burn-rate decision benchmark.

See problem.md in this directory for the full spec.
"""

from __future__ import annotations


def canary_decision(
    samples: list[tuple[int, int]],
    slo_target: float,
    burn_rate_rollback: float,
    burn_rate_hold: float,
    budget_remaining: float,
    min_total_requests: int = 1,
) -> str:
    # 1. Error budget already exhausted: nothing else matters.
    if budget_remaining <= 0:
        return "rollback"

    # 2. Aggregate counts across the whole window (volume-weighted, not a
    #    per-sample mean).
    total_good = 0
    total_requests = 0
    for good, total in samples:
        total_good += good
        total_requests += total

    # 3. Insufficient data to make a promote/rollback call.
    if total_requests < min_total_requests:
        return "hold"

    success_ratio = total_good / total_requests
    error_ratio = 1 - success_ratio
    allowed_error_ratio = 1 - slo_target

    if allowed_error_ratio <= 0:
        # Degenerate SLO (100% target); any error at all is an infinite
        # burn rate.
        burn_rate = float("inf") if error_ratio > 0 else 0.0
    else:
        burn_rate = error_ratio / allowed_error_ratio

    # 4. Threshold decision, inclusive boundaries favor the worse bucket.
    if burn_rate >= burn_rate_rollback:
        return "rollback"
    if burn_rate >= burn_rate_hold:
        return "hold"
    return "promote"
