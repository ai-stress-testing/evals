"""Reference implementation of the RBAC/ABAC permission-resolution engine.

See problem.md in this directory for the full contract:
- role inheritance (with cycle safety)
- deny-overrides-allow (flat, no specificity tie-break)
- default deny (fail-closed) when nothing matches
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
                # Already visited (including via a cycle) - skip to avoid
                # infinite looping and redundant work.
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
                # Deny is absolute - we could return immediately, but keep
                # scanning is harmless; short-circuit for clarity/perf.
                break
            else:
                saw_allow = True

        if saw_deny:
            return "deny"
        if saw_allow:
            return "allow"
        return "deny"  # default deny / fail-closed / least privilege
