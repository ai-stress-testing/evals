"""Deliberately-broken variant of the feature-flag evaluation engine.

Bug (intentional): the precedence order from problem.md is violated —
this version checks `user_overrides` BEFORE `kill_switch`, so a user with
an explicit override still sees the flag "on" even when the kill switch
is engaged. Per problem.md rule 1, the kill switch must override *every*
other signal, including an explicit per-user override. Everything else in
this file is otherwise a correct implementation (same stable-hash
bucketing formula), so a correct checker must isolate this one
precedence bug.
"""
import hashlib


def _bucket(flag_key: str, user_id: str) -> int:
    digest = hashlib.sha256(f"{flag_key}:{user_id}".encode("utf-8")).hexdigest()
    return int(digest, 16) % 100


def evaluate(flag_config: dict, user_id: str) -> bool:
    # BUG: user_overrides is consulted before kill_switch, so an
    # explicit override incorrectly bypasses the kill switch.
    user_overrides = flag_config.get("user_overrides") or {}
    if user_id in user_overrides:
        return bool(user_overrides[user_id])

    if flag_config.get("kill_switch", False):
        return False

    for rule in flag_config.get("targeting_rules") or []:
        if user_id in rule.get("user_ids", []):
            return bool(rule["value"])

    rollout_percentage = flag_config.get("rollout_percentage")
    if rollout_percentage is not None:
        flag_key = flag_config["key"]
        return _bucket(flag_key, user_id) < rollout_percentage

    return bool(flag_config.get("default", False))
