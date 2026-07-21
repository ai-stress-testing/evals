# Data Team

Owns the pipelines, storage, and data quality that everything else reads
from - distinct from `backend/` (which owns the services that call into
this data) and `ai/` (which owns the models that consume it).

- [`data-engineer/`](data-engineer/) - ETL/ELT pipelines, medallion
  lakehouse architecture, streaming ingestion, data contracts.
- [`database-optimizer/`](database-optimizer/) - operational database
  schema, indexing, and query performance.
- [`database-administrator/`](database-administrator/) - operational
  database availability and recoverability: replication/failover, backup
  and point-in-time recovery, connection pooling, schema-change safety.
- [`ai-data-remediation-engineer/`](ai-data-remediation-engineer/) -
  surgical, pattern-level fixes for data broken at scale, via local SLMs.
- [`device-intelligence-engineer/`](device-intelligence-engineer/) -
  server-side of a device-intelligence pipeline for fraud/bot detection and
  consented analytics: signal ingestion, stable device-ID resolution
  (stateful ⋈ stateless), IP intelligence (regional blocks, DNS-routing,
  datacenter/VPN detection), and calibrated ML fraud scoring. Operates only
  on lawfully-collected data, IP/PII encrypted and fraud-scoped; pairs with
  `frontend/client-telemetry-engineer`. From issue
  [#55](https://github.com/ai-stress-testing/Ges-Talt/issues/55).
- [`evolutionary-data-engineer/`](evolutionary-data-engineer/) - the data
  controls that make evolutionary software safe: expand-contract (parallel-
  change) schema evolution, backward/forward-compatible data contracts,
  versioned and reversible migrations, and experiment/cohort data governance,
  so code can ship in toggled increments without a broken read at any ramp
  step. From issue [#58](https://github.com/ai-stress-testing/Ges-Talt/issues/58);
  pairs with `mx/feature-flag-engineer` and `docs/fitness-functions.md`.

Same `agent.md` + `SPEC.md` convention as every other team in this repo. Add
a role here when it owns a durable subclass of data-infrastructure work.
