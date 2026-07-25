"""Deliberately-broken variant of the RBAC/ABAC permission-resolution engine.

Bug (security-relevant, on purpose): precedence is inverted. This
implementation lets an "allow" rule override a "deny" rule instead of the
required deny-overrides-allow contract in problem.md. Role inheritance,
cycle-safety, wildcard matching, and default-deny-on-no-match are all still
implemented correctly - only the allow/deny precedence is wrong - so a
correct checker must catch specifically the deny-overrides-allow property,
not just "is anything broken."
"""
from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass(frozen=True)
class Rule:
    role: str
    resource: str
    action: str
    effect: str  # "allow" or "deny"


class PermissionResolver:
    def __init__(self, role_parents: Dict[str, List[str]], rules: List[Rule]) -> None:
        for rule in rules:
            if rule.effect not in ("allow", "deny"):
                raise ValueError(f"invalid effect {rule.effect!r}; must be 'allow' or 'deny'")
        self._role_parents = role_parents
        self._rules = list(rules)

    def resolve_roles(self, principal_roles: List[str]) -> Set[str]:
        effective: Set[str] = set()
        stack: List[str] = list(principal_roles)
        while stack:
            role = stack.pop()
            if role in effective:
                continue
            effective.add(role)
            for parent in self._role_parents.get(role, []):
                if parent not in effective:
                    stack.append(parent)
        return effective

    def decide(self, principal_roles: List[str], resource: str, action: str) -> str:
        effective_roles = self.resolve_roles(principal_roles)

        saw_allow = False
        saw_deny = False
        for rule in self._rules:
            if rule.role not in effective_roles:
                continue
            if rule.resource != resource and rule.resource != "*":
                continue
            if rule.action != action and rule.action != "*":
                continue
            if rule.effect == "deny":
                saw_deny = True
            else:
                saw_allow = True
                # BUG: an allow short-circuits and wins immediately,
                # regardless of any deny rule that also matched (or would
                # have matched later in the list). This is the inverted,
                # insecure precedence.
                break

        if saw_allow:
            return "allow"
        if saw_deny:
            return "deny"
        return "deny"  # default deny / fail-closed / least privilege
