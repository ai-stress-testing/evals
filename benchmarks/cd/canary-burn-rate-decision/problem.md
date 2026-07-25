# Canary burn-rate decision function

## Niche

This is a **progressive-delivery / SLO error-budget** problem, the kind of
decision function a `cd/release-engineer` or `cd/sre` would wire into a
canary analysis step: given the request counts observed during a canary
window, decide whether the rollout should **promote**, **hold**, or
**rollback**, using multi-window burn-rate thresholds against the service's
SLO (the same style of decision described in the Google SRE workbook's
multi-window, multi-burn-rate alerting, adapted here to a single canary
window plus an incoming error-budget state).

## Required signature

Implement a module-level function with exactly this signature:

```python
def canary_decision(
    samples: list[tuple[int, int]],
    slo_target: float,
    burn_rate_rollback: float,
    burn_rate_hold: float,
    budget_remaining: float,
    min_total_requests: int = 1,
) -> str:
    ...
```

Returns one of the literal strings `"promote"`, `"hold"`, `"rollback"`.

### Inputs

- `samples`: a chronological list of `(good_count, total_count)` integer
  pairs, one pair per sampling interval inside the canary window
  (e.g. one pair per minute). `good_count <= total_count` for every entry.
  The list may be empty.
- `slo_target`: the service's target success ratio, a float in `(0, 1)`
  (e.g. `0.999` for 99.9%).
- `burn_rate_rollback`: the burn-rate multiplier at or above which the
  canary must be rolled back immediately (e.g. `14.4`).
- `burn_rate_hold`: the burn-rate multiplier at or above which the canary
  must be held for more data, but which is not yet bad enough to roll back
  (e.g. `6.0`). Always `burn_rate_hold < burn_rate_rollback`.
- `budget_remaining`: the fraction (can be negative) of the service's
  overall error budget left *before* this canary window started. This is
  state carried in from the SLO's rolling budget, not computed from
  `samples`.
- `min_total_requests`: the minimum number of *total* requests, summed
  across all samples, required before a `"promote"` or `"rollback"`
  verdict may be issued on the strength of the observed data alone.
  Defaults to `1`.

### Algorithm (this is the spec, not a hint — implement exactly this)

1. **Error budget already exhausted.** If `budget_remaining <= 0`, return
   `"rollback"` immediately, regardless of what the samples show. Policy:
   you don't get to spend a budget you don't have, even if the canary
   itself looks perfect.
2. **Insufficient data.** Otherwise, sum `good_count` and `total_count`
   across all samples. If the summed `total_count` is `< min_total_requests`
   (this includes the empty-list and the all-zero-traffic case), return
   `"hold"` — there isn't enough traffic yet to make a promote/rollback
   call.
3. **Aggregate burn rate.** Otherwise, compute the aggregate success ratio
   over the *whole window* — `sum(good) / sum(total)` — do **not** average
   the per-sample burn rates or per-sample ratios; a window with one
   high-volume good interval and one low-volume bad interval must be
   dominated by request volume, not treated as two equally-weighted votes.
   Let `error_ratio = 1 - success_ratio` and
   `allowed_error_ratio = 1 - slo_target`. The burn rate is
   `error_ratio / allowed_error_ratio`.
4. **Decision, in this order, using `>=` (inclusive) comparisons:**
   - `burn_rate >= burn_rate_rollback` → `"rollback"`.
   - `burn_rate >= burn_rate_hold` → `"hold"`.
   - otherwise → `"promote"`.

### Edge cases the checker exercises

- Zero-traffic window (`samples` all `(0, 0)`, or `samples == []`): must
  be `"hold"`, never a false `"promote"`.
- Burn rate landing **exactly** on a threshold (`== burn_rate_rollback` or
  `== burn_rate_hold`): the inclusive boundary belongs to the *worse*
  bucket (`rollback` at the rollback threshold, `hold` at the hold
  threshold) — a `>` instead of `>=` is a bug the checker catches.
  Test vectors are chosen so the threshold equality is exact in IEEE-754
  double precision (no floating-point tolerance is needed or allowed).
- Error budget already exhausted (`budget_remaining <= 0`) with a
  perfect-looking canary (zero errors in every sample): must still be
  `"rollback"`.
- Multiple samples of very different volume: the decision must be driven
  by the volume-weighted aggregate, not a naive mean of per-sample
  results.

### Non-goals

No I/O, no timestamps, no concurrency. Pure function over the inputs
above. Stdlib only.
