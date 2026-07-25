#!/usr/bin/env python3
"""Automated judge for the canary burn-rate decision benchmark.

Usage:
    python3 check.py <path-to-solution.py>

Dynamically imports the given module, calls its `canary_decision`
function against a fixed set of deterministic test cases (see
problem.md for the spec each case is exercising), prints a pass/fail
summary, and exits 0 iff every case passes.
"""

from __future__ import annotations

import importlib.util
import sys
import types


def load_module(path: str) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("solution_under_test", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load a module spec from {path!r}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Each case: (name, kwargs, expected_result)
REALISTIC = dict(
    slo_target=0.999,
    burn_rate_rollback=14.4,
    burn_rate_hold=6.0,
    budget_remaining=1.0,
    min_total_requests=100,
)

SPECIAL = dict(
    # Power-of-two denominators keep the burn-rate arithmetic exact in
    # IEEE-754 double precision, so "exactly at threshold" is a real
    # equality, not a floating-point approximation.
    slo_target=0.75,
    burn_rate_rollback=2.0,
    burn_rate_hold=1.0,
    budget_remaining=1.0,
    min_total_requests=1,
)

CASES = [
    (
        "promote: perfect canary, normal budget",
        dict(REALISTIC, samples=[(10000, 10000), (10000, 10000)]),
        "promote",
    ),
    (
        "rollback: burn rate far over the rollback threshold",
        dict(REALISTIC, samples=[(9000, 10000)]),
        "rollback",
    ),
    (
        "hold: burn rate between hold and rollback thresholds",
        dict(REALISTIC, samples=[(9900, 10000)]),
        "hold",
    ),
    (
        "hold: zero-traffic window (all-zero samples)",
        dict(REALISTIC, samples=[(0, 0), (0, 0)]),
        "hold",
    ),
    (
        "hold: empty samples list",
        dict(REALISTIC, samples=[]),
        "hold",
    ),
    (
        "rollback: error budget already exhausted, perfect canary",
        dict(REALISTIC, samples=[(10000, 10000)], budget_remaining=0.0),
        "rollback",
    ),
    (
        "rollback: error budget already negative (over-spent), perfect canary",
        dict(REALISTIC, samples=[(10000, 10000)], budget_remaining=-0.2),
        "rollback",
    ),
    (
        "promote: volume-weighted aggregate, not a naive per-sample mean",
        dict(REALISTIC, samples=[(1000, 1000), (0, 1)], min_total_requests=1),
        "promote",
    ),
    (
        "rollback: burn rate lands exactly on the rollback threshold",
        dict(SPECIAL, samples=[(4, 8)]),
        "rollback",
    ),
    (
        "hold: burn rate lands exactly on the hold threshold",
        dict(SPECIAL, samples=[(6, 8)]),
        "hold",
    ),
    (
        "promote: burn rate below the hold threshold (special config sanity check)",
        dict(SPECIAL, samples=[(7, 8)]),
        "promote",
    ),
]


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: python3 {sys.argv[0]} <path-to-solution.py>")
        return 1

    solution_path = sys.argv[1]

    try:
        module = load_module(solution_path)
    except Exception as exc:  # noqa: BLE001 - want to report any import failure
        print(f"FAIL: could not import {solution_path!r}: {exc}")
        return 1

    fn = getattr(module, "canary_decision", None)
    if fn is None or not callable(fn):
        print(f"FAIL: {solution_path!r} does not define a callable canary_decision()")
        return 1

    failures = []
    for name, kwargs, expected in CASES:
        try:
            actual = fn(**kwargs)
        except Exception as exc:  # noqa: BLE001 - a raising solution is a failing solution
            failures.append(f"  [ERROR] {name}: raised {exc!r}")
            continue
        if actual != expected:
            failures.append(f"  [FAIL]  {name}: expected {expected!r}, got {actual!r}")

    total = len(CASES)
    passed = total - len(failures)
    print(f"canary-burn-rate-decision check: {passed}/{total} cases passed")

    if failures:
        print("Failures:")
        for line in failures:
            print(line)
        return 1

    print("All cases passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
