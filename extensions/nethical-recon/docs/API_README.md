# Nethical Recon REST API

Professional-grade REST API for cybersecurity reconnaissance and threat hunting.

## Features

- **Full REST API**: Complete CRUD operations for targets, jobs, runs, findings, and reports
- **OpenAPI Documentation**: Auto-generated Swagger UI and ReDoc
- **Authentication**: JWT tokens and API key support
- **Authorization**: Role-based access control (viewer/operator/admin)
- **Filtering & Pagination**: Advanced query capabilities on all endpoints
- **Async Workers**: Integration with Celery worker queue
- **Health Checks**: Monitor API and dependencies status

## Quick Start

### Start the API Server

```bash
# Start with default settings (http://0.0.0.0:8000)
nethical api serve

# Custom host and port
nethical api serve --host 127.0.0.1 --port 8080

# With auto-reload for development
nethical api serve --reload

# With multiple workers for production
nethical api serve --workers 8
```

### Access Documentation

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## Authentication

The API supports two authentication methods:

### 1. JWT Tokens (OAuth2)

**Default Users:**
- `admin` / `admin123` - Full access (scopes: read, write, admin)
- `operator` / `admin123` - Read/write access (scopes: read, write)
- `viewer` / `admin123` - Read-only access (scope: read)

**Get a token:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Use the token:**
```bash
curl -H "Authorization: Bearer <your_token>" \
  http://localhost:8000/api/v1/jobs
```

### 2. API Keys

**Default API Key:**
- `nethical_test_key_12345` (scopes: read, write)

**Use an API key:**
```bash
curl -H "Authorization: Bearer nethical_test_key_12345" \
  http://localhost:8000/api/v1/jobs
```

**Create a new API key:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/api-keys" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My API Key", "scopes": ["read", "write"]}'
```

## API Endpoints

### Health & Version
- `GET /health` - Health check
- `GET /version` - API version

### Authentication
- `POST /api/v1/auth/token` - Get JWT token
- `POST /api/v1/auth/api-keys` - Create API key (admin)
- `GET /api/v1/auth/me` - Get current user info

### Targets
- `POST /api/v1/targets` - Create target
- `GET /api/v1/targets` - List targets (with filtering)
- `GET /api/v1/targets/{id}` - Get target
- `PATCH /api/v1/targets/{id}` - Update target
- `DELETE /api/v1/targets/{id}` - Delete target (admin)

### Jobs
- `POST /api/v1/jobs` - Create and submit job
- `GET /api/v1/jobs` - List jobs (with filtering)
- `GET /api/v1/jobs/{id}` - Get job
- `GET /api/v1/jobs/{id}/status` - Get job status with stats
- `DELETE /api/v1/jobs/{id}` - Delete job (admin)

### Tool Runs
- `GET /api/v1/runs` - List tool runs (with filtering)
- `GET /api/v1/runs/{id}` - Get tool run

### Findings
- `GET /api/v1/findings` - List findings (with extensive filtering)
- `GET /api/v1/findings/{id}` - Get finding

**Filters:**
- `severity` - Filter by severity level
- `run_id` - Filter by tool run
- `job_id` - Filter by job
- `tag` - Filter by tag
- `tool` - Filter by tool name
- `since` - Filter by creation timestamp

### Reports
- `GET /api/v1/reports/{job_id}` - Generate job report

## Usage Examples

### Create a Target
```bash
curl -X POST "http://localhost:8000/api/v1/targets" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "example.com",
    "type": "domain",
    "scope": "in_scope",
    "description": "Example target"
  }'
```

### Submit a Scan Job
```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "target_id": "<target_uuid>",
    "name": "Security Scan",
    "tools": ["nmap"],
    "description": "Comprehensive security scan"
  }'
```

### Check Job Status
```bash
curl "http://localhost:8000/api/v1/jobs/<job_id>/status" \
  -H "Authorization: Bearer <token>"
```

### List Findings
```bash
# All findings
curl "http://localhost:8000/api/v1/findings" \
  -H "Authorization: Bearer <token>"

# High severity findings only
curl "http://localhost:8000/api/v1/findings?severity=high" \
  -H "Authorization: Bearer <token>"

# Findings for a specific job
curl "http://localhost:8000/api/v1/findings?job_id=<job_id>" \
  -H "Authorization: Bearer <token>"

# With pagination
curl "http://localhost:8000/api/v1/findings?page=2&page_size=20" \
  -H "Authorization: Bearer <token>"
```

### Generate Report
```bash
curl "http://localhost:8000/api/v1/reports/<job_id>" \
  -H "Authorization: Bearer <token>"
```

## Configuration

Environment variables:

```bash
# Server
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
API_WORKERS=4

# Security
API_SECRET_KEY=your-secret-key-here
API_ALGORITHM=HS256
API_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_PREFIX=/api/v1
API_TITLE="Nethical Recon API"
API_VERSION=1.0.0

# CORS
API_CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Pagination
API_DEFAULT_PAGE_SIZE=50
API_MAX_PAGE_SIZE=1000
```

## Security

### Production Checklist

1. **Change default credentials**: Update or remove default users
2. **Set strong secret key**: `API_SECRET_KEY=<random-256-bit-key>`
3. **Use HTTPS**: Deploy behind a reverse proxy with TLS
4. **Enable CORS carefully**: Only allow trusted origins
5. **Rotate API keys**: Implement key rotation policy
6. **Use proper database**: Replace in-memory storage with real database
7. **Rate limiting**: Add rate limiting middleware
8. **Monitoring**: Set up logging and metrics

### Scopes

- `read` - View targets, jobs, runs, findings, reports
- `write` - Create and update resources
- `admin` - Delete resources, manage API keys

## Integration Examples

### Python Client
```python
import requests

# Authenticate
response = requests.post(
    "http://localhost:8000/api/v1/auth/token",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Make authenticated request
headers = {"Authorization": f"Bearer {token}"}
jobs = requests.get("http://localhost:8000/api/v1/jobs", headers=headers)
print(jobs.json())
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

// Authenticate
const authResponse = await axios.post(
  'http://localhost:8000/api/v1/auth/token',
  new URLSearchParams({
    username: 'admin',
    password: 'admin123'
  })
);
const token = authResponse.data.access_token;

// Make authenticated request
const jobs = await axios.get('http://localhost:8000/api/v1/jobs', {
  headers: { Authorization: `Bearer ${token}` }
});
console.log(jobs.data);
```

## Development

### Run in Development Mode
```bash
# With auto-reload
nethical api serve --reload

# Or with uvicorn directly
uvicorn nethical_recon.api.app:create_app --reload --factory
```

### Run Tests
```bash
pytest tests/test_api.py -v
```

## Architecture

```
src/nethical_recon/api/
├── __init__.py          # Package exports
├── app.py               # FastAPI application factory
├── config.py            # Configuration management
├── models.py            # Request/response models
├── auth.py              # Authentication & authorization
└── routers/
    ├── __init__.py
    ├── auth.py          # Auth endpoints
    ├── targets.py       # Target management
    ├── jobs.py          # Job management
    ├── runs.py          # Tool run queries
    ├── findings.py      # Finding queries
    └── reports.py       # Report generation
```

## See Also

- [PHASE_D_SUMMARY.md](../../PHASE_D_SUMMARY.md) - Complete implementation details
- [roadmap_3.md](../../roadmap_3.md) - Project roadmap
- [OpenAPI Specification](http://localhost:8000/api/v1/openapi.json)
