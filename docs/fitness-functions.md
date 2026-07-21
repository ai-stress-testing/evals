# Architectural fitness functions

The governance half of **evolutionary architecture** (issue #58). Software is
allowed to change continuously — but only while the characteristics that make
it *good* still hold. A **fitness function** is an objective, automated
measure of one architectural characteristic that gates that change: not "is
the code nice" but "does coupling still point inward / does p99 still fit the
budget / is the auth invariant still true," answered mechanically, every time.

This is the same shape as the hard verifiers (`docs/opsec/hard-verifiers.md`)
and, in fact, the **same mechanism**: a fitness function *is* a verifier with
an architectural-characteristic property. The GT-43 registry
(`scripts/verifiers/` + `scripts/verify.py`) is how fitness functions run and
gate the verdict loop (`agents/WORKFLOW.md §5`). This doc names the concept
and who owns it; it does not add a second machine.

## The evolutionary-architecture triad

Evolutionary software needs all three, and they interlock (issue #58, grounded
in the feature-toggle literature — Rahman et al., MSR 2016 — and the
evolutionary-architecture practice around fitness functions):

1. **Fitness functions** — the objective measures that say a change kept the
   architecture's guarantees. Without them, "evolve freely" is just "drift."
2. **Feature toggles** — the mechanism to ship change incrementally, ramp it,
   and kill it. Owned by `mx/feature-flag-engineer`. Without them, change is
   all-or-nothing and can't be gated mid-flight.
3. **Evolutionary version control + data controls** — the data underneath must
   evolve as safely as the code (expand-contract, compatible contracts,
   reversible migrations). Owned by `data/evolutionary-data-engineer`. The
   literature is explicit that toggles and fitness functions are unsafe
   *without* these data controls — a half-migrated schema fails at some ramp %.

A fitness function gates the ramp; the toggle performs it; the data controls
keep every ramp step readable. Miss one and evolutionary delivery becomes
either drift, a flag day, or a broken read.

## Anatomy of a fitness function

Same contract as a verifier — one property, binary verdict, counterexample,
fail-closed:

- **Characteristic** — the architectural quality it protects (coupling
  direction, latency budget, security invariant, compatibility across a
  rollout window, licensing, size/complexity ceiling).
- **Kind** — *atomic* (one component in isolation) vs *holistic* (emergent
  across components); *triggered* (runs in CI on change) vs *continuous*
  (monitors production).
- **Method** — reuse the verifier registry's `static | ptest | probe | reason`.
  Most fitness functions are `static`/`ptest`; a few (does p99 hold under real
  load) are `probe`.
- **Verdict** — PASS, or FAIL with the concrete violating input/state. A
  fitness function that can't fail is decoration.

## Ownership

- **Design** — `logicians/software-architect`: which characteristics must hold
  as the system evolves, and the objective measure for each (it already owns
  ADRs and dependency-direction; fitness functions are that made executable).
- **Mechanism** — `scripts/verifiers/` (static/property) and `testing/`
  (empirical). A fitness function ships as a registered verifier so
  `verify.py` gates on it.
- **The two supporting pillars** — `mx/feature-flag-engineer` (toggles) and
  `data/evolutionary-data-engineer` (data controls).

For the meta-repo, the ten seed verifiers *are* the org's own fitness
functions (roster integrity, reason-tier read-only boundary, INDEX/repo-map
freshness, …). A target repo adopting this org authors its
domain fitness functions into the same `scripts/verifiers/` registry.
