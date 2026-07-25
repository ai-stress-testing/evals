"""Deliberately-broken variant of the canary burn-rate decision function.

Bug (single, intentional): the threshold comparisons use strict `>`
instead of the spec's inclusive `>=`. Everywhere else this matches
reference_solution.py. This silently mis-classifies any burn rate that
lands exactly on a threshold, pushing it one bucket "safer" than the spec
requires (e.g. a canary burning error budget at *exactly* the rollback
multiplier gets held instead of rolled back).
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
    if budget_remaining <= 0:
        return "rollback"

    total_good = 0
    total_requests = 0
    for good, total in samples:
        total_good += good
        total_requests += total

    if total_requests < min_total_requests:
        return "hold"

    success_ratio = total_good / total_requests
    error_ratio = 1 - success_ratio
    allowed_error_ratio = 1 - slo_target

    if allowed_error_ratio <= 0:
        burn_rate = float("inf") if error_ratio > 0 else 0.0
    else:
        burn_rate = error_ratio / allowed_error_ratio

    # BUG: strict `>` instead of the spec's inclusive `>=` -- an exact
    # threshold hit is mis-classified into the safer bucket.
    if burn_rate > burn_rate_rollback:
        return "rollback"
    if burn_rate > burn_rate_hold:
        return "hold"
    return "promote"
