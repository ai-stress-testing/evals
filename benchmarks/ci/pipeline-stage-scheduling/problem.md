# Pipeline Stage-Graph Scheduling

**Niche:** pipeline-as-code stage-graph scheduling — the function
`ci/pipeline-engineer` owns: given a CI pipeline's stage graph (the
`needs:`/`dependsOn:` edges you'd write in a GitHub Actions workflow,
GitLab CI `.gitlab-ci.yml`, or a Jenkins declarative pipeline), compute
the parallel execution plan the pipeline engine would actually run, or
report why the graph can never run.

A pipeline is not a list of steps; it's a DAG of stages, each declaring
the stages that must finish before it can start. The engine's job is to
group stages into the fewest possible sequential **levels**, where every
stage in a level can run in parallel (all of its dependencies finished in
an earlier level), and no stage is scheduled before every one of its
dependencies has been scheduled. If the declared graph has a cycle
(`build` needs `test`, `test` needs `build`), the pipeline can never
start — the engine must detect that and report the offending cycle
instead of hanging or silently dropping stages.

## Required signature

Implement, in a module importable via `importlib`, a top-level function:

```python
def schedule_pipeline(stages: dict[str, list[str]]) -> dict:
    ...
```

- `stages`: maps each stage name to the list of stage names it directly
  depends on (must complete first). A stage with no dependencies maps to
  `[]`. Every name appearing anywhere in a dependency list MUST also be a
  key of `stages` — if not, the input itself is invalid pipeline
  configuration (like a GitHub Actions workflow with `needs: some_typo`)
  and the function MUST raise (any `Exception` subclass, e.g.
  `ValueError`) rather than silently ignoring it.

- **Return value on success** (no cycle):
  ```python
  {"ok": True, "levels": [[...stage names...], [...], ...]}
  ```
  `levels[0]` is every stage with no dependencies. `levels[i]` is every
  stage whose dependencies are all fully satisfied by stages in
  `levels[0..i-1]`, and for which level `i` is the *earliest* level at
  which that holds (a stage must not be pushed later than necessary, and
  must not be scheduled before every dependency's level has passed —
  i.e. for a stage depending on stages at levels `2` and `4`, the stage's
  own level must be exactly `5`, not `3` and not `6`). The order of stage
  names *within* a level does not matter to the checker. If `stages` is
  empty, return `{"ok": True, "levels": []}`.

- **Return value when the graph contains a cycle**:
  ```python
  {"ok": False, "cycle": [s0, s1, ..., s0]}
  ```
  `cycle` is a closed walk through the actual dependency edges proving a
  cycle exists: `cycle[0] == cycle[-1]`, `len(cycle) >= 2`, and for every
  consecutive pair, `cycle[i+1]` is a genuine entry in
  `stages[cycle[i]]` (i.e. `cycle[i]` really does depend on
  `cycle[i+1]`). A single self-dependency (`"x": ["x"]`) is a valid
  (length-2) cycle report: `["x", "x"]`.

## Edge cases the solution must handle

1. **Empty pipeline** — no stages at all.
2. **Diamond dependency** — `build` depends on both `lint` and `test`,
   which both depend on `checkout`.
3. **Disconnected stages** — two or more independent dependency chains
   with no edges between them; both must still be leveled correctly,
   starting at level 0 each.
4. **Asymmetric fan-in** — a stage that depends on two other stages
   whose own dependency chains are of *different* lengths. The fan-in
   stage's level must be driven by the *longest* incoming chain, not the
   first (or shortest) one — a scheduler that just uses "one dependency's
   level + 1" instead of the max over all dependencies will schedule the
   stage too early, i.e. before every dependency has actually finished.
5. **Self-loop cycle** — a stage depending on itself.
6. **Multi-stage cycle** — e.g. `a -> b -> c -> a`.
7. **Cycle coexisting with valid stages** — some stages in the input
   form a clean DAG while a disjoint subset forms a cycle; the whole
   pipeline must still be reported as unschedulable (`ok: False`).
8. **Unknown dependency reference** — a stage lists a dependency name
   that is not itself a key in `stages` (a workflow config typo) — must
   raise, not silently schedule around it.

## Notes

- Stdlib only. No network access, no third-party packages.
- The judge (`check.py`) is fully automated and deterministic: same
  input, same exit code, every run.
