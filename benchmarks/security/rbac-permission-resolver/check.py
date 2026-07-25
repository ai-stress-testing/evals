#!/usr/bin/env python3
"""Automated judge for the RBAC/ABAC permission-resolution engine benchmark.

Usage:
    python3 check.py <path-to-solution.py>

Dynamically imports the given module by path, exercises `PermissionResolver`
(and its `Rule` dataclass) against a fixed, deterministic set of test cases
covering the contract in problem.md - role inheritance, inheritance-cycle
safety, deny-overrides-allow, and default-deny-on-no-match/empty-policy -
prints a pass/fail summary per case, and exits 0 iff every case passes,
1 otherwise (or on any error loading/using the module).
"""
import contextlib
import importlib.util
import signal
import sys
from pathlib import Path

CASE_TIMEOUT_SECONDS = 5


class CheckTimeout(Exception):
    pass


@contextlib.contextmanager
def time_limit(seconds):
    """Best-effort wall-clock guard so a broken solution with an unguarded
    role-inheritance cycle (infinite loop) fails fast instead of hanging
    the checker forever. No-ops on platforms without SIGALRM."""
    if not hasattr(signal, "SIGALRM"):
        yield
        return

    def _handler(signum, frame):
        raise CheckTimeout(
            f"exceeded {seconds}s - likely an infinite loop "
            f"(e.g. an unguarded role-inheritance cycle)"
        )

    old_handler = signal.signal(signal.SIGALRM, _handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def load_module(path: str):
    module_path = Path(path).resolve()
    if not module_path.is_file():
        raise FileNotFoundError(f"no such file: {module_path}")
    spec = importlib.util.spec_from_file_location("solution_under_test", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load a module spec from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_cases(mod):
    """Returns a list of (name, callable) pairs. Each callable takes no
    args, returns nothing, and raises AssertionError (or lets any other
    exception propagate) on failure."""
    Rule = mod.Rule
    Resolver = mod.PermissionResolver

    cases = []

    def add(name, fn):
        cases.append((name, fn))

    def case_basic_allow():
        r = Resolver({}, [Rule("admin", "reports", "read", "allow")])
        got = r.decide(["admin"], "reports", "read")
        assert got == "allow", f"expected 'allow', got {got!r}"

    add("basic allow on exact match", case_basic_allow)

    def case_default_deny_no_match():
        r = Resolver({}, [Rule("admin", "reports", "read", "allow")])
        got = r.decide(["admin"], "reports", "write")
        assert got == "deny", f"expected 'deny' (no matching rule), got {got!r}"

    add("default deny when no rule matches", case_default_deny_no_match)

    def case_empty_policy_denies():
        r = Resolver({}, [])
        got = r.decide(["admin"], "anything", "anything")
        assert got == "deny", f"expected 'deny' for empty policy set, got {got!r}"

    add("empty policy set denies everything (fail-closed)", case_empty_policy_denies)

    def case_deny_overrides_allow_same_role():
        r = Resolver(
            {},
            [
                Rule("admin", "reports", "read", "allow"),
                Rule("admin", "reports", "read", "deny"),
            ],
        )
        got = r.decide(["admin"], "reports", "read")
        assert got == "deny", (
            f"conflicting allow+deny for the identical rule triple must "
            f"deny; got {got!r}"
        )

    add("deny overrides allow: identical (role, resource, action)", case_deny_overrides_allow_same_role)

    def case_deny_overrides_allow_across_inherited_roles():
        role_parents = {"editor": ["viewer"]}
        rules = [
            Rule("viewer", "reports", "read", "allow"),
            Rule("editor", "reports", "read", "deny"),
        ]
        r = Resolver(role_parents, rules)
        got = r.decide(["editor"], "reports", "read")
        assert got == "deny", (
            f"a deny on the directly-assigned role must beat an allow "
            f"inherited from a parent role; got {got!r}"
        )

    add(
        "deny overrides allow across inherited roles",
        case_deny_overrides_allow_across_inherited_roles,
    )

    def case_role_inheritance_grants_access():
        role_parents = {"editor": ["viewer"]}
        rules = [Rule("viewer", "reports", "read", "allow")]
        r = Resolver(role_parents, rules)
        got = r.decide(["editor"], "reports", "read")
        assert got == "allow", (
            f"editor should inherit viewer's allow rule; got {got!r}"
        )

    add("role inherits parent's allow rule", case_role_inheritance_grants_access)

    def case_inheritance_cycle_resolves_and_terminates():
        role_parents = {"a": ["b"], "b": ["a"]}
        rules = [Rule("b", "docs", "read", "allow")]
        r = Resolver(role_parents, rules)
        with time_limit(CASE_TIMEOUT_SECONDS):
            effective = r.resolve_roles(["a"])
            got = r.decide(["a"], "docs", "read")
        assert effective == {"a", "b"}, (
            f"resolve_roles(['a']) with a<->b cycle should be {{'a','b'}}, "
            f"got {effective!r}"
        )
        assert got == "allow", (
            f"role 'a' should inherit role 'b's allow through the cycle; "
            f"got {got!r}"
        )

    add(
        "role-inheritance cycle terminates and resolves correctly",
        case_inheritance_cycle_resolves_and_terminates,
    )

    def case_longer_cycle_terminates():
        # a -> b -> c -> a (3-node cycle), plus an unrelated extra parent.
        role_parents = {"a": ["b"], "b": ["c"], "c": ["a", "extra"]}
        rules = [Rule("extra", "x", "y", "allow")]
        r = Resolver(role_parents, rules)
        with time_limit(CASE_TIMEOUT_SECONDS):
            effective = r.resolve_roles(["a"])
            got = r.decide(["a"], "x", "y")
        assert effective == {"a", "b", "c", "extra"}, (
            f"expected full transitive closure through the 3-cycle plus "
            f"'extra', got {effective!r}"
        )
        assert got == "allow", f"expected 'allow' via transitive inheritance, got {got!r}"

    add("longer (3-node) inheritance cycle terminates and resolves", case_longer_cycle_terminates)

    def case_wildcard_resource():
        r = Resolver({}, [Rule("support", "*", "read", "allow")])
        assert r.decide(["support"], "tickets", "read") == "allow"
        assert r.decide(["support"], "invoices", "read") == "allow"
        assert r.decide(["support"], "tickets", "write") == "deny"

    add("wildcard resource ('*') matches any resource", case_wildcard_resource)

    def case_wildcard_action():
        r = Resolver({}, [Rule("auditor", "logs", "*", "allow")])
        assert r.decide(["auditor"], "logs", "delete") == "allow"
        assert r.decide(["auditor"], "logs", "read") == "allow"
        assert r.decide(["auditor"], "metrics", "read") == "deny"

    add("wildcard action ('*') matches any action", case_wildcard_action)

    def case_narrow_deny_overrides_wildcard_allow():
        r = Resolver(
            {},
            [
                Rule("intern", "*", "*", "allow"),
                Rule("intern", "payroll", "read", "deny"),
            ],
        )
        assert r.decide(["intern"], "payroll", "read") == "deny", (
            "a narrow explicit deny must override a broad wildcard allow "
            "(no specificity tie-break - deny is absolute)"
        )
        assert r.decide(["intern"], "docs", "read") == "allow", (
            "requests outside the narrow deny's scope should still be "
            "allowed by the wildcard allow"
        )

    add(
        "narrow deny overrides broad wildcard allow (flat precedence)",
        case_narrow_deny_overrides_wildcard_allow,
    )

    def case_unknown_role_denies():
        r = Resolver({}, [Rule("admin", "x", "y", "allow")])
        got = r.decide(["ghost"], "x", "y")
        assert got == "deny", (
            f"a role with no rules and no parents should contribute "
            f"nothing and fall through to default deny; got {got!r}"
        )

    add("unknown/unassigned role falls through to default deny", case_unknown_role_denies)

    def case_multiple_roles_union():
        r = Resolver({}, [Rule("roleA", "x", "read", "allow")])
        got = r.decide(["roleA", "roleB"], "x", "read")
        assert got == "allow", (
            f"the union of directly-assigned roles should grant access "
            f"if any one of them does; got {got!r}"
        )

    add("multiple directly-assigned roles are unioned", case_multiple_roles_union)

    def case_empty_string_values_are_real_values():
        r = Resolver({}, [Rule("", "", "", "allow")])
        assert r.decide([""], "", "") == "allow", (
            "empty-string role/resource/action must be matched like any "
            "other string value, not treated as absent"
        )
        assert r.decide(["nonempty"], "", "") == "deny"

    add("empty-string role/resource/action are valid, distinct values", case_empty_string_values_are_real_values)

    def case_independent_resources_dont_interact():
        r = Resolver(
            {},
            [
                Rule("clerk", "invoices", "read", "allow"),
                Rule("clerk", "payroll", "read", "deny"),
            ],
        )
        assert r.decide(["clerk"], "invoices", "read") == "allow"
        assert r.decide(["clerk"], "payroll", "read") == "deny"

    add(
        "a deny on one resource does not leak into an unrelated allow",
        case_independent_resources_dont_interact,
    )

    return cases


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: python3 {sys.argv[0]} <path-to-solution.py>", file=sys.stderr)
        return 1

    solution_path = sys.argv[1]

    try:
        mod = load_module(solution_path)
    except Exception as exc:  # noqa: BLE001 - report and fail, don't crash
        print(f"FAIL: could not load module {solution_path!r}: {exc!r}")
        return 1

    for required in ("Rule", "PermissionResolver"):
        if not hasattr(mod, required):
            print(f"FAIL: module {solution_path!r} does not define required name {required!r}")
            return 1

    try:
        cases = build_cases(mod)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: error constructing test cases against {solution_path!r}: {exc!r}")
        return 1

    total = len(cases)
    failures = []

    for name, fn in cases:
        try:
            with time_limit(CASE_TIMEOUT_SECONDS):
                fn()
        except CheckTimeout as exc:
            failures.append((name, str(exc)))
        except AssertionError as exc:
            failures.append((name, str(exc)))
        except Exception as exc:  # noqa: BLE001
            failures.append((name, f"unexpected exception: {exc!r}"))

    passed = total - len(failures)
    for name, _ in cases:
        status = "FAIL" if any(name == fname for fname, _ in failures) else "PASS"
        print(f"[{status}] {name}")

    print(f"\n{passed}/{total} cases passed.")

    if failures:
        print("\nFailure details:")
        for name, msg in failures:
            print(f"  - {name}: {msg}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
