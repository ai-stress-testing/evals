#!/usr/bin/env python3
"""Automated judge for the CIDR longest-prefix-match (LPM) routing benchmark.

Usage:
    python3 benchmarks/networking/cidr-longest-prefix-match/check.py <path-to-solution.py>

Dynamically imports the given module by path, calls its `resolve_routes`
function against a fixed set of deterministic test cases (see problem.md),
prints a pass/fail summary, and exits 0 iff every case passes, 1 otherwise.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def _load_module(solution_path: str):
    path = Path(solution_path).resolve()
    if not path.is_file():
        print(f"FAIL: solution file not found: {path}")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("candidate_solution", path)
    if spec is None or spec.loader is None:
        print(f"FAIL: could not build an import spec for {path}")
        sys.exit(1)

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - deliberately broad: any import-time
        # error in a candidate solution is a checker failure, not a crash.
        print(f"FAIL: solution raised on import: {exc!r}")
        sys.exit(1)

    if not hasattr(module, "resolve_routes"):
        print("FAIL: solution module does not define `resolve_routes`")
        sys.exit(1)

    return module


# Each case: (description, routing_table, destinations, expected_outputs)
CASES: List[Tuple[str, List[Tuple[str, str]], List[str], List[Optional[str]]]] = [
    (
        "single non-overlapping block, direct hit",
        [("10.0.0.0/24", "hop-A")],
        ["10.0.0.5"],
        ["hop-A"],
    ),
    (
        "no matching route at all -> None",
        [("10.0.0.0/24", "hop-A")],
        ["192.168.1.1"],
        [None],
    ),
    (
        "overlapping blocks: longest prefix (most specific) wins",
        [("10.0.0.0/8", "hop-A"), ("10.1.0.0/16", "hop-B")],
        ["10.1.2.3", "10.2.2.3"],
        ["hop-B", "hop-A"],
    ),
    (
        "table order does not matter: more-specific route listed first",
        [("10.1.0.0/16", "hop-B"), ("10.0.0.0/8", "hop-A")],
        ["10.1.2.3", "10.2.2.3"],
        ["hop-B", "hop-A"],
    ),
    (
        "three-level nesting resolves to the deepest match",
        [
            ("0.0.0.0/0", "hop-default"),
            ("10.0.0.0/8", "hop-A"),
            ("10.1.0.0/16", "hop-B"),
            ("10.1.2.0/24", "hop-C"),
        ],
        ["10.1.2.5", "10.1.9.9", "10.9.9.9", "8.8.8.8"],
        ["hop-C", "hop-B", "hop-A", "hop-default"],
    ),
    (
        "subnet boundary addresses: network address and last address both match",
        [("10.0.0.0/24", "hop-A")],
        ["10.0.0.0", "10.0.0.255"],
        ["hop-A", "hop-A"],
    ),
    (
        "/32 host route matches only the exact address",
        [("10.0.0.0/8", "hop-A"), ("10.0.0.5/32", "hop-host")],
        ["10.0.0.5", "10.0.0.6"],
        ["hop-host", "hop-A"],
    ),
    (
        "duplicate CIDR string: later table entry wins",
        [("10.0.0.0/24", "hop-old"), ("192.168.0.0/16", "hop-other"), ("10.0.0.0/24", "hop-new")],
        ["10.0.0.7"],
        ["hop-new"],
    ),
    (
        "IPv4 destination never matches an IPv6 block, even an all-covering ::/0",
        [("::/0", "hop-v6-default"), ("10.0.0.0/8", "hop-v4")],
        ["10.5.5.5"],
        ["hop-v4"],
    ),
    (
        "IPv6 longest-prefix-match with boundary and default route",
        [
            ("::/0", "hop-v6-default"),
            ("2001:db8::/32", "hop-v6-a"),
            ("2001:db8:1::/48", "hop-v6-b"),
        ],
        ["2001:db8:1::1", "2001:db8:2::1", "::1", "2001:db8:1::ffff"],
        ["hop-v6-b", "hop-v6-a", "hop-v6-default", "hop-v6-b"],
    ),
    (
        "/128 IPv6 host route matches only the exact address",
        [("2001:db8::/32", "hop-v6-a"), ("2001:db8::5/128", "hop-v6-host")],
        ["2001:db8::5", "2001:db8::6"],
        ["hop-v6-host", "hop-v6-a"],
    ),
    (
        "empty routing table -> every destination is None",
        [],
        ["10.0.0.1", "::1"],
        [None, None],
    ),
    (
        "empty destinations -> empty result list",
        [("10.0.0.0/8", "hop-A")],
        [],
        [],
    ),
]


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 check.py <path-to-solution.py>")
        sys.exit(1)

    module = _load_module(sys.argv[1])

    total = len(CASES)
    failures = []

    for description, routing_table, destinations, expected in CASES:
        try:
            actual = module.resolve_routes(list(routing_table), list(destinations))
        except Exception as exc:  # noqa: BLE001 - a raising solution is a failed case
            failures.append(f"  - [{description}] raised {exc!r}")
            continue

        if actual != expected:
            failures.append(
                f"  - [{description}] expected {expected!r}, got {actual!r}"
            )

    passed = total - len(failures)
    print(f"CIDR longest-prefix-match check: {passed}/{total} cases passed")

    if failures:
        print("Failures:")
        for line in failures:
            print(line)
        sys.exit(1)

    print("All cases passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
