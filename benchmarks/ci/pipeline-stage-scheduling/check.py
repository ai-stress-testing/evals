#!/usr/bin/env python3
"""Automated judge for the pipeline-stage-scheduling benchmark.

Usage:
    python3 check.py <path-to-solution.py>

Dynamically imports the given module by path, exercises `schedule_pipeline`
against a fixed, deterministic set of test cases (diamond dependency,
disconnected stages, asymmetric fan-in, self-loop, multi-stage cycle, a
cycle coexisting with valid stages, and an undeclared-dependency error),
prints a pass/fail summary per case, and exits 0 iff every case passes,
non-zero otherwise.
"""
import importlib.util
import sys


def load_module(path: str):
    spec = importlib.util.spec_from_file_location("solution_under_test", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load spec for {path!r}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_levels(levels):
    """Sort stage names within each level; level order itself is meaningful
    and must not be reordered."""
    return [sorted(bucket) for bucket in levels]


def is_valid_cycle_report(stages, cycle):
    if not isinstance(cycle, list) or len(cycle) < 2:
        return False, "cycle report must be a list of length >= 2"
    if cycle[0] != cycle[-1]:
        return False, "cycle report must start and end on the same stage"
    for name in cycle:
        if name not in stages:
            return False, f"cycle references unknown stage {name!r}"
    for i in range(len(cycle) - 1):
        a, b = cycle[i], cycle[i + 1]
        if b not in stages[a]:
            return False, (
                f"cycle step {a!r} -> {b!r} is not a real dependency edge "
                f"(stages[{a!r}] = {stages[a]!r})"
            )
    return True, ""


# Each case: (name, stages, expectation)
# expectation is one of:
#   ("ok", expected_levels)
#   ("cycle",)
#   ("error",)
CASES = [
    (
        "empty_pipeline",
        {},
        ("ok", []),
    ),
    (
        "single_stage",
        {"only": []},
        ("ok", [["only"]]),
    ),
    (
        "diamond_dependency",
        {
            "checkout": [],
            "lint": ["checkout"],
            "test": ["checkout"],
            "build": ["lint", "test"],
            "deploy": ["build"],
        },
        ("ok", [["checkout"], ["lint", "test"], ["build"], ["deploy"]]),
    ),
    (
        "disconnected_stages",
        {"a": [], "b": [], "c": ["a"], "d": ["b"]},
        ("ok", [["a", "b"], ["c", "d"]]),
    ),
    (
        "asymmetric_fanin",
        {
            "a": [],
            "b": ["a"],
            "c": ["b"],
            "d": [],
            "e": ["d"],
            "f": ["c", "e"],
        },
        # level(a)=0 level(d)=0; level(b)=1 level(e)=1; level(c)=2;
        # level(f) must wait for the LONGER chain (c, level 2) -> level 3.
        ("ok", [["a", "d"], ["b", "e"], ["c"], ["f"]]),
    ),
    (
        "self_loop_cycle",
        {"x": ["x"]},
        ("cycle",),
    ),
    (
        "three_stage_cycle",
        {"a": ["b"], "b": ["c"], "c": ["a"]},
        ("cycle",),
    ),
    (
        "cycle_alongside_valid_stages",
        {"a": [], "b": ["a"], "x": ["y"], "y": ["x"]},
        ("cycle",),
    ),
    (
        "undeclared_dependency_raises",
        {"a": ["ghost"]},
        ("error",),
    ),
]


def run_cases(module):
    results = []
    fn = getattr(module, "schedule_pipeline", None)
    if fn is None or not callable(fn):
        return [("module_shape", False, "no callable schedule_pipeline() found")]

    for name, stages, expectation in CASES:
        kind = expectation[0]
        try:
            result = fn(stages)
        except Exception as exc:  # noqa: BLE001 - judge must catch anything
            if kind == "error":
                results.append((name, True, f"raised as expected: {exc!r}"))
            else:
                results.append((name, False, f"raised unexpectedly: {exc!r}"))
            continue

        if kind == "error":
            results.append(
                (name, False, f"expected an exception, got return value {result!r}")
            )
            continue

        if not isinstance(result, dict) or "ok" not in result:
            results.append((name, False, f"malformed return value: {result!r}"))
            continue

        if kind == "ok":
            if result.get("ok") is not True:
                results.append(
                    (name, False, f"expected ok=True, got {result!r}")
                )
                continue
            expected_levels = expectation[1]
            actual = result.get("levels")
            if not isinstance(actual, list):
                results.append((name, False, f"'levels' missing/not a list: {result!r}"))
                continue
            if canonical_levels(actual) != canonical_levels(expected_levels):
                results.append(
                    (
                        name,
                        False,
                        f"expected levels {expected_levels!r}, got {actual!r}",
                    )
                )
                continue
            results.append((name, True, ""))

        elif kind == "cycle":
            if result.get("ok") is not False:
                results.append(
                    (name, False, f"expected ok=False (cycle), got {result!r}")
                )
                continue
            cycle = result.get("cycle")
            ok, reason = is_valid_cycle_report(stages, cycle)
            if not ok:
                results.append((name, False, f"invalid cycle report: {reason}"))
                continue
            results.append((name, True, ""))

    return results


def main():
    if len(sys.argv) != 2:
        print("usage: python3 check.py <path-to-solution.py>", file=sys.stderr)
        sys.exit(2)

    path = sys.argv[1]
    try:
        module = load_module(path)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: could not import {path!r}: {exc!r}")
        sys.exit(1)

    results = run_cases(module)

    failures = 0
    for name, passed, detail in results:
        status = "PASS" if passed else "FAIL"
        if passed:
            print(f"[{status}] {name}")
        else:
            print(f"[{status}] {name}: {detail}")
            failures += 1

    total = len(results)
    print(f"{total - failures}/{total} cases passed")

    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
