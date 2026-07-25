"""Reference implementation of an idempotency-key store with TTL eviction.

See problem.md in this directory for the full contract.
"""
from typing import Any, Callable, Dict, Tuple


class IdempotencyConflictError(Exception):
    """Raised when the same idempotency key is reused with a different
    request fingerprint while the original entry is still live (not
    expired)."""


class IdempotencyStore:
    def __init__(self, ttl_seconds: float, clock: Callable[[], float]) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._ttl = ttl_seconds
        self._clock = clock
        # key -> (fingerprint, result, stored_at)
        self._entries: Dict[str, Tuple[str, Any, float]] = {}

    def _is_expired(self, stored_at: float) -> bool:
        # Inclusive boundary: exactly `ttl_seconds` elapsed counts as expired.
        return (self._clock() - stored_at) >= self._ttl

    def execute(self, key: str, fingerprint: str, operation: Callable[[], Any]) -> Any:
        entry = self._entries.get(key)

        if entry is not None and not self._is_expired(entry[2]):
            stored_fingerprint, stored_result, _stored_at = entry
            if stored_fingerprint != fingerprint:
                raise IdempotencyConflictError(
                    f"idempotency key {key!r} already used with a different request"
                )
            return stored_result

        # No live entry for this key (never seen, or the prior entry has
        # expired): execute fresh. If operation() raises, we deliberately
        # do not touch self._entries, so the key stays free for a retry.
        result = operation()
        self._entries[key] = (fingerprint, result, self._clock())
        return result
