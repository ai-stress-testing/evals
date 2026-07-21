# Writing descriptions that actually trigger

Claude Code auto-delegates by matching incoming work against a subagent's
`description` frontmatter. A description written for a human/orchestrator
reader — "Designs the linear-iterations queue…" — gives the runtime nothing
to match, so the role never fires and the roster stays decorative (issue
#59). This is the convention that makes a role *reachable*.

Enforced by `scripts/verifiers/description_triggers.py` (part of the
`verify.py` gate) and installed into the discovery path by
`scripts/build_personas.py` (GT-60). Owned by
`ai/multi-agent-systems-architect`.

## The rule

Every role `description` must contain a **task-matching trigger phrase** —
an action-first cue that names *when to invoke the role*, phrased so the
runtime can match it to a task. Accepted stems: `Use for…`, `Use to…`,
`Use when…`, `Use before/after…`, `Use PROACTIVELY…`, `invoke when…`.

Keep the existing shape around it — the description still leads with what the
role owns and ends with the `Not for X (other-role)` disambiguation. The
trigger *replaces filler*, it doesn't add a paragraph; the one-liner budget
the INDEX renders is unchanged.

## Before / after

- **Before** (human-readable, unmatchable):
  "Owns lifecycle policy for long-lived artifacts — API versions, images,
  dependencies, schemas. Sets states, owners, and dates."
  **After** (adds the trigger):
  "…Sets states, owners, and dates. **Use when a task introduces, deprecates,
  or sunsets a long-lived artifact**, or needs a lifecycle policy/owner
  assigned."

- **Before**: "Spec-driven PM. Turns a user goal plus the current sprint docs
  into issues and granular sub-issues…"
  **After**: "…following docs/templates/issue-spec.md. **Use PROACTIVELY when
  a new user goal arrives or work needs decomposing into assignable issues**
  before implementation."

- **Already compliant** (most of the roster): "…**Use for** signal ingestion,
  device-ID resolution, and fraud scoring. **Not for** the client collector
  (frontend/client-telemetry-engineer)…" — an action trigger plus the
  disambiguation clause. Leave these alone.

## Why "Not for X" stays

The trigger says when to *pick* the role; the `Not for X (role)` clause says
when to pick a *different* one. Both feed matching — one attracts the right
task, the other repels the wrong one. Deleting the disambiguation to "make
room" for the trigger trades one kind of mismatch for another.
