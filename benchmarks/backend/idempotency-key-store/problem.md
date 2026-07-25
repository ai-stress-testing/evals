# Idempotency-Key Store with TTL Eviction

## Niche

Implement an **idempotency-key store** — the mechanism a backend uses to make
a mutating API endpoint (e.g. `POST /payments`, `POST /orders`) safe to
retry. A client that doesn't receive a response (timeout, dropped
connection, proxy retry, etc.) resends the exact same request with the same
`Idempotency-Key` header. The server must not perform the underlying
side-effecting operation (charge a card, create an order) twice — it must
detect the duplicate, skip re-execution, and return the original result.
Keys are also **TTL-scoped**: after the TTL window elapses, the key is
considered free again (the store must not grow unbounded, and a client
reusing an old key after the window is treated as a brand-new request).

This is a request-deduplication / exactly-once-mutation problem, not a
generic data-structure exercise.

## Required interface

Your solution file must define, at module scope, exactly these two names:

```python
class IdempotencyConflictError(Exception):
    """Raised when a key is reused with a different request fingerprint
    while the original entry is still live."""

class IdempotencyStore:
    def __init__(self, ttl_seconds: float, clock: Callable[[], float]) -> None:
        """
        ttl_seconds: how long an idempotency-key entry stays live after it
            is written.
        clock: a zero-argument callable returning the current time as a
            float (seconds). You MUST call this injected clock for all
            time reads — never call time.time(), time.monotonic(), or any
            wall-clock/random source directly. This is what makes the
            store's behavior deterministically testable.
        """

    def execute(self, key: str, fingerprint: str, operation: Callable[[], Any]) -> Any:
        """
        key: the idempotency key (e.g. the client-supplied header value).
        fingerprint: an opaque string identifying the *content* of this
            particular request (e.g. a hash of the request body). Two
            calls with the same key but different fingerprints represent
            a client bug/attack — reusing a key for a different request.
        operation: a zero-argument callable that performs the actual
            side-effecting work and returns a result. It must be invoked
            AT MOST ONCE per distinct (key, time-window) — i.e. duplicate
            calls within the TTL window must be served from cache, not
            by re-invoking `operation`.

        Returns the result of `operation()` (either freshly computed or
        the cached value from a prior call with the same key+fingerprint
        within the TTL window).
        """
```

## Behavior contract

1. **First time a key is seen** (or the key's prior entry has expired —
   see rule 3): call `operation()` exactly once, store the result together
   with `fingerprint` and the current time (`clock()`), and return the
   result.
2. **Duplicate within the TTL window** — a call arrives for a key whose
   stored entry has NOT yet expired:
   - If `fingerprint` matches the stored fingerprint: this is a genuine
     retry. Do **not** call `operation()` again. Return the previously
     stored result.
   - If `fingerprint` differs from the stored fingerprint: this is a key
     reused for a different request. Raise `IdempotencyConflictError`.
     `operation` must NOT be called in this case.
3. **TTL boundary / expiry**: an entry stored at time `t0` is considered
   expired once `clock() - t0 >= ttl_seconds` (expiry is **inclusive** of
   the exact boundary — at `clock() - t0 == ttl_seconds` the entry is
   already expired). A call for an expired key is treated exactly like a
   brand-new key: `operation()` is called again (regardless of whether the
   fingerprint matches the old, now-expired entry), and the new result
   overwrites the old entry with a fresh timestamp.
4. **Independent keys never interact.** Storing/expiring/conflicting on
   one key must have no effect on any other key.
5. **Failed operations are not cached.** If `operation()` raises an
   exception, that exception must propagate to the caller of `execute`,
   and no entry may be recorded for that call (so a subsequent call with
   the same key/fingerprint is free to retry `operation` again — it is
   *not* treated as a duplicate and is *not* a conflict).
6. **No unbounded growth requirement beyond laziness**: you do not need a
   background thread/timer to sweep expired entries; lazy expiry-on-access
   (as described above) is sufficient and expected.

## Edge cases to handle

- Same key/fingerprint called twice back-to-back at the same instant
  (`clock()` returns an identical value both times) — must be served from
  cache, not re-executed.
- A call landing exactly on the TTL boundary (`clock() - t0 == ttl_seconds`)
  must be treated as expired, per rule 3.
- A key reused with a different fingerprint *after* expiry must NOT raise
  `IdempotencyConflictError` — it's a fresh window, so `operation()` runs
  again normally.
- A key reused with a different fingerprint *before* expiry must raise
  `IdempotencyConflictError` and must not invoke `operation`.
- `operation` raising must not poison the key — the very next call (even
  with the same fingerprint, even before any time has passed) must invoke
  `operation` again rather than treating the failed attempt as cached or
  conflicting.
- Empty-string keys and fingerprints are valid values and must be handled
  like any other string.

## What NOT to do

- Do not call `time.time()`, `time.monotonic()`, `datetime.now()`, or any
  RNG inside `IdempotencyStore` — all time reads must go through the
  injected `clock` callable, or the behavior is not deterministically
  testable and will fail the automated checker.
