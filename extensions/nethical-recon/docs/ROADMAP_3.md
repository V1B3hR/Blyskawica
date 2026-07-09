# 🦾 NETHICAL RECON — ROADMAP 3.0 (PROFESSIONAL-GRADE)
**Repo:** `V1B3hR/nethical-recon`  
**Date:** 2025-12-16  
**Audience:** profesjonalni ethical hackers, red team / purple team, threat hunters, SOC/security engineers  
**Cel:** przejście z “rozbudowanego prototypu + CLI toolkit” do **zintegrowanej, testowalnej, skalowalnej platformy** (CLI + TUI + API) z AI-driven threat intelligence i automatyzacją.


## 📊 Implementation Status

- ✅ **PHASE A** — Foundation & Repo Professionalization (Completed: 2025-12-16)
- ✅ **PHASE B** — Unified Data Model + Normalization (Completed: 2025-12-17)
- ✅ **PHASE C** — Worker Queue + Scheduler + Concurrency Policy (Completed: 2025-12-24)
- ✅ **PHASE D** — API (REST) + OpenAPI + Auth (Completed: 2025-12-25)
- ✅ **PHASE E** — Observability: Logging + Metrics + Tracing (Completed: 2025-12-26)
- ✅ **PHASE F** — Docker / Kubernetes / Helm (Completed: 2025-12-26)
- ✅ **PHASE G** — Secrets Management (Completed: 2025-12-27)
- ✅ **PHASE H** — AI-Driven Threat Intelligence (Completed: 2025-12-27)
- ✅ **PHASE I** — Pro Recon Plugins (Completed: 2025-12-27)
---

## 0) Zasady projektowe (non‑negotiables)
### 0.1 Legal / Ethics by default
- Wymuszona zgoda użytkownika + tryb “authorized-only” (już jest — utrzymać).
- “Guard rails”:
  - domyślnie ograniczony zakres skanów (rate limiting, concurrency cap),
  - obowiązkowe logowanie działań (audit trail),
  - “Rules of Engagement” (RoE) jako plik konfiguracyjny dla sesji.
- “Evidence integrity”:
  - hash wyników, podpisywanie raportów, spójność czasu (UTC).

### 0.2 Product-grade engineering
- Testy, CI, wydania, changelog, wersjonowanie semver.
- Modularność: `core/services/adapters/cli/ui`.
- Stabilny model danych i kontrakty API.
- Observability: logging/metrics/traces.
- Security hardening: sekrety, SAST/DAST, SBOM.

---

## 1) Docelowa architektura (Target Architecture)
### 1.1 Warstwy
- **core/**
  - modele domenowe: Target, Asset, Finding, Evidence, ScanJob, ToolRun, IOC, Threat, Baseline
  - walidacje, reguły scoringu, normalizacja danych
- **services/**
  - orkiestracja skanów, enrichment (Shodan/Censys/DNS), correlation, reporting
  - “policy engine” (RoE, limity, allowlist/denylist)
- **adapters/**
  - integracje: nmap/nikto/dirb/sublist3r, shodan/censys, DB backends, LLM provider, SIEM
- **api/**
  - REST + OpenAPI (na start), opcjonalnie GraphQL później
- **cli/**
  - narzędzie w stylu `nethical` (Typer/Click) z subkomendami
- **ui/**
  - dashboard TUI (rich/textual), ewentualnie web UI później
- **worker/**
  - kolejka zadań (Celery/RQ/Arq) i scheduler (APScheduler/Celery beat)
- **infra/**
  - Docker, Helm, K8s manifests, compose dla lokalnego stacku
- **docs/**
  - Sphinx/MkDocs + OpenAPI + ADR (Architecture Decision Records)

### 1.2 Event bus / kolejka zadań
- Cel: asynchroniczne, skalowalne uruchamianie skanów i enrichment.
- Minimalny “bus”:
  - `ScanRequested` → `ToolRunStarted` → `ToolRunFinished` → `FindingsNormalized` → `ReportGenerated`
- Implementacja:
  - **Celery + Redis** (szybki start) albo **RQ** (prościej), docelowo możliwość podmiany.
- Idempotencja:
  - każdy job ma `job_id`, każdy tool run `run_id`, retry bez duplikacji.

### 1.3 Plugin system dla skanerów
- Interfejs: `ScannerPlugin` z metodami:
  - `validate_target()`, `build_command()`, `run()`, `parse_output()`, `to_findings()`
- Rejestracja pluginów:
  - entrypoints (setuptools) albo mechanizm “discover from folder”.
- Cel: łatwo dodać np. `masscan`, `naabu`, `httpx`, `nuclei`, `ffuf`, `amass`.

---

## 2) Roadmap 3.0 — Etapy (z kryteriami “Definition of Done”)
Poniżej etapy są ułożone tak, by **szybko uzyskać profesjonalny “core”**, a potem skalować funkcje.

---

### PHASE A — Foundation & Repo Professionalization ✅ COMPLETE (Implemented 2025-12-16)
**Cel:** repo gotowe do rozwoju jak produkt.

**A.1 Packaging & structure** ✅
- ✅ Migracja do `pyproject.toml` (Poetry lub uv/pip-tools).
- ✅ Struktura `src/nethical_recon/...` + entrypoint `nethical`.
- ✅ Konfiguracja `black`, `mypy` (opcjonalnie), `pre-commit`.

**A.2 CI/CD** ✅
- ✅ GitHub Actions:
  - ✅ lint + tests,
  - ✅ dependency scanning,
  - ✅ build artifact (wheel),
  - opcjonalnie publish do PyPI (później).
- ✅ Security checks:
  - ✅ **Bandit**, **pip-audit**, Safety.

**A.3 Release discipline** ✅
- ✅ `CHANGELOG.md` (Keep a Changelog)
- ✅ Tagowanie `v0.x` → `v1.0` po spełnieniu kryteriów stabilności.

**DoD PHASE A** ✅ ALL VERIFIED
- ✅ `pip install -e .` działa
- ✅ `nethical --help` działa
- ✅ CI przechodzi na PR (workflow created and configured)
- ✅ podstawowe testy smoke istnieją (5 tests passing)

---

### PHASE B — Unified Data Model + Normalization (3–6 tyg.)
**Status:** ✅ COMPLETE (Implemented 2025-12-17)

All objectives achieved:
- ✅ Pydantic v2 domain models (Target, ScanJob, ToolRun, Evidence, Finding, Asset, IOC)
- ✅ SQLAlchemy + Alembic migrations
- ✅ Repository pattern for data access
- ✅ Nmap XML parser with Finding normalization
- ✅ Full evidence provenance tracking
- ✅ 32 tests passing (25 model tests + 7 parser tests)

**Cel:** wspólny model danych dla wszystkich modułów i narzędzi.

**B.1 Domain model**
- Pydantic v2 modele:
  - `Target` (domain/ip/cidr, scope)
  - `ScanJob`, `ToolRun`, `Evidence`
  - `Finding` (severity, confidence, tags, references)
  - `Asset` (host/service/url)
  - `IOC` (ip/domain/hash/url/email)
- Normalizacja wyników skanerów do `Finding`.

**B.2 Storage**
- Minimum: SQLite jako “dev default”.
- Docelowo: Postgres jako rekomendowany backend.
- SQLAlchemy + Alembic migracje.
- “Multi-backend” zostaje w roadmap, ale najpierw jeden stabilny.

**B.3 Evidence & provenance**
- Każdy output ma:
  - timestamp UTC,
  - tool version,
  - command line,
  - hash pliku wynikowego,
  - referencję do job/run.

**DoD PHASE B**
- Jedna komenda CLI potrafi uruchomić 2 narzędzia i zapisać wyniki jako zunifikowane `Findings`.
- Można odtworzyć “co i czym było uruchomione” (auditability).

---

### PHASE C — Worker Queue + Scheduler + Concurrency Policy ✅ COMPLETE (Implemented 2025-12-24)
**Cel:** skany asynchroniczne, stabilne, skalowalne, zgodne z RoE.
**Status:** ✅ COMPLETE (Implemented 2025-12-24)

All objectives achieved:
- ✅ Celery + Redis worker queue implementation
- ✅ 5 core tasks: run_scan_job, run_tool, normalize_results, finalize_job, generate_report
- ✅ 2 scheduled tasks: update_baselines, cleanup_old_results
- ✅ Celery Beat scheduler with cron-based schedules
- ✅ Policy Engine (RoE) with network, tool, and rate limit policies
- ✅ Nmap tool adapter with evidence generation
- ✅ 36 comprehensive tests (29 policy + 7 worker)
- ✅ Black formatting applied
- ✅ Full documentation in PHASE_C_SUMMARY.md


**C.1 Queue**
- Celery/RQ worker + Redis.
- Zadania:
  - `run_scan_job(job_id)`

- ✅ `nethical job submit ...` i `nethical job status ...` działają
- ✅ Worker może odpalać równolegle, ale trzyma limity RoE
  - `generate_report(job_id)`
- ✅ 68 tests passing (32 model + 7 parser + 5 smoke + 29 policy + 7 worker)


**C.2 Scheduler**
- APScheduler/Celery beat:
  - cykliczne recon (np. co 6h/24h),
  - baseline update.

**C.3 Policy engine (RoE)**
- Limity: requests/sec, max parallel tools, allowlist networks.
- Blokady “high-risk tools” bez wyraźnego flag/konfigu.

**DoD PHASE C**
- `nethical job submit ...` i `nethical job status ...` działają
- Worker może odpalać równolegle, ale trzyma limity RoE

---

### PHASE D — API (REST) + OpenAPI + Auth ✅ COMPLETE (Implemented 2025-12-25)
**Cel:** profesjonalna rozszerzalność i integracja z innymi systemami.
**Status:** ✅ COMPLETE (Implemented 2025-12-25)

All objectives achieved:
- ✅ FastAPI REST API with comprehensive endpoints
- ✅ 20+ endpoints: /targets, /jobs, /runs, /findings, /reports
- ✅ Filtering, pagination, and sorting on all list endpoints
- ✅ JWT token authentication (OAuth2)
- ✅ API key authentication (Bearer tokens)
- ✅ Role-based access control (viewer/operator/admin)
- ✅ Scope-based authorization (read, write, admin)
- ✅ OpenAPI auto-generated documentation
- ✅ Swagger UI at /api/v1/docs
- ✅ ReDoc at /api/v1/redoc
- ✅ CLI integration: `nethical api serve`
- ✅ 27 comprehensive tests (all passing)
- ✅ Full documentation in PHASE_D_SUMMARY.md


**D.1 REST API**
- FastAPI:
  - /targets, /jobs, /runs, /findings, /reports
  - filtrowanie po czasie, severity, tagach, toolach
- OpenAPI auto-generowane.

**D.2 AuthN/AuthZ**
- Start: API key / token (dev/pro).
- Docelowo: OAuth2/JWT + role: viewer/operator/admin.

**D.3 Documentation**
- Swagger/OpenAPI + przykładowe requesty
- “Integration cookbook” (SIEM, ticketing, pipelines)

**DoD PHASE D**
- ✅ Można odpalić job przez API i odebrać wyniki
- ✅ OpenAPI kompletne, działa w CI jako “contract”

---

### PHASE E — Observability: Logging + Metrics + Tracing ✅ COMPLETE (Implemented 2025-12-26)
**Cel:** debugowanie, monitoring, audyt w środowisku pro.
**Status:** ✅ COMPLETE (Implemented 2025-12-26)

All objectives achieved:
- ✅ Structured logging with structlog (JSON + console modes)
- ✅ Correlation IDs (job_id, run_id, target_id) throughout logs
- ✅ Multi-level logging (audit/security/ops)
- ✅ Prometheus metrics collection (12+ metric families)
- ✅ Comprehensive metrics: tool runs, findings, jobs, queue, API, errors
- ✅ /metrics endpoint on API
- ✅ API metrics middleware (automatic request tracking)
- ✅ Worker integration with structured logging
- ✅ Docker Compose stack (7 services: API, Worker, Scheduler, Redis, Postgres, Prometheus, Grafana)
- ✅ Grafana dashboard template (10 panels)
- ✅ Prometheus alert rules (6 alerts)
- ✅ 20 comprehensive tests (all passing)
- ✅ Full documentation in PHASE_E_SUMMARY.md

**E.1 Logging**
- `structlog` + JSON logs (łatwe pod ELK).
- Korelacja: `job_id`, `run_id`, `target_id`.
- Poziomy: audit/security/ops.

**E.2 Metrics**
- Prometheus:
  - czas trwania tool runs,
  - liczba findings per job,
  - error rate,
  - queue depth.

**E.3 Dashboards & alerts**
- Grafana dashboard template:
  - throughput skanów,
  - top failing tools,
  - "noisy targets".

**DoD PHASE E** ✅ ALL VERIFIED
- ✅ Lokalny stack `docker compose` z Prometheus+Grafana i JSON logs do stdout
- ✅ Metryki dostępne na `/metrics`
- ✅ 20 tests passing (100% success rate)

---

### PHASE F — Docker / Kubernetes / Helm ✅ COMPLETE (Implemented 2025-12-26)
**Cel:** skalowalność i standard wdrożeń.
**Status:** ✅ COMPLETE (Implemented 2025-12-26)

All objectives achieved:
- ✅ Multi-stage Dockerfiles with optimized builds
- ✅ Service-specific images: API, Worker, Scheduler
- ✅ Complete Kubernetes manifests (11 files)
- ✅ Helm chart with production-ready templates
- ✅ PostgreSQL StatefulSet with persistent storage
- ✅ Redis deployment with configurable persistence
- ✅ PersistentVolumeClaim for evidence/reports (ReadWriteMany)
- ✅ HPA (Horizontal Pod Autoscaler) for workers (2-10 replicas)
- ✅ Ingress configuration with TLS support
- ✅ Secret and ConfigMap management
- ✅ Security contexts (non-root, capabilities dropped)
- ✅ Health checks for all services
- ✅ Comprehensive documentation (3 guides)

**F.1 Docker** ✅
- ✅ Multi-stage build, minimalny obraz
- ✅ Oddzielne obrazy: `Dockerfile.api`, `Dockerfile.worker`, `Dockerfile.scheduler`
- ✅ Non-root user (UID 1000)
- ✅ Health checks included
- ✅ Optimized layer caching

**F.2 Kubernetes** ✅
- ✅ Complete K8s manifests in `infra/k8s/`
- ✅ Helm chart in `infra/helm/nethical-recon/`
  - ✅ deployment api (2 replicas, rolling updates)
  - ✅ deployment worker (2+ replicas with HPA)
  - ✅ deployment scheduler (1 replica, Celery Beat)
  - ✅ secret management (ConfigMap + Secrets)
  - ✅ HPA (autoscaling) dla workerów (2-10 replicas)
  - ✅ ServiceAccount with RBAC
  - ✅ Ingress with rate limiting

**F.3 Storage & networking** ✅
- ✅ Postgres jako StatefulSet with persistent storage (10Gi)
- ✅ Persistent volume na evidence/report artifacts (50Gi, ReadWriteMany)
- ✅ Support for cloud storage (EFS, Azure Files, Filestore, NFS)
- ✅ Network policies ready
- ✅ Service mesh ready

**DoD PHASE F** ✅ ALL VERIFIED
- ✅ `helm install nethical infra/helm/nethical-recon` deploys full stack to K8s
- ✅ All services start and pass health checks
- ✅ Workers auto-scale based on CPU/memory
- ✅ Documentation complete (kubernetes-deployment.md, docker-deployment.md, Helm README)
- ✅ Full documentation in PHASE_F_SUMMARY.md

---

### PHASE G — Secrets Management ✅ COMPLETE (Implemented 2025-12-27)
**Cel:** bezpieczne zarządzanie kluczami API i tokenami.
**Status:** ✅ COMPLETE (Implemented 2025-12-27)

All objectives achieved:
- ✅ Centralized secrets management module (`src/nethical_recon/secrets/`)
- ✅ Multiple backend support: EnvBackend, DotEnvBackend
- ✅ Prepared for future: VaultBackend, K8sSecretsBackend
- ✅ Secrets sanitizer with pattern matching (15+ patterns)
- ✅ API and Worker config integration
- ✅ `.env.example` template with all required secrets
- ✅ Enhanced .gitignore to prevent secret commits
- ✅ CI secret scanning with gitleaks
- ✅ Secret leakage prevention tests in CI
- ✅ 35 comprehensive tests (all passing)
- ✅ Full documentation in PHASE_G_SUMMARY.md

**G.1 Minimalnie** ✅
- ✅ `.env` + env vars, brak sekretów w repo
- ✅ Wymuszenie: brak kluczy w logach (automatic sanitization)
- ✅ Pattern matching for API keys, tokens, passwords, connection strings
- ✅ Sanitization utilities for dicts, strings, lists

**G.2 Docelowo** (Prepared)
- 🔄 HashiCorp Vault / Kubernetes External Secrets (backend stubs ready)
- 🔄 Rotacja sekretów (manual process, automation ready)
- ✅ "Secret scopes" per connector (via get_external_api_keys())

**DoD PHASE G** ✅ ALL VERIFIED
- ✅ Sekrety nie pojawiają się w outputach (sanitizer tested)
- ✅ Test "secret-leak" w CI (gitleaks + pytest)
- ✅ 35 tests passing (100% success rate)
- ✅ Documentation complete (PHASE_G_SUMMARY.md)


---

### PHASE H — AI-Driven Threat Intelligence ✅ COMPLETE (Implemented 2025-12-27)
**Cel:** AI jako realna przewaga, nie tylko metafora.
**Status:** ✅ COMPLETE (Implemented 2025-12-27)

All objectives achieved:
- ✅ LLM Client with evidence-based reporting (OpenAI integration)
- ✅ Guardrails to prevent hallucinations
- ✅ Deduplication engine with smart merging
- ✅ Finding correlation and similarity detection
- ✅ Threat Intelligence Manager with feed support
- ✅ STIX 2.1 export format
- ✅ JSON, Markdown, PDF (stub) export formats
- ✅ Evidence reference tracking throughout
- ✅ 16 comprehensive tests (all passing)
- ✅ Full documentation in PHASE_H_SUMMARY.md

**H.1 Realistic AI layers**
- **LLM**: raportowanie, triage, deduplikacja, summarization (z twardymi guardrails).
- **Rules/heuristics**: szybka klasyfikacja i scoring.
- **Statistical baseline**: anomaly detection (np. proste modele statystyczne).
- **Graph correlation**: zależności IOC ↔ asset ↔ finding ↔ campaign.

**H.2 “Evidence-based LLM”**
- LLM dostaje tylko:
  - znormalizowane findings,
  - dowody (wycinki), bez “zgadywania”.
- Automatyczna walidacja: “no hallucination policy”:
  - raport musi referencjonować evidence_id.

**H.3 Threat knowledge**
- Integracja feedów:
  - MISP (opcjonalnie),
  - OpenCTI (opcjonalnie),
  - STIX/TAXII (później).
- Eksport do formatów SOC:
  - STIX 2.1, JSON, Markdown, PDF.

**DoD PHASE H**
- AI raport jest “traceable”: każde twierdzenie wskazuje evidence/findings
- Jest dedup i correlation (mniej szumu)

---

### PHASE I — Pro Recon Plugins ✅ COMPLETE (Implemented 2025-12-27)
**Cel:** narzędzie realnie używalne przez pro red team/hunters.
**Status:** ✅ COMPLETE (Implemented 2025-12-27)

All objectives achieved:
- ✅ Unified plugin architecture with ToolPlugin base class
- ✅ 5 professional reconnaissance tool adapters implemented
- ✅ Evidence-based execution with full provenance tracking
- ✅ Unified Finding normalization across all tools
- ✅ JSON/JSON Lines output parsing
- ✅ Intelligent severity and confidence assessment
- ✅ 34 comprehensive tests (all passing)
- ✅ Full documentation in PHASE_I_SUMMARY.md

**I.1 Nowe narzędzia** ✅
- ✅ Discovery: `masscan` (fast port scanner, 10M pps capable)
- ✅ HTTP: `httpx` (HTTP toolkit with tech detection)
- ✅ Vuln: `nuclei` (vulnerability scanner with 3000+ templates)
- ✅ Content: `ffuf` (fast web fuzzer for content discovery)
- ✅ Subdomains: `amass` (OSINT-based subdomain enumeration)
- 🔄 Additional tools: `naabu`, `katana`, `theHarvester` (future enhancements)

**I.2 Parsery** ✅
- ✅ JSON/JSON Lines parsing for all tools
- ✅ Unified severity mapping (Critical/High/Medium/Low/Info)
- ✅ Confidence scoring based on tool characteristics
- ✅ CVE/CWE extraction (nuclei)
- ✅ Evidence preservation with checksums
- ✅ Automatic version detection

**DoD PHASE I** ✅ ALL VERIFIED
- ✅ 6 pluginów działa w jednym modelu Findings (nmap + masscan + nuclei + httpx + ffuf + amass)
- ✅ Wszystkie adaptery używają base_plugin.py interface
- ✅ Pełny evidence chain dla każdego narzędzia
- ✅ 34 tests passing (100% success rate)
- ✅ Documentation complete (PHASE_I_SUMMARY.md)

---

## 3) Usprawnienia istniejących modułów (konkretne pomysły)
### 3.1 `nethical_recon.py` → CLI “front-end”, nie monolit
- Rozbić na:
  - `cli/commands/*.py` (Typer)
  - `adapters/tools/nmap.py`, `nikto.py` itd.
  - `services/orchestrator.py`
- Zachować menu jako opcjonalny tryb interaktywny (`nethical tui` lub `nethical interactive`).

### 3.2 UI: Dashboard “prawdy danych”
- Obecny TUI jest fajny, ale docelowo:
  - dashboard ma czytać z API/DB (job status, findings, alerts),
  - live feed na eventach (websocket lub polling).
- Dodać:
  - widok “Findings Explorer” (filtry: severity/tool/target),
  - “Evidence viewer”,
  - “RoE & limits” screen.

### 3.3 AI: od heurystyk do “verified intelligence”
- `ai/reporter.py`:
  - dodać prawdziwy scoring pipeline: base severity + confidence + exploitability indicators
  - “CVSS-like” może zostać, ale koniecznie z evidence references.
- `ai/learner.py`:
  - baseline: rozdzielić per target/segment,
  - metryki: robust statistics (median, MAD) zamiast samych średnich.

### 3.4 Forest metaphor: z “ładnej abstrakcji” do asset inventory
- Forest = asset inventory + relationships:
  - Trees = hosty,
  - Branches = usługi/porty/procesy,
  - Leaves = requesty/sesje/artefakty.
- Dodać graf relacji:
  - eksport do Graphviz,
  - w DB trzymać relacje.

### 3.5 Database module: pragmatyzm
- Multi-backend to super wizja, ale:
  - “Tier 1”: SQLite + Postgres (pełne wsparcie)
  - “Tier 2”: reszta jako eksperymentalne pluginy
- Migrations + indeksy pod query (po target_id, time, severity).

---

## 4) Security & Quality Plan (dla pro użycia)
### 4.1 Testy
- **Unit**: parsers, model validations, policy engine.
- **Integration**: “run tool in container/mock”, DB migrations, API endpoints.
- **Security scans**:
  - Bandit, Semgrep, pip-audit,
  - secret scanning (gitleaks).
- Golden files:
  - stałe próbki outputów nmap/nikto/nuclei jako fixtures.

### 4.2 Threat model
- Dokument “Threat Model”:
  - ataki na pipeline (poisoning outputów, LLM prompt injection),
  - ryzyka przechowywania evidence,
  - ryzyka nadużyć przez użytkownika.

### 4.3 Safe defaults
- Domyślny tryb “low impact” (rate limiting).
- Wymóg explicit flag na agresywne tryby.

---

## 5) Integracje pro (opcjonalne, ale bardzo pod “security pros”)
- SIEM:
  - Splunk HEC, Elastic, Sentinel (connectors)
- Ticketing:
  - Jira/GitHub Issues export (znormalizowane findings → ticket)
- Reporting:
  - PDF export (WeasyPrint) + “client-ready template”
- Collaboration:
  - multi-user (RBAC), namespaces/tenants

---

## 6) Mierniki sukcesu (KPIs)
- **Noise ratio**: % zduplikowanych/low-confidence findings spada z czasem.
- **Reproducibility**: każdy raport można odtworzyć z DB+evidence.
- **Time-to-triage**: skrócony dzięki AI+dedup.
- **Operator trust**: AI nie “zmyśla” — wszystko ma evidence.

---

## 7) Proponowana ścieżka wersji (SemVer)
- `v0.1–0.3`: PHASE A–B (foundation + model)
- `v0.4–0.6`: PHASE C (queue/scheduler)
- `v0.7–0.9`: PHASE D–E (API + observability)
- `v1.0`: stabilny core, API contract, test coverage, docker compose, podstawowe pluginy
- `v1.1+`: K8s/Helm, advanced AI correlation, SIEM integrations

---

## 8) Backlog “nice to have” (wysoki impact)
- SBOM (CycloneDX) + podpisywanie artefaktów.
- “Replay mode”: odtworzenie joba z evidence bez ponownego skanowania.
- “Attack surface diff”: porównanie wyników między tygodniami (co się zmieniło).
- “Engagement profiles”: preset konfiguracji pod bug bounty / internal / red team.
- “Scoping DSL”: opis zakresu i zasad w YAML (co wolno, czego nie).

---

## 9) Minimalny plan na najbliższe 2 tygodnie (praktycznie)
1. `pyproject.toml`, reorganizacja katalogów do `src/`
2. CLI na Typer: `nethical scan`, `nethical report`, `nethical job`
3. Pydantic models: Target/Job/Run/Finding/Evidence
4. SQLite storage + Alembic
5. 1 parser w pełni: Nmap → Findings (XML preferowane)
6. CI: lint + unit tests + security scans

---

**Efekt końcowy Roadmap 3.0:** Nethical Recon jako **profesjonalna platforma**:  
- szybka w użyciu (CLI/TUI),  
- rozszerzalna (pluginy + API),  
- skalowalna (queue + Docker/K8s),  
- obserwowalna (ELK/Prom/Grafana),  
- bezpieczna (sekrety, SAST/DAST, policy engine),  
- i z AI, które jest “evidence-based”, a nie “story-based”.
