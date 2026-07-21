# PM Team

Owns planning, sequencing, and tracking of work across teams — never the
implementation itself. Every role here is Read/Grep/Glob (+Write for
roles whose deliverable is a document, +Task tools for roles that own
backlog state). No role on this team gets Edit or Bash: a bad plan should
never be able to turn into a bad edit.

`project-manager` is the **spec-driven** entry point: it decomposes a
user goal against the current sprint's `docs/sprint-*/prd.md` and
`user-journeys/`, producing issues and granular sub-issues (one
deliverable, one owner) that each carry an assignee from
`agents/INDEX.md`, checkable acceptance criteria, and a negative prompt,
per `docs/templates/issue-spec.md`.

Altitude, low to high:
`project-manager` (single request → tickets) → `program-tracker`
(multi-sprint initiative) → `delivery-lead` (cross-initiative portfolio
tradeoffs). Each of `experiment-tracker`, `ticket-workflow-steward`,
`meeting-notes-specialist`, and `team-operations` is a narrow specialist
that feeds tickets or decisions into that chain rather than sitting in it.

Which sign-offs ride the altitude chain vs. stay with the PM personally
(spec ambiguity, cross-team conflict, scope changes, retry-cap
escalations, access-widening) is defined in `agents/WORKFLOW.md`, not
repeated here.

The whole team shares two references rather than restating them per
role: `agents/WORKFLOW.md` for the verdict loop and delegation rules, and
`docs/enterprise.md` for the Tiering/Ontology/Taxonomy/Semantics
classification every role's decomposition or tradeoff reasoning cites.

## Roles

| Role | Model | Tools | One-liner |
|---|---|---|---|
| [project-manager](project-manager/) | opus | Read, Grep, Glob, Write (docs-only), Task tools, GitHub issue tools | Spec-driven: decomposes a goal against sprint docs into issues + granular sub-issues, each with assignee, acceptance criteria, and negative prompt. |
| [program-tracker](program-tracker/) | sonnet | Read, Grep, Glob, Write, TaskCreate/Update/List | Tracks a multi-sprint/quarter initiative's milestones, risk register, and cross-team dependencies over its whole lifecycle. |
| [delivery-lead](delivery-lead/) | sonnet | Read, Grep, Glob, Write, TaskList | Makes resourcing/prioritization tradeoffs across competing initiatives; rolls up portfolio status. |
| [experiment-tracker](experiment-tracker/) | sonnet | Read, Grep, Glob, Write, TaskCreate/Update/List | Designs A/B tests and feature experiments, sizes them properly, and calls ship/kill/extend from the data. |
| [ticket-workflow-steward](ticket-workflow-steward/) | sonnet | Read, Grep, Glob, Write | Enforces ticket-linked branch/commit/PR conventions so every change traces back to a tracked ticket. |
| [meeting-notes-specialist](meeting-notes-specialist/) | haiku | Read, Write | Extracts a 4-section record (attendees, decisions, action items, open questions) from raw meeting input. |
| [team-operations](team-operations/) | sonnet | Read, Grep, Glob, Write | Writes SOPs for recurring workflows and diagnoses process bottlenecks. |

## Provenance and skip decisions

Converted from `agency-agents/project-management/*.md` (7 verbose source
personas). Two were skipped as duplicates rather than ported:

- **project-manager-senior** — skipped. Its entire job (convert a spec
  into scoped tasks with acceptance criteria) is already
  `pm/project-manager`'s job; porting it would just be a second agent
  doing the same work with different flavor text.
- **project-shepherd** — not skipped outright, but not ported as-is
  either. Most of its scope (stakeholder comms, timeline management,
  cross-team coordination) also duplicates `pm/project-manager`. The one
  genuinely distinct capability — tracking a long-running, multi-sprint
  initiative as a first-class thing rather than a single request — became
  `pm/program-tracker`.

The remaining renames trade studio/creative-agency framing for
enterprise-engineering equivalents: `studio-operations` →
`team-operations`, `studio-producer` → `delivery-lead` (kept only its
portfolio-prioritization core, dropped the creative-vision/market-strategy
scope that doesn't apply here), `jira-workflow-steward` →
`ticket-workflow-steward` (generalized off Jira specifically to whatever
tracker is in use).
