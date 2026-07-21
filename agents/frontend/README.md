# Frontend Team

Owns everything the user's browser/app renders and interacts with. This is
the reference example for **nested roles under one team**:

- [`designer/`](designer/) — UI/UX design intent: layout, interaction,
  accessibility. Produces specs, not code.
- [`react-dev/`](react-dev/) — implementation in React against those specs.
- [`desktop-app-engineer/`](desktop-app-engineer/) — Electron/Tauri desktop
  packaging, IPC security, code signing, and auto-update pipelines.
- [`microanimation-engineer/`](microanimation-engineer/) — motion specs for
  UI micro-interactions: duration, easing, trigger, reduced-motion fallback.
- [`section-508-specialist/`](section-508-specialist/) — accessibility
  audit and remediation against Section 508 / ADA Title II / WCAG AA.
- [`i18n-engineer/`](i18n-engineer/) — internationalization: string
  externalization/ICU, CLDR plural rules, RTL/bidi layout, locale-aware
  formatting. Moved here when `platform/` was dissolved — i18n is
  mostly presentation.
- [`client-telemetry-engineer/`](client-telemetry-engineer/) — consent-gated,
  first-party client-side signal collection for analytics and fraud/bot
  detection: stateless + stateful identifiers, the browser device-signal set
  (navigator/canvas/WebGL/AudioContext), and async encrypted transmission
  (sendBeacon/pixel, ECDH). Gated on legal's consent decision; hands
  server-side resolution to `data/device-intelligence-engineer`. From issue
  [#55](https://github.com/ai-stress-testing/Ges-Talt/issues/55).

Add more roles the same way — one folder per role, same `agent.md` +
`SPEC.md` convention as everywhere else in this repo. A role doesn't need a
reason to exist beyond "this team now owns a subclass of work distinct
enough to deserve its own persona."
