# 🛣️ Highway Map — bioart (critical path)

Highway = the minimal, fastest, and measurable path to deliver value from PoC to the first public release, with clearly defined gates (Go/No‑Go).

Related documents:
- Vision/strategy: [ROADMAP.md](./docs/ROADMAP.md)
- Execution details: pathwaymap.md (planned - detailed checklists, SLO, DoD)

## 1) “Highway” goals and constraints

- R1 release goal:
  - Deliver a stable core (VM + I/O), a basic interface (CLI or simple API), and one working “sandbox” adapter for simulated/safe integration.
- Constraints (minimum SLO/SLA):
  - Success rate ≥ 99% for the critical path
  - MTTR ≤ 30 minutes (based on runbooks)
  - Cost per 100 jobs ≤ defined threshold (TBD - to be defined in planned pathwaymap.md)
- R1 scope (included):
  - Packaging (library + CLI), basic docs and quickstart
  - Baseline telemetry (structured logs, timing and error metrics)
  - “Sandbox” adapter + E2E tests
- Out of scope for R1 (deferred):
  - Production wet‑lab integrations, full GUI/playground, accelerators (FPGA), advanced ECC/ML

## 2) Critical path (milestones and dependencies)

- M0: PoC and repo hardening
  - Deliverables: formatting/lint/CI, test harness, configuration validation, structured logs
  - Dependencies: none
  - Go/No‑Go: “green” CI, ≥60% coverage in key modules, reproducible dev setup
- M1: Profiling and first optimizations
  - Deliverables: hot‑path profile, eliminate top‑N bottlenecks, cache (with TTL)
  - Dependencies: M0
  - Go/No‑Go: ≥30% reduction in critical‑path latency
- M2: Cost telemetry and guardrails
  - Deliverables: cost instrumentation per iteration, budgets and anomaly alerts
  - Dependencies: M0
  - Go/No‑Go: cost/100 jobs report within the allowed threshold
- M3: Ports/adapters + “sandbox” E2E
  - Deliverables: interfaces (ports), mock + sandbox adapter, contract tests and E2E
  - Dependencies: M0, M1 (stability), M2 (limits)
  - Go/No‑Go: full, auditable job trace in the sandbox
- M4: Reliability and resilience
  - Deliverables: retry/backoff + jitter, idempotency, circuit breaker, concurrency limits
  - Dependencies: M3
  - Go/No‑Go: fault/chaos tests ≥95% pass
- M5: Distribution (R1)
  - Deliverables: package (PyPI or other), CLI, documentation (README, Quickstart, Runbook), SBOM, release notes
  - Dependencies: M3–M4
  - Go/No‑Go: fresh install < 15 min, E2E smoke green, SLOs met
- M6: Post‑release stabilization
  - Deliverables: feedback triage, bugfixes, docs enhancements, usage metrics
  - Dependencies: M5
  - Go/No‑Go: no P0/P1 blockers for 7 days

Dependencies overview (D = dependency chain):
- D1: M0 → M1 → M3 → M4 → M5 → M6
- D2 (parallel): M2 can run after M0 and before M3 (enables limits and reporting)

## 3) Minimal PR set for the “Highway”

- PR‑01: Repo infrastructure (format/lint/CI, CODEOWNERS, SECURITY, CONTRIBUTING)
- PR‑02: Test harness + first critical‑path tests
- PR‑03: Structured logs + baseline metrics
- PR‑04: Profiling + hot‑path optimizations (1/2)
- PR‑05: Cost instrumentation + budgets + alerts
- PR‑06: Ports/adapters: interfaces + mock + contract tests
- PR‑07: Sandbox adapter + E2E + retry/backoff + limits
- PR‑08: Packaging + CLI + user docs + release pipeline
- PR‑09: Post‑R1 stabilization (bugfixes + feedback)

Guidelines:
- One logical change per PR; tests and docs in the same PR.
- PR size optimized for quick review (< 30 min).
- Every PR references the “Highway R1” tracking issue.

## 4) Quality criteria (summary)

- Performance: ≥30% reduction in critical‑path latency vs baseline
- Reliability: success ≥99%, chaos tests ≥95% pass
- Cost: cost/100 jobs ≤ threshold (to be defined in planned pathwaymap.md)
- Observability: structured logs + timing/error metrics, basic tracing
- Security: secrets management, least privilege, audit trail for external operations

## 5) High‑impact risks and mitigations

- Escalating cost with volume → cache/batching, budgets, anomaly alerts
- Unstable external APIs → adapter pattern, feature flags, circuit breaker, sandbox
- Unpredictable data formats → contracts and schema validation, contract tests
- Divergent dev environments → containers/lockfiles, pinned versions, reproducible builds

## 6) Execution mechanics

- Tracking: 1 epic/issue “Highway R1” + board (todo/in‑progress/review/done)
- Cadence: small PRs, frequent merges, release candidate before R1
- Decision docs: ADRs in `docs/adr/` for key choices
- Runbooks: `docs/runbooks/` (incident response, release, rollback)

## 7) Links and sources

- Vision: [ROADMAP.md](./docs/ROADMAP.md)
- Execution: pathwaymap.md (planned)

## 8) Changelog

- v0.1 — first version of the Highway Map (this document)
