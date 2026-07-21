# MX — Multi-Experience

Owns delivery across the full spread of end-user surfaces, not just one.
"Multi-experience" (issue #27, and the "multi experience" category from the
issue #16 triage) is the frame: one product reaches people through mobile,
web, voice, conversational, wearable, and AR/VR surfaces, and this team
owns making an experience work on whichever surface it targets.

Mobile is the surface built out first — one experience within the
multi-experience whole, not the boundary of it. Add a role here when a new
surface (voice, AR/VR, wearable, chat) becomes a durable subclass of work,
same `agent.md` + `SPEC.md` convention as everywhere else.

- [`mobile-app-builder/`](mobile-app-builder/) - native/cross-platform UI,
  offline-first data, native feature integration.
- [`mobile-release-engineer/`](mobile-release-engineer/) - signing,
  fastlane pipelines, store submission, phased rollouts, release health.
- [`feature-flag-engineer/`](feature-flag-engineer/) - feature toggles /
  flags as the engine of evolutionary, incremental delivery across surfaces:
  toggle taxonomy (release/experiment/ops/permission), staged & cohort
  rollout, kill switches, A/B experimentation, and the toggle-debt discipline
  (a flag is born with a removal plan). Grounded in the feature-toggle
  literature (Rahman et al., MSR 2016). From issue
  [#58](https://github.com/ai-stress-testing/Ges-Talt/issues/58); pairs with
  `data/evolutionary-data-engineer` and the fitness-function convention
  (`docs/fitness-functions.md`).

## Boundaries

- Web UI is `frontend/`; MX covers non-web / cross-surface experiences and
  the surface-specific packaging (stores, devices) web doesn't have.
- Service progressive-delivery gating is `cd/release-engineer`;
  `mx/mobile-release-engineer` owns the app-store-specific release path.
- Design intent comes from `design/` and `frontend/designer`; MX builds
  the surface, it doesn't set the UX.
