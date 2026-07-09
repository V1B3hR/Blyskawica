# Worker Queue Module

This module implements Phase C of the Nethical Recon roadmap: Worker Queue + Scheduler + Concurrency Policy.

## Components

### 1. Celery Task Queue

The worker queue system uses Celery with Redis as the broker and result backend.

**Key Tasks:**
- `run_scan_job` - Orchestrates a complete scan job with multiple tools
- `run_tool` - Executes a single tool scan
- `normalize_results` - Parses tool output into normalized findings
- `finalize_job` - Completes a job and aggregates results
- `generate_report` - Generates reports for completed jobs

**Scheduled Tasks:**
- `update_baselines` - Periodic baseline updates (daily at 2 AM UTC)
- `cleanup_old_results` - Clean up old results (weekly)

### 2. Policy Engine (Rules of Engagement)

The policy engine enforces security and compliance policies for scan operations.

**Components:**
- `NetworkPolicy` - Controls which targets can be scanned (allowlist/denylist)
- `ToolPolicy` - Controls which tools can be used and their risk levels
- `RateLimitPolicy` - Controls scan concurrency and rate limits

**Risk Levels:**
- `LOW` - Passive reconnaissance (nmap, shodan, dns)
- `MEDIUM` - Active scanning (nikto, dirb, gobuster)
- `HIGH` - Aggressive/exploitation tools (sqlmap, metasploit)

**Features:**
- Network allowlist/denylist (CIDR notation)
- Domain allowlist/denylist
- Tool risk classification
- High-risk tool approval requirements
- Audit mode for logging violations without blocking
- Configurable via environment variables

### 3. Tool Adapters

Adapters provide a consistent interface for running security tools.

**Currently Supported:**
- `NmapAdapter` - Runs nmap scans with XML output

**Adapter Features:**
- Version detection
- Command building
- Output capture
- Evidence generation with checksums
- Error handling

## Configuration

### Environment Variables

**Celery Configuration:**
```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_TASK_ALWAYS_EAGER=false  # Set to true for testing
WORKER_CONCURRENCY=4
TASK_SOFT_TIME_LIMIT=3600
TASK_TIME_LIMIT=7200
RESULT_EXPIRES=86400
```

**Policy Engine Configuration:**
```bash
# Rate Limits
ROE_MAX_REQUESTS_PER_SEC=10.0
ROE_MAX_CONCURRENT_TOOLS=3
ROE_MAX_SCANS_PER_TARGET=1
ROE_INTER_REQUEST_DELAY=0.1

# Network Policy
ROE_ALLOWED_NETWORKS=192.168.1.0/24,10.0.0.0/8
ROE_DENIED_NETWORKS=172.16.0.0/12
ROE_ALLOWED_DOMAINS=example.com,testdomain.org
ROE_DENIED_DOMAINS=evil.com

# Tool Policy
ROE_RESTRICTED_TOOLS=nikto,masscan
ROE_DISABLED_TOOLS=metasploit,hydra

# Enforcement
ROE_ENFORCE=true
ROE_AUDIT_MODE=false
```

## Running the Worker

### Start Redis (required)
```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or install locally
sudo apt-get install redis-server
redis-server
```

### Start Celery Worker
```bash
# From project root
celery -A nethical_recon.worker worker --loglevel=info
```

### Start Celery Beat (for scheduled tasks)
```bash
celery -A nethical_recon.worker beat --loglevel=info
```

### Start Both Worker and Beat
```bash
celery -A nethical_recon.worker worker --beat --loglevel=info
```

## Usage Examples

### Submit a Scan Job via CLI
```bash
# Submit a job
nethical job submit example.com --name "Example Scan" --tools nmap

# Check job status
nethical job status <job-id>

# List recent jobs
nethical job list

# View job logs
nethical job logs <job-id>
```

### Submit a Job Programmatically
```python
from nethical_recon.worker.tasks import run_scan_job
from nethical_recon.core.models import Target, ScanJob
from nethical_recon.core.storage import init_database

# Create target and job in database
db = init_database()
with db.session() as session:
    target = Target(value="example.com", type="domain")
    job = ScanJob(target_id=target.id, tools=["nmap"])
    # Save to DB...

# Submit to worker queue
result = run_scan_job.delay(str(job.id))
print(f"Task ID: {result.id}")
```

### Check Policy Compliance
```python
from nethical_recon.worker.policy import get_policy_engine

policy = get_policy_engine()
is_valid, messages = policy.validate_scan(
    target="192.168.1.100",
    tools=["nmap", "nikto"],
    explicit_approval=False
)

if not is_valid:
    print("Policy violations:")
    for msg in messages:
        print(f"  - {msg}")
```

## Testing

### Run Tests
```bash
# All worker tests
pytest tests/test_worker.py -v

# Policy tests
pytest tests/test_policy.py -v

# All tests
pytest tests/ -v
```

### Enable Eager Mode for Testing
```python
import os
os.environ["CELERY_TASK_ALWAYS_EAGER"] = "true"
# Tasks will run synchronously in the same process
```

## Architecture

### Task Flow
```
CLI/API Request
    ↓
run_scan_job (orchestrator)
    ↓
Policy Validation
    ↓
├── run_tool (nmap) → normalize_results
├── run_tool (nikto) → normalize_results
└── run_tool (dirb) → normalize_results
    ↓
finalize_job (aggregate results)
    ↓
generate_report (optional)
```

### Data Flow
```
Target → ScanJob → ToolRun → Evidence → Finding
```

### Policy Enforcement
```
Scan Request
    ↓
Network Policy Check
    ├── Allowed Networks?
    ├── Denied Networks?
    └── Domain Restrictions?
    ↓
Tool Policy Check
    ├── Disabled Tools?
    ├── Risk Level?
    └── Approval Required?
    ↓
Rate Limit Check
    ├── Max Concurrent Tools?
    └── Requests Per Second?
    ↓
Execute or Reject
```

## Security Considerations

1. **Network Isolation**: Workers should run in isolated networks with limited access
2. **Credential Management**: Never store API keys or credentials in code
3. **Tool Sandboxing**: Consider running tools in containers for isolation
4. **Audit Logging**: All policy decisions are logged for compliance
5. **Rate Limiting**: Prevents accidental DoS of target systems
6. **Evidence Integrity**: All outputs are checksummed for tamper detection

## Future Enhancements

- Additional tool adapters (masscan, nuclei, httpx, etc.)
- Advanced scheduling (cron-based, periodic scans)
- Result correlation and deduplication
- Multi-tenancy support
- Distributed worker pools
- Priority queues for urgent scans
- Worker health monitoring
- Auto-scaling based on queue depth

## Troubleshooting

### Worker won't start
- Check Redis is running: `redis-cli ping`
- Check broker URL is correct
- Check firewall/network connectivity

### Tasks are stuck in pending
- Verify worker is running and connected
- Check worker logs for errors
- Verify task routing configuration

### Policy blocks all scans
- Check policy configuration
- Use `ROE_AUDIT_MODE=true` to log without blocking
- Use `ROE_ENFORCE=false` to disable enforcement

### Tests fail with Redis connection error
- Set `CELERY_TASK_ALWAYS_EAGER=true` for tests
- Tests don't require Redis in eager mode
