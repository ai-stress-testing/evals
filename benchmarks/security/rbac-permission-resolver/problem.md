# RBAC/ABAC Permission-Resolution Engine (deny-overrides-allow, default-deny)

## Niche

Implement the core decision engine of a **role-based access-control (RBAC)
authorization system with role inheritance and explicit allow/deny rules** —
the component that sits behind an `authorize(principal, resource, action)`
call in a real access-control layer (the same kind of engine a
`security/rbac-abac-consultant`-designed policy model gets implemented
against). Given:

- a **role hierarchy** (roles may inherit from parent roles, so a role
  automatically holds every permission its ancestors hold), and
- a **policy set** of rules, each granting or denying a `(role, resource,
  action)` triple (with an optional `"*"` wildcard for resource and/or
  action),

decide whether a request from a principal (the set of roles directly
assigned to them) to perform `action` on `resource` is allowed or denied.

This is an access-control / policy-resolution problem, not a generic
graph or string-matching exercise — correctness is judged specifically
against three security properties:

1. **Deny overrides allow.** If *any* matching rule (at any inherited
   role, at any specificity) denies the request, the request is denied —
   even if another matching rule allows it. There is no "most specific
   rule wins" tie-break; deny is absolute.
2. **Default deny (fail-closed / least privilege).** If no rule matches
   at all — including when the policy set is empty — the request is
   denied. Access is never granted by default.
3. **Role-inheritance cycles must not break resolution.** The role graph
   may contain cycles (e.g. role `a` lists `b` as a parent and `b` lists
   `a`). Resolving the effective role set for a principal must terminate
   and must still produce the mathematically-correct set of ancestors.

## Required interface

Your solution file must define, at module scope, exactly these names:

```python
from dataclasses import dataclass
from typing import Dict, List, Set

@dataclass(frozen=True)
class Rule:
    role: str        # the role this rule applies to
    resource: str     # a resource name, or "*" to match any resource
    action: str       # an action name, or "*" to match any action
    effect: str        # "allow" or "deny"

class PermissionResolver:
    def __init__(self, role_parents: Dict[str, List[str]], rules: List[Rule]) -> None:
        """
        role_parents: maps a role name to the list of roles it directly
            inherits from (its parents). A role not present as a key has
            no parents. The graph may contain cycles; your implementation
            must not infinite-loop on one.
        rules: the full policy set. Order is not significant — the
            decision must be computed the same way regardless of the
            order rules are listed in.
        """

    def resolve_roles(self, principal_roles: List[str]) -> Set[str]:
        """
        Return the full *effective* role set for a principal directly
        assigned `principal_roles`: the roles themselves plus every
        ancestor reachable through role_parents (transitively), with
        each role appearing at most once even if reachable via multiple
        paths or a cycle.
        """

    def decide(self, principal_roles: List[str], resource: str, action: str) -> str:
        """
        Return "allow" or "deny" for whether a principal holding
        `principal_roles` (directly) may perform `action` on `resource`,
        per the behavior contract below. Must return exactly the string
        "allow" or "deny" (lowercase).
        """
```

## Behavior contract

1. Compute the principal's **effective role set**: `principal_roles` plus
   every role transitively reachable via `role_parents` (parents, parents'
   parents, etc.), deduplicated, safe against cycles.
2. A rule **matches** the request if: `rule.role` is in the effective role
   set, AND (`rule.resource == resource` OR `rule.resource == "*"`), AND
   (`rule.action == action` OR `rule.action == "*"`).
3. Collect the effects of every matching rule.
   - If **any** matching rule has `effect == "deny"`: return `"deny"`.
   - Else if **any** matching rule has `effect == "allow"`: return
     `"allow"`.
   - Else (no rule matched at all): return `"deny"` (default deny).
4. Wildcard rules are exactly as specific as exact-match rules for the
   purpose of step 3 — there is deliberately no "most specific rule wins"
   resolution. A narrow `deny` still overrides a broad wildcard `allow`,
   and (per the same flat rule) a broad wildcard `deny` overrides a narrow
   `allow` too. Effect precedence, not specificity, decides ties.

## Edge cases to handle

- **Conflicting allow + deny for the identical `(role, resource, action)`
  triple** — deny must win.
- **Deny and allow granted through different inherited roles** (e.g. a
  principal's directly-assigned role grants `deny` on something a parent
  role's rule `allow`s) — deny must still win.
- **Role-inheritance cycle** (`a` inherits `b`, `b` inherits `a`, directly
  or through a longer chain) — `resolve_roles` must terminate and return
  the correct union, not hang or raise.
- **Empty policy set** (`rules == []`) — every request is denied,
  regardless of role hierarchy.
- **Unknown/unassigned role** — a role in `principal_roles` that appears
  in no rule and has no entry in `role_parents` is valid input; it simply
  contributes no matching rules (falls through to default deny unless
  another of the principal's roles grants access).
- **Multiple directly-assigned roles** — the effective permission is the
  union of what each assigned role (and its ancestors) grants, still
  subject to deny-overrides-allow across the whole set.
- **Wildcard resource or action (`"*"`)** granting broadly, with a
  narrower explicit rule for the same role denying a specific
  `resource`/`action` pair — the narrower deny wins (see contract point 4).
- **Empty-string role/resource/action values** are valid values and must
  be matched like any other string (not treated as "no rule"/wildcard).

## What NOT to do

- Do not implement "most specific rule wins" or any specificity-based
  tie-break — this benchmark's contract is flat deny-overrides-allow,
  full stop.
- Do not default to `"allow"` when no rule matches or when the policy set
  is empty — that is a fail-open bug, the opposite of least privilege.
- Do not let a role-inheritance cycle cause infinite recursion/looping.
