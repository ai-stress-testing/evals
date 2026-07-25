#!/usr/bin/env python3
"""Automated judge for the flake-rate / quarantine analyzer problem.

Usage:
    python3 check.py <path-to-solution.py>

Dynamically imports the given module by path, calls its
`analyze_flake_rates(run_history, threshold)` function against a fixed
set of deterministic cases, prints a short pass/fail summary, and exits
0 if every case passes, non-zero otherwise.
"""
import importlib.util
import math
import sys


FIELDS = ("total_runs", "pass_count", "fail_count", "flake_rate", "classification", "quarantine")


def load_solution(path):
    spec = importlib.util.spec_from_file_location("solution_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entries_match(actual, expected):
    if not isinstance(actual, dict):
        return False, f"expected a dict of fields, got {type(actual).__name__}"
    for field in FIELDS:
        if field not in actual:
            return False, f"missing field {field!r}"
    extra = set(actual.keys()) - set(FIELDS)
    if extra:
        return False, f"unexpected extra field(s): {sorted(extra)}"
    for field in ("total_runs", "pass_count", "fail_count", "classification", "quarantine"):
        if actual[field] != expected[field]:
            return False, f"field {field!r}: expected {expected[field]!r}, got {actual[field]!r}"
    if not isinstance(actual["flake_rate"], (int, float)):
        return False, f"field 'flake_rate': expected a number, got {type(actual['flake_rate']).__name__}"
    if not math.isclose(actual["flake_rate"], expected["flake_rate"], abs_tol=1e-9):
        return False, f"field 'flake_rate': expected {expected['flake_rate']!r}, got {actual['flake_rate']!r}"
    return True, ""


def build_cases():
    cases = []

    # 1. Zero-run test: no evidence, must not default to "stable".
    cases.append((
        "zero_runs -> insufficient_data",
        {"t_zero": []},
        0.5,
        {"t_zero": {"total_runs": 0, "pass_count": 0, "fail_count": 0,
                    "flake_rate": 0.0, "classification": "insufficient_data",
                    "quarantine": False}},
    ))

    # 2. 100%-passing test: stable, never quarantined even at threshold 0.
    cases.append((
        "all_pass -> stable",
        {"t_stable": [True, True, True, True]},
        0.0,
        {"t_stable": {"total_runs": 4, "pass_count": 4, "fail_count": 0,
                      "flake_rate": 0.0, "classification": "stable",
                      "quarantine": False}},
    ))

    # 3. 100%-failing test: broken, NOT flaky, NOT quarantined -- even at
    # a threshold of 0.0 which would quarantine any nonzero flake rate.
    cases.append((
        "all_fail -> broken, never quarantined",
        {"t_broken": [False, False, False, False, False, False]},
        0.0,
        {"t_broken": {"total_runs": 6, "pass_count": 0, "fail_count": 6,
                      "flake_rate": 0.0, "classification": "broken",
                      "quarantine": False}},
    ))

    # 4. Genuinely flaky, comfortably above threshold.
    mixed_10 = [True] * 7 + [False] * 3  # 10 runs, 3 fails -> rate 0.3
    cases.append((
        "flaky well above threshold",
        {"t_flaky": mixed_10},
        0.1,
        {"t_flaky": {"total_runs": 10, "pass_count": 7, "fail_count": 3,
                     "flake_rate": 0.3, "classification": "flaky",
                     "quarantine": True}},
    ))

    # 5. Same history, threshold above the flake rate -> flaky but not quarantined.
    cases.append((
        "flaky below threshold -> not quarantined",
        {"t_flaky": mixed_10},
        0.5,
        {"t_flaky": {"total_runs": 10, "pass_count": 7, "fail_count": 3,
                     "flake_rate": 0.3, "classification": "flaky",
                     "quarantine": False}},
    ))

    # 6. Exact tie at the threshold boundary (3/10 == 0.3) -> inclusive -> quarantined.
    cases.append((
        "flaky exactly at threshold -> quarantined (inclusive boundary)",
        {"t_tie": mixed_10},
        0.3,
        {"t_tie": {"total_runs": 10, "pass_count": 7, "fail_count": 3,
                   "flake_rate": 0.3, "classification": "flaky",
                   "quarantine": True}},
    ))

    # 7. Smallest possible flaky case, tie at 0.5.
    cases.append((
        "single pass/fail tie at 0.5 -> quarantined",
        {"t_small_tie": [True, False]},
        0.5,
        {"t_small_tie": {"total_runs": 2, "pass_count": 1, "fail_count": 1,
                         "flake_rate": 0.5, "classification": "flaky",
                         "quarantine": True}},
    ))

    # 8. Independence: several distinct tests (zero-run, broken, stable,
    # flaky-above, flaky-below) evaluated together in a single call must
    # each get their own correct, uncontaminated entry, and the result
    # must contain exactly these keys -- no more, no fewer.
    combined_history = {
        "combo_zero": [],
        "combo_broken": [False, False, False],
        "combo_stable": [True, True],
        "combo_flaky_hi": [True, False, False, False],   # 4 runs, 3 fails -> 0.75
        "combo_flaky_lo": [True, True, True, False],     # 4 runs, 1 fail -> 0.25
    }
    combined_expected = {
        "combo_zero": {"total_runs": 0, "pass_count": 0, "fail_count": 0,
                       "flake_rate": 0.0, "classification": "insufficient_data",
                       "quarantine": False},
        "combo_broken": {"total_runs": 3, "pass_count": 0, "fail_count": 3,
                         "flake_rate": 0.0, "classification": "broken",
                         "quarantine": False},
        "combo_stable": {"total_runs": 2, "pass_count": 2, "fail_count": 0,
                         "flake_rate": 0.0, "classification": "stable",
                         "quarantine": False},
        "combo_flaky_hi": {"total_runs": 4, "pass_count": 1, "fail_count": 3,
                           "flake_rate": 0.75, "classification": "flaky",
                           "quarantine": True},
        "combo_flaky_lo": {"total_runs": 4, "pass_count": 3, "fail_count": 1,
                           "flake_rate": 0.25, "classification": "flaky",
                           "quarantine": False},
    }
    cases.append((
        "multiple independent tests in one call",
        combined_history,
        0.5,
        combined_expected,
    ))

    return cases


def run_checks(module):
    if not hasattr(module, "analyze_flake_rates"):
        print("FAIL: solution module does not define `analyze_flake_rates`")
        return False

    fn = module.analyze_flake_rates
    cases = build_cases()
    all_ok = True

    for description, run_history, threshold, expected in cases:
        try:
            actual = fn(dict(run_history), threshold)
        except Exception as exc:  # noqa: BLE001 - want to report, not crash
            print(f"FAIL [{description}]: raised {type(exc).__name__}: {exc}")
            all_ok = False
            continue

        if not isinstance(actual, dict):
            print(f"FAIL [{description}]: expected a dict return, got {type(actual).__name__}")
            all_ok = False
            continue

        if set(actual.keys()) != set(expected.keys()):
            print(
                f"FAIL [{description}]: key mismatch -- expected {sorted(expected.keys())}, "
                f"got {sorted(actual.keys())}"
            )
            all_ok = False
            continue

        case_ok = True
        for test_name, expected_entry in expected.items():
            ok, reason = entries_match(actual[test_name], expected_entry)
            if not ok:
                print(f"FAIL [{description}] (test={test_name!r}): {reason}")
                case_ok = False

        if case_ok:
            print(f"PASS [{description}]")
        else:
            all_ok = False

    return all_ok


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <path-to-solution.py>")
        sys.exit(1)

    solution_path = sys.argv[1]

    try:
        module = load_solution(solution_path)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: could not import solution module {solution_path!r}: "
              f"{type(exc).__name__}: {exc}")
        sys.exit(1)

    ok = run_checks(module)

    total = len(build_cases())
    if ok:
        print(f"SUMMARY: {total}/{total} cases passed -- PASS")
        sys.exit(0)
    else:
        print("SUMMARY: one or more cases FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
