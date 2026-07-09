# Infrastructure Deployment

This directory contains all infrastructure-as-code for deploying Nethical Recon.

## Directory Structure

```
infra/
├── Dockerfile.api          # Optimized Dockerfile for API service
├── Dockerfile.worker       # Optimized Dockerfile for Worker service
├── Dockerfile.scheduler    # Optimized Dockerfile for Scheduler service
├── deploy.sh              # Quick deployment script
├── docs/                  # Deployment documentation
│   ├── docker-deployment.md
│   └── kubernetes-deployment.md
├── helm/                  # Helm charts
│   └── nethical-recon/   # Main Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── README.md
│       └── templates/    # Kubernetes resource templates
└── k8s/                  # Raw Kubernetes manifests
    ├── namespace.yaml
    ├── configmap.yaml
    ├── secrets.yaml
    ├── postgres.yaml
    ├── redis.yaml
    ├── pvc.yaml
    ├── api.yaml
    ├── worker.yaml
    ├── scheduler.yaml
    └── ingress.yaml
```

## Quick Start

### Docker Compose (Development)

```bash
# From repository root
docker-compose up -d
```

### Kubernetes with kubectl

```bash
# From repository root
bash infra/deploy.sh
# or manually:
kubectl apply -f infra/k8s/
```

### Kubernetes with Helm

```bash
# Install
helm install nethical infra/helm/nethical-recon

# Install with custom values
helm install nethical infra/helm/nethical-recon \
  -f my-values.yaml

# Upgrade
helm upgrade nethical infra/helm/nethical-recon

# Uninstall
helm uninstall nethical
```

## Documentation

- **[Docker Deployment Guide](docs/docker-deployment.md)**: Complete guide for Docker and Docker Compose
- **[Kubernetes Deployment Guide](docs/kubernetes-deployment.md)**: Complete guide for Kubernetes deployment
- **[Helm Chart README](helm/nethical-recon/README.md)**: Helm chart documentation and configuration reference

## Components

### Docker Images

Three optimized Docker images are provided:

1. **API Image** (`Dockerfile.api`):
   - FastAPI application
   - Database migration runner
   - Health checks enabled
   - Optimized for HTTP workload

2. **Worker Image** (`Dockerfile.worker`):
   - Celery worker with scanning tools
   - Includes nmap, nikto, dirb
   - Optimized for long-running tasks
   - Configurable concurrency

3. **Scheduler Image** (`Dockerfile.scheduler`):
   - Celery Beat scheduler
   - Lightweight, minimal dependencies
   - Manages periodic tasks

### Kubernetes Resources

Complete set of Kubernetes manifests:

- **Namespace**: Isolated namespace for Nethical Recon
- **ConfigMap**: Centralized configuration
- **Secrets**: Sensitive data management
- **StatefulSet**: PostgreSQL with persistent storage
- **Deployments**: API (2 replicas), Workers (2+), Scheduler (1)
- **Services**: Internal cluster communication
- **HPA**: Auto-scaling for workers (2-10 replicas)
- **PVC**: Persistent storage for evidence/reports
- **Ingress**: External access configuration

### Helm Chart

Production-ready Helm chart with:

- Flexible configuration via `values.yaml`
- Support for external databases and Redis
- Configurable resources and scaling
- Security contexts and RBAC
- Health checks and probes
- Monitoring integration (Prometheus)
- Storage class configuration
- Ingress with TLS support

## Features

### Security

- **Non-root containers**: All services run as UID 1000
- **Minimal capabilities**: DROP ALL, add only NET_RAW for workers
- **Security contexts**: Enforced at pod and container level
- **Secret management**: External secrets operator ready
- **Network policies**: Template included

### Scalability

- **Horizontal Pod Autoscaling**: Workers scale 2-10 based on CPU/memory
- **StatefulSet for database**: Stable network identity and storage
- **ReadWriteMany storage**: Shared evidence between API and workers
- **Resource limits**: Defined for all services
- **Rolling updates**: Zero-downtime deployments

### Observability

- **Health checks**: All services have liveness and readiness probes
- **Prometheus metrics**: Exposed on API and annotated on pods
- **Structured logging**: JSON logs with correlation IDs
- **Service monitoring**: ServiceMonitor templates ready

### High Availability

- **Multiple replicas**: API runs with 2+ replicas
- **Auto-scaling**: Workers scale based on load
- **StatefulSet**: Database with persistent storage
- **Rolling updates**: Gradual rollout with zero downtime
- **Pod disruption budgets**: Control over voluntary disruptions

## Configuration

### Environment Variables

Key configuration via ConfigMap:
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `JSON_LOGS`: Enable JSON structured logging (true/false)
- `MAX_CONCURRENT_SCANS`: Maximum concurrent scans
- `RATE_LIMIT_PER_SECOND`: Rate limit for API requests
- `CELERY_WORKER_CONCURRENCY`: Worker concurrency level

Secrets (via Kubernetes Secret):
- `API_SECRET_KEY`: JWT signing key
- `DATABASE_USER`, `DATABASE_PASSWORD`: Database credentials
- `SHODAN_API_KEY`, `CENSYS_API_ID`, `CENSYS_API_SECRET`: External API keys
- `OPENAI_API_KEY`: AI integration key

### Storage

Required storage:
- **Database**: 10Gi (ReadWriteOnce) - PostgreSQL data
- **Evidence/Reports**: 50Gi (ReadWriteMany) - Shared between API and Workers
- **Redis**: 1Gi (optional, can use emptyDir)

Supported storage classes:
- AWS EFS (via efs-csi driver)
- Azure Files (via azurefile-csi driver)
- GCP Filestore (via filestore-csi driver)
- NFS
- Local storage (development only)

### Resource Requirements

Minimum resources per service:

| Service | CPU Request | Memory Request | CPU Limit | Memory Limit |
|---------|-------------|----------------|-----------|--------------|
| API | 250m | 256Mi | 1000m | 1Gi |
| Worker | 500m | 512Mi | 2000m | 2Gi |
| Scheduler | 100m | 128Mi | 500m | 256Mi |
| PostgreSQL | 250m | 256Mi | 1000m | 1Gi |
| Redis | 100m | 128Mi | 500m | 512Mi |

## Deployment Modes

### Development

Use Docker Compose:
```bash
docker-compose up -d
```

### Staging

Deploy to Kubernetes with default values:
```bash
helm install nethical-staging infra/helm/nethical-recon \
  --namespace nethical-staging \
  --create-namespace
```

### Production

Deploy with custom values and external services:
```bash
helm install nethical-prod infra/helm/nethical-recon \
  --namespace nethical-prod \
  --create-namespace \
  -f prod-values.yaml
```

Example `prod-values.yaml`:
```yaml
postgresql:
  enabled: false
  
externalDatabase:
  enabled: true
  host: prod-postgres.example.com
  port: 5432
  database: nethical_recon
  user: nethical
  password: "use-external-secrets"

redis:
  enabled: false

externalRedis:
  enabled: true
  host: prod-redis.example.com
  port: 6379

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: nethical.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: nethical-tls
      hosts:
        - nethical.example.com

worker:
  autoscaling:
    minReplicas: 5
    maxReplicas: 20

api:
  replicaCount: 3
```

## Monitoring

### Prometheus

Metrics are exposed at:
- API: `http://api:8000/metrics`
- Annotations on pods for auto-discovery

### Grafana

Pre-built dashboards available in:
- `../observability/grafana/dashboards/`

### Logs

Structured JSON logs with correlation IDs:
```bash
kubectl logs -n nethical-recon -l app.kubernetes.io/component=api -f
```

## Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod <pod-name> -n nethical-recon
   kubectl logs <pod-name> -n nethical-recon
   ```

2. **Database connection issues**
   ```bash
   kubectl exec -it deployment/nethical-api -n nethical-recon -- \
     psql postgresql://user:pass@postgres:5432/db
   ```

3. **Workers not processing jobs**
   ```bash
   kubectl exec -it deployment/nethical-worker -n nethical-recon -- \
     celery -A nethical_recon.worker.celery_app inspect active
   ```

4. **Storage issues**
   ```bash
   kubectl get pvc -n nethical-recon
   kubectl describe pvc nethical-evidence-pvc -n nethical-recon
   ```

### Debug Commands

```bash
# Check all resources
kubectl get all -n nethical-recon

# Check events
kubectl get events -n nethical-recon --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n nethical-recon

# Port forward to API
kubectl port-forward -n nethical-recon svc/nethical-api 8000:8000

# Access pod shell
kubectl exec -it deployment/nethical-api -n nethical-recon -- /bin/bash
```

## Support

For detailed guides and troubleshooting:
- Read [Docker Deployment Guide](docs/docker-deployment.md)
- Read [Kubernetes Deployment Guide](docs/kubernetes-deployment.md)
- Check [Helm Chart README](helm/nethical-recon/README.md)
- See [PHASE_F_SUMMARY.md](../PHASE_F_SUMMARY.md) for implementation details

For issues:
- GitHub Issues: https://github.com/V1B3hR/nethical-recon/issues
