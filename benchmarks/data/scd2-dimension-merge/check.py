#!/usr/bin/env python3
"""Deterministic automated judge for the SCD2 dimension merge benchmark.

Usage:
    python3 check.py <path-to-solution.py>

Dynamically imports the given module, calls its `merge_scd2` function
against a fixed set of test cases (each with a precomputed expected
output), prints a pass/fail summary per case, and exits 0 only if every
case passes.
"""
import copy
import importlib.util
import sys


def load_module(path: str):
    spec = importlib.util.spec_from_file_location("solution_under_test", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load a module spec from {path!r}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_rows(rows):
    """Order-independent, duplicate-sensitive canonical form of a row set."""
    if not isinstance(rows, list):
        raise TypeError(f"expected a list of dicts, got {type(rows).__name__}")
    canon = []
    for row in rows:
        if not isinstance(row, dict):
            raise TypeError(f"expected each row to be a dict, got {type(row).__name__}")
        # Sort by key only (keys are unique strings); values may be
        # heterogeneous (None/str/bool) and thus not always orderable.
        canon.append(tuple(sorted(row.items(), key=lambda kv: kv[0])))
    # Order the row tuples themselves via a safely-orderable proxy (repr),
    # since row values (None/str/bool) are not always comparable directly.
    return sorted(canon, key=repr)


def rows_equal(actual, expected):
    return normalize_rows(actual) == normalize_rows(expected)


# ---------------------------------------------------------------------------
# Fixed, deterministic test cases with hand-computed expected outputs.
# ---------------------------------------------------------------------------

TRACKED = ["name", "tier"]

C1_NO_OP = {
    "id": "C1", "name": "Alice", "tier": "gold",
    "effective_start": "2024-01-01", "effective_end": None, "is_current": True,
}

C2_HISTORY = {
    "id": "C2", "name": "Bob", "tier": "silver",
    "effective_start": "2023-01-01", "effective_end": "2023-06-01", "is_current": False,
}
C2_CURRENT_BEFORE = {
    "id": "C2", "name": "Bob", "tier": "gold",
    "effective_start": "2023-06-01", "effective_end": None, "is_current": True,
}

C4_MISSING_FROM_SOURCE = {
    "id": "C4", "name": "Dave", "tier": "gold",
    "effective_start": "2024-01-01", "effective_end": None, "is_current": True,
}

COMBINED_CURRENT = [C1_NO_OP, C2_HISTORY, C2_CURRENT_BEFORE, C4_MISSING_FROM_SOURCE]
COMBINED_SOURCE = [
    {"id": "C1", "name": "Alice", "tier": "gold"},       # no-op (rule 1)
    {"id": "C2", "name": "Robert", "tier": "platinum"},  # 2 attrs change (rule 2)
    {"id": "C3", "name": "Carol", "tier": "silver"},     # brand new (rule 3)
    # C4 intentionally absent -> rule 4
]
COMBINED_AS_OF = "2024-06-01"

COMBINED_EXPECTED = [
    dict(C1_NO_OP),
    dict(C2_HISTORY),
    {
        "id": "C2", "name": "Bob", "tier": "gold",
        "effective_start": "2023-06-01", "effective_end": "2024-06-01", "is_current": False,
    },
    {
        "id": "C2", "name": "Robert", "tier": "platinum",
        "effective_start": "2024-06-01", "effective_end": None, "is_current": True,
    },
    dict(C4_MISSING_FROM_SOURCE),
    {
        "id": "C3", "name": "Carol", "tier": "silver",
        "effective_start": "2024-06-01", "effective_end": None, "is_current": True,
    },
]

CASES = []

CASES.append({
    "name": "no-op update (attributes unchanged)",
    "current_rows": [C1_NO_OP],
    "source_rows": [{"id": "C1", "name": "Alice", "tier": "gold"}],
    "as_of": "2024-06-01",
    "tracked_attributes": TRACKED,
    "expected": [dict(C1_NO_OP)],
})

CASES.append({
    "name": "multiple changed attributes in one batch + prior history preserved",
    "current_rows": [C2_HISTORY, C2_CURRENT_BEFORE],
    "source_rows": [{"id": "C2", "name": "Robert", "tier": "platinum"}],
    "as_of": "2024-06-01",
    "tracked_attributes": TRACKED,
    "expected": [
        dict(C2_HISTORY),
        {
            "id": "C2", "name": "Bob", "tier": "gold",
            "effective_start": "2023-06-01", "effective_end": "2024-06-01", "is_current": False,
        },
        {
            "id": "C2", "name": "Robert", "tier": "platinum",
            "effective_start": "2024-06-01", "effective_end": None, "is_current": True,
        },
    ],
})

CASES.append({
    "name": "brand-new dimension member (no prior row at all)",
    "current_rows": [],
    "source_rows": [{"id": "C3", "name": "Carol", "tier": "silver"}],
    "as_of": "2024-06-01",
    "tracked_attributes": TRACKED,
    "expected": [
        {
            "id": "C3", "name": "Carol", "tier": "silver",
            "effective_start": "2024-06-01", "effective_end": None, "is_current": True,
        },
    ],
})

CASES.append({
    "name": "member missing from this batch's source snapshot is left untouched",
    "current_rows": [C4_MISSING_FROM_SOURCE],
    "source_rows": [],
    "as_of": "2024-06-01",
    "tracked_attributes": TRACKED,
    "expected": [dict(C4_MISSING_FROM_SOURCE)],
})

CASES.append({
    "name": "combined batch (no-op + multi-attr change + new member + missing member)",
    "current_rows": COMBINED_CURRENT,
    "source_rows": COMBINED_SOURCE,
    "as_of": COMBINED_AS_OF,
    "tracked_attributes": TRACKED,
    "expected": COMBINED_EXPECTED,
})

CASES.append({
    "name": "idempotency: re-running an already-applied snapshot is a pure no-op",
    "current_rows": COMBINED_EXPECTED,
    "source_rows": COMBINED_SOURCE,
    "as_of": "2024-07-01",
    "tracked_attributes": TRACKED,
    "expected": COMBINED_EXPECTED,
})


def run_case(fn, case):
    current_rows = copy.deepcopy(case["current_rows"])
    source_rows = copy.deepcopy(case["source_rows"])
    actual = fn(
        current_rows,
        source_rows,
        case["as_of"],
        list(case["tracked_attributes"]),
    )
    return rows_equal(actual, case["expected"]), actual


def main():
    if len(sys.argv) != 2:
        print("usage: python3 check.py <path-to-solution.py>")
        sys.exit(1)

    solution_path = sys.argv[1]

    try:
        module = load_module(solution_path)
    except Exception as exc:
        print(f"FAIL: could not import module at {solution_path!r}: {exc}")
        sys.exit(1)

    if not hasattr(module, "merge_scd2"):
        print(f"FAIL: module at {solution_path!r} does not define merge_scd2")
        sys.exit(1)

    fn = module.merge_scd2

    total = len(CASES)
    passed = 0
    failures = []

    for case in CASES:
        try:
            ok, actual = run_case(fn, case)
        except Exception as exc:
            ok = False
            actual = f"<raised {type(exc).__name__}: {exc}>"

        if ok:
            passed += 1
            print(f"PASS: {case['name']}")
        else:
            failures.append(case["name"])
            print(f"FAIL: {case['name']}")
            print(f"      expected: {normalize_rows(case['expected'])}")
            if isinstance(actual, list):
                print(f"      actual:   {normalize_rows(actual)}")
            else:
                print(f"      actual:   {actual}")

    print(f"\n{passed}/{total} cases passed")

    if failures:
        print(f"FAILED cases: {', '.join(failures)}")
        sys.exit(1)

    print("ALL CASES PASSED")
    sys.exit(0)


if __name__ == "__main__":
    main()
