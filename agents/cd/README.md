# CD Team — safely deliver and operate

Continuous Delivery/Deployment, read strictly: everything from a **signed,
attested artifact** (the output of `ci/`) to that artifact running in
production and staying trustworthy there. This team owns the right of the
DevSecOps pipeline — stages 5–6 (deploy, operate/monitor) — with a
deliberate bias toward **moving failure off prod**: to a canary slice, a
reverted commit, a health-gated instance, a continuously re-verified
posture.

**Tool-agnostic by charter.** Every role owns a *function*, not a product.
Argo CD, Kubernetes, Prometheus, DataDog, Terraform, Falco are concrete
instances of functions that outlive them; swapping the tool must not require
a new role.

## Roster

| Role | Model | Owns (function) | Instances |
|---|---|---|---|
| [gitops-engineer](gitops-engineer/) | sonnet | Git as the source of truth for deployable state — pull-based reconciliation, drift detection, rollback-by-revert | Argo CD, Flux |
| [orchestration-engineer](orchestration-engineer/) | sonnet | Scheduling + health-gating workloads — declarative specs, health checks, limits, rollout strategy, RBAC | Kubernetes, Nomad, ECS |
| [release-engineer](release-engineer/) | sonnet | Progressive delivery — canary/blue-green gates, halt/rollback on error signal | Argo Rollouts, Flagger |
| [sre](sre/) | sonnet | Reliability — SLOs/error budgets, observability (logs/metrics/traces), toil reduction, chaos/capacity | Prometheus, DataDog, Grafana |
| [runtime-security-engineer](runtime-security-engineer/) | sonnet | Runtime posture — continuous CIS benchmarking, deployed-image CVE rescan, runtime detection, CVE→SBOM→remediation-PR loop | kube-bench, Trivy Operator, Falco |
| [disaster-recovery-engineer](disaster-recovery-engineer/) | sonnet | Catastrophic recovery — RPO/RTO, immutable backups, tested restore/failover drills | Velero, cloud-native snapshot/replication |
| [finops-engineer](finops-engineer/) | sonnet | Cloud cost allocation, waste elimination, rightsizing, commitment planning | Cloud cost tools, Kubecost |
| [lifecycle-manager](lifecycle-manager/) | sonnet | Lifecycle policy for long-lived artifacts (versions, images, deps, schemas) — states, owners, dates | — (policy role) |

## Pipeline stages this team owns

5. **Deploy** — `gitops-engineer` (pull-based reconciliation, admission
   verification of the signed artifact) + `release-engineer` (env approval
   gates, canary) + `orchestration-engineer` (health-gated scheduling).
6. **Operate / Monitor** — `sre` (Prometheus + DataDog observability, SLOs)
   + `runtime-security-engineer` (CIS benchmarking, continuous rescan,
   CVE→SBOM→remediation-PR) + `disaster-recovery-engineer` (drills) +
   `finops-engineer` (cost) + `lifecycle-manager` (sunset policy).

## Where failure gets moved off prod

The shift-left goal is shared, not one role's job: `ci/` produces an artifact
already gated for correctness and security; `gitops-engineer` makes prod a
reflection of reviewed git (nothing lands out-of-band; rollback is one
revert); `release-engineer` exposes a change to a canary slice and halts on
error signals before full rollout; `orchestration-engineer` keeps a sick
instance out of the load balancer; `sre` owns the error budget that decides
when to stop shipping; `runtime-security-engineer` re-verifies posture
continuously so a once-secure deploy doesn't rot silently.

## Boundaries

- **CI owns everything up to the signed artifact; CD starts there.**
- **`runtime-security-engineer` (posture of what's running) is distinct from
  `sre` (reliability of what's running)** and from
  `security/incident-responder` (breach response) — it wires continuous
  verification and routes confirmed compromise to the security team.

Same `agent.md` + `SPEC.md` convention as every team. Add a role here when it
owns a durable subclass of delivery-or-operations work, not a one-off deploy
task.
