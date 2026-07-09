# Nethical Recon Helm Chart

This Helm chart deploys Nethical Recon - an advanced cybersecurity reconnaissance and threat hunting platform - on Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PV provisioner support in the underlying infrastructure (for persistence)
- ReadWriteMany volumes for shared storage between API and Worker pods

## Installing the Chart

### Basic Installation

To install the chart with the release name `nethical`:

```bash
helm install nethical ./infra/helm/nethical-recon
```

### Custom Configuration

Create a `values-override.yaml` file with your custom configuration:

```yaml
# values-override.yaml
secrets:
  apiSecretKey: "your-secret-key-here"
  databasePassword: "your-db-password"
  shodanApiKey: "your-shodan-key"

ingress:
  enabled: true
  hosts:
    - host: nethical.yourdomain.com
      paths:
        - path: /
          pathType: Prefix

persistence:
  storageClass: "your-storage-class"
```

Install with custom values:

```bash
helm install nethical ./infra/helm/nethical-recon -f values-override.yaml
```

### Using External Database and Redis

To use external PostgreSQL and Redis instances:

```yaml
postgresql:
  enabled: false

redis:
  enabled: false

externalDatabase:
  enabled: true
  host: postgres.example.com
  port: 5432
  database: nethical_recon
  user: nethical
  password: "your-password"

externalRedis:
  enabled: true
  host: redis.example.com
  port: 6379
```

## Uninstalling the Chart

To uninstall/delete the `nethical` deployment:

```bash
helm uninstall nethical
```

This command removes all the Kubernetes components associated with the chart and deletes the release.

## Configuration

The following table lists the configurable parameters and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.imageRegistry` | Global Docker image registry | `""` |
| `global.imagePullSecrets` | Global Docker registry secret names | `[]` |
| `global.storageClass` | Global storage class for PVCs | `""` |

### Image Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Image repository | `nethical-recon` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |

### API Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `api.enabled` | Enable API deployment | `true` |
| `api.replicaCount` | Number of API replicas | `2` |
| `api.service.type` | Kubernetes service type | `ClusterIP` |
| `api.service.port` | Service port | `8000` |
| `api.resources.limits.cpu` | CPU limit | `1000m` |
| `api.resources.limits.memory` | Memory limit | `1Gi` |
| `api.autoscaling.enabled` | Enable HPA for API | `false` |

### Worker Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `worker.enabled` | Enable Worker deployment | `true` |
| `worker.replicaCount` | Number of Worker replicas | `2` |
| `worker.concurrency` | Celery worker concurrency | `4` |
| `worker.resources.limits.cpu` | CPU limit | `2000m` |
| `worker.resources.limits.memory` | Memory limit | `2Gi` |
| `worker.autoscaling.enabled` | Enable HPA for Workers | `true` |
| `worker.autoscaling.minReplicas` | Minimum number of replicas | `2` |
| `worker.autoscaling.maxReplicas` | Maximum number of replicas | `10` |

### Scheduler Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `scheduler.enabled` | Enable Scheduler deployment | `true` |
| `scheduler.replicaCount` | Number of Scheduler replicas (should be 1) | `1` |

### PostgreSQL Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.enabled` | Deploy PostgreSQL | `true` |
| `postgresql.auth.username` | PostgreSQL username | `nethical` |
| `postgresql.auth.password` | PostgreSQL password | `changeme-in-production` |
| `postgresql.auth.database` | PostgreSQL database name | `nethical_recon` |
| `postgresql.primary.persistence.enabled` | Enable persistence | `true` |
| `postgresql.primary.persistence.size` | PVC size | `10Gi` |

### Redis Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.enabled` | Deploy Redis | `true` |
| `redis.master.persistence.enabled` | Enable persistence | `false` |

### Persistence Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `persistence.enabled` | Enable evidence/reports persistence | `true` |
| `persistence.accessMode` | PVC access mode | `ReadWriteMany` |
| `persistence.size` | PVC size | `50Gi` |

### Ingress Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.hosts[0].host` | Hostname | `nethical.example.com` |

### Secrets Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `secrets.apiSecretKey` | API secret key (JWT signing) | `changeme-your-secret-key-minimum-32-characters-long` |
| `secrets.databasePassword` | Database password | `changeme-in-production` |
| `secrets.shodanApiKey` | Shodan API key (optional) | `""` |
| `secrets.censysApiId` | Censys API ID (optional) | `""` |
| `secrets.censysApiSecret` | Censys API secret (optional) | `""` |
| `secrets.openaiApiKey` | OpenAI API key (optional) | `""` |

## Storage Requirements

### Evidence and Reports Storage

The chart requires a ReadWriteMany (RWX) persistent volume for evidence and reports storage, as both API and Worker pods need concurrent access.

Supported storage solutions:
- **AWS**: EFS (Elastic File System) with EFS CSI driver
- **Azure**: Azure Files with Azure File CSI driver
- **GCP**: Filestore with Filestore CSI driver
- **On-Premise**: NFS, GlusterFS, CephFS

Example for AWS EFS:

```yaml
persistence:
  enabled: true
  storageClass: "efs-sc"
  accessMode: ReadWriteMany
  size: 50Gi
```

### Database Storage

PostgreSQL requires ReadWriteOnce (RWO) storage. Most cloud providers support this with their default storage classes.

## Security Considerations

### Secrets Management

For production deployments, consider using external secret management:

- **Kubernetes External Secrets Operator**: Sync secrets from AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, etc.
- **HashiCorp Vault**: Use Vault CSI provider or Vault Agent Injector
- **Sealed Secrets**: Encrypt secrets in Git

Example with External Secrets Operator:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: nethical-secrets
spec:
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: nethical-recon-secrets
  data:
    - secretKey: API_SECRET_KEY
      remoteRef:
        key: nethical/api-secret-key
```

### Network Policies

Consider implementing NetworkPolicies to restrict traffic between pods:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nethical-network-policy
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: nethical-recon
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: nethical-recon
  egress:
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: nethical-recon
```

### Pod Security

The chart includes security contexts by default:
- Runs as non-root user (UID 1000)
- Drops all capabilities
- Read-only root filesystem where possible

## Monitoring

### Prometheus Metrics

The API and Worker pods expose Prometheus metrics. To scrape metrics:

```yaml
metrics:
  enabled: true
  serviceMonitor:
    enabled: true
```

This creates a ServiceMonitor for Prometheus Operator.

### Grafana Dashboards

Pre-built Grafana dashboards are available in `observability/grafana/dashboards/`.

## Scaling

### Horizontal Pod Autoscaling

Workers support HPA based on CPU and memory utilization:

```yaml
worker:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
```

### Vertical Scaling

Adjust resource requests and limits based on your workload:

```yaml
worker:
  resources:
    requests:
      cpu: 1000m
      memory: 1Gi
    limits:
      cpu: 4000m
      memory: 4Gi
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n <namespace> -l app.kubernetes.io/name=nethical-recon
```

### View Logs

```bash
# API logs
kubectl logs -n <namespace> -l app.kubernetes.io/component=api -f

# Worker logs
kubectl logs -n <namespace> -l app.kubernetes.io/component=worker -f

# Scheduler logs
kubectl logs -n <namespace> -l app.kubernetes.io/component=scheduler -f
```

### Database Migration Issues

If the database migration fails, you can run it manually:

```bash
kubectl exec -n <namespace> deployment/nethical-api -- alembic upgrade head
```

### Worker Not Processing Jobs

Check Celery worker status:

```bash
kubectl exec -n <namespace> deployment/nethical-worker -- celery -A nethical_recon.worker.celery_app inspect active
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/V1B3hR/nethical-recon/issues
- Documentation: https://github.com/V1B3hR/nethical-recon
