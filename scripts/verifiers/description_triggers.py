"""Assert every role description carries a task-matching trigger (GT-61).

Claude Code's auto-delegation matches incoming work against a subagent's
`description`. A description written only for a human reader ("Designs the
linear-iterations queue…") gives the runtime nothing to match, so the role
never fires. The convention (docs/agent-triggering.md): every description
contains an action-first trigger phrase — "Use for/to/when…", "Use
PROACTIVELY…", or "invoke when…". A description with none is the
counterexample.
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402

PROPERTY = "Every role description contains a task-matching trigger phrase (Use for/when/PROACTIVELY, invoke when)."
METHOD = "static"
OWNER = "ai/multi-agent-systems-architect"

# Trigger stems that give the runtime something to match on. Case-insensitive.
TRIGGER = re.compile(
    r"\b(use (proactively|for|to|when|during|after|whenever|before|as)"
    r"|invoke when|invoke for|call when|call for)\b",
    re.I,
)


def check():
    _lib.in_repo_root()
    bi = _lib.import_build_index()
    missing = []
    total = 0
    for path in sorted(glob.glob("agents/*/*/agent.md")):
        if "/TEMPLATE/" in path:
            continue
        total += 1
        desc = bi.parse(path).get("description", "")
        if not TRIGGER.search(desc):
            _, team, role, _ = path.split("/")
            missing.append(f"{team}/{role}")
    if total == 0:
        return _lib.FAIL, "no roles found — empty roster or wrong cwd"
    if missing:
        return _lib.FAIL, f"description has no trigger phrase: {missing}"
    return _lib.PASS, f"all {total} descriptions carry a trigger phrase"


if __name__ == "__main__":
    sys.exit(_lib.run_standalone(check))
