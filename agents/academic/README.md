# Academic

Research-grade rigor aimed at the org itself, not at code that ships. Where
other teams build and fix, academic roles investigate and report: they
pressure-test claims, reconstruct history, and check that what the org
says about itself is true. Advisory by design — every role here hands
findings to the team that owns the fix, or to `pm/project-manager` when
the finding is a decision, not a defect.

These are the same six disciplines a verbose source repo used for
worldbuilding (anthropologist, geographer, historian, narratologist,
psychologist, statistician), reframed for an enterprise engineering org:
the questions a staff-level specialist in each discipline would actually
ask about a codebase, a team, and its metrics — not a university seminar.

## Roster

| Role | Model | Tools | One-liner |
|---|---|---|---|
| [statistician](statistician/) | opus | Read, Grep, Glob | Pressure-tests experiment design and dashboard metrics for statistical validity; read-only, reasoning-bound. |
| [historian](historian/) | sonnet | Read, Grep, Glob, Bash | Reconstructs why code/architecture is the way it is from git history, ADRs, and old issues. |
| [anthropologist](anthropologist/) | sonnet | Read, Grep, Glob, Bash | Compares observed team practice (commits, review habits) against what docs/process claim. |
| [psychologist](psychologist/) | sonnet | Read, Grep, Glob | Diagnoses developer-experience friction and cognitive load; sanity-checks user-research claims. |
| [geographer](geographer/) | sonnet | Read, Grep, Glob | Reviews data locality/residency, regional infrastructure placement, and i18n/l10n coverage. |
| [narratologist](narratologist/) | sonnet | Read, Grep, Glob | Audits whether docs, product narrative, and naming stay internally consistent. |
| [codebase-onboarding-engineer](codebase-onboarding-engineer/) | haiku | Read, Grep, Glob | Explains an unfamiliar codebase by reading source and tracing execution paths — facts grounded in code actually inspected. |

`codebase-onboarding-engineer` moved here when `platform/` was dissolved:
it extends the same read-only investigative charter as the six disciplines
above — reconstructing how a system actually works, rather than shipping
changes to it.

Every role here is advisory: it reports findings to the owning team (or to
`pm/project-manager` when the finding is a scope/priority/legal call), and
none of them edit code or docs directly.
