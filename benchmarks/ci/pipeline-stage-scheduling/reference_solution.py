"""Reference solution: pipeline stage-graph scheduling.

Computes the parallel execution levels for a CI pipeline stage graph
(the ``needs:``/``dependsOn:`` edges you'd write for GitHub Actions,
GitLab CI, or a Jenkins declarative pipeline), or reports a cycle if the
graph can never run.

See problem.md for the full contract.
"""
from __future__ import annotations


class _CycleError(Exception):
    """Internal signal carrying the closed-walk cycle path."""

    def __init__(self, path):
        super().__init__("cycle detected")
        self.path = list(path)


def schedule_pipeline(stages: dict) -> dict:
    # Validate every referenced dependency is itself a declared stage.
    for name, deps in stages.items():
        for dep in deps:
            if dep not in stages:
                raise ValueError(
                    f"stage {name!r} depends on undeclared stage {dep!r}"
                )

    level: dict = {}
    stack: list = []          # current DFS recursion path, in call order
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

        max_dep_level = -1
        for dep in stages[name]:
            dep_level = visit(dep)
            if dep_level > max_dep_level:
                max_dep_level = dep_level

        stack.pop()
        stack_set.discard(name)
        done.add(name)
        level[name] = max_dep_level + 1
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
