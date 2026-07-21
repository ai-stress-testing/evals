# evals

## Agent org

This repo runs on the Ges-Talt agent-org convention: a roster of
project-subclass-driven subagents (`agents/<team>/<role>/`), installed as
callable `subagent_type`s at `.claude/agents/` via
`python3 scripts/build_personas.py`, plus the docs scaffold under `docs/`
(backlog, sprint PRDs/logs, templates) and a hard-verifier gate
(`python3 scripts/verify.py`). See [`CLAUDE.md`](CLAUDE.md) for the session
operating manual and `agents/README.md` / `agents/INDEX.md` for the roster
itself.
