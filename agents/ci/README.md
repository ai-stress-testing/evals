# CI Team — make a trustworthy artifact

Continuous Integration, read strictly: everything from a commit up to a
**signed, attested, deployable artifact**. This team owns the left of the
DevSecOps pipeline — the shift-left gates (stages 1–4: plan/code, source,
build, test) — where the cost of catching a defect is lowest. Its output is
not a running system; it is an artifact you can trust, with the evidence
attached. Delivery and operation of that artifact is `cd/`.

**Tool-agnostic by charter.** Every role here owns a *function*, not a
product. The user's stack names concrete instances — Jenkins, Jest, Docker,
Gitleaks, Trivy, Cosign, OWASP ZAP, Checkov — but each is one implementation
of a function that outlives it. Swapping the tool must not require a new
role.

## Roster

| Role | Model | Owns (function) | Instances |
|---|---|---|---|
| [pipeline-engineer](pipeline-engineer/) | sonnet | The pipeline as code — stage graph, ordering, ephemeral least-privilege runners, OIDC creds, self-supply-chain audit | Jenkins, GitHub Actions, GitLab CI |
| [quality-gate-engineer](quality-gate-engineer/) | sonnet | Fast correctness gates — pre-commit hooks, unit-test gate, lint/format, coverage floor | pre-commit, Jest/PyTest, ESLint/Ruff |
| [code-security-analyst](code-security-analyst/) | sonnet | Static security gates — SAST, secret detection, IaC scanning — as blocking gates + triage | CodeQL/SonarQube, Gitleaks, Checkov |
| [containerization-engineer](containerization-engineer/) | sonnet | Reproducible, hardened image build; dev-prod parity | Docker, Podman/Buildah, distroless/Alpine |
| [supply-chain-engineer](supply-chain-engineer/) | sonnet | Artifact integrity — SCA, SBOM, signing, provenance/attestation | Trivy/Grype, Syft, Cosign, SLSA |
| [dynamic-security-tester](dynamic-security-tester/) | sonnet | DAST against the running build in an ephemeral env, as a gate | OWASP ZAP, Burp, Nuclei |

## Pipeline stages this team owns (shift-left)

1. **Plan & Code** — `quality-gate-engineer` (pre-commit, unit, lint,
   coverage) + `code-security-analyst` (secret detection).
2. **Source** — `code-security-analyst` (IaC scanning) + `pipeline-engineer`
   (workflow auditing, OIDC short-lived creds).
3. **Build** — `code-security-analyst` (SAST) + `supply-chain-engineer`
   (SCA, SBOM) + `containerization-engineer` (hardened image).
4. **Test** — `dynamic-security-tester` (DAST) + `supply-chain-engineer`
   (signing/attestation); functional E2E is `testing/test-automation-engineer`.

## Boundaries

- **Security team owns the *standard*; CI owns the *gate*.**
  `security/appsec-engineer` and `security/senior-secops` define what secure
  means and do deep manual review; CI wires the automated checks that block
  a build and triages their output. A finding that needs judgment escalates
  up; a finding that needs a fix goes to the owning implementer.
- **Testing owns *functional* verification.**
  `testing/test-automation-engineer` builds the E2E suites and
  `testing/reality-checker` is the final empirical gate; CI's
  `dynamic-security-tester` is *security* testing of the running build, not
  functional testing.
- **CD owns everything after the signed artifact exists** — delivery,
  rollout, runtime, operation.

Same `agent.md` + `SPEC.md` convention as every team. Add a role here when it
owns a durable subclass of artifact-integrity work, not a one-off tool
integration.
