# Legal Team

Owns legal exposure of what the org builds: privacy law compliance
verified against the actual code ("true to code"), the privacy program,
user-facing legal documents, and general legal risk. Created from issue
[#1](https://github.com/ai-stress-testing/Ges-Talt/issues/1).

**Team-wide rule**: no legal role holds Edit or Bash, ever. Legal reads
code and writes documents; it never changes systems. The reasoning-bound
role (`general-counsel`) follows the roster's opus + read-only pattern
with no Write at all.

## Roles

| Role | Model | One-liner |
|---|---|---|
| [privacy-engineer](privacy-engineer/) | sonnet | Verifies privacy claims against the codebase: data flows, consent, retention/deletion — findings with file:line evidence. |
| [data-protection-officer](data-protection-officer/) | sonnet | Owns the privacy program: classification, retention, DSRs, processor agreements, breach-notification clock. |
| [product-counsel](product-counsel/) | sonnet | Drafts ToS/privacy policy/EULA grounded in what the code does; audits OSS license compatibility. |
| [accessibility-counsel](accessibility-counsel/) | sonnet | Owns the cross-jurisdiction accessibility-law obligation (ADA/508/EN 301 549/EAA/AODA), sets the legally-required WCAG target, reads VPAT/ACR liability, tracks exposure — hands audit to testing and remediation to frontend. |
| [general-counsel](general-counsel/) | opus | Read-only legal issue-spotting across features/plans; maintains the risk register routing every risk to an owner. |

## Boundaries (who legal does NOT replace)

- **WCAG/accessibility**: empirical audit → `testing/accessibility-auditor`;
  remediation + VPAT/conformance docs → `frontend/section-508-specialist`.
  `legal/accessibility-counsel` owns the *legal obligation* layer above them
  — which regimes bind (ADA Title III, Section 508, EN 301 549, EAA, AODA),
  the legally-required WCAG level and deadline, VPAT liability — and tracks
  the exposure in the risk register, citing their outputs. Created from issue
  [#52](https://github.com/ai-stress-testing/Ges-Talt/issues/52).
- **Certification frameworks** (SOC 2, ISO 27001, HIPAA, PCI-DSS) →
  `security/compliance-auditor`. Legal owns law and contract, not
  certifications.
- **Data residency implementation advice** → `academic/geographer`
  (advisory); legal owns the *obligation*, geographer the *topology*.
- **Breach handling**: `security/incident-responder` contains and
  investigates; `data-protection-officer` owns notification obligations
  and the 72-hour clock.
- **A licensed attorney**: none of these agents give legal advice; drafts
  and findings are inputs for human counsel review.
