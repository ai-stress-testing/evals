# Flake-Rate / Quarantine Analyzer

## Niche

Implement the core logic of a **flake-rate analyzer over test-run
history** — the tool a CI/quality pipeline uses to decide which tests to
**quarantine** (exclude from blocking the build) versus which are simply
**broken** (deterministically failing and need a real fix, not a
quarantine label) versus which are healthy.

Given, for each test name, the ordered list of pass/fail outcomes across
recent CI builds, compute a per-test flakiness report and a quarantine
recommendation driven by a stated threshold rule. This is a
test-results-triage problem (the domain owned by
`agents/testing/test-results-analyzer` and the CI signal
`agents/testing/test-automation-engineer` acts on) — not a generic
counting/statistics exercise.

**A test is not "flaky" merely because it fails.** The niche distinction
this problem is built to test:

- A test that fails on **every** run in its history has a **consistent,
  reproducible** failure — that's a **broken** test (a real bug in the
  test or the code under test). It must NOT be classified as flaky and
  must NOT be recommended for quarantine (quarantining it would hide a
  real, deterministic bug rather than surface it).
- A test that is **flaky** shows **inconsistent** outcomes — at least one
  pass and at least one fail in its history — for what is presumably the
  same code. Only flaky tests are candidates for quarantine, and only once
  their failure rate crosses the caller-supplied threshold.
- A test with **zero recorded runs** has no evidence either way and must
  be reported as such, not silently defaulted to "stable."

## Required interface

Your solution file must define, at module scope, exactly this function:

```python
from typing import Dict, List

def analyze_flake_rates(run_history: Dict[str, List[bool]], threshold: float) -> Dict[str, dict]:
    """
    run_history: maps a test name to the ordered list of its pass/fail
        outcomes across builds, oldest first. `True` = that build's run
        of the test passed; `False` = it failed. The list may be empty.
    threshold: a flake-rate fraction in [0.0, 1.0]. A flaky test whose
        flake_rate is >= threshold (inclusive) is recommended for
        quarantine.

    Returns a dict keyed by test name (every key of `run_history` must
    appear exactly once, and no extra keys). Each value is a dict with
    exactly these fields:

        {
            "total_runs": int,      # len(results)
            "pass_count": int,
            "fail_count": int,
            "flake_rate": float,    # see classification rules below
            "classification": str, # one of: "insufficient_data",
                                    #         "stable", "broken", "flaky"
            "quarantine": bool,
        }
    """
```

## Classification / flake-rate rules

For a given test's `results: List[bool]`, let `total = len(results)`,
`pass_count = results.count(True)`, `fail_count = total - pass_count`.

1. **`total == 0`** → `classification = "insufficient_data"`,
   `flake_rate = 0.0`, `quarantine = False`. (No evidence either way; do
   not guess.)
2. **`fail_count == 0`** (every run passed) → `classification = "stable"`,
   `flake_rate = 0.0`, `quarantine = False`.
3. **`pass_count == 0`** (every run failed, `total >= 1`) →
   `classification = "broken"`, `flake_rate = 0.0`, `quarantine = False`.
   This is the case a naive implementation gets wrong: a 100%-failing
   test is NOT flaky (its outcome is perfectly consistent — consistently
   bad) and must never be quarantined by this rule; quarantining it would
   hide a real bug instead of fixing it.
4. **Otherwise** (`pass_count > 0` and `fail_count > 0` — a genuine mix)
   → `classification = "flaky"`, `flake_rate = fail_count / total`,
   `quarantine = flake_rate >= threshold` (the boundary is inclusive: a
   test whose flake rate lands exactly on the threshold IS quarantined).

Every test name in the input `run_history` is evaluated independently —
one test's history must have zero effect on another test's report.

## Edge cases to handle

- A test with an empty run list (`[]`) → `insufficient_data`, not
  `stable` and not `flaky`.
- A test that is 100% failing (`[False, False, False]`) → `broken`, not
  `flaky`; `quarantine` must be `False` regardless of how low `threshold`
  is.
- A test whose flake rate lands **exactly** on `threshold` (e.g. 3 fails
  out of 10 runs with `threshold=0.3`, or 1 fail out of 2 runs with
  `threshold=0.5`) → `quarantine = True` (inclusive boundary).
- A test whose flake rate is just under `threshold` → `classification =
  "flaky"` but `quarantine = False`.
- Multiple unrelated tests passed in the same `run_history` dict in one
  call must each get their own independently correct entry — no key may
  leak state into another.

## What NOT to do

- Do not classify a 100%-failing test as `"flaky"` — that is the single
  most common wrong shortcut here (checking `fail_count > 0` instead of
  requiring `pass_count > 0 and fail_count > 0`) and is exactly what the
  automated checker in this directory tests for.
- Do not use a strict `>` comparison for the threshold boundary — the
  spec requires inclusive `>=`.
- Do not read any wall-clock time, randomness, or external I/O — this is
  a pure function over the data passed in.
