# Kubernetes Deployment Guide

This guide covers deploying Nethical Recon to Kubernetes using kubectl and raw manifests.

## Prerequisites

- Kubernetes cluster (1.19+)
- kubectl configured to access your cluster
- Storage provisioner for PersistentVolumeClaims
- Ingress controller (optional, for external access)

## Quick Start

### 1. Create Namespace

```bash
kubectl apply -f infra/k8s/namespace.yaml
```

### 2. Configure Secrets

**Important**: Update the secrets before deploying!

Edit `infra/k8s/secrets.yaml` and change:
- Database credentials
- API secret key
- External API keys (Shodan, Censys, OpenAI)

```bash
kubectl apply -f infra/k8s/secrets.yaml
```

### 3. Deploy Core Services

```bash
# Deploy ConfigMap
kubectl apply -f infra/k8s/configmap.yaml

# Deploy PostgreSQL
kubectl apply -f infra/k8s/postgres.yaml

# Deploy Redis
kubectl apply -f infra/k8s/redis.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=database -n nethical-recon --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=cache -n nethical-recon --timeout=300s
```

### 4. Create Persistent Volume

```bash
kubectl apply -f infra/k8s/pvc.yaml
```

### 5. Deploy Application Services

```bash
# Deploy API
kubectl apply -f infra/k8s/api.yaml

# Deploy Workers
kubectl apply -f infra/k8s/worker.yaml

# Deploy Scheduler
kubectl apply -f infra/k8s/scheduler.yaml

# Wait for services to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=api -n nethical-recon --timeout=300s
```

### 6. (Optional) Deploy Ingress

Edit `infra/k8s/ingress.yaml` to configure your domain and TLS settings:

```bash
kubectl apply -f infra/k8s/ingress.yaml
```

## Verification

### Check All Resources

```bash
kubectl get all -n nethical-recon
```

Expected output should show:
- 2 API pods running
- 2+ Worker pods running
- 1 Scheduler pod running
- 1 PostgreSQL pod running
- 1 Redis pod running

### Check Logs

```bash
# API logs
kubectl logs -n nethical-recon -l app.kubernetes.io/component=api --tail=50

# Worker logs
kubectl logs -n nethical-recon -l app.kubernetes.io/component=worker --tail=50

# Scheduler logs
kubectl logs -n nethical-recon -l app.kubernetes.io/component=scheduler --tail=50
```

### Test API

Port-forward the API service:

```bash
kubectl port-forward -n nethical-recon svc/nethical-api 8000:8000
```

Access the API:
- API docs: http://localhost:8000/api/v1/docs
- Health check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

## Storage Configuration

### ReadWriteMany Storage

The application requires ReadWriteMany (RWX) storage for evidence and reports, as both API and Worker pods need concurrent access.

#### AWS EFS

1. Install EFS CSI driver:
```bash
kubectl apply -k "github.com/kubernetes-sigs/aws-efs-csi-driver/deploy/kubernetes/overlays/stable/?ref=release-1.7"
```

2. Create EFS filesystem in AWS Console or CLI

3. Create StorageClass:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: efs-sc
provisioner: efs.csi.aws.com
parameters:
  provisioningMode: efs-ap
  fileSystemId: fs-xxxxxxxxx  # Your EFS ID
  directoryPerms: "700"
```

4. Update `infra/k8s/pvc.yaml`:
```yaml
spec:
  storageClassName: efs-sc
```

#### Azure Files

1. Create StorageClass:
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: azurefile-csi
provisioner: file.csi.azure.com
parameters:
  skuName: Standard_LRS
mountOptions:
  - dir_mode=0777
  - file_mode=0777
```

#### GCP Filestore

1. Create Filestore instance in GCP Console

2. Create PersistentVolume:
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: filestore-pv
spec:
  capacity:
    storage: 1Ti
  accessModes:
    - ReadWriteMany
  nfs:
    server: 10.x.x.x  # Filestore IP
    path: /share
```

#### NFS (On-Premise)

1. Setup NFS server

2. Create PersistentVolume:
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteMany
  nfs:
    server: nfs-server.example.com
    path: /exported/path
```

## Database Configuration

### Using External PostgreSQL

If you have an existing PostgreSQL instance:

1. Don't deploy the PostgreSQL StatefulSet:
```bash
# Skip: kubectl apply -f infra/k8s/postgres.yaml
```

2. Update ConfigMap with external database details:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nethical-recon-config
  namespace: nethical-recon
data:
  DATABASE_HOST: "postgres.example.com"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "nethical_recon"
```

3. Update Secrets with database credentials:
```yaml
stringData:
  DATABASE_USER: "your-user"
  DATABASE_PASSWORD: "your-password"
```

### Database Backups

Create a CronJob for automated backups:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: nethical-recon
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: postgres:15-alpine
              command:
                - /bin/sh
                - -c
                - |
                  pg_dump -h $DATABASE_HOST -U $DATABASE_USER -d $DATABASE_NAME > /backup/backup-$(date +%Y%m%d-%H%M%S).sql
              env:
                - name: DATABASE_HOST
                  value: nethical-postgres
                - name: DATABASE_USER
                  valueFrom:
                    secretKeyRef:
                      name: nethical-recon-secrets
                      key: DATABASE_USER
                - name: PGPASSWORD
                  valueFrom:
                    secretKeyRef:
                      name: nethical-recon-secrets
                      key: DATABASE_PASSWORD
                - name: DATABASE_NAME
                  valueFrom:
                    configMapKeyRef:
                      name: nethical-recon-config
                      key: DATABASE_NAME
              volumeMounts:
                - name: backup
                  mountPath: /backup
          volumes:
            - name: backup
              persistentVolumeClaim:
                claimName: postgres-backup-pvc
          restartPolicy: OnFailure
```

## Scaling

### Horizontal Scaling

The HPA for workers is already configured. To scale manually:

```bash
# Scale API
kubectl scale deployment nethical-api -n nethical-recon --replicas=5

# Scale Workers
kubectl scale deployment nethical-worker -n nethical-recon --replicas=10
```

### View HPA Status

```bash
kubectl get hpa -n nethical-recon
```

### Adjust HPA Settings

Edit `infra/k8s/worker.yaml` to modify HPA behavior:
- Change min/max replicas
- Adjust CPU/memory thresholds
- Modify scale-up/scale-down policies

## Security

### Network Policies

Create a NetworkPolicy to restrict traffic:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: nethical-network-policy
  namespace: nethical-recon
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: nethical-recon
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # Allow traffic from ingress controller
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
    # Allow inter-pod communication
    - from:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: nethical-recon
  egress:
    # Allow DNS
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: UDP
          port: 53
    # Allow PostgreSQL
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/component: database
      ports:
        - protocol: TCP
          port: 5432
    # Allow Redis
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/component: cache
      ports:
        - protocol: TCP
          port: 6379
    # Allow external API calls
    - to:
        - namespaceSelector: {}
      ports:
        - protocol: TCP
          port: 443
```

### Pod Security Standards

Apply Pod Security Standards to the namespace:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: nethical-recon
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Secret Management

For production, use external secret management:

#### Using Sealed Secrets

```bash
# Install sealed-secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Seal your secrets
kubeseal --format yaml < infra/k8s/secrets.yaml > infra/k8s/sealed-secrets.yaml

# Deploy sealed secrets
kubectl apply -f infra/k8s/sealed-secrets.yaml
```

#### Using External Secrets Operator

```bash
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets-system --create-namespace

# Create SecretStore (example for AWS Secrets Manager)
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secretsmanager
  namespace: nethical-recon
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
EOF

# Create ExternalSecret
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: nethical-secrets
  namespace: nethical-recon
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secretsmanager
    kind: SecretStore
  target:
    name: nethical-recon-secrets
  data:
    - secretKey: API_SECRET_KEY
      remoteRef:
        key: nethical/api-secret-key
    - secretKey: DATABASE_PASSWORD
      remoteRef:
        key: nethical/database-password
EOF
```

## Monitoring

### Prometheus Setup

If using Prometheus Operator:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: nethical-api
  namespace: nethical-recon
spec:
  selector:
    matchLabels:
      app.kubernetes.io/component: api
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

### Grafana Dashboards

Import pre-built dashboards from `observability/grafana/dashboards/`.

## Troubleshooting

### Pods Not Starting

Check events:
```bash
kubectl describe pod <pod-name> -n nethical-recon
```

### Database Connection Issues

Test database connectivity:
```bash
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -n nethical-recon -- \
  psql -h nethical-postgres -U nethical -d nethical_recon
```

### Worker Not Processing Jobs

Check Celery status:
```bash
kubectl exec -n nethical-recon deployment/nethical-worker -- \
  celery -A nethical_recon.worker.celery_app inspect active
```

### Storage Issues

Check PVC status:
```bash
kubectl get pvc -n nethical-recon
kubectl describe pvc nethical-evidence-pvc -n nethical-recon
```

### View All Logs

```bash
# Stream all logs
kubectl logs -n nethical-recon --all-containers=true -l app.kubernetes.io/name=nethical-recon -f
```

## Maintenance

### Update Application

1. Build and push new image:
```bash
docker build -t your-registry/nethical-recon:v0.2.0 .
docker push your-registry/nethical-recon:v0.2.0
```

2. Update deployments:
```bash
kubectl set image deployment/nethical-api -n nethical-recon api=your-registry/nethical-recon:v0.2.0
kubectl set image deployment/nethical-worker -n nethical-recon worker=your-registry/nethical-recon:v0.2.0
kubectl set image deployment/nethical-scheduler -n nethical-recon scheduler=your-registry/nethical-recon:v0.2.0
```

3. Check rollout status:
```bash
kubectl rollout status deployment/nethical-api -n nethical-recon
```

### Rollback

```bash
kubectl rollout undo deployment/nethical-api -n nethical-recon
```

## Clean Up

Remove all resources:

```bash
kubectl delete namespace nethical-recon
```

Or remove specific resources:

```bash
kubectl delete -f infra/k8s/
```
