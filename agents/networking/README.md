# Networking Team

Owns connectivity and access boundaries: what can reach what, and how it's
proxied, served, and resolved. The team that keeps `environments/`'s
network policy honest.

- [`network-engineer/`](network-engineer/) — connectivity and access
  boundaries: MCP tunnels, egress allowlists, proxy rules, per-environment
  network policy, DNS. Owns and applies `environments/network-policy.md`.
- [`nginx-specialist/`](nginx-specialist/) — consultant: NGINX reverse-proxy
  and web-server design — topology, TLS floor, rate/connection limits,
  caching, upstream load-balancing + health checks, header/banner hygiene.
  Advises during spec modeling, hands the running config to
  `network-engineer`.
- [`network-automation-engineer/`](network-automation-engineer/) — the network
  device fleet as code: declarative router/switch/firewall config, linting
  (weak SNMP strings, over-broad ACLs), static intent validation, and
  rehearsal in a virtual topology twin (GNS3/Cisco CML/Arista cEOS) with
  ping/traceroute before a change touches a real device.
- [`network-reliability-engineer/`](network-reliability-engineer/) — safe
  delivery of network changes and the failsafes that prevent lockout:
  commit-confirm/auto-rollback timers, the dead-man switch, an out-of-band
  management path, self-healing, and health-gated staged rollout. Answers
  "how do I reach the router after I break its config?" before shipping.

Both network-infra roles are from issue
[#54](https://github.com/ai-stress-testing/Ges-Talt/issues/54) and are
**tool-agnostic** — they own the function (network-as-code; safe delivery),
not a product. They are deliberately **distinct from `ci`/`cd`** (application/
cloud pipelines) and from `network-engineer` (env/session egress + MCP +
proxy policy): this is enterprise network-device infrastructure, which has
failure modes — you can lock yourself out of the box you're configuring —
that app deploy does not. Network *defense/detection* (IDPS, wireless,
behavior analytics) lives in `security/` (`ids-ips-architect`,
`network-detection-engineer`).

Reverse proxy / web serving / load balancing lives here (not in ci/cd) —
it's a connectivity concern, and the OPSEC recon checklist already assigns
reverse-proxy controls to this team. Same `agent.md` + `SPEC.md` convention
as every other team; add a role when it owns a durable connectivity
subclass.
