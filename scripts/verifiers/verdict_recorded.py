"""Assert a major output records a verdict (GT-64).

The behavioral half of issue #59: the roster is only real if work actually
passes through the review/adversarial gate — and the only way to know it did
is a recorded artifact. Objective trigger for "major output": a sprint-log
entry that carries a run-manifest header (a fenced block with `run-id:`).
Every such block must have a non-empty `verdicts:` field — the recorded
outcome of the loop (`WORKFLOW.md §1/§5`). An empty verdicts line is the
counterexample.

Scope is the CURRENT sprint only, so the check enforces the discipline going
forward without retroactively failing pre-GT-38 history. SKIP when the
current sprint has no run-manifest to gate (nothing major shipped yet).
Distinct from `verify_comms.py`, which validates attribution *content*; this
checks the *presence* of a recorded verdict.
"""
import datetime
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402

PROPERTY = "Every run-manifest in the current sprint's log records a non-empty verdicts field."
METHOD = "static"
OWNER = "pm/project-manager"
SPRINT_RE = re.compile(r"sprint-(\d{1,2})-(\d{2})-(\d{1,2})-(\d{1,2})$")
FENCE_RE = re.compile(r"```.*?```", re.S)
# Horizontal whitespace only ([ \t]) so the capture can't cross the newline
# into the closing fence — a bare `verdicts:` must read as empty, not swallow
# the next line.
VERDICTS_RE = re.compile(r"^[ \t]*verdicts:[ \t]*(.*)$", re.I | re.M)


def current_sprint_dir(today):
    for d in glob.glob("docs/sprint-*/"):
        m = SPRINT_RE.search(d.rstrip("/"))
        if not m:
            continue
        month, yy, d1, d2 = (int(x) for x in m.groups())
        try:
            start = datetime.date(2000 + yy, month, d1)
            end = datetime.date(2000 + yy, month, d2)
        except ValueError:
            continue
        if start <= today <= end:
            return d.rstrip("/")
    return None


def check():
    _lib.in_repo_root()
    sprint = current_sprint_dir(datetime.date.today())
    if sprint is None:
        return _lib.SKIP, "no sprint window covers today (sprint_window_current owns that)"

    empty = []
    manifests = 0
    for entry in sorted(glob.glob(f"{sprint}/sprint-log/*.md")):
        text = open(entry, encoding="utf-8").read()
        for block in FENCE_RE.findall(text):
            if "run-id:" not in block:
                continue
            manifests += 1
            m = VERDICTS_RE.search(block)
            if not m or not m.group(1).strip():
                empty.append(os.path.basename(entry))
    if manifests == 0:
        return _lib.SKIP, f"no run-manifest in {sprint}/sprint-log yet — nothing major to gate"
    if empty:
        return (_lib.FAIL,
                f"run-manifest with empty verdicts in: {sorted(set(empty))} — "
                "record the review/adversarial verdict (WORKFLOW.md §5)")
    return _lib.PASS, f"{manifests} run-manifest(s) in {sprint} record a verdict"


if __name__ == "__main__":
    sys.exit(_lib.run_standalone(check))
