# Observability Module

Production-grade observability infrastructure for Nethical Recon with structured logging, Prometheus metrics, and monitoring dashboards.

## Overview

The observability module provides three main capabilities:

1. **Structured Logging** - JSON logging with correlation IDs using structlog
2. **Metrics Collection** - Prometheus metrics for monitoring and alerting
3. **Monitoring Stack** - Complete Docker Compose stack with Grafana dashboards

## Quick Start

### Install Dependencies

```bash
pip install structlog prometheus-client
```

### Configure Logging

```python
from nethical_recon.observability import configure_logging, get_logger

# Configure (call once at startup)
configure_logging(level="INFO", json_logs=True)

# Get logger with context
logger = get_logger(__name__, job_id="job-123", target_id="target-456")

# Log events
logger.info("scan started", tool="nmap")
logger.error("scan failed", error="timeout", exc_info=True)
```

### Track Metrics

```python
from nethical_recon.observability import track_tool_run, track_findings

# Track tool execution
with track_tool_run("nmap") as metrics:
    # Run your tool
    results = run_nmap_scan()
    
    # Track findings
    track_findings(
        findings_count=len(results),
        severity="high",
        tool_name="nmap",
        job_id="job-123"
    )
```

### Start Monitoring Stack

```bash
# Start all services
docker-compose up -d

# Access dashboards
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:9090  # Prometheus
open http://localhost:8000/metrics  # Metrics endpoint
```

## Structured Logging

### Features

- **JSON Output**: Machine-readable logs for ELK, Splunk, etc.
- **Console Output**: Human-readable logs for development
- **Correlation IDs**: Automatic job_id, run_id, target_id tracking
- **Log Categories**: audit/security/ops classification
- **Context Binding**: Pre-bind context to loggers
- **Exception Handling**: Full stack traces with context

### Usage Examples

#### Basic Logging

```python
from nethical_recon.observability import get_logger

logger = get_logger(__name__)
logger.info("application started")
logger.warning("rate limit approaching", current=95, limit=100)
logger.error("connection failed", host="example.com", port=443)
```

#### Correlation IDs

```python
# Create logger with IDs
logger = get_logger(__name__, job_id="job-123", run_id="run-456")
logger.info("scan started")  # Automatically includes job_id and run_id

# Bind additional context
bound_logger = logger.bind(target_id="target-789")
bound_logger.info("target scanned")  # Includes all IDs
```

#### Log Categories

```python
from nethical_recon.observability import audit_log, security_log, ops_log

# Audit events
audit_log("user login", username="alice", ip="192.168.1.100")

# Security events
security_log("suspicious activity", source_ip="10.0.0.1", action="blocked")

# Operational events
ops_log("cache cleared", cache_size_mb=256)
```

### Configuration

```python
from nethical_recon.observability import configure_logging

# Production: JSON logs
configure_logging(level="INFO", json_logs=True)

# Development: Console logs with colors
configure_logging(level="DEBUG", json_logs=False)

# With file output
configure_logging(
    level="INFO",
    json_logs=True,
    output_file="/var/log/nethical/app.log"
)
```

## Prometheus Metrics

### Available Metrics

#### Tool Run Metrics
- `nethical_tool_run_duration_seconds` (histogram) - Tool execution time
- `nethical_tool_run_total` (counter) - Total tool runs
- `nethical_tool_run_errors_total` (counter) - Tool failures

#### Finding Metrics
- `nethical_findings_total` (counter) - Total findings discovered
- `nethical_findings_per_job` (histogram) - Findings distribution per job

#### Job Metrics
- `nethical_job_duration_seconds` (histogram) - Job execution time
- `nethical_job_total` (counter) - Total jobs

#### Queue Metrics
- `nethical_queue_depth` (gauge) - Current queue size
- `nethical_queue_processing_seconds` (summary) - Task processing time

#### API Metrics
- `nethical_api_requests_total` (counter) - API request count
- `nethical_api_request_duration_seconds` (histogram) - API latency

#### System Metrics
- `nethical_active_workers` (gauge) - Active worker count
- `nethical_errors_total` (counter) - Total errors

### Usage Examples

#### Context Manager

```python
from nethical_recon.observability import track_tool_run

with track_tool_run("nmap") as metrics:
    try:
        result = run_nmap()
        metrics["status"] = "success"
    except Exception as e:
        metrics["status"] = "error"
        metrics["error_type"] = type(e).__name__
        raise
```

#### Track Findings

```python
from nethical_recon.observability import track_findings

# Track multiple findings
track_findings(5, "critical", "nmap", job_id="job-123")
track_findings(10, "high", "nmap", job_id="job-123")
track_findings(25, "medium", "nmap", job_id="job-123")
```

#### Manual Metric Updates

```python
from nethical_recon.observability import (
    increment_counter,
    observe_value,
    update_queue_depth,
    update_active_workers,
)

# Increment counters
increment_counter("job_total", {"status": "completed"})

# Observe histogram values
observe_value("tool_run_duration", 120.5, {"tool_name": "nmap"})

# Update gauges
update_queue_depth("celery", 42)
update_active_workers(4)
```

#### Decorator

```python
from nethical_recon.observability import track_duration

@track_duration("tool_run", {"tool_name": "nmap", "status": "success"})
def run_nmap_scan(target: str):
    # Implementation automatically tracked
    return scan_results
```

## Monitoring Stack

### Architecture

```
┌─────────────┐
│   Grafana   │ ← Visualizations
└──────┬──────┘
       │
┌──────▼──────┐
│ Prometheus  │ ← Metrics Collection
└──────┬──────┘
       │
┌──────▼──────┐
│  API/Worker │ ← Metrics Exposition
│  /metrics   │
└─────────────┘
```

### Services

1. **Redis** - Celery broker (port 6379)
2. **PostgreSQL** - Database (port 5432)
3. **API** - Nethical API (port 8000)
4. **Worker** - Celery worker
5. **Scheduler** - Celery beat
6. **Prometheus** - Metrics collection (port 9090)
7. **Grafana** - Dashboards (port 3000)

### Docker Compose Commands

```bash
# Start stack
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f worker

# Check status
docker-compose ps

# Stop stack
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Accessing Services

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/v1/docs
- **Metrics**: http://localhost:8000/metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Grafana Dashboards

### Nethical Recon Overview Dashboard

10 panels covering all key metrics:

1. **API Request Rate** - Requests/sec by endpoint
2. **Tool Run Success Rate** - Success percentage
3. **Active Workers** - Current worker count
4. **Tool Run Duration (p95)** - 95th percentile by tool
5. **Findings by Severity** - Distribution pie chart
6. **Queue Depth** - Queue size over time
7. **Error Rate by Component** - Errors/sec per component
8. **API Response Time (p95)** - Latency percentiles
9. **Total Jobs** - Cumulative count
10. **Total Findings** - Cumulative count

### Custom Dashboards

Add custom dashboards to:
```
observability/grafana/dashboards/my-dashboard.json
```

They will be auto-loaded on Grafana startup.

## Alert Rules

### Built-in Alerts

1. **HighErrorRate** - Error rate > 5/sec
2. **ToolRunFailureRate** - Failure rate > 0.1/sec
3. **HighQueueDepth** - Queue > 100 tasks
4. **SlowAPIResponse** - p95 > 5 seconds
5. **NoActiveWorkers** - Zero workers
6. **LongRunningToolRun** - p95 > 1 hour

### Custom Alerts

Add to `observability/alert_rules.yml`:

```yaml
- alert: CustomAlert
  expr: your_metric_query > threshold
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Alert description"
    description: "Detailed information"
```

Reload Prometheus:
```bash
docker-compose exec prometheus kill -HUP 1
```

## Prometheus Queries

### Useful PromQL Queries

```promql
# API request rate
rate(nethical_api_requests_total[5m])

# Tool success rate percentage
sum(rate(nethical_tool_run_total{status="success"}[5m])) 
/ sum(rate(nethical_tool_run_total[5m])) * 100

# 95th percentile API latency
histogram_quantile(0.95, 
  rate(nethical_api_request_duration_seconds_bucket[5m]))

# Error rate by component
rate(nethical_errors_total[5m])

# Top 5 slowest endpoints
topk(5, histogram_quantile(0.95, 
  rate(nethical_api_request_duration_seconds_bucket[5m])))

# Findings per hour
rate(nethical_findings_total[1h]) * 3600
```

## Integration

### ELK Stack

Forward JSON logs to Elasticsearch:

```yaml
# filebeat.yml
filebeat.inputs:
  - type: docker
    containers.ids: '*'
    json.keys_under_root: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

### Splunk

Configure Universal Forwarder:

```bash
/opt/splunkforwarder/bin/splunk add monitor \
  /var/log/nethical/ \
  -sourcetype json
```

### Datadog

Use Datadog Agent with Prometheus integration:

```yaml
# datadog.yaml
prometheus_metrics:
  enabled: true
  checks:
    - prometheus_url: http://localhost:8000/metrics
```

## Best Practices

### Logging

1. **Use Correlation IDs** - Always bind job_id, run_id, target_id
2. **Log at Appropriate Levels** - DEBUG for development, INFO for production
3. **Include Context** - Add relevant fields to every log
4. **Don't Log Secrets** - Sanitize credentials and tokens
5. **Use Structured Data** - Log as key=value pairs, not strings

### Metrics

1. **Use Labels Wisely** - Limit cardinality (< 1000 unique combinations)
2. **Choose Right Metric Type** - Counter, Gauge, Histogram, Summary
3. **Set Appropriate Buckets** - Match your use case
4. **Track What Matters** - Focus on business and performance metrics
5. **Document Custom Metrics** - Add HELP text

### Dashboards

1. **Start with Overview** - High-level metrics first
2. **Use Time Windows** - Show trends, not just current values
3. **Add Alerts** - Visualize alert thresholds
4. **Keep it Simple** - 5-10 panels per dashboard
5. **Update Regularly** - Review and refine

## Troubleshooting

### Logs Not Appearing

**Check**:
```python
# Is logging configured?
from nethical_recon.observability import configure_logging
configure_logging(level="DEBUG", json_logs=True)

# Are you using the right logger?
from nethical_recon.observability import get_logger
logger = get_logger(__name__)
```

### Metrics Not Collected

**Verify**:
```bash
# Can you access /metrics?
curl http://localhost:8000/metrics

# Is Prometheus scraping?
docker-compose logs prometheus | grep "error"

# Check Prometheus targets
open http://localhost:9090/targets
```

### Grafana Not Showing Data

**Steps**:
1. Check datasource connection in Grafana
2. Verify Prometheus is collecting metrics
3. Test PromQL query directly in Prometheus
4. Check dashboard panel queries

## Performance

### Overhead

- **Logging**: 5-15% depending on format and volume
- **Metrics**: <1% for collection, <100ms for export
- **Memory**: ~50MB for typical workload

### Optimization

1. **Use JSON in Production** - More efficient than console
2. **Adjust Scrape Intervals** - Balance freshness vs. load
3. **Set Retention Policies** - Limit Prometheus storage
4. **Use Recording Rules** - Pre-compute expensive queries
5. **Sample High-Volume Metrics** - Reduce cardinality

## Security

### Production Checklist

- [ ] Change default Grafana password
- [ ] Secure /metrics endpoint (authentication)
- [ ] Use TLS for all services
- [ ] Don't log secrets/credentials
- [ ] Restrict Prometheus scrape targets
- [ ] Enable Grafana OAuth/LDAP
- [ ] Set up firewall rules
- [ ] Encrypt logs at rest
- [ ] Use secrets management for passwords

## Testing

Run observability tests:

```bash
# All observability tests
pytest tests/test_observability.py -v

# Specific test class
pytest tests/test_observability.py::TestMetrics -v

# With coverage
pytest tests/test_observability.py --cov=nethical_recon.observability
```

## Further Reading

- [Structlog Documentation](https://www.structlog.org/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Documentation](https://grafana.com/docs/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [Logging Best Practices](https://12factor.net/logs)

## Support

For issues or questions about observability:

1. Check this README
2. Review PHASE_E_SUMMARY.md
3. Check example logs/metrics
4. Open a GitHub issue

---

**Last Updated**: 2025-12-26  
**Phase**: E (Observability)  
**Status**: ✅ Complete
