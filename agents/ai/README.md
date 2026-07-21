# AI Team

Owns the models, prompts, and agent pipelines that give the product
intelligent behavior - distinct from `data/` (which owns the data those
models train on and read) and `logicians/` (which reviews logic/code
correctness, not model behavior).

- [`ai-engineer/`](ai-engineer/) - ML/AI feature integration, inference
  APIs, MLOps.
- [`prompt-engineer/`](prompt-engineer/) - prompt design, versioning, and
  regression testing for a single model call.
- [`multi-agent-systems-architect/`](multi-agent-systems-architect/) -
  topology, contracts, and failure-mode design for pipelines of more than
  one agent.
- [`model-evaluator/`](model-evaluator/) - eval harnesses, model-QA gates,
  and adversarial probing (prompt-injection, jailbreak/misuse, degraded
  input) of the org's own AI features; regression evals on model/prompt
  change.

Same `agent.md` + `SPEC.md` convention as every other team in this repo. Add
a role here when it owns a durable subclass of AI/ML-system work.
