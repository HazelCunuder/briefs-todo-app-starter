# Deployment Guide

This document provides comprehensive deployment instructions for the To-Do App project.

---

## 📋 Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Deployment Options](#-deployment-options)
3. [Docker Deployment](#-docker-deployment)
4. [Kubernetes Deployment](#-kubernetes-deployment)
5. [Cloud Provider Guides](#-cloud-provider-guides)
6. [Configuration](#-configuration)
7. [Environment Variables](#-environment-variables)
8. [Health Checks](#-health-checks)
9. [Monitoring](#-monitoring)
10. [Troubleshooting](#-troubleshooting)

---

## 📦 Prerequisites

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Docker | >= 24.0 | Container runtime |
| Docker Compose | >= 2.24 | Multi-container orchestration |
| Git | >= 2.40 | Version control |
| Bun | >= 1.0 | JavaScript runtime (for tooling) |
| Node.js | >= 20.0 | JavaScript runtime (optional) |
| Python | >= 3.12 | Python runtime |

### System Requirements

- **Minimum**: 2 CPU cores, 4GB RAM, 10GB disk
- **Recommended**: 4 CPU cores, 8GB RAM, 20GB disk
- **OS**: Linux (Ubuntu 22.04+ recommended), macOS, Windows (WSL2)

---

## 🚀 Deployment Options

### Option 1: Local Development (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/HazelCunuder/briefs-todo-app-starter.git
cd briefs-todo-app-starter

# Start all services with Docker Compose
docker compose up -d

# Access the application
# API: http://localhost:8000
# Web: http://localhost:5173
```

### Option 2: Production with Docker Compose

```bash
# Clone the repository
git clone https://github.com/HazelCunuder/briefs-todo-app-starter.git
cd briefs-todo-app-starter

# Create production environment file
cp .env.example .env
# Edit .env with your production values

# Build and start production containers
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# View logs
docker compose logs -f
```

### Option 3: Kubernetes (Production)

See [Kubernetes Deployment](#-kubernetes-deployment) section.

### Option 4: Cloud Providers

See [Cloud Provider Guides](#-cloud-provider-guides) section.

---

## 🐳 Docker Deployment

### Quick Start

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# Stop services
docker compose down

# View status
docker compose ps

# View logs
docker compose logs -f
```

### Production Configuration

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: api/Dockerfile
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  web:
    build:
      context: .
      dockerfile: web/Dockerfile
      args:
        - NODE_ENV=production
    environment:
      - NODE_ENV=production
      - VITE_API_URL=http://api:8000
    ports:
      - "3000:3000"
    restart: unless-stopped
    depends_on:
      api:
        condition: service_healthy

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-appuser}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
      POSTGRES_DB: ${POSTGRES_DB:-tododb}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-appuser}"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Dockerfile Optimization

Both `api/Dockerfile` and `web/Dockerfile` use multi-stage builds to minimize image size:

- **API**: Python slim base, separate build and runtime dependencies
- **Web**: Node.js alpine base, optimized for production builds

### Image Tags

| Service | Image | Tag |
|---------|-------|-----|
| API | `ghcr.io/hazelcunuder/briefs-todo-app-starter/api` | `latest`, `v1.0.0`, `dev-<sha>` |
| Web | `ghcr.io/hazelcunuder/briefs-todo-app-starter/web` | `latest`, `v1.0.0`, `dev-<sha>` |

---

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (v1.28+)
- kubectl configured
- Helm (optional)
- Ingress controller (NGINX, Traefik, etc.)
- Persistent storage provisioner

### Helm Chart

Create `charts/todo-app/Chart.yaml`:

```yaml
apiVersion: v2
name: todo-app
description: To-Do App Helm Chart
version: 0.1.0
appVersion: 0.1.0
type: application

home: https://github.com/HazelCunuder/briefs-todo-app-starter
sources:
  - https://github.com/HazelCunuder/briefs-todo-app-starter

maintainers:
  - name: HazelCunuder
    email: hazel@example.com

dependencies:
  - name: postgres
    version: 12.1.0
    repository: https://charts.bitnami.com/bitnami
    condition: postgres.enabled
```

Create `charts/todo-app/values.yaml`:

```yaml
# Global configuration
replicaCount: 1
image:
  repository: ghcr.io/hazelcunuder/briefs-todo-app-starter
  pullPolicy: IfNotPresent
  tag: "latest"

# API Configuration
api:
  enabled: true
  image:
    repository: ghcr.io/hazelcunuder/briefs-todo-app-starter/api
    tag: "latest"
  port: 8000
  targetPort: 8000
  environment:
    ENVIRONMENT: production
    DEBUG: "false"
    DATABASE_URL: postgresql://${POSTGRES_USER:appuser}:${POSTGRES_PASSWORD:changeme}@postgres:5432/${POSTGRES_DB:tododb}
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  livenessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 30
    periodSeconds: 10
  readinessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 5
    periodSeconds: 5

# Web Configuration
web:
  enabled: true
  image:
    repository: ghcr.io/hazelcunuder/briefs-todo-app-starter/web
    tag: "latest"
  port: 3000
  targetPort: 3000
  environment:
    NODE_ENV: production
    VITE_API_URL: http://api:8000
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 256Mi
  livenessProbe:
    httpGet:
      path: /
      port: 3000
    initialDelaySeconds: 30
    periodSeconds: 10
  readinessProbe:
    httpGet:
      path: /
      port: 3000
    initialDelaySeconds: 5
    periodSeconds: 5

# PostgreSQL Configuration
postgres:
  enabled: true
  auth:
    username: appuser
    password: changeme
    database: tododb
  primary:
    persistence:
      enabled: true
      size: 10Gi
    resources:
      requests:
        cpu: 100m
        memory: 256Mi
      limits:
        cpu: 500m
        memory: 512Mi

# Ingress Configuration
ingress:
  enabled: true
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: todo.example.com
      paths:
        - path: /api
          pathType: Prefix
          backend:
            service:
              name: api
              port:
                number: 8000
        - path: /
          pathType: Prefix
          backend:
            service:
              name: web
              port:
                number: 3000
  tls:
    - secretName: todo-app-tls
      hosts:
        - todo.example.com

# Service Configuration
service:
  type: ClusterIP
  ports:
    - name: api
      port: 8000
      targetPort: 8000
    - name: web
      port: 3000
      targetPort: 3000
```

### Deploy with Helm

```bash
# Add Helm repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install the chart
helm install todo-app ./charts/todo-app \
  --namespace todo-app \
  --create-namespace \
  --values ./charts/todo-app/values.yaml \
  --set postgres.auth.password=mysecretpassword

# Upgrade the chart
helm upgrade todo-app ./charts/todo-app \
  --namespace todo-app \
  --values ./charts/todo-app/values.yaml

# Uninstall the chart
helm uninstall todo-app --namespace todo-app
```

### Deploy with kubectl

```bash
# Create namespace
kubectl create namespace todo-app

# Apply configurations
kubectl apply -f k8s/

# View resources
kubectl get all -n todo-app

# View logs
kubectl logs -f deployment/api -n todo-app
kubectl logs -f deployment/web -n todo-app
```

---

## ☁️ Cloud Provider Guides

### AWS Deployment

#### Prerequisites

- AWS account
- AWS CLI configured
- EKS cluster or ECS
- RDS PostgreSQL instance
- S3 bucket for storage

#### Using ECS Fargate

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name todo-app

# Create task definition
aws ecs register-task-definition \
  --cli-input-json file://ecs/task-definition.json

# Create service
aws ecs create-service \
  --cluster todo-app \
  --service-name todo-app \
  --task-definition todo-app:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-123456],securityGroups=[sg-123456],assignPublicIp=ENABLED}"
```

#### Using EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name todo-app \
  --region us-west-2 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 2

# Deploy with Helm (see Kubernetes section)
helm install todo-app ./charts/todo-app \
  --namespace todo-app \
  --create-namespace
```

### Google Cloud Deployment

#### Prerequisites

- Google Cloud account
- gcloud CLI configured
- GKE cluster
- Cloud SQL PostgreSQL instance

#### Using Cloud Run

```bash
# Build and push images
gcloud builds submit --tag gcr.io/PROJECT_ID/api:latest api/
gcloud builds submit --tag gcr.io/PROJECT_ID/web:latest web/

# Deploy API service
gcloud run deploy api \
  --image gcr.io/PROJECT_ID/api:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars "DATABASE_URL=postgresql://user:pass@/db"

# Deploy Web service
gcloud run deploy web \
  --image gcr.io/PROJECT_ID/web:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 3000
```

#### Using GKE

```bash
# Create GKE cluster
gcloud container clusters create todo-app \
  --zone us-central1-a \
  --machine-type e2-medium \
  --num-nodes 2

# Deploy with Helm (see Kubernetes section)
helm install todo-app ./charts/todo-app \
  --namespace todo-app \
  --create-namespace
```

### Azure Deployment

#### Prerequisites

- Azure account
- Azure CLI configured
- AKS cluster
- Azure Database for PostgreSQL

#### Using Azure Container Instances

```bash
# Create container group
az container create \
  --resource-group myResourceGroup \
  --name todo-app \
  --image ghcr.io/hazelcunuder/briefs-todo-app-starter/api:latest \
  --ports 8000 \
  --environment-variables DATABASE_URL=postgresql://user:pass@server/database
```

#### Using AKS

```bash
# Create AKS cluster
az aks create \
  --resource-group myResourceGroup \
  --name todo-app \
  --node-count 2 \
  --generate-ssh-keys

# Deploy with Helm (see Kubernetes section)
helm install todo-app ./charts/todo-app \
  --namespace todo-app \
  --create-namespace
```

---

## ⚙️ Configuration

### Environment Files

| File | Purpose | Required |
|------|---------|----------|
| `.env` | Development environment | Yes |
| `.env.production` | Production environment | Yes |
| `.env.test` | Test environment | No |

### Configuration Options

#### API Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Environment name |
| `DEBUG` | `true` | Enable debug mode |
| `DATABASE_URL` | - | PostgreSQL connection string |
| `SECRET_KEY` | - | Secret key for JWT signing |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT expiration time |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |

#### Web Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_ENV` | `development` | Node.js environment |
| `VITE_API_URL` | `http://localhost:8000` | API endpoint URL |
| `VITE_APP_NAME` | `To-Do App` | Application name |
| `VITE_APP_VERSION` | `0.1.0` | Application version |

#### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | `appuser` | Database username |
| `POSTGRES_PASSWORD` | `changeme` | Database password |
| `POSTGRES_DB` | `tododb` | Database name |
| `POSTGRES_HOST` | `postgres` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |

---

## 🔐 Environment Variables

### Example `.env` File

```bash
# Environment
ENVIRONMENT=development
DEBUG=true

# API Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Database Configuration
DATABASE_URL=postgresql://appuser:changeme@postgres:5432/tododb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=changeme
POSTGRES_DB=tododb
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Web Configuration
VITE_API_URL=http://localhost:8000
VITE_APP_NAME="To-Do App"
VITE_APP_VERSION="0.1.0"
```

### Example `.env.production` File

```bash
# Environment
ENVIRONMENT=production
DEBUG=false

# API Configuration
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
CORS_ORIGINS=https://todo.example.com

# Database Configuration
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Web Configuration
VITE_API_URL=https://api.example.com
VITE_APP_NAME="To-Do App"
VITE_APP_VERSION="0.1.0"
```

---

## 🏥 Health Checks

### API Health Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Basic health check |
| `/health/db` | GET | Database connectivity check |
| `/health/full` | GET | Full health check with all dependencies |

### Response Examples

#### Healthy Response

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production",
  "timestamp": "2024-01-01T00:00:00Z",
  "checks": {
    "database": "healthy",
    "cache": "healthy"
  }
}
```

#### Unhealthy Response

```json
{
  "status": "unhealthy",
  "version": "0.1.0",
  "environment": "production",
  "timestamp": "2024-01-01T00:00:00Z",
  "checks": {
    "database": "unhealthy",
    "error": "Connection refused"
  }
}
```

---

## 📊 Monitoring

### Prometheus Metrics

The API exposes Prometheus metrics at `/metrics`:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'todo-api'
    scrape_interval: 15s
    static_configs:
      - targets: ['api:8000']
```

### Grafana Dashboard

Import the following dashboard JSON for monitoring:

```json
{
  "title": "To-Do App Dashboard",
  "panels": [
    {
      "title": "API Requests",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(http_requests_total[1m])",
          "legendFormat": "{{method}} {{path}}"
        }
      ]
    },
    {
      "title": "Error Rate",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(http_requests_total{status=~"5.."}[1m]) / rate(http_requests_total[1m])",
          "legendFormat": "Error Rate"
        }
      ]
    },
    {
      "title": "Database Query Time",
      "type": "graph",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum(rate(db_query_duration_seconds_bucket[1m])) by (le))",
          "legendFormat": "p95"
        }
      ]
    }
  ]
}
```

### Logging

#### API Logging

```python
# api/logging.conf
[loggers]
keys=root,api

[handlers]
keys=console,file

[formatters]
keys=standard,json

[logger_root]
level=INFO
handlers=console

[logger_api]
level=DEBUG
handlers=console,file
qualname=api
propagate=0

[handler_console]
class=StreamHandler
level=INFO
formatter=standard
args=(sys.stdout,)

[handler_file]
class=FileHandler
level=DEBUG
formatter=json
args=('logs/api.log', 'a')

[formatter_standard]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_json]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

#### Web Logging

```javascript
// web/src/lib/logging.js
import { pino } from 'pino';

export const logger = pino({
  level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
  formatters: {
    level: (label) => ({ level: label }),
    log: (object) => ({
      ...object,
      timestamp: new Date().toISOString(),
    }),
  },
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true,
      ignore: 'pid,hostname',
    },
  },
});
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Symptoms**: API returns 500 errors, logs show connection refused

**Solutions**:
- Check database is running: `docker compose ps`
- Verify connection string in `.env`
- Check database credentials
- Test connection manually: `psql postgresql://appuser:changeme@postgres:5432/tododb`

#### 2. Port Already in Use

**Symptoms**: Docker compose fails with "port already allocated"

**Solutions**:
- Find and kill the process: `lsof -i :8000` then `kill -9 <PID>`
- Change the port mapping in `docker-compose.yml`
- Use different ports for development

#### 3. Migration Errors

**Symptoms**: Database errors on startup

**Solutions**:
- Run migrations manually: `alembic upgrade head`
- Check migration files for errors
- Reset database (development only): `docker compose down -v && docker compose up -d`

#### 4. CORS Errors

**Symptoms**: Browser console shows CORS errors

**Solutions**:
- Add frontend URL to `CORS_ORIGINS` in `.env`
- Verify API is running and accessible
- Check browser console for detailed error messages

#### 5. Build Failures

**Symptoms**: Docker build fails

**Solutions**:
- Check Dockerfile syntax
- Verify base images exist
- Clean build cache: `docker system prune -a`
- Build with `--no-cache`: `docker compose build --no-cache`

### Debug Commands

```bash
# View all container logs
docker compose logs -f

# View specific container logs
docker compose logs -f api
docker compose logs -f web
docker compose logs -f postgres

# Enter a running container
docker compose exec api sh
docker compose exec web sh
docker compose exec postgres psql -U appuser -d tododb

# Check container resource usage
docker stats

# Inspect container configuration
docker inspect todo-app-api-1

# View network connections
docker network inspect todo-app_default

# Test API endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/todos -H "Content-Type: application/json" -d '{"title": "Test"}'
```

### Performance Issues

#### High Memory Usage

- Increase container memory limits
- Optimize database queries
- Add caching (Redis)
- Use connection pooling

#### Slow API Responses

- Check database query performance
- Add indexes to frequently queried columns
- Implement caching for common queries
- Use pagination for large datasets

#### High CPU Usage

- Check for infinite loops
- Optimize expensive computations
- Implement background tasks for long-running operations
- Scale horizontally (add more replicas)

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/home/)
- [Helm Documentation](https://helm.sh/docs/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Azure Container Instances Documentation](https://docs.microsoft.com/en-us/azure/container-instances/)

---

## 🔄 Update Guide

### Updating the Application

1. **Pull the latest changes**:
   ```bash
   git pull origin main
   ```

2. **Update dependencies**:
   ```bash
   # API dependencies
   cd api
   pip install -r requirements.txt
   
   # Web dependencies
   cd ../web
   npm install
   ```

3. **Rebuild Docker images**:
   ```bash
   docker compose build --no-cache
   ```

4. **Restart services**:
   ```bash
   docker compose down && docker compose up -d
   ```

5. **Run migrations**:
   ```bash
   docker compose exec api alembic upgrade head
   ```

### Rolling Back

1. **Revert to previous commit**:
   ```bash
   git revert HEAD
   ```

2. **Rebuild and restart**:
   ```bash
   docker compose build --no-cache && docker compose up -d
   ```

---

*Last updated: 2026-04-29*
*Part of the To-Do App deployment documentation*
