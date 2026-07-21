# Testing

Empirical verification: running the thing and observing what actually
happens. Screenshots, test runs, load generators, assistive-technology
sessions, re-executed verification commands — evidence produced by doing,
not by reading.

## Boundary with `logicians`

`agents/logicians/logician/` does **static** review — reads code and
specs, reasons about invariants and edge cases, never executes anything.
This team does the opposite: every role here defaults to running
something (a scanner, a test suite, a load generator, a screen reader
session) and reporting what it observed. If a finding didn't come from
executing something, it belongs to `logicians`, not here.

## Roster

| Role | Model | Tools | One-liner |
|---|---|---|---|
| [accessibility-auditor](accessibility-auditor/) | sonnet | Bash, Read, Grep, Glob, Write | Audits WCAG compliance via automated scan + manual assistive-tech testing. |
| [api-tester](api-tester/) | sonnet | Bash, Read, Grep, Glob, Write | Runs functional/security/load tests against APIs. |
| [evidence-collector](evidence-collector/) | sonnet | Bash, Read, Grep, Glob, Write | Screenshots/traces a UI and diffs it against exact spec text. |
| [performance-benchmarker](performance-benchmarker/) | sonnet | Bash, Read, Grep, Glob, Write | Measures load/latency/Core Web Vitals against stated SLAs. |
| [reality-checker](reality-checker/) | sonnet | Bash, Read, Grep, Glob, Write | Final empirical gate — re-verifies other agents' evidence before "production ready". |
| [test-automation-engineer](test-automation-engineer/) | sonnet | Read, Edit, Write, Bash, Grep, Glob | Builds/maintains E2E suites and CI wiring; eliminates flakiness. |
| [test-results-analyzer](test-results-analyzer/) | haiku | Read, Grep, Glob, Write | Summarizes existing test-run artifacts into a go/no-go trend report. |
| [tool-evaluator](tool-evaluator/) | sonnet | Bash, Read, Grep, Glob, Write | Trials testing/QA tooling hands-on before recommending one. |

## Skipped

- **workflow-optimizer** (source: `testing-workflow-optimizer.md`) — not
  converted. Its actual scope is business-process/automation optimization
  (SOPs, cross-department handoffs, change management), which isn't
  empirical software verification and doesn't fit this team's charter.
  Reframing it narrowly enough to fit would just reinvent `pm` or a
  future ops team; better skipped than force-fit.

Note: `tool-evaluator` was converted but scoped down from its source —
see the "Scope note" in its `SPEC.md`. The source persona also covered
general business/SaaS procurement (vendor contracts, TCO, change
management), which is out of charter here; this role only evaluates
testing/QA tooling.
