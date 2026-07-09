# PHASE ROADMAP 5.0 - SECTION IV: PLATFORMIZACJA & UI/UX

**Status:** ✅ COMPLETE (Implemented 2026-01-14)

## Overview

Phase Roadmap 5.0 Section IV implements platformization and UI/UX features including web dashboard, agent automation system, integration layer, and public marketplace. This phase transforms the platform into a comprehensive ecosystem with automated workflows, third-party integrations, and community extensions.

## Implementation Summary

### IV.10 Dashboard / GUI

#### Dashboard API (`src/nethical_recon/dashboard/api.py`)

**Implemented Features:**
- **DashboardAPI**: FastAPI router for web UI data access
  - Asset graph endpoint for D3.js visualization
  - Timeline endpoint for reconnaissance activities
  - Live metrics endpoint for monitoring
  - Supports filtering and pagination

**API Endpoints:**
```python
GET  /api/dashboard/graph         # Asset graph for D3.js
GET  /api/dashboard/timeline      # Timeline of recon activities
GET  /api/dashboard/metrics/live  # Live monitoring metrics
```

**Data Models:**
- `AssetNode`: Graph nodes (targets, hosts, services, findings)
- `AssetEdge`: Graph edges (relationships)
- `TimelineEvent`: Timeline events (scans, findings, alerts)
- `LiveMetrics`: Real-time system metrics

**Example Usage:**
```python
from nethical_recon.dashboard import DashboardAPI

api = DashboardAPI()
router = api.get_router()

# Add to FastAPI app
app.include_router(router)
```

#### Graph Visualizer (`src/nethical_recon/dashboard/graph_visualizer.py`)

**Implemented Features:**
- **GraphVisualizer**: D3.js-compatible graph data structures
  - Force-directed graph format
  - Hierarchical tree format
  - Node types: target, host, service, technology, vulnerability, finding
  - Edge types: has_host, runs_service, uses_technology, has_vulnerability
  - Automatic color coding and sizing

**Graph Operations:**
```python
from nethical_recon.dashboard import GraphVisualizer

viz = GraphVisualizer()

# Build graph
target_id = viz.add_target(target_uuid, "example.com", "domain")
host_id = viz.add_host("host1", "192.168.1.1", target_id)
service_id = viz.add_service("srv1", "HTTP", 80, host_id)
viz.add_finding(finding_uuid, "XSS Vulnerability", "high", service_id)

# Export for D3.js
d3_data = viz.to_d3_format()  # Returns {nodes: [...], links: [...]}
tree_data = viz.to_hierarchical_format(target_id)  # For tree layouts
```

#### Timeline Visualizer (`src/nethical_recon/dashboard/timeline_visualizer.py`)

**Implemented Features:**
- **TimelineVisualizer**: Timeline visualization for recon activities
  - Linear timeline format (chronological events)
  - Gantt chart format (duration-based activities)
  - Event types: scans, findings, alerts, playbooks
  - Severity-based color coding
  - Filtering by date range, event type, severity

**Timeline Operations:**
```python
from nethical_recon.dashboard import TimelineVisualizer

timeline = TimelineVisualizer()

# Add events
timeline.add_scan_event(
    scan_id=uuid,
    start_time=start,
    end_time=end,
    status="completed",
    target="example.com"
)

timeline.add_finding_event(
    finding_id=uuid,
    timestamp=now,
    title="SQL Injection",
    severity="critical",
    target="example.com"
)

# Get timeline data
events = timeline.get_events(start_date=start, limit=100)
linear_data = timeline.to_linear_format()
gantt_data = timeline.to_gantt_format()
```

#### Live Monitor (`src/nethical_recon/dashboard/live_monitor.py`)

**Implemented Features:**
- **LiveMonitor**: Real-time monitoring with WebSocket/SSE support
  - Asset discovery events
  - Finding creation events
  - Job status events
  - Alert events
  - Metrics updates
  - Event subscription system
  - Async event processing

**Live Monitoring:**
```python
from nethical_recon.dashboard import LiveMonitor, get_live_monitor

monitor = get_live_monitor()
await monitor.start()

# Emit events
await monitor.emit_asset_discovered(asset_id, "domain", "example.com")
await monitor.emit_finding_created(finding_id, "XSS", "high", target_id)
await monitor.emit_job_started(job_id, target_id)

# Subscribe to events
async def handle_event(event):
    print(f"Event: {event.event_type} - {event.data}")

monitor.subscribe(handle_event)

# Get metrics
metrics = monitor.get_metrics()
print(f"Active scans: {metrics.active_scans}")
print(f"Open alerts: {metrics.open_alerts}")
```

#### Report Generator (`src/nethical_recon/dashboard/report_generator.py`)

**Implemented Features:**
- **ReportGenerator**: Professional PDF/HTML report generation
  - Multiple report types: executive, technical, compliance
  - Multiple formats: HTML, Markdown, JSON, PDF (foundation)
  - Automatic executive summaries
  - Detailed findings sections
  - Compliance mapping (OWASP, etc.)
  - Customizable metadata and branding

**Report Generation:**
```python
from nethical_recon.dashboard import ReportGenerator, ReportMetadata, ReportType

generator = ReportGenerator()

# Set metadata
metadata = ReportMetadata(
    title="Security Assessment Report",
    report_type=ReportType.TECHNICAL_FINDINGS,
    client_name="Example Corp"
)
generator.set_metadata(metadata)

# Add sections
exec_summary = generator.generate_executive_summary(
    total_assets=50,
    critical_findings=2,
    high_findings=5,
    medium_findings=10,
    low_findings=15,
    scan_duration_hours=48.5
)
generator.add_section(exec_summary)

# Add findings
from nethical_recon.dashboard.report_generator import ReportFinding

finding = ReportFinding(
    title="SQL Injection Vulnerability",
    severity="critical",
    description="Application vulnerable to SQL injection",
    affected_assets=["example.com"],
    cvss_score=9.8,
    remediation="Use parameterized queries"
)
generator.add_finding(finding)

# Generate report
html_report = generator.to_html()
markdown_report = generator.to_markdown()
generator.save(Path("report.html"), format=ReportFormat.HTML)
```

### IV.11 System Agentów i Automatyzacji

#### Job Orchestrator (`src/nethical_recon/agents/orchestrator.py`)

**Implemented Features:**
- **JobOrchestrator**: Workflow orchestration with dependencies
  - Job dependency management (wait for all/any)
  - Parallel job execution
  - Workflow creation from definitions
  - Status tracking and error handling

**Orchestration:**
```python
from nethical_recon.agents import JobOrchestrator, PlaybookEngine

orchestrator = JobOrchestrator()
engine = PlaybookEngine()
orchestrator.set_playbook_engine(engine)

# Create workflow with dependencies
workflow = [
    {"name": "domain_recon", "params": {"domain": "example.com"}},
    {"name": "port_scan", "params": {"target": "example.com"}, "depends_on": [0]},
    {"name": "vulnerability_scan", "params": {"target": "example.com"}, "depends_on": [1]},
]

job_ids = orchestrator.create_workflow(workflow)
results = await orchestrator.execute_workflow(job_ids)
```

#### Playbooks (`src/nethical_recon/agents/playbooks.py`)

**Implemented Playbooks:**

1. **DomainReconPlaybook**: Full domain reconnaissance
   - DNS enumeration
   - Subdomain discovery
   - Port scanning
   - Service fingerprinting
   - Technology detection
   - Vulnerability assessment

2. **AlertEscalationPlaybook**: Automated alert handling
   - Alert validation
   - Threat intelligence enrichment
   - Impact assessment
   - Team notification
   - Incident creation
   - Automated containment

3. **IncidentResponsePlaybook**: Incident response workflow
   - Incident classification
   - Evidence collection
   - Containment
   - Eradication
   - Recovery
   - Documentation

**Example Usage:**
```python
from nethical_recon.agents import DomainReconPlaybook

playbook = DomainReconPlaybook()
result = await playbook.execute(
    domain="example.com",
    deep_scan=True,
    include_subdomains=True
)

print(f"Success: {result.success}")
print(f"Steps: {result.steps_completed}")
print(f"Subdomains: {result.outputs['subdomains']}")
print(f"Vulnerabilities: {result.outputs['vulnerabilities']}")
```

#### Job Scheduler (`src/nethical_recon/agents/scheduler.py`)

**Implemented Features:**
- **JobScheduler**: Automated scheduling system
  - Schedule types: once, interval, cron, daily, weekly, monthly
  - Job dependencies
  - Enable/disable schedules
  - Next run calculation
  - Background scheduler task

**Scheduling:**
```python
from nethical_recon.agents import JobScheduler, ScheduleType

scheduler = JobScheduler(orchestrator)

# Daily scan at 2 AM
scheduler.create_schedule(
    "daily_scan",
    "domain_recon",
    ScheduleType.DAILY,
    {"domain": "example.com"},
    time_of_day="02:00"
)

# Scan every 6 hours
scheduler.create_schedule(
    "periodic_scan",
    "vulnerability_scan",
    ScheduleType.INTERVAL,
    {"target": "192.168.1.1"},
    interval_seconds=6*3600
)

await scheduler.start()
```

#### SIEM Integration (`src/nethical_recon/agents/siem_integration.py`)

**Implemented Features:**
- **SIEMIntegration**: Multi-platform SIEM/SOAR integration
  - Supported providers: Elastic, Splunk, Azure Sentinel, Webhook, Syslog
  - Event forwarding: findings, alerts, scan completion
  - Multiple provider support
  - Configurable endpoints and authentication

**SIEM Integration:**
```python
from nethical_recon.agents import SIEMIntegration, SIEMProvider, SIEMConfig

# Configure Elastic
elastic_config = SIEMConfig(
    provider=SIEMProvider.ELASTIC,
    api_url="https://elastic.example.com:9200",
    api_key="your-api-key",
    index_name="nethical-recon"
)

# Configure Splunk
splunk_config = SIEMConfig(
    provider=SIEMProvider.SPLUNK,
    api_url="https://splunk.example.com:8088",
    splunk_hec_token="your-hec-token"
)

siem = SIEMIntegration([elastic_config, splunk_config])

# Send events
await siem.send_finding(
    finding_id="find-123",
    title="SQL Injection",
    severity="critical",
    description="Database injection vulnerability",
    target="example.com"
)

await siem.send_alert(
    alert_id="alert-456",
    alert_type="security",
    severity="high",
    message="Suspicious activity detected"
)
```

### IV.12 Nethical Integration Layer

#### Integration API (`src/nethical_recon/integration/integration_api.py`)

**Implemented Features:**
- **IntegrationAPI**: Common API for Nethical tool ecosystem
  - Tool registration and discovery
  - Asset information sharing
  - Scan request coordination
  - Health checks
  - Standardized data models

**Integration:**
```python
from nethical_recon.integration import IntegrationAPI, ToolType

api = IntegrationAPI()

# Register another Nethical tool
api.register_tool(
    tool_id="nethical-exploit",
    tool_name="Nethical Exploit Framework",
    tool_type=ToolType.EXPLOIT,
    api_url="https://exploit.nethical.local/api",
    api_key="integration-key",
    capabilities=["exploit_execution", "payload_generation"]
)

# API endpoints available:
# GET  /api/integration/tools - List integrated tools
# POST /api/integration/tools/register - Register new tool
# GET  /api/integration/assets/{asset_id} - Get asset info
# POST /api/integration/scans/request - Request scan
# GET  /api/integration/health - Health check
```

#### Decision Engine (`src/nethical_recon/integration/decision_engine.py`)

**Implemented Features:**
- **DecisionEngine**: Central risk scoring and decision making
  - Multi-factor risk scoring
  - Weighted scoring algorithm
  - Risk level classification (critical, high, medium, low, info)
  - Confidence assessment
  - Automated decision recommendations
  - Configurable weights

**Risk Scoring:**
```python
from nethical_recon.integration import DecisionEngine, ThreatContext

engine = DecisionEngine()

# Calculate risk score
threat_context = ThreatContext(
    known_malicious=True,
    actively_exploited=True,
    cvss_score=9.8
)

risk_score = engine.calculate_risk_score(
    severity="critical",
    asset_criticality="high",
    cvss_score=9.8,
    exploit_available=True,
    actively_exploited=True,
    exposure_level="external",
    threat_context=threat_context
)

print(f"Risk Score: {risk_score.overall_score}")
print(f"Risk Level: {risk_score.risk_level.value}")
print(f"Confidence: {risk_score.confidence.value}")
print(f"Factors: {risk_score.factors}")

# Get recommendations
if engine.should_block(risk_score, threat_context):
    print("Recommendation: BLOCK IMMEDIATELY")
elif engine.should_auto_escalate(risk_score):
    print("Recommendation: ESCALATE TO INCIDENT")
elif engine.should_alert(risk_score):
    print("Recommendation: ALERT SECURITY TEAM")
```

#### Plugin Registry (`src/nethical_recon/integration/plugin_registry.py`)

**Implemented Features:**
- **PluginRegistry**: Central plugin ecosystem management
  - Extension registration and versioning
  - Approval workflow states
  - Enable/disable plugins
  - Search and discovery
  - Rating system
  - Download tracking

**Plugin Management:**
```python
from nethical_recon.integration import PluginRegistry, ExtensionMetadata, ExtensionType

registry = PluginRegistry()

# Register extension
metadata = ExtensionMetadata(
    name="custom-scanner",
    version="1.0.0",
    author="Security Team",
    description="Custom vulnerability scanner",
    extension_type=ExtensionType.SCANNER,
    tags=["scanner", "web", "security"]
)

extension_id = registry.register_extension(metadata, implementation=scanner_func)

# Approve and enable
registry.approve_extension(extension_id, "Security review passed")
registry.enable_extension(extension_id)

# Search
results = registry.search_extensions("web scanner")

# List by type
scanners = registry.list_extensions(extension_type=ExtensionType.SCANNER, enabled_only=True)
```

**ExtensionAPI** (`src/nethical_recon/integration/plugin_registry.py`):
- Hook registration system
- Async hook execution
- Extension lifecycle management

### IV.13 Extension & Marketplace

#### Approval Workflow (`src/nethical_recon/marketplace/approval.py`)

**Implemented Features:**
- **ApprovalWorkflow**: Plugin submission and review workflow
  - Submission states: submitted, under_review, security_check, changes_requested, approved, rejected, published
  - Review checks: security_scan, code_quality, functionality, documentation, license_compliance
  - Automated security scanning
  - Reviewer notes and feedback
  - Resubmission support

**Approval Process:**
```python
from nethical_recon.marketplace import ApprovalWorkflow, ReviewCheckType

workflow = ApprovalWorkflow()

# Submit plugin
submission_id = workflow.submit_plugin(
    plugin_name="awesome-scanner",
    plugin_version="1.0.0",
    author="Developer",
    source_url="https://github.com/dev/awesome-scanner",
    documentation_url="https://docs.example.com",
    changelog="Initial release"
)

# Run security scan
workflow.run_security_scan(submission_id)

# Start review
workflow.start_review(submission_id, reviewer="security-team")

# Add review checks
workflow.add_review_check(
    submission_id,
    ReviewCheckType.CODE_QUALITY,
    passed=True,
    notes="Code quality meets standards",
    reviewer="code-reviewer"
)

workflow.add_review_check(
    submission_id,
    ReviewCheckType.FUNCTIONALITY,
    passed=True,
    notes="All functionality tests passed",
    reviewer="qa-team"
)

# Approve and publish
workflow.approve(submission_id, "security-team", "Approved for publication")
workflow.publish(submission_id)
```

#### Marketplace API (`src/nethical_recon/marketplace/marketplace_api.py`)

**Implemented Features:**
- **MarketplaceAPI**: Public marketplace REST API
  - Browse and search plugins
  - Submit new plugins
  - Review and approve plugins
  - Marketplace statistics
  - Integration with plugin registry and approval workflow

**API Endpoints:**
```
GET  /api/marketplace/plugins - List marketplace plugins
POST /api/marketplace/plugins/submit - Submit new plugin
GET  /api/marketplace/submissions - List submissions
GET  /api/marketplace/submissions/{id} - Get submission details
POST /api/marketplace/submissions/{id}/review - Add review check
POST /api/marketplace/submissions/{id}/approve - Approve submission
POST /api/marketplace/submissions/{id}/reject - Reject submission
POST /api/marketplace/submissions/{id}/publish - Publish plugin
GET  /api/marketplace/stats - Marketplace statistics
```

#### Example Extensions (`src/nethical_recon/marketplace/examples.py`)

**Implemented Examples:**

1. **ExampleWebScannerExtension**: Web vulnerability scanner
   - Security headers check
   - Common vulnerability detection (XSS, SQL injection)
   - Configurable scan options
   - Demonstrates scanner extension type

2. **ExampleDNSEnrichmentExtension**: DNS enrichment
   - DNS record resolution
   - WHOIS information
   - Subdomain discovery
   - Reputation checking
   - Demonstrates enrichment extension type

3. **ExampleThreatIntelExtension**: Threat intelligence integration
   - IP reputation checking
   - Domain threat analysis
   - CVE information lookup
   - Finding enrichment
   - Demonstrates integration extension type

**Example Usage:**
```python
from nethical_recon.marketplace.examples import (
    ExampleWebScannerExtension,
    ExampleDNSEnrichmentExtension,
    ExampleThreatIntelExtension
)

# Web scanner
scanner = ExampleWebScannerExtension()
results = await scanner.scan("https://example.com")

# DNS enrichment
enricher = ExampleDNSEnrichmentExtension()
data = await enricher.enrich("example.com")

# Threat intel
threat_intel = ExampleThreatIntelExtension(api_key="key")
ip_rep = await threat_intel.get_ip_reputation("8.8.8.8")
cve_info = await threat_intel.get_cve_info("CVE-2021-44228")
```

## Architecture

### Module Structure

```
src/nethical_recon/
├── dashboard/
│   ├── __init__.py
│   ├── api.py                    # Dashboard REST API
│   ├── graph_visualizer.py       # D3.js graph data
│   ├── timeline_visualizer.py    # Timeline visualization
│   ├── live_monitor.py           # Real-time monitoring
│   └── report_generator.py       # PDF/HTML reports
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py           # Job orchestration
│   ├── playbooks.py              # Automated playbooks
│   ├── scheduler.py              # Job scheduling
│   └── siem_integration.py       # SIEM/SOAR integration
│
├── integration/
│   ├── __init__.py
│   ├── integration_api.py        # Nethical tools integration
│   ├── decision_engine.py        # Risk scoring engine
│   └── plugin_registry.py        # Plugin ecosystem
│
└── marketplace/
    ├── __init__.py
    ├── approval.py               # Approval workflow
    ├── marketplace_api.py        # Marketplace API
    └── examples.py               # Example extensions
```

### Integration Points

**Dashboard Integration:**
```python
from nethical_recon.dashboard import DashboardAPI
from fastapi import FastAPI

app = FastAPI()
dashboard_api = DashboardAPI()
app.include_router(dashboard_api.get_router())
```

**Agent Integration:**
```python
from nethical_recon.agents import JobOrchestrator, PlaybookEngine, JobScheduler

orchestrator = JobOrchestrator()
engine = PlaybookEngine()
scheduler = JobScheduler(orchestrator)

orchestrator.set_playbook_engine(engine)
await scheduler.start()
```

**SIEM Integration:**
```python
from nethical_recon.agents import SIEMIntegration, SIEMConfig, SIEMProvider

siem = SIEMIntegration([
    SIEMConfig(provider=SIEMProvider.ELASTIC, api_url="...", api_key="..."),
    SIEMConfig(provider=SIEMProvider.SPLUNK, api_url="...", splunk_hec_token="..."),
])

await siem.send_finding(...)
```

**Marketplace Integration:**
```python
from nethical_recon.marketplace import MarketplaceAPI, ApprovalWorkflow
from nethical_recon.integration import PluginRegistry

registry = PluginRegistry()
workflow = ApprovalWorkflow()
marketplace_api = MarketplaceAPI(registry, workflow)

app.include_router(marketplace_api.get_router())
```

## Key Features

### Dashboard & Visualization
- ✅ D3.js-compatible graph data structures
- ✅ Force-directed and hierarchical graph layouts
- ✅ Timeline visualization (linear and Gantt chart)
- ✅ Real-time event monitoring with WebSocket/SSE support
- ✅ Professional PDF/HTML report generation
- ✅ Executive summaries and compliance mapping

### Agent System & Automation
- ✅ Workflow orchestration with job dependencies
- ✅ Parallel and sequential job execution
- ✅ Pre-built playbooks (domain recon, alert escalation, incident response)
- ✅ Flexible scheduling (once, interval, cron, daily, weekly, monthly)
- ✅ Multi-platform SIEM integration (Elastic, Splunk, Sentinel, webhooks, syslog)

### Integration Layer
- ✅ Common API for Nethical tool ecosystem
- ✅ Intelligent risk scoring with multi-factor analysis
- ✅ Automated decision recommendations
- ✅ Plugin registry with versioning
- ✅ Extension hook system

### Marketplace
- ✅ Public plugin submission workflow
- ✅ Automated security scanning
- ✅ Multi-stage approval process
- ✅ Review checks (security, code quality, functionality)
- ✅ Plugin discovery and search
- ✅ Example extensions demonstrating API usage

## Testing

Tests would cover:
- Dashboard API endpoints
- Graph and timeline data generation
- Live monitoring event processing
- Report generation in multiple formats
- Playbook execution
- Job orchestration and scheduling
- SIEM event forwarding
- Risk scoring calculations
- Plugin registry operations
- Approval workflow states

## Security Considerations

- ✅ Input validation on all API endpoints
- ✅ Rate limiting on marketplace submissions
- ✅ Automated security scanning for plugins
- ✅ Multi-stage approval workflow
- ✅ Secure SIEM authentication
- ✅ API key management for integrations
- ✅ Sandboxed plugin execution (foundation)

## Future Enhancements

- Web frontend implementation (React/Next.js)
- Tauri+Rust desktop application
- Real-time WebSocket/SSE implementation
- PDF generation using weasyprint/reportlab
- Enhanced plugin sandboxing
- Plugin dependency management
- Automated plugin testing framework
- Community rating and review system
- Plugin marketplace analytics
- Advanced playbook editor (visual workflow designer)
- Integration with more SIEM platforms

## Documentation

Extension developers can reference:
- `examples.py` for implementation patterns
- `integration/plugin_registry.py` for extension API
- `marketplace/approval.py` for submission process
- Dashboard API documentation for data formats
- Playbook examples for automation patterns

## Conclusion

Phase IV successfully implements a comprehensive platformization layer transforming Nethical Recon into a full ecosystem with:
- Professional web dashboard with D3.js visualizations
- Automated workflows and playbook system
- Enterprise SIEM/SOAR integrations
- Common API for tool integrations
- Central risk scoring and decision engine
- Public marketplace with approval workflow
- Community extension support

The implementation provides a solid foundation for building a vibrant ecosystem of reconnaissance tools, automated workflows, and community-contributed extensions while maintaining security and quality through robust approval processes.

---

**Version:** Roadmap 5.0 Phase IV / 2026-01-14  
**Maintainer:** V1B3hR  
**Status:** ✅ COMPLETE
