# Feature-Flag Evaluation Engine — Deterministic Rollout & Targeting

## Niche

Implement the core **evaluation function of a feature-flag / feature-toggle
engine** (the mechanism `agents/mx/feature-flag-engineer` owns): given a
flag's configuration and a user id, decide whether that user sees the
flag "on" or "off". This is the function that platforms like LaunchDarkly,
Unleash, and Flagsmith all implement at their core — it is not a generic
algorithm exercise.

The engine must support, in strict precedence order:

1. **Kill switch** — an ops-controlled emergency off switch. When set, the
   flag is off for *everyone*, no exceptions, regardless of any override,
   targeting rule, or rollout percentage.
2. **Explicit per-user override** — a specific user has been manually
   pinned to a value (e.g. support granted a customer early access). This
   wins over any targeting rule or rollout percentage, but NOT over the
   kill switch.
3. **Targeting rule** — a named cohort/segment of user ids gets a fixed
   value. Rules are evaluated in list order; the **first** rule that
   contains the user wins.
4. **Percentage rollout via stable hashing** — the remaining, un-targeted
   population is bucketed deterministically: the same `(flag_key, user_id)`
   pair must **always** land in the same bucket, on every call, in every
   process, forever (no unseeded randomness, no reliance on call order or
   iteration order of dicts/sets).
5. **Default** — used only when the flag has no rollout percentage
   configured at all (and no override/rule matched).

## Required interface

Your solution file must define, at module scope, exactly this function:

```python
def evaluate(flag_config: dict, user_id: str) -> bool:
    """
    flag_config: a dict with the following keys —
      - "key" (str): the flag's unique key. Required. Used as part of the
        hash input so that the same user_id buckets independently for
        different flags.
      - "kill_switch" (bool, optional, default False): if True, evaluate()
        MUST return False for every user_id, unconditionally.
      - "user_overrides" (dict[str, bool], optional, default {}): maps a
        user_id to an explicit boolean result.
      - "targeting_rules" (list[dict], optional, default []): each rule is
        {"user_ids": list[str], "value": bool}. Evaluated in list order;
        the first rule whose "user_ids" contains user_id applies.
      - "rollout_percentage" (int, optional): an integer in [0, 100]. If
        this key is present (and not None), the user is bucketed via
        stable hashing (see "Bucketing algorithm" below) and gated against
        this percentage.
      - "default" (bool, optional, default False): the result to return
        when "rollout_percentage" is absent/None and no override/rule
        matched.

    user_id: the subject being evaluated. May be an empty string; empty
      string is a valid, ordinary user id, not a special case.

    Returns: bool.
    """
```

## Bucketing algorithm (must match exactly)

To keep the checker deterministic and exact (not statistical), your
bucketing MUST use this precise formula — any other stable hash will
produce different bucket assignments and will be marked wrong by the
checker:

```python
import hashlib

def _bucket(flag_key: str, user_id: str) -> int:
    digest = hashlib.sha256(f"{flag_key}:{user_id}".encode("utf-8")).hexdigest()
    return int(digest, 16) % 100  # an integer in [0, 99]
```

A user is "in" the rollout when `_bucket(flag_key, user_id) < rollout_percentage`.

Do **not** use Python's unseeded `random` module, `hash()` (salted
per-process), or any wall-clock/PID-based value — none of those are stable
across calls/processes, and the checker will treat non-deterministic
output as a failure.

## Precedence, spelled out

For a given `(flag_config, user_id)`, apply in this exact order and
return on the first that applies:

1. `kill_switch` is `True` → return `False`.
2. `user_id` is a key in `user_overrides` → return `user_overrides[user_id]`.
3. The first `targeting_rules` entry (in list order) whose `user_ids`
   contains `user_id` → return that rule's `value`.
4. `rollout_percentage` is present and not `None` → return
   `_bucket(flag_config["key"], user_id) < rollout_percentage`.
5. Otherwise → return `flag_config.get("default", False)`.

## Edge cases you must handle

- **Kill switch beats everything**, including a `user_overrides` entry
  that would otherwise say `True` for this exact user.
- **User override beats a targeting rule and beats the rollout**, even
  when the rule/rollout would produce a different result for that user.
- **Rollout boundary at 0%**: `rollout_percentage == 0` means *nobody*
  qualifies — every user_id must evaluate to `False` (since bucket values
  are always in `[0, 99]`, and `bucket < 0` is never true).
- **Rollout boundary at 100%**: `rollout_percentage == 100` means
  *everybody* qualifies — every user_id must evaluate to `True`
  (`bucket < 100` is always true for `bucket` in `[0, 99]`).
- **Determinism**: calling `evaluate()` twice with the exact same
  `flag_config` and `user_id` must return the exact same result both
  times — including across separate, unrelated calls in between.
- **Missing optional keys**: `flag_config` may omit `user_overrides`,
  `targeting_rules`, or `default` entirely — treat as empty
  dict/list/`False` respectively, don't raise.
- **`default` is only a fallback**: if `rollout_percentage` is present,
  `default` must be ignored even if it disagrees with the bucket result.
- **Empty-string `user_id`** is valid input and must be handled like any
  other string (it still hashes, buckets, and can appear in
  `user_overrides`/`targeting_rules` like any other id).

## What NOT to do

- Do not use `random`, `hash()`, `time.time()`, `os.getpid()`, or any
  other non-stable source for bucketing.
- Do not memoize/cache results in a way that depends on call order across
  different `flag_config` dicts that happen to share a `user_id`.
- Do not short-circuit on `default` before checking `rollout_percentage`.
