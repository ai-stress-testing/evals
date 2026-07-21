# 2026-07-21 — Initialize Ges-Talt agent org in evals

**Session/agent**: orchestrator (direct, single tightly-coupled scaffolding
change — no roster delegation; see caveat in `CLAUDE.md` "Routing").
**Issues touched**: none yet (pre-backlog initialization).

## Done
- Installed the Ges-Talt roster (`agents/`, 105 role charters across 15
  teams) and its tooling (`scripts/`, `.claude/settings.json`,
  `.claude/hooks/`, `.claude/skills/run-gate` + `scaffold-sprint`) into
  this repo, copied from `ai-stress-testing/Ges-Talt`.
- Copied the generic convention docs (`docs/model-tiers.md`,
  `docs/depth-packs.md`, `docs/credit.md`, `docs/feedback-loop.md`,
  `docs/branching.md`, `docs/agent-triggering.md`,
  `docs/fitness-functions.md`) and `docs/templates/` — these are
  reusable conventions, not Ges-Talt's own project history, so
  Ges-Talt's `docs/backlog.md`, `docs/sprint-*`, `docs/opsec/`,
  `docs/reviews/`, `docs/evals/`, and `docs/agent-ledger.jsonl` were
  deliberately NOT copied — this repo starts its own.
- Ran the scaffold + build pipeline: `scripts/init_docs.py .`,
  `scripts/build_personas.py` (105 personas → `.claude/agents/`),
  `scripts/build_index.py` (`agents/INDEX.md`), `scripts/build_repo_index.py`
  (`docs/repo-map.md`).
- Filled `docs/enterprise.md` with an evals-scoped tiering/ontology/
  taxonomy/semantics pass (adapted from Ges-Talt's, not copied verbatim)
  so `enterprise_count_fresh` has a real "105 agents total" figure to
  check instead of the bare template.
- Added an "Agent org" pointer section to `README.md`.
- Ran the gate: `python3 scripts/verify.py` → 12 PASS, 0 FAIL, 2 SKIP
  (`ledger_wellformed` and `verdict_recorded` SKIP — no ledger history or
  run-manifest exists yet in a fresh repo; both are legitimate SKIPs, not
  deferred FAILs).

## Decisions
- Adopt the roster wholesale rather than a curated subset — the roster is
  project-subclass-driven (backend, security, testing, …), not
  feature-specific, so there's no principled way to pre-select "the evals
  roles" without knowing the work yet. `pm/project-manager` narrows by
  assignment per issue, not by roster size.
- `docs/agent-ledger.jsonl` starts empty in this repo (not copied from
  Ges-Talt) — credit/selection scores (`scripts/credit.py`) must reflect
  this repo's own runs, not Ges-Talt's.

## Blocked / carried
- No PRD written yet — `docs/sprint-7-26-21-28/prd.md` is still the bare
  template. This session initialized the org/tooling only; the first real
  user goal for evals should go through `pm/project-manager` next to
  populate the PRD and backlog.
- This entry has no run-manifest (`run-id:`/`verdicts:` block) because
  the review/adversarial gate (`WORKFLOW.md` §5) applies to *major
  outputs* — this was scaffolding/tooling install, not a designed
  artifact with a falsifiable claim to adversarially check. The first
  substantive issue built through the roster should carry one.
