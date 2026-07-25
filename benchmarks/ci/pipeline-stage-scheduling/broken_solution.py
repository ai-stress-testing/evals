"""Deliberately-broken variant of the pipeline stage-graph scheduler.

Bug: when a stage has more than one dependency, this version takes the
level of the *last-visited* dependency instead of the maximum level over
*all* dependencies. Everything else (cycle detection, validation) is
correct. This under-schedules fan-in stages: a stage that depends on a
short chain and a long chain gets scheduled as soon as the short chain
finishes, before its longer-chain dependency has actually completed --
exactly the class of bug a real pipeline-as-code scheduler must not have.
"""
from __future__ import annotations


class _CycleError(Exception):
    def __init__(self, path):
        super().__init__("cycle detected")
        self.path = list(path)


def schedule_pipeline(stages: dict) -> dict:
    for name, deps in stages.items():
        for dep in deps:
            if dep not in stages:
                raise ValueError(
                    f"stage {name!r} depends on undeclared stage {dep!r}"
                )

    level: dict = {}
    stack: list = []
    stack_set: set = set()
    done: set = set()

    def visit(name):
        if name in done:
            return level[name]
        if name in stack_set:
            idx = stack.index(name)
            raise _CycleError(stack[idx:] + [name])

        stack.append(name)
        stack_set.add(name)

        dep_level = -1
        for dep in stages[name]:
            # BUG: overwrites instead of taking the max across all deps.
            dep_level = visit(dep)

        stack.pop()
        stack_set.discard(name)
        done.add(name)
        level[name] = dep_level + 1
        return level[name]

    try:
        for name in stages:
            if name not in done:
                visit(name)
    except _CycleError as exc:
        return {"ok": False, "cycle": exc.path}

    if not level:
        return {"ok": True, "levels": []}

    max_level = max(level.values())
    levels = [[] for _ in range(max_level + 1)]
    for name, lvl in level.items():
        levels[lvl].append(name)
    for bucket in levels:
        bucket.sort()

    return {"ok": True, "levels": levels}
