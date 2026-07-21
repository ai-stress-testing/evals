#!/usr/bin/env python3
"""SessionStart hook (GT-63): reinject the roster-routing discipline.

Claude Code adds this script's stdout to the session context at start, making
the routing directive a runtime event instead of a CLAUDE.md line the session
can quietly skip (issue #59). No network, no deps — stdlib print only. The
authority is CLAUDE.md's "Routing" section; this is the nudge that points at
it every session.
"""
print(
    "Roster-routing check (Ges-Talt): before acting on a non-trivial task, "
    "name which roster role owns it (agents/INDEX.md, docs/repo-map.md) and "
    "route to that subagent unless it's a single-file/tightly-coupled change. "
    "Regardless of who implements: run the review/adversarial gate as a REAL "
    "gate before shipping a major output — security/legal at spec time, an "
    "explicit logicians/falsifier disproof pass, and a COMMS.md attribution "
    "line — and record it (WORKFLOW.md §5). Skipping the gate is the "
    "violation; keeping a small change inline is not. See CLAUDE.md 'Routing'."
)
