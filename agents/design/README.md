# Design

Owns the design org's non-implementation surface: user research,
information architecture, brand/design-system governance, and inclusive
visual representation. This team decides *what the right design is and
why*; it hands off to the teams that build it.

## Boundary with `frontend/designer`

`frontend/designer` (existing, unchanged by this team) stays canonical for
implementation-adjacent UI spec work: turning one feature's requirements
into a concrete layout/interaction/accessibility spec that
`frontend/react-dev` builds against. This team's roles sit one layer up or
to the side of that:

- **Research and structure feed `frontend/designer`** — `ux-researcher` and
  `ux-architect` produce personas, journey maps, and information
  architecture that `frontend/designer` turns into a per-feature spec.
- **Governance roles constrain `frontend/designer`** — `ui-designer` owns
  the shared design-token/component system `frontend/designer` draws from;
  `brand-guardian` owns the voice/identity `frontend/designer` must stay
  consistent with.
- **Visual-asset roles serve marketing/docs, not product UI** —
  `image-prompt-engineer` and `inclusive-visuals-specialist` produce and
  review AI-generated imagery for docs, marketing, and comms assets; they
  don't touch in-product UI.

None of these roles write per-feature specs or production code — that
stays with `frontend/designer` and `frontend/react-dev`.

## Roster

| Role | Model | Tools | One-liner |
|---|---|---|---|
| [brand-guardian](brand-guardian/) | sonnet | Read, Grep, Glob, Write, Artifact | Owns brand voice/identity guidelines and audits surfaces against them. |
| [ux-architect](ux-architect/) | sonnet | Read, Grep, Glob, Write, Artifact | Defines information architecture — nav structure, taxonomy — across products. |
| [ux-researcher](ux-researcher/) | sonnet | Read, Grep, Glob, Write, Artifact | Plans research, builds evidence-grounded personas and journey maps. |
| [ui-designer](ui-designer/) | sonnet | Read, Grep, Glob, Write, Artifact | Owns the design-token/component system shared across products. |
| [inclusive-visuals-specialist](inclusive-visuals-specialist/) | sonnet | Read, Grep, Glob, Write | Adds representation/bias constraints to people-depicting image prompts and reviews output. |
| [image-prompt-engineer](image-prompt-engineer/) | haiku | Read, Grep, Glob, Write | Translates a visual concept into a structured AI image-gen prompt for docs/marketing assets. |
| [persona-walkthrough](persona-walkthrough/) | sonnet | Read, Grep, Glob, Write | Simulates a persona's step-by-step reaction to a surface, reports friction against a framework. |
| [technical-writer](technical-writer/) | sonnet | Read, Edit, Write, Bash, Grep, Glob | Writes developer documentation — READMEs, API references, tutorials, docs-as-code pipelines that fail the build on stale docs. |

`technical-writer` moved here when `platform/` was dissolved: it owns the
developer-facing communication surface (docs), a content deliverable
alongside this team's other communication surfaces. It is the one role
here that writes production artifacts (docs-as-code), distinct from the
research/governance roles above.

## Skipped sources

Converted from `agency-agents/design/*.md` (9 source personas). Two were
deliberately not carried over:

- **visual-storyteller** — core value is multimedia/social-platform
  storytelling (Instagram/TikTok/Pinterest content, video, motion
  graphics), which has no home in an enterprise engineering org. The
  data-viz slice it also covers is already handled by the `dataviz` skill
  and by `ux-researcher`'s journey-map/findings output; no dedicated
  persona is missing.
- **whimsy-injector** — delight/gamification/Easter-egg injection is
  consumer-growth-product territory, not an enterprise software concern.
  Its one legitimate carry-over (accessible motion — respecting
  reduced-motion preferences) is already a bullet under
  `frontend/designer`'s accessibility responsibility.
