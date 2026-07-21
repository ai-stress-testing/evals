# Backend Team

Owns server-side logic and the data behind it: how a request becomes a
correct, durable state change, and how services expose and defend that
behavior. Distinct from `frontend/`/`mx/` (what the client renders),
`data/` (analytics/ETL/warehouse, not the operational request path), and
`networking/` (what can reach what). Split by *altitude* (design vs.
implementation) and by *durable subclass of hard problem* (payments,
realtime, search) rather than by feature.

- [`backend-architect/`](backend-architect/) — designs backend architecture
  before implementation: service boundaries, data schemas, API contracts,
  failure-isolation. The design-time altitude for this team.
- [`backend-dev/`](backend-dev/) — implements server-side logic, APIs, and
  data models per a ticket: endpoints, business logic, schema/migrations,
  external-service integration. The default implementer.
- [`api-platform-engineer/`](api-platform-engineer/) — public/partner-facing
  APIs: contract-first OpenAPI/gRPC, versioning and deprecation policy, SDK
  generation, gateway concerns (auth, rate limiting, quotas).
- [`payments-billing-engineer/`](payments-billing-engineer/) — payment and
  billing flows: PSP integrations, idempotent money mutations, webhook
  processing, subscription lifecycles. The correctness bar here is money, so
  idempotency and reconciliation are non-negotiable.
- [`realtime-collaboration-engineer/`](realtime-collaboration-engineer/) —
  realtime systems: WebSocket/SSE transport, presence, CRDT/OT collaborative
  editing, offline-first sync, reconnect-safe fan-out.
- [`search-relevance-engineer/`](search-relevance-engineer/) — search: index
  and analyzer design, BM25 tuning, hybrid lexical+vector retrieval, and
  judgment-based relevance evaluation.

Same `agent.md` + `SPEC.md` convention as every team. Add a role here when it
owns a durable subclass of server-side work (a distinct hard problem with
its own correctness bar), not a one-off endpoint.
