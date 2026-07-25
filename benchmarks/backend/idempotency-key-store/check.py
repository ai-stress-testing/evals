#!/usr/bin/env python3
"""Automated judge for the idempotency-key-store benchmark.

Usage:
    python3 check.py <path-to-solution.py>

Dynamically imports the given module by path, exercises it against a fixed,
deterministic set of test cases (a fake, manually-advanced clock — no
wall-clock, no randomness), prints a pass/fail summary per case, and exits
0 iff every case passes, non-zero otherwise.
"""
import importlib.util
import sys
import traceback


class FakeClock:
    """Zero-argument callable clock, manually advanced. Deterministic."""

    def __init__(self, start: float = 0.0):
        self._t = float(start)

    def __call__(self) -> float:
        return self._t

    def advance(self, dt: float) -> None:
        self._t += dt

    def set(self, t: float) -> None:
        self._t = float(t)


class Counter:
    """Tracks how many times operation() actually ran, and returns a
    fresh, distinguishable value each call."""

    def __init__(self):
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return f"result-{self.calls}"


def load_module(path: str):
    spec = importlib.util.spec_from_file_location("solution_under_test", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load spec for {path!r}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cases(module):
    """Returns a list of (case_name, passed: bool, detail: str)."""
    results = []

    def record(name, passed, detail=""):
        results.append((name, passed, detail))

    IdempotencyStore = getattr(module, "IdempotencyStore", None)
    IdempotencyConflictError = getattr(module, "IdempotencyConflictError", None)

    if IdempotencyStore is None or IdempotencyConflictError is None:
        record(
            "required names present",
            False,
            "module must define both IdempotencyStore and IdempotencyConflictError",
        )
        return results
    record("required names present", True)

    # --- Case 1: basic dedup within TTL, same fingerprint served from cache ---
    try:
        clock = FakeClock(0.0)
        store = IdempotencyStore(ttl_seconds=100.0, clock=clock)
        op = Counter()

        r1 = store.execute("k1", "fp1", op)
        clock.advance(10.0)
        r2 = store.execute("k1", "fp1", op)

        ok = (r1 == r2 == "result-1") and op.calls == 1
        record(
            "case1_basic_dedup",
            ok,
            f"r1={r1!r} r2={r2!r} calls={op.calls} (expected r1==r2=='result-1', calls==1)",
        )
    except Exception:
        record("case1_basic_dedup", False, "raised: " + traceback.format_exc(limit=1))

    # --- Case 2: TTL boundary is inclusive -> treated as expired, re-executes ---
    try:
        clock = FakeClock(0.0)
        store = IdempotencyStore(ttl_seconds=100.0, clock=clock)
        op = Counter()

        r1 = store.execute("k2", "fp1", op)
        clock.advance(100.0)  # exactly at ttl_seconds -> must be expired
        r2 = store.execute("k2", "fp1", op)

        ok = r1 == "result-1" and r2 == "result-2" and op.calls == 2
        record(
            "case2_ttl_boundary_inclusive_expiry",
            ok,
            f"r1={r1!r} r2={r2!r} calls={op.calls} "
            "(expected r1=='result-1', r2=='result-2', calls==2 -- boundary must expire)",
        )
    except Exception:
        record(
            "case2_ttl_boundary_inclusive_expiry",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    # --- Case 3: still-live entry, one tick before boundary -> still cached ---
    try:
        clock = FakeClock(0.0)
        store = IdempotencyStore(ttl_seconds=100.0, clock=clock)
        op = Counter()

        r1 = store.execute("k3", "fp1", op)
        clock.advance(99.999)  # just under ttl -> still live
        r2 = store.execute("k3", "fp1", op)

        ok = r1 == r2 == "result-1" and op.calls == 1
        record(
            "case3_just_under_ttl_still_cached",
            ok,
            f"r1={r1!r} r2={r2!r} calls={op.calls} (expected cached, calls==1)",
        )
    except Exception:
        record(
            "case3_just_under_ttl_still_cached",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    # --- Case 4: conflicting fingerprint within TTL -> IdempotencyConflictError ---
    try:
        clock = FakeClock(0.0)
        store = IdempotencyStore(ttl_seconds=100.0, clock=clock)
        op = Counter()

        store.execute("k4", "fpA", op)
        clock.advance(1.0)
        raised = False
        try:
            store.execute("k4", "fpB", op)
        except IdempotencyConflictError:
            raised = True

        ok = raised and op.calls == 1
        record(
            "case4_conflict_raises_and_skips_operation",
            ok,
            f"raised={raised} calls={op.calls} (expected raised==True, calls==1)",
        )
    except Exception:
        record(
            "case4_conflict_raises_and_skips_operation",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    # --- Case 5: different fingerprint AFTER expiry -> no conflict, fresh run ---
    try:
        clock = FakeClock(0.0)
        store = IdempotencyStore(ttl_seconds=100.0, clock=clock)
        op = Counter()

        r1 = store.execute("k5", "fpA", op)
        clock.advance(100.0)  # expired
        r2 = store.execute("k5", "fpB", op)  # different fingerprint, but fresh window

        ok = r1 == "result-1" and r2 == "result-2" and op.calls == 2
        record(
            "case5_conflict_only_before_expiry",
            ok,
            f"r1={r1!r} r2={r2!r} calls={op.calls} (expected no error, calls==2)",
        )
    except Exception:
        record(
            "case5_conflict_only_before_expiry",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    # --- Case 6: independent keys never interact ---
    try:
        clock = FakeClock(0.0)
        store = IdempotencyStore(ttl_seconds=100.0, clock=clock)
        op_a = Counter()
        op_b = Counter()

        ra1 = store.execute("keyA", "fp", op_a)
        rb1 = store.execute("keyB", "fp", op_b)
        clock.advance(5.0)
        ra2 = store.execute("keyA", "fp", op_a)
        rb2 = store.execute("keyB", "fp", op_b)

        ok = (
            ra1 == ra2 == "result-1"
            and rb1 == rb2 == "result-1"
            and op_a.calls == 1
            and op_b.calls == 1
        )
        record(
            "case6_independent_keys",
            ok,
            f"ra1={ra1!r} ra2={ra2!r} rb1={rb1!r} rb2={rb2!r} "
            f"calls_a={op_a.calls} calls_b={op_b.calls}",
        )
    except Exception:
        record("case6_independent_keys", False, "raised: " + traceback.format_exc(limit=1))

    # --- Case 7: failed operation is not cached; a retry re-invokes operation ---
    try:
        clock = FakeClock(0.0)
        store = IdempotencyStore(ttl_seconds=100.0, clock=clock)

        attempts = {"n": 0}

        def flaky():
            attempts["n"] += 1
            if attempts["n"] == 1:
                raise ValueError("transient failure")
            return f"ok-{attempts['n']}"

        raised = False
        try:
            store.execute("k7", "fp1", flaky)
        except ValueError:
            raised = True

        # No time has passed at all -- retry must still re-invoke, not cache
        # the failure and not treat it as a conflict.
        r2 = store.execute("k7", "fp1", flaky)

        ok = raised and attempts["n"] == 2 and r2 == "ok-2"
        record(
            "case7_failed_operation_not_cached",
            ok,
            f"raised={raised} attempts={attempts['n']} r2={r2!r} "
            "(expected raised==True, attempts==2, r2=='ok-2')",
        )
    except Exception:
        record(
            "case7_failed_operation_not_cached",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    # --- Case 8: empty-string key/fingerprint handled like any other value ---
    try:
        clock = FakeClock(0.0)
        store = IdempotencyStore(ttl_seconds=100.0, clock=clock)
        op = Counter()

        r1 = store.execute("", "", op)
        r2 = store.execute("", "", op)

        ok = r1 == r2 == "result-1" and op.calls == 1
        record(
            "case8_empty_string_key_and_fingerprint",
            ok,
            f"r1={r1!r} r2={r2!r} calls={op.calls}",
        )
    except Exception:
        record(
            "case8_empty_string_key_and_fingerprint",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    return results


def main():
    if len(sys.argv) != 2:
        print(f"usage: python3 {sys.argv[0]} <path-to-solution.py>")
        sys.exit(1)

    path = sys.argv[1]

    try:
        module = load_module(path)
    except Exception:
        print(f"FAIL: could not import module at {path!r}")
        print(traceback.format_exc())
        sys.exit(1)

    results = run_cases(module)

    passed = 0
    failed = 0
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        line = f"[{status}] {name}"
        if detail:
            line += f" -- {detail}"
        print(line)
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\n{passed}/{passed + failed} cases passed")

    if failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
