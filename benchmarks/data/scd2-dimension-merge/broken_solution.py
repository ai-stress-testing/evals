"""Deliberately broken SCD2 merge for check.py to catch.

Bug: when closing an old version (rule 2), this implementation forgets to
flip `is_current` to False on the closed row — it copies the old row's
`is_current=True` verbatim, so the output ends up with *two* rows marked
`is_current=True` for the same id (the stale one and the new one). This is
the classic "missing is_current flip" SCD2 bug.
"""
from collections import defaultdict


def merge_scd2(
    current_rows: list[dict],
    source_rows: list[dict],
    as_of: str,
    tracked_attributes: list[str],
) -> list[dict]:
    result: list[dict] = []

    by_id: dict[str, list[dict]] = defaultdict(list)
    for row in current_rows:
        by_id[row["id"]].append(dict(row))

    source_by_id = {row["id"]: row for row in source_rows}

    def make_new_row(id_: str, source_row: dict) -> dict:
        new_row = {"id": id_}
        for attr in tracked_attributes:
            new_row[attr] = source_row.get(attr)
        new_row["effective_start"] = as_of
        new_row["effective_end"] = None
        new_row["is_current"] = True
        return new_row

    for id_, rows in by_id.items():
        historical_rows = [r for r in rows if not r.get("is_current")]
        current_row = next((r for r in rows if r.get("is_current")), None)

        result.extend(historical_rows)

        if current_row is None:
            continue

        source_row = source_by_id.get(id_)
        if source_row is None:
            result.append(current_row)
            continue

        changed = any(
            current_row.get(attr) != source_row.get(attr)
            for attr in tracked_attributes
        )
        if not changed:
            result.append(current_row)
        else:
            closed_row = dict(current_row)
            closed_row["effective_end"] = as_of
            # BUG: missing `closed_row["is_current"] = False` here.
            result.append(closed_row)
            result.append(make_new_row(id_, source_row))

    for id_, source_row in source_by_id.items():
        if id_ not in by_id:
            result.append(make_new_row(id_, source_row))

    return result
