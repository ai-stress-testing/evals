# Issue: Per-team functional-capability benchmark suite (leetcode/hackathon-style, auto-judged)

**Sprint**: sprint-7-26-21-28 · **Source**: `prd.md` §1–6
**Assignee (parent)**: `agents/pm/project-manager` (decomposition only) →
implementation to `agents/ai/model-evaluator` per sub-issue.
**Goal**: Give each code-shipping team a small set of niche-targeted,
interview-style coding questions with automated deterministic judges, so an
agent's functional capability can be scored pass/fail without a human.

## Spec

What must be true when this issue closes:
- A new top-level `benchmarks/` directory exists, laid out
  `benchmarks/<team>/<question-slug>/` with, per question, a problem statement,
  a reference solution, and a runnable checker script.
- All 11 in-scope teams (`backend`, `frontend`, `data`, `ai`, `ci`, `cd`,
  `security`, `testing`, `networking`, `mx`, `design`) are covered, 1–2
  questions each.
- Every checker is deterministic and exits 0 on its reference solution and
  non-zero on at least one deliberately-broken variant.
- Every question is targeted to the team's actual niche per `agents/INDEX.md`,
  not a generic algorithm.
- No new repo dependencies; checkers use stdlib / already-present tooling.
- No file under `agents/`, `scripts/`, or `.claude/` is modified.

## Sub-issues

Granularity rule: one team = one deliverable = one owner, independently
verifiable via its own checker. All route to `agents/ai/model-evaluator`: the
deliverable shape (a verifiable, niche-targeted benchmark question with an
automated judge) is identical across teams and is exactly this role's charter
("builds eval harnesses and benchmark suites"). The niche named per sub-issue
is a strong candidate; the assignee may refine it provided it stays inside the
named team's charter and remains auto-judgeable.

Common acceptance criteria (apply to every sub-issue below):
- [ ] 1–2 question directories present under `benchmarks/<team>/`, each with a
      problem statement, a reference solution, and a checker script.
- [ ] Checker exits 0 on the reference solution AND non-zero on at least one
      deliberately-broken variant.
- [ ] Problem statement names the team's actual niche tool/pattern (below),
      not a generic algorithm problem.
- [ ] Checker is deterministic (seeds any randomness; no network/clock
      dependence) and runs from repo root with a single documented command
      using only stdlib / already-installed deps.

Common negative prompt (applies to every sub-issue below):
- Do NOT edit any other team's directory under `benchmarks/`.
- Do NOT modify `agents/`, `scripts/` (esp. `scripts/verify.py`), or `.claude/`.
- Do NOT add a new repo dependency, a shared framework, or a cross-team
  harness abstraction — each question directory is self-contained.
- Do NOT replace the auto-judge with a human-graded rubric.

### 1. backend benchmark
- **Assignee**: `agents/ai/model-evaluator`
- **Scope**: `benchmarks/backend/` — 1–2 questions on the backend niche.
- **Candidate niche**: idempotent request/mutation handling (idempotency-key
  dedup with TTL / exactly-once semantics) or a token-bucket rate limiter —
  server-side correctness patterns, not a generic array puzzle.
- **Acceptance criteria**: common list above, for `benchmarks/backend/`.
- **Negative prompt**: common list above.
- **Verify**: `python3 benchmarks/backend/<slug>/check.py benchmarks/backend/<slug>/reference_solution.*` exits 0; same checker on the broken variant exits non-zero.

### 2. frontend benchmark
- **Assignee**: `agents/ai/model-evaluator`
- **Scope**: `benchmarks/frontend/` — 1–2 questions on the frontend niche.
- **Candidate niche**: ICU MessageFormat plural/select resolution under CLDR
  plural rules (i18n), or an ARIA state/keyboard-operability reducer — a
  frontend-specific pattern, pure-function testable.
- **Acceptance criteria**: common list above, for `benchmarks/frontend/`.
- **Negative prompt**: common list above.
- **Verify**: `python3 benchmarks/frontend/<slug>/check.py benchmarks/frontend/<slug>/reference_solution.*` exits 0; broken variant exits non-zero.

### 3. data benchmark
- **Assignee**: `agents/ai/model-evaluator`
- **Scope**: `benchmarks/data/` — 1–2 questions on the data niche.
- **Candidate niche**: Slowly-Changing-Dimension Type 2 merge, expand-contract
  (parallel-change) schema migration transform, or watermarked streaming
  dedup — data-pipeline correctness, not a generic sort.
- **Acceptance criteria**: common list above, for `benchmarks/data/`.
- **Negative prompt**: common list above.
- **Verify**: `python3 benchmarks/data/<slug>/check.py benchmarks/data/<slug>/reference_solution.*` exits 0; broken variant exits non-zero.

### 4. ai benchmark
- **Assignee**: `agents/ai/model-evaluator`
- **Scope**: `benchmarks/ai/` — 1–2 questions on the ai niche.
- **Candidate niche**: RAG context packing under a token budget (greedy/knapsack
  chunk selection) or cosine-similarity top-k retrieval — an LLM-feature
  building block, deterministic given fixed embeddings/token counts.
- **Acceptance criteria**: common list above, for `benchmarks/ai/`.
- **Negative prompt**: common list above.
- **Verify**: `python3 benchmarks/ai/<slug>/check.py benchmarks/ai/<slug>/reference_solution.*` exits 0; broken variant exits non-zero.

### 5. ci benchmark
- **Assignee**: `agents/ai/model-evaluator`
- **Scope**: `benchmarks/ci/` — 1–2 questions on the ci niche.
- **Candidate niche**: pipeline stage-graph scheduling — topological sort of a
  DAG with cycle detection and parallel-level grouping, or semver dependency
  resolution — CI-pipeline-as-code correctness.
- **Acceptance criteria**: common list above, for `benchmarks/ci/`.
- **Negative prompt**: common list above.
- **Verify**: `python3 benchmarks/ci/<slug>/check.py benchmarks/ci/<slug>/reference_solution.*` exits 0; broken variant exits non-zero.

### 6. cd benchmark
- **Assignee**: `agents/ai/model-evaluator`
- **Scope**: `benchmarks/cd/` — 1–2 questions on the cd niche.
- **Candidate niche**: canary/progressive-delivery decision function
  (error-rate or error-budget burn-rate → promote/hold/rollback) or an
  SLO error-budget computation — deployment-safety logic.
- **Acceptance criteria**: common list above, for `benchmarks/cd/`.
- **Negative prompt**: common list above.
- **Verify**: `python3 benchmarks/cd/<slug>/check.py benchmarks/cd/<slug>/reference_solution.*` exits 0; broken variant exits non-zero.

### 7. security benchmark
- **Assignee**: `agents/ai/model-evaluator`
- **Scope**: `benchmarks/security/` — 1–2 questions on the security niche.
- **Candidate niche**: RBAC/ABAC permission-resolution engine (role
  inheritance, deny-overrides, least-privilege) or constant-time token
  comparison / JWT-claim validation — access-control correctness.
- **Acceptance criteria**: common list above, for `benchmarks/security/`.
- **Negative prompt**: common list above.
- **Verify**: `python3 benchmarks/security/<slug>/check.py benchmarks/security/<slug>/reference_solution.*` exits 0; broken variant exits non-zero.

### 8. testing benchmark
- **Assignee**: `agents/ai/model-evaluator`
- **Scope**: `benchmarks/testing/` — 1–2 questions on the testing niche.
- **Candidate niche**: flake-rate / pass-fail-trend analyzer over a test-run
  history, or coverage-delta computation, or a test-quarantine selector —
  test-signal analysis, not a generic parser.
- **Acceptance criteria**: common list above, for `benchmarks/testing/`.
- **Negative prompt**: common list above.
- **Verify**: `python3 benchmarks/testing/<slug>/check.py benchmarks/testing/<slug>/reference_solution.*` exits 0; broken variant exits non-zero.

### 9. networking benchmark
- **Assignee**: `agents/ai/model-evaluator`
- **Scope**: `benchmarks/networking/` — 1–2 questions on the networking niche.
- **Candidate niche**: CIDR longest-prefix-match routing / subnet containment,
  or ordered ACL rule evaluation (first-match allow/deny) — packet-path
  correctness.
- **Acceptance criteria**: common list above, for `benchmarks/networking/`.
- **Negative prompt**: common list above.
- **Verify**: `python3 benchmarks/networking/<slug>/check.py benchmarks/networking/<slug>/reference_solution.*` exits 0; broken variant exits non-zero.

### 10. mx benchmark
- **Assignee**: `agents/ai/model-evaluator`
- **Scope**: `benchmarks/mx/` — 1–2 questions on the mx niche.
- **Candidate niche**: feature-flag evaluation engine — deterministic
  percentage/cohort bucketing via stable hashing, with kill-switch and
  targeting-rule precedence — flag-rollout correctness.
- **Acceptance criteria**: common list above, for `benchmarks/mx/`.
- **Negative prompt**: common list above.
- **Verify**: `python3 benchmarks/mx/<slug>/check.py benchmarks/mx/<slug>/reference_solution.*` exits 0; broken variant exits non-zero.

### 11. design benchmark
- **Assignee**: `agents/ai/model-evaluator`
- **Scope**: `benchmarks/design/` — 1–2 questions on the design niche.
- **Candidate niche**: WCAG contrast-ratio computation (sRGB → relative
  luminance → contrast ratio → AA/AAA pass/fail), or design-token
  alias/reference resolution — design-system correctness, fully deterministic.
- **Acceptance criteria**: common list above, for `benchmarks/design/`.
- **Negative prompt**: common list above.
- **Verify**: `python3 benchmarks/design/<slug>/check.py benchmarks/design/<slug>/reference_solution.*` exits 0; broken variant exits non-zero.

## Dependencies

- Parent (#PARENT) blocks all of #1–#11 (the `benchmarks/` root layout is
  established by whichever sub-issue lands first; treat the layout in the Spec
  as fixed so the 11 run in parallel without collision).
- #1–#11 are mutually independent (isolated per-team directories) and may run
  in parallel.

## Assignment note (PM)

All 11 sub-issues are assigned to `agents/ai/model-evaluator` (sonnet —
cheapest sufficient tier for harness authoring). This is the deliberate
"one role, many teams" pattern: the craft is identical (a verifiable,
niche-targeted benchmark with an automated judge). The per-team niche is
supplied so the assignee designs *inside* each team's charter rather than
producing 11 generic puzzles. No disagreement with the default assignment for
any team — design and networking were the two worth double-checking, and both
have clean deterministic niches (WCAG contrast math; CIDR longest-prefix
match) that suit an auto-judge.
