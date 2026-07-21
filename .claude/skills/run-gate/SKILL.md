---
name: run-gate
description: Run the Ges-Talt roster gate and record the result. Use when finishing substantial work, before committing a roster/docs change, or whenever the verdict loop needs the gate's PASS/FAIL — regenerates the derived files, runs every lint + the verifier registry, and writes the outcome into the sprint-log run-manifest.
---

# run-gate

The exact, repeatable procedure to gate a change in this repo. Not persona,
not knowledge — the steps. Run from the repo root.

## Steps

1. Regenerate the derived files (order matters — content feeds the maps):
   ```
   python3 scripts/build_index.py            # agents/INDEX.md (+ roster lint)
   python3 scripts/build_personas.py         # .claude/agents/ (subagents)
   python3 scripts/build_repo_index.py       # docs/repo-map.md (last)
   ```
   If `build_index.py` exits non-zero, stop and fix the lint before continuing —
   a red roster lint blocks everything downstream.

2. Run the lints and the verifier gate:
   ```
   python3 scripts/verify_comms.py
   python3 scripts/credit.py
   python3 scripts/audit_skills.py
   python3 scripts/verify.py                  # the hard-verifier registry
   ```
   `verify.py` exits non-zero on any FAIL and prints failures first. A FAIL is
   a to-do, not noise: fix it, then re-run from step 1 (regeneration may be the
   fix — e.g. a stale INDEX/repo-map/persona verifier).

3. Record the outcome in the current sprint-log entry's run-manifest header
   (`docs/templates/sprint-log-entry.md`): put the gate result in the
   `verdicts:` field — e.g. `verdicts: build_index PASS; verify.py N/N PASS`.
   An empty `verdicts:` field FAILs `verdict_recorded`; the gate result is
   exactly what belongs there.

## Done when

- Every generator exits 0 and leaves no diff on a second run (idempotent).
- `verify.py` reports all verifiers PASS (or SKIP), exit 0.
- The sprint-log run-manifest `verdicts:` field records the result.
