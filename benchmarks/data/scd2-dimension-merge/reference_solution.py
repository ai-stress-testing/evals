"""Reference implementation of an SCD2 dimension merge.

See problem.md for the full spec. Stdlib only.
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

    # Rows/versions for ids already present in the dimension table.
    for id_, rows in by_id.items():
        historical_rows = [r for r in rows if not r.get("is_current")]
        current_row = next((r for r in rows if r.get("is_current")), None)

        # Rule 5: history is sacred, always carried through unchanged.
        result.extend(historical_rows)

        if current_row is None:
            # No open row for this id — nothing else to do.
            continue

        source_row = source_by_id.get(id_)
        if source_row is None:
            # Rule 4: missing from source, leave the open row unchanged.
            result.append(current_row)
            continue

        changed = any(
            current_row.get(attr) != source_row.get(attr)
            for attr in tracked_attributes
        )
        if not changed:
            # Rule 1 / 6: no-op (also covers idempotent re-runs).
            result.append(current_row)
        else:
            # Rule 2: close the old version, open a new one.
            closed_row = dict(current_row)
            closed_row["effective_end"] = as_of
            closed_row["is_current"] = False
            result.append(closed_row)
            result.append(make_new_row(id_, source_row))

    # Rule 3: brand-new members present in source but absent from current.
    for id_, source_row in source_by_id.items():
        if id_ not in by_id:
            result.append(make_new_row(id_, source_row))

    return result
