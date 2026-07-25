#!/usr/bin/env python3
"""Automated judge for the feature-flag-rollout-engine benchmark.

Usage:
    python3 check.py <path-to-solution.py>

Dynamically imports the given module by path, exercises its `evaluate`
function against a fixed set of deterministic test cases (precedence,
kill switch, rollout boundaries, and bucketing stability), prints a
pass/fail summary, and exits 0 iff every case passes, else 1.

Self-contained: computes its own expected bucket values with the exact
hashing formula prescribed in problem.md, independent of the solution
under test.
"""
import hashlib
import importlib.util
import sys
from pathlib import Path


def _bucket(flag_key: str, user_id: str) -> int:
    """Reference bucketing formula from problem.md, computed independently
    of the solution under test."""
    digest = hashlib.sha256(f"{flag_key}:{user_id}".encode("utf-8")).hexdigest()
    return int(digest, 16) % 100


def _load_evaluate(path: str):
    module_path = Path(path).resolve()
    if not module_path.is_file():
        print(f"FAIL: solution file not found: {module_path}")
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("solution_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001 - any import-time error is a failure
        print(f"FAIL: solution raised on import: {exc!r}")
        sys.exit(1)
    if not hasattr(module, "evaluate"):
        print("FAIL: solution does not define a module-level `evaluate` function")
        sys.exit(1)
    return module.evaluate


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: python3 {sys.argv[0]} <path-to-solution.py>")
        return 1

    evaluate = _load_evaluate(sys.argv[1])

    failures = []

    def check(name, flag_config, user_id, expected):
        try:
            actual = evaluate(flag_config, user_id)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{name}: raised {exc!r} (expected {expected!r})")
            return
        if bool(actual) != expected:
            failures.append(f"{name}: got {actual!r}, expected {expected!r}")

    # --- 1. Kill switch overrides an explicit user override ------------
    check(
        "kill_switch beats user_override(True)",
        {
            "key": "checkout-v2",
            "kill_switch": True,
            "user_overrides": {"alice": True},
            "rollout_percentage": 100,
            "default": True,
        },
        "alice",
        False,
    )

    # --- 2. Kill switch overrides targeting rule + 100% rollout ---------
    check(
        "kill_switch beats targeting rule and 100% rollout",
        {
            "key": "checkout-v2",
            "kill_switch": True,
            "targeting_rules": [{"user_ids": ["zoe"], "value": True}],
            "rollout_percentage": 100,
            "default": True,
        },
        "zoe",
        False,
    )

    # --- 3. Kill switch off -> user override(True) applies --------------
    check(
        "no kill_switch: user_override(True) applies",
        {
            "key": "checkout-v2",
            "kill_switch": False,
            "user_overrides": {"alice": True},
            "rollout_percentage": 0,
            "default": False,
        },
        "alice",
        True,
    )

    # --- 4. User override beats targeting rule and rollout ---------------
    check(
        "user_override(False) beats targeting rule(True) and 100% rollout",
        {
            "key": "checkout-v2",
            "user_overrides": {"bob": False},
            "targeting_rules": [{"user_ids": ["bob"], "value": True}],
            "rollout_percentage": 100,
            "default": True,
        },
        "bob",
        False,
    )

    # --- 5. Targeting rule beats rollout percentage (both directions) ---
    check(
        "targeting rule(True) beats 0% rollout",
        {
            "key": "checkout-v2",
            "targeting_rules": [{"user_ids": ["carol"], "value": True}],
            "rollout_percentage": 0,
            "default": False,
        },
        "carol",
        True,
    )
    check(
        "targeting rule(False) beats 100% rollout",
        {
            "key": "checkout-v2",
            "targeting_rules": [{"user_ids": ["dave"], "value": False}],
            "rollout_percentage": 100,
            "default": True,
        },
        "dave",
        False,
    )

    # --- 6. First matching targeting rule wins ---------------------------
    check(
        "first matching targeting rule wins",
        {
            "key": "checkout-v2",
            "targeting_rules": [
                {"user_ids": ["eve"], "value": False},
                {"user_ids": ["eve"], "value": True},
            ],
            "rollout_percentage": 100,
            "default": True,
        },
        "eve",
        False,
    )

    # --- 7. Rollout boundary: 0% => nobody qualifies ---------------------
    for uid in ["frank", "user-1", "user-7", "", "user-42"]:
        check(
            f"0% rollout => False for {uid!r}",
            {"key": "checkout-v2", "rollout_percentage": 0, "default": True},
            uid,
            False,
        )

    # --- 8. Rollout boundary: 100% => everybody qualifies ----------------
    for uid in ["frank", "user-1", "user-7", "", "user-42"]:
        check(
            f"100% rollout => True for {uid!r}",
            {"key": "checkout-v2", "rollout_percentage": 100, "default": False},
            uid,
            True,
        )

    # --- 9. Exact bucket boundary using the prescribed hash formula ------
    flag_key = "checkout-v2"
    uid = "user-42"
    b = _bucket(flag_key, uid)  # == 95 for this (flag_key, uid) pair
    check(
        f"rollout_percentage == bucket({b}) excludes user (bucket < pct is False)",
        {"key": flag_key, "rollout_percentage": b, "default": False},
        uid,
        False,
    )
    check(
        f"rollout_percentage == bucket+1 ({b + 1}) includes user",
        {"key": flag_key, "rollout_percentage": b + 1, "default": False},
        uid,
        True,
    )

    # --- 10. Default used only when rollout_percentage is absent ---------
    check(
        "default=True used when rollout_percentage absent",
        {"key": "checkout-v2", "default": True},
        "grace",
        True,
    )
    check(
        "default=False used when rollout_percentage absent",
        {"key": "checkout-v2", "default": False},
        "grace",
        False,
    )
    check(
        "default ignored when rollout_percentage present (0%)",
        {"key": "checkout-v2", "rollout_percentage": 0, "default": True},
        "grace",
        False,
    )

    # --- 11. Missing optional keys don't crash ---------------------------
    check(
        "missing user_overrides/targeting_rules/default -> falls to rollout",
        {"key": "checkout-v2", "rollout_percentage": 100},
        "henry",
        True,
    )
    check(
        "totally minimal config (only key) -> default False",
        {"key": "checkout-v2"},
        "henry",
        False,
    )

    # --- 12. Empty-string user_id is an ordinary valid id ----------------
    check(
        "empty-string user_id honors user_overrides",
        {"key": "checkout-v2", "user_overrides": {"": True}, "rollout_percentage": 0},
        "",
        True,
    )

    # --- 13. Determinism / bucketing stability: same call twice ----------
    stable_config = {"key": "checkout-v2", "rollout_percentage": 50, "default": False}
    for uid in ["user-1", "user-42", "alice", "bob", "carol", ""]:
        r1 = evaluate(stable_config, uid)
        r2 = evaluate(stable_config, uid)
        if bool(r1) != bool(r2):
            failures.append(
                f"bucketing instability: evaluate() called twice with same "
                f"input ({uid!r}) returned {r1!r} then {r2!r}"
            )
        expected = _bucket("checkout-v2", uid) < 50
        if bool(r1) != expected:
            failures.append(
                f"stable-hash mismatch for {uid!r}: got {r1!r}, expected {expected!r} "
                f"(bucket={_bucket('checkout-v2', uid)})"
            )

    # --- 14. Independent flags bucket independently for the same user ---
    # (Different flag key => different hash input => not required to
    # differ, but must each independently follow their own rollout.)
    check(
        "flag A at 0% excludes user regardless of flag B",
        {"key": "flag-a", "rollout_percentage": 0, "default": False},
        "user-42",
        False,
    )
    check(
        "flag B at 100% includes same user",
        {"key": "flag-b", "rollout_percentage": 100, "default": False},
        "user-42",
        True,
    )

    if failures:
        print(f"FAIL: {len(failures)} case(s) failed:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("PASS: all feature-flag-rollout-engine checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
