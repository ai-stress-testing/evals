"""Reference implementation of a feature-flag evaluation engine.

See problem.md in this directory for the full contract. Precedence:
kill switch > explicit user override > targeting rule (first match) >
percentage rollout (stable hash bucketing) > default.
"""
import hashlib


def _bucket(flag_key: str, user_id: str) -> int:
    """Deterministic bucket in [0, 99] for a (flag_key, user_id) pair.

    Stable across calls and processes: same inputs always produce the
    same digest, so the same user always lands in the same bucket for a
    given flag.
    """
    digest = hashlib.sha256(f"{flag_key}:{user_id}".encode("utf-8")).hexdigest()
    return int(digest, 16) % 100


def evaluate(flag_config: dict, user_id: str) -> bool:
    # 1. Kill switch always wins, overrides everything else.
    if flag_config.get("kill_switch", False):
        return False

    # 2. Explicit per-user override beats targeting rules and rollout.
    user_overrides = flag_config.get("user_overrides") or {}
    if user_id in user_overrides:
        return bool(user_overrides[user_id])

    # 3. First matching targeting rule wins.
    for rule in flag_config.get("targeting_rules") or []:
        if user_id in rule.get("user_ids", []):
            return bool(rule["value"])

    # 4. Percentage rollout via stable hashing, only if configured.
    rollout_percentage = flag_config.get("rollout_percentage")
    if rollout_percentage is not None:
        flag_key = flag_config["key"]
        return _bucket(flag_key, user_id) < rollout_percentage

    # 5. Default fallback.
    return bool(flag_config.get("default", False))
