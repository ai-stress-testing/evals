# Enterprise Doc — evals

This doc UPDATES OVER TIME. The spec-driven PM (`agents/pm/project-manager`)
classifies new work against it during decomposition and extends it when a
decomposition reveals a concept, tier, class, or term that isn't here yet.
Stale entries are deleted, not preserved — this is a living reference, not
an append-only log.

## Tiering

- **Strategic** — the repo owner (human) plus each sprint's `prd.md`: sets
  direction and states what a sprint will and won't do.
- **Tactical** — the `pm/` team, specifically `pm/project-manager`
  (spec-driven decomposition into issues/sub-issues) governed by
  `agents/WORKFLOW.md`'s verdict loop.
- **Operational** — the implementer teams (backend, frontend, data, ci, cd,
  ai, mx, networking, security) plus `logicians/` (static review) and
  `testing/` (empirical verification), each executing against acceptance
  criteria a sub-issue already fixed.

## Ontology

- goal —(enters through)→ `pm/project-manager`
- goal —(is stated by)→ PRD (`docs/sprint-*/prd.md`)
- PRD —(is decomposed into)→ issue (`docs/templates/issue-spec.md`)
- issue —(is decomposed into)→ sub-issue (one deliverable, one owner)
- sub-issue —(is assigned to)→ agent (one, from `agents/INDEX.md`)
- implementer agent —(produces)→ diff/artifact
- `logicians/*` —(statically reviews)→ diff/artifact
- `testing/*` —(empirically verifies)→ diff/artifact
- attempt 4 FAIL —(escalates to)→ `pm/project-manager`
- agent —(belongs to)→ team —(is bound by)→ charter (`agent.md` + `SPEC.md`)
- agent —(is scoped by)→ tool boundary (its `tools:` frontmatter list)

## Taxonomy

- Teams (15): academic, ai, backend, cd, ci, data, design, frontend, legal,
  logicians, mx, networking, pm, security, testing
  — see `agents/INDEX.md` (generated, 105 agents total).
- Artifact types: `agent.md` (loadable subagent contract), `SPEC.md`
  (human-readable role card), PRD (`docs/sprint-*/prd.md`), issue-spec
  (`docs/templates/issue-spec.md`), sprint-log entry
  (`docs/templates/sprint-log-entry.md`).

## Semantics

- **Roster** — the full set of `agents/<team>/<role>/` charters installed
  as callable `subagent_type`s via `scripts/build_personas.py`.
- **Gate** — the hard-verifier registry, `python3 scripts/verify.py`; a red
  verifier is a to-do, not noise.
- **Verdict** — the PASS/FAIL outcome of the review/adversarial gate on a
  major output, recorded per `agents/WORKFLOW.md` §5.
