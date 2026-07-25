# SCD2 Dimension Merge

## Niche

This is a **Slowly Changing Dimension Type 2 (SCD2) merge** — the core
operation of a dimensional-modeling / data-warehouse Silver→Gold load: given
the current state of a dimension table (with full version history) and a
fresh snapshot of source rows for today's load, produce the row-set changes
needed to correctly version the dimension: close out rows whose tracked
attributes changed, insert new "current" rows for the new values, insert
brand-new members, and leave everything else — including all prior history —
untouched.

## Required signature

Implement exactly this function (module-level, importable):

```python
def merge_scd2(
    current_rows: list[dict],
    source_rows: list[dict],
    as_of: str,
    tracked_attributes: list[str],
) -> list[dict]:
    ...
```

## Inputs

- `current_rows`: the full existing dimension table, as a list of dicts.
  Each row has:
  - `"id"` (str) — the natural/business key.
  - Zero or more attribute keys (e.g. `"name"`, `"tier"`) — the dimension's
    tracked business attributes. Not every row for a given `id` need have
    identical attribute keys across history in general, but in this problem
    every row carries the same attribute keys.
  - `"effective_start"` (str, `"YYYY-MM-DD"`) — when this version became
    active.
  - `"effective_end"` (str `"YYYY-MM-DD"` or `None`) — when this version
    stopped being active; `None` means still open.
  - `"is_current"` (bool) — `True` for exactly the one open/live row per
    `id` that has `effective_end is None`; `False` for closed historical
    rows.

- `source_rows`: today's snapshot from the source system, as a list of
  dicts. Each row has `"id"` plus the current attribute values for that id
  (no effective-date fields — the source only knows "now").

- `as_of` (str, `"YYYY-MM-DD"`): the effective date of this load batch —
  the date to stamp on any row this call closes or opens.

- `tracked_attributes` (list[str]): which attribute keys to compare between
  a dimension member's current row and its source row to decide whether a
  new version is needed. Attributes not in this list are ignored for
  change detection (and are not expected to appear in the row shape at
  all in this problem — every row's non-key/non-effective fields are
  exactly `tracked_attributes`).

## Output

Return the **new full row-set for the dimension table** as a list of dicts
(same row shape as `current_rows`). Row order in the returned list does not
matter.

## Merge rules

For every `id` appearing in `current_rows` and/or `source_rows`:

1. **No-op update** — the `id` has an open (`is_current=True`) row in
   `current_rows` and a row in `source_rows`, and every attribute in
   `tracked_attributes` is equal between them: emit that open row
   unchanged. Do not close it, do not insert anything.

2. **Changed attribute(s)** — the `id` has an open row in `current_rows`
   and a row in `source_rows`, and **one or more** attributes in
   `tracked_attributes` differ (a batch may change multiple attributes at
   once — that is still a single new version, not one per attribute):
   - Close the old open row: copy it, set `effective_end = as_of` and
     `is_current = False`, keep its other fields (including
     `effective_start` and its old attribute values) as they were.
   - Insert a new row for the `id`: attribute values taken from the
     source row, `effective_start = as_of`, `effective_end = None`,
     `is_current = True`.

3. **Brand-new member** — the `id` appears in `source_rows` but has no
   row at all in `current_rows`: insert a new row exactly as in rule 2's
   "insert" step (`effective_start = as_of`, `effective_end = None`,
   `is_current = True`).

4. **Missing from source** — the `id` has an open row in `current_rows`
   but no row in `source_rows` for this batch: leave that row unchanged
   (this problem does not require expiring/soft-deleting dropped members).

5. **History is sacred** — every row in `current_rows` with
   `is_current=False` is carried through to the output completely
   unchanged, regardless of what happens to that `id`'s current row.

6. **Idempotency** — since rule 1 is keyed on attribute equality (not on
   `as_of`), re-running `merge_scd2` with a source snapshot that already
   matches the dimension's current values must be a pure no-op even if
   `as_of` has advanced — no duplicate versions.

## Edge cases a correct solution must handle

- No-op update where nothing changed (rule 1).
- Multiple tracked attributes changing in the same batch, producing exactly
  one new version, not several (rule 2).
- A brand-new dimension member with no prior history at all (rule 3).
- A member absent from this load's source snapshot (rule 4) — must not be
  incorrectly expired or dropped.
- An `id` that already has closed historical rows *and* is being
  versioned again this batch — the old history must survive untouched
  and only the currently-open row gets closed.
- Re-applying an already-applied snapshot (rule 6) must not create
  duplicate/extra rows.

## Stdlib only

No third-party packages (no pandas, no pip installs). Use only the Python
standard library.
