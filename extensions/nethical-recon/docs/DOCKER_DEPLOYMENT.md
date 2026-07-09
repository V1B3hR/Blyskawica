# Docker Deployment Guide

This guide covers building and running Nethical Recon using Docker and Docker Compose.

## Building Images

### Build Main Image (Multi-stage)

The main Dockerfile creates an optimized multi-stage build:

```bash
docker build -t nethical-recon:latest .
```

This image can be used for all services (API, Worker, Scheduler) by overriding the command.

### Build Service-Specific Images

For optimized service-specific images:

```bash
# API image
docker build -f infra/Dockerfile.api -t nethical-recon-api:latest .

# Worker image (includes scanning tools)
docker build -f infra/Dockerfile.worker -t nethical-recon-worker:latest .

# Scheduler image (lightweight)
docker build -f infra/Dockerfile.scheduler -t nethical-recon-scheduler:latest .
```

## Running with Docker Compose

### Quick Start

1. **Start all services:**

```bash
docker-compose up -d
```

2. **Check service status:**

```bash
docker-compose ps
```

3. **View logs:**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
```

4. **Access the API:**

- API docs: http://localhost:8000/api/v1/docs
- Health check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Configuration

Edit `docker-compose.yml` to customize:

```yaml
services:
  api:
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/db
      - API_SECRET_KEY=your-secret-key
      - LOG_LEVEL=INFO
```

Or use environment file:

```bash
# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://nethical:nethical_password@postgres:5432/nethical_recon
API_SECRET_KEY=your-secret-key-change-in-production
SHODAN_API_KEY=your-shodan-key
CENSYS_API_ID=your-censys-id
CENSYS_API_SECRET=your-censys-secret
EOF

# Start with environment file
docker-compose --env-file .env up -d
```

### Scaling Workers

Scale worker instances:

```bash
docker-compose up -d --scale worker=5
```

## Production Deployment

### Using Docker Swarm

1. **Initialize Swarm:**

```bash
docker swarm init
```

2. **Create secrets:**

```bash
echo "your-secret-key" | docker secret create api_secret_key -
echo "your-db-password" | docker secret create db_password -
```

3. **Deploy stack:**

```bash
docker stack deploy -c docker-compose.yml nethical
```

4. **Scale services:**

```bash
docker service scale nethical_worker=10
```

### Using Docker Compose in Production

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    image: registry.example.com/nethical-recon:latest
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
        max_attempts: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 256M
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - API_SECRET_KEY=${API_SECRET_KEY}
      - LOG_LEVEL=INFO
      - JSON_LOGS=true
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  worker:
    image: registry.example.com/nethical-recon:latest
    deploy:
      replicas: 5
      restart_policy:
        condition: on-failure
        max_attempts: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BROKER_URL=${BROKER_URL}
      - LOG_LEVEL=INFO
      - JSON_LOGS=true
```

Deploy:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Image Registry

### Push to Docker Hub

```bash
# Tag image
docker tag nethical-recon:latest username/nethical-recon:latest
docker tag nethical-recon:latest username/nethical-recon:v0.1.0

# Push
docker push username/nethical-recon:latest
docker push username/nethical-recon:v0.1.0
```

### Push to Private Registry

```bash
# Tag image
docker tag nethical-recon:latest registry.example.com/nethical-recon:latest

# Login to registry
docker login registry.example.com

# Push
docker push registry.example.com/nethical-recon:latest
```

### Push to AWS ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name nethical-recon

# Login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag nethical-recon:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/nethical-recon:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/nethical-recon:latest
```

## Development

### Build for Development

```bash
# Build with BuildKit for better caching
DOCKER_BUILDKIT=1 docker build -t nethical-recon:dev .
```

### Run Single Service

```bash
# Start dependencies
docker-compose up -d postgres redis

# Run API in development mode
docker run -it --rm \
  --network nethical-recon_default \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/evidence:/app/evidence \
  -e DATABASE_URL=postgresql://nethical:nethical_password@postgres:5432/nethical_recon \
  -e BROKER_URL=redis://redis:6379/0 \
  -p 8000:8000 \
  nethical-recon:dev \
  nethical api serve --reload
```

### Debug Container

```bash
# Start container with shell
docker run -it --rm \
  --network nethical-recon_default \
  -e DATABASE_URL=postgresql://nethical:nethical_password@postgres:5432/nethical_recon \
  nethical-recon:latest \
  /bin/bash

# Or attach to running container
docker exec -it nethical-api /bin/bash
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker logs nethical-api
docker-compose logs api
```

### Database Connection Issues

Test database connectivity:
```bash
docker exec -it nethical-api \
  psql postgresql://nethical:nethical_password@postgres:5432/nethical_recon
```

### Worker Not Processing Jobs

Check worker status:
```bash
docker exec -it nethical-worker \
  celery -A nethical_recon.worker.celery_app inspect active
```

### Permission Issues

The container runs as non-root user (UID 1000). Ensure volumes have correct permissions:

```bash
# Fix evidence directory permissions
sudo chown -R 1000:1000 ./evidence
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove volumes
docker-compose down -v

# Remove images
docker rmi nethical-recon:latest
```

## Health Checks

### API Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected",
  "redis": "connected"
}
```

### Worker Health Check

```bash
docker exec nethical-worker \
  celery -A nethical_recon.worker.celery_app inspect ping
```

### Database Health Check

```bash
docker exec nethical-postgres pg_isready -U nethical
```

## Performance Tuning

### Worker Concurrency

Adjust worker concurrency based on CPU cores:

```yaml
services:
  worker:
    environment:
      - CELERY_WORKER_CONCURRENCY=8  # 2x CPU cores
```

### Database Connection Pooling

Configure PostgreSQL connection pooling:

```yaml
services:
  postgres:
    command:
      - postgres
      - -c
      - max_connections=200
      - -c
      - shared_buffers=256MB
```

### Redis Memory Limits

Configure Redis memory:

```yaml
services:
  redis:
    command:
      - redis-server
      - --maxmemory
      - 1gb
      - --maxmemory-policy
      - allkeys-lru
```

## Security Best Practices

### 1. Use Secrets Management

Don't hardcode secrets in docker-compose.yml:

```yaml
services:
  api:
    secrets:
      - db_password
      - api_secret_key

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_secret_key:
    file: ./secrets/api_secret_key.txt
```

### 2. Run as Non-Root

Already configured in Dockerfiles (UID 1000).

### 3. Scan Images for Vulnerabilities

```bash
# Using Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image nethical-recon:latest

# Using Snyk
snyk container test nethical-recon:latest
```

### 4. Use Multi-Stage Builds

Already implemented in Dockerfile to minimize image size.

### 5. Enable Content Trust

```bash
export DOCKER_CONTENT_TRUST=1
docker push nethical-recon:latest
```

## Monitoring

### View Container Stats

```bash
docker stats
```

### Export Metrics

Prometheus metrics are exposed at:
- API: http://localhost:8000/metrics
- Prometheus: http://localhost:9090

### Log Aggregation

Configure log driver:

```yaml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

Or use external logging:

```yaml
services:
  api:
    logging:
      driver: "gelf"
      options:
        gelf-address: "udp://logstash:12201"
```

## Backup and Restore

### Backup Database

```bash
docker exec nethical-postgres pg_dump -U nethical nethical_recon > backup.sql
```

### Restore Database

```bash
docker exec -i nethical-postgres psql -U nethical nethical_recon < backup.sql
```

### Backup Evidence

```bash
tar -czf evidence-backup.tar.gz ./evidence
```

## Maintenance

### Update Images

```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d

# Remove old images
docker image prune -f
```

### Database Migrations

```bash
docker exec -it nethical-api alembic upgrade head
```

### Clean Up Resources

```bash
# Remove unused containers
docker container prune -f

# Remove unused volumes
docker volume prune -f

# Remove unused networks
docker network prune -f

# Remove unused images
docker image prune -a -f
```
