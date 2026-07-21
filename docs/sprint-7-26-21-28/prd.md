# PRD — sprint-7-26-21-28

**User goal**: "Setup per team leetcode/hackathon adjacent interview style
questions to test the agents for verifiable and successful outcomes targeted
to their niche. Use my agents." Concretely: stand up a functional-capability
benchmark suite — 1–2 niche-targeted, interview-style coding questions per
code-shipping team — where every question ships with a runnable, deterministic
checker that scores a candidate solution pass/fail with no human in the loop.

**Out of scope**: named explicitly —
- Non-code-shipping teams: `academic`, `legal`, `logicians`, `pm`. No
  benchmark questions for these this sprint.
- The `logicians/agent-evaluator` structural-closure evaluations under
  `docs/evals/` — this suite is a *different*, functional-capability benchmark
  and lives in a new top-level `benchmarks/` directory, not under `docs/evals/`.
- Authoring the benchmark *content* is the assigned agent's job (next pipeline
  step), not this PM decomposition. This sprint's PM deliverable is the PRD,
  the issue spec, the tracked issues, and the backlog rows.
- Any change to `agents/`, `scripts/`, or `.claude/` — the installed roster
  infrastructure is frozen for this task.

## Requirements

Numbered, so issues can cite `prd.md §n`.

1. A new top-level `benchmarks/` directory exists, laid out as
   `benchmarks/<team>/<question-slug>/`, with each question directory
   containing a problem statement, a reference solution, and a runnable
   checker script.
2. Exactly the 11 code-shipping teams are covered, one sub-issue each:
   `backend`, `frontend`, `data`, `ai`, `ci`, `cd`, `security`, `testing`,
   `networking`, `mx`, `design`.
3. Each team ships 1–2 flagship questions (lean pass first — 1 is acceptable,
   2 is the ceiling this sprint).
4. Every question's checker is an automated, deterministic judge: it exits 0
   on the provided reference solution and exits non-zero on at least one
   deliberately-broken variant of that solution. No rubric a human grades by
   eye.
5. Every question is targeted to the team's actual niche (its real tool /
   pattern / domain per `agents/INDEX.md`), not a generic algorithm problem
   that any team could own.
6. Each question directory is self-contained: the checker runs from the repo
   root with a single documented command, using only the language's standard
   library / already-installed dependencies (no new repo dependencies).

## Constraints

- No new repo dependencies; checkers use stdlib / already-present tooling.
- Deterministic only — no network calls, no wall-clock/randomness that would
  make a pass/fail flaky. If randomness is intrinsic to the niche, the checker
  seeds it.
- Team directories are isolated: work on one team's benchmarks must not edit
  another team's directory, the roster (`agents/`), the gate
  (`scripts/verify.py` and siblings), or `.claude/`.
- Assignment: the method — designing a verifiable, niche-targeted benchmark
  question with an automated judge — is the same shape across all 11 teams, so
  all sub-issues route to `agents/ai/model-evaluator` (the roster's
  eval-harness / benchmark-suite builder), the same "one role, many teams"
  precedent used for the existing evaluator suite.

## Success criteria

How the sprint as a whole is judged done — checkable, like everything else.
- [ ] `benchmarks/` exists with all 11 in-scope team subdirectories populated.
- [ ] Each team directory holds 1–2 question directories, each with a problem
      statement, a reference solution, and a checker script.
- [ ] For every question, the checker exits 0 on the reference solution and
      non-zero on at least one broken variant (demonstrated per sub-issue's
      **Verify** line).
- [ ] Every question names its team's actual niche tool/pattern in the problem
      statement.
- [ ] No file under `agents/`, `scripts/`, or `.claude/` changed by this work;
      `python3 scripts/verify.py` stays green.
