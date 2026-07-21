"""Assert .claude/agents/ is a fresh 1:1 mirror of the roster (GT-60).

The roster is only *reachable* by the runtime if every role is installed as a
discoverable subagent at .claude/agents/. A missing, extra, or stale persona
means a role that can't be delegated to (or a ghost that no longer exists) —
the exact "decorative roster" failure of issue #59. Compares the installed
files to what build_personas.render_all() produces now; any drift is the
counterexample.
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _lib  # noqa: E402

PROPERTY = ".claude/agents/ is a fresh 1:1 mirror of the roster (build_personas)."
METHOD = "static"
OWNER = "ci/pipeline-engineer"


def check():
    _lib.in_repo_root()
    scripts_dir = os.path.join(_lib.repo_root(), "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import build_personas  # noqa: E402

    expected = build_personas.render_all()
    if not expected:
        return _lib.FAIL, "no roles found — empty roster or wrong cwd"

    out_dir = build_personas.OUT_DIR
    installed = {
        os.path.basename(p)[:-3]: open(p, encoding="utf-8").read()
        for p in glob.glob(f"{out_dir}/*.md")
    }

    missing = sorted(set(expected) - set(installed))
    extra = sorted(set(installed) - set(expected))
    if missing:
        return _lib.FAIL, f"roles not installed as subagents: {missing} — run build_personas.py"
    if extra:
        return _lib.FAIL, f"stale persona file(s) with no role: {extra} — run build_personas.py"

    stale = sorted(s for s in expected if installed[s] != expected[s])
    if stale:
        return _lib.FAIL, f"persona(s) out of date vs roster: {stale} — run build_personas.py"
    return _lib.PASS, f"{len(expected)} personas installed and fresh"


if __name__ == "__main__":
    sys.exit(_lib.run_standalone(check))
