# Troubleshooting Guide

Comprehensive troubleshooting guide for the To-Do App project.

---

## 📋 Table of Contents

1. [General Troubleshooting](#-general-troubleshooting)
2. [API Troubleshooting](#-api-troubleshooting)
3. [Frontend Troubleshooting](#-frontend-troubleshooting)
4. [Database Troubleshooting](#-database-troubleshooting)
5. [Docker Troubleshooting](#-docker-troubleshooting)
6. [Testing Troubleshooting](#-testing-troubleshooting)
7. [CI/CD Troubleshooting](#-cicd-troubleshooting)
8. [Performance Troubleshooting](#-performance-troubleshooting)
9. [Error Reference](#-error-reference)

---

## 🔍 General Troubleshooting

### Issue: Application Not Starting

**Symptoms**:
- `docker compose up` fails
- Containers exit immediately
- No logs or error messages

**Diagnosis**:

```bash
# Check container status
docker compose ps -a

# View exit codes
docker compose ps -a --format "table {{.Name}}\t{{.Status}}\t{{.ExitCode}}"

# View logs for failed containers
docker compose logs --tail=100

# Check for port conflicts
netstat -tuln | grep -E "8000|5173|3000|5432"
# or
lsof -i :8000
```

**Solutions**:

1. **Port Conflict**:
   ```bash
   # Find and kill the conflicting process
   lsof -i :8000
   kill -9 <PID>
   
   # Or change the port in docker-compose.yml
   ports:
     - "8001:8000"
   ```

2. **Missing Dependencies**:
   ```bash
   # Install required dependencies
   # For API
   cd api && pip install -r requirements.txt
   
   # For Web
   cd web && npm install
   ```

3. **Permission Issues**:
   ```bash
   # Ensure proper permissions
   chmod +x api/entrypoint.sh web/entrypoint.sh 2>/dev/null || true
   
   # Fix volume permissions
   docker compose down -v
   docker compose up -d
   ```

4. **Environment Variables Missing**:
   ```bash
   # Check .env file exists
   ls -la .env
   
   # Create from example
   cp .env.example .env
   
   # Verify required variables
   grep -E "DATABASE_URL|SECRET_KEY" .env
   ```

---

## 🔧 API Troubleshooting

### Issue: API Returns 500 Errors

**Symptoms**:
- API endpoints return HTTP 500
- Error messages in browser console
- Server logs show exceptions

**Diagnosis**:

```bash
# Check API logs
docker compose logs api

# Test health endpoint
curl -v http://localhost:8000/health

# Test with verbose output
curl -v -X GET http://localhost:8000/api/todos

# Check database connectivity
curl -v http://localhost:8000/health/db
```

**Common Causes and Solutions**:

#### 1. Database Connection Failed

**Error**: `sqlalchemy.exc.OperationalError: connection refused`

**Solutions**:
```bash
# Check if database is running
docker compose ps | grep postgres

# Test database connection manually
docker compose exec postgres psql -U appuser -d tododb -c "SELECT 1"

# Verify connection string in .env
cat .env | grep DATABASE_URL

# Update connection string if needed
# Format: postgresql://user:password@host:port/database
```

#### 2. Migration Errors

**Error**: `alembic.util.exc.CommandError: Can't locate revision`

**Solutions**:
```bash
# Run migrations manually
docker compose exec api alembic upgrade head

# Check migration history
docker compose exec api alembic history

# Reset database (DEVELOPMENT ONLY)
docker compose down -v
docker compose up -d

# Create missing migrations
docker compose exec api alembic revision --autogenerate -m "fix_missing_migration"
```

#### 3. Missing Required Fields

**Error**: `pydantic.error_wrappers.ValidationError`

**Solutions**:
```bash
# Check the API schema
cat api/schemas.py

# Verify request payload
curl -v -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Todo", "description": "Test description"}'

# Add missing required fields
# Check Pydantic models for required fields
```

#### 4. CORS Errors

**Error**: `Access to fetch at 'http://localhost:8000/api/todos' from origin 'http://localhost:5173' has been blocked by CORS policy`

**Solutions**:
```bash
# Add frontend URL to CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Restart API
docker compose restart api

# Verify CORS headers
curl -I http://localhost:8000/api/todos
```

#### 5. Authentication Errors

**Error**: `401 Unauthorized` or `403 Forbidden`

**Solutions**:
```bash
# Check if authentication is enabled
cat .env | grep -E "SECRET_KEY|AUTH_ENABLED"

# Verify JWT token
# If using JWT, ensure token is valid and not expired

# Check authentication middleware
cat api/middleware.py 2>/dev/null || echo "No middleware file"

# Temporarily disable auth for testing (not for production)
# In api/main.py, comment out dependency
```

---

## 🖥️ Frontend Troubleshooting

### Issue: Blank Page or Loading Forever

**Symptoms**:
- White screen
- Loading spinner never stops
- No errors in console

**Diagnosis**:

```bash
# Check browser console (F12)
# Look for JavaScript errors

# Check network tab
# Look for failed API requests

# Check Vite dev server logs
docker compose logs web

# Test API endpoint directly
curl -v http://localhost:8000/api/todos
```

**Common Causes and Solutions**:

#### 1. API URL Misconfigured

**Error**: `Failed to fetch` or `404 Not Found`

**Solutions**:
```bash
# Check VITE_API_URL in .env
cat .env | grep VITE_API_URL

# Update to correct URL
VITE_API_URL=http://localhost:8000

# For Docker, use service name
VITE_API_URL=http://api:8000

# Rebuild web container
docker compose build web
docker compose up -d web
```

#### 2. TypeScript Compilation Errors

**Error**: `svelte-check` errors in console

**Solutions**:
```bash
# Run type checking manually
cd web && npm run check

# Fix type errors
# Check for missing types, incorrect imports, etc.

# If errors are expected, add @ts-ignore comments
```

#### 3. Missing Environment Variables

**Error**: `import.meta.env.VITE_API_URL is undefined`

**Solutions**:
```bash
# Ensure .env file exists in web directory
ls -la web/.env

# Create .env file
cd web && cp ../.env.example .env

# Or use docker-compose environment
# Variables prefixed with VITE_ are automatically exposed
```

#### 4. Svelte Compilation Errors

**Error**: `Compilation failed` or `Unexpected token`

**Solutions**:
```bash
# Check Svelte version
cat web/package.json | grep svelte

# Ensure using Svelte 5 runes
# Replace $: with $state, $derived, etc.

# Check for syntax errors
npm run check

# Clear Svelte cache
rm -rf .svelte-kit
```

#### 5. Tailwind CSS Not Working

**Error**: Styles not applied, classes not recognized

**Solutions**:
```bash
# Check Tailwind configuration
cat web/tailwind.config.js 2>/dev/null || echo "No config"

# Ensure Tailwind is imported
cat web/src/app.css | grep -E "@tailwind|@apply"

# Check content configuration
# In tailwind.config.js, ensure content paths are correct
content: [
  './src/**/*.{html,js,svelte,ts}',
]

# Rebuild CSS
npm run dev
```

---

## 🗄️ Database Troubleshooting

### Issue: Database Connection Problems

**Symptoms**:
- API returns database errors
- Connection timeouts
- Authentication failures

**Diagnosis**:

```bash
# Check database container status
docker compose ps | grep postgres

# Test connection from API container
docker compose exec api psql postgresql://appuser:changeme@postgres:5432/tododb -c "SELECT 1"

# Check database logs
docker compose logs postgres

# Connect to database directly
docker compose exec postgres psql -U appuser -d tododb
```

**Common Causes and Solutions**:

#### 1. Wrong Credentials

**Error**: `password authentication failed`

**Solutions**:
```bash
# Check credentials in .env
cat .env | grep -E "POSTGRES_USER|POSTGRES_PASSWORD|POSTGRES_DB"

# Update credentials in docker-compose.yml
postgres:
  environment:
    POSTGRES_USER: appuser
    POSTGRES_PASSWORD: changeme
    POSTGRES_DB: tododb

# Restart database
docker compose restart postgres
```

#### 2. Database Not Ready

**Error**: `connection refused` or `server closed the connection unexpectedly`

**Solutions**:
```bash
# Wait for database to be ready
docker compose exec postgres pg_isready -U appuser -d tododb

# Add health check to docker-compose.yml
postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U appuser -d tododb"]
    interval: 5s
    timeout: 5s
    retries: 5

# Add depends_on with health check
depends_on:
  postgres:
    condition: service_healthy
```

#### 3. Database Migration Issues

**Error**: `relation "todos" does not exist`

**Solutions**:
```bash
# Run migrations
docker compose exec api alembic upgrade head

# Check migration status
docker compose exec api alembic current

# Create new migration if models changed
docker compose exec api alembic revision --autogenerate -m "add_todos_table"

# Apply migration
docker compose exec api alembic upgrade head
```

#### 4. Database Performance Issues

**Error**: Slow queries, timeouts

**Solutions**:
```bash
# Enable query logging
# In api/database.py or connection string
DATABASE_URL=postgresql://appuser:changeme@postgres:5432/tododb?options=-c%20log_statement%3Dall

# Check slow queries
docker compose logs postgres | grep "duration:"

# Add indexes
# In models.py, add indexes to frequently queried columns

# Use EXPLAIN to analyze queries
docker compose exec postgres psql -U appuser -d tododb -c "EXPLAIN ANALYZE SELECT * FROM todos"
```

#### 5. Database Data Corruption

**Error**: Inconsistent data, constraint violations

**Solutions**:
```bash
# Check for constraint violations
docker compose exec postgres psql -U appuser -d tododb -c "\\d"

# Validate data integrity
# Run custom validation queries

# Restore from backup (if available)
# Or reset database (DEVELOPMENT ONLY)
docker compose down -v
docker compose up -d
```

---

## 🐳 Docker Troubleshooting

### Issue: Docker Build Fails

**Symptoms**:
- `docker compose build` fails
- Build errors in output
- Image not created

**Diagnosis**:

```bash
# View build output
docker compose build 2>&1 | tail -50

# Check Dockerfile syntax
docker build -t test-api -f api/Dockerfile . 2>&1

# Check disk space
df -h

# Check Docker disk usage
docker system df
```

**Common Causes and Solutions**:

#### 1. Dockerfile Syntax Error

**Error**: `ERROR: for api Cannot locate specified Dockerfile`

**Solutions**:
```bash
# Verify Dockerfile exists
ls -la api/Dockerfile

# Check Dockerfile syntax
# Each FROM must be first in its stage
# Each RUN, COPY, etc. must be properly formatted

# Test Dockerfile
docker build -t test-api -f api/Dockerfile .
```

#### 2. Missing Base Image

**Error**: `ERROR: pull access denied for python:3.12-slim`

**Solutions**:
```bash
# Pull base image manually
docker pull python:3.12-slim

# Check if image exists
docker images | grep python

# Use different base image
# In Dockerfile, change FROM line
FROM python:3.12-alpine
```

#### 3. Build Context Issues

**Error**: `ERROR: for api COPY failed: stat /path/to/file: no such file or directory`

**Solutions**:
```bash
# Verify file exists in build context
ls -la api/requirements.txt

# Check .dockerignore
cat .dockerignore

# Ensure files are in correct location
# COPY . /app copies from build context root
```

#### 4. Disk Space Issues

**Error**: `ERROR: No space left on device`

**Solutions**:
```bash
# Clean Docker system
docker system prune -a --volumes

# Remove unused images
docker image prune -a

# Remove unused containers
docker container prune

# Remove unused volumes
docker volume prune

# Check disk space
df -h
```

#### 5. Permission Issues

**Error**: `ERROR: for api COPY failed: permission denied`

**Solutions**:
```bash
# Check file permissions
ls -la api/

# Ensure files are readable
chmod -R a+r api/

# Use non-root user in Dockerfile
USER appuser

# Or run as root temporarily
USER root
```

---

## 🧪 Testing Troubleshooting

### Issue: Tests Failing

**Symptoms**:
- pytest or vitest returns failures
- Tests timeout
- Assertion errors

**Diagnosis**:

```bash
# Run tests with verbose output
cd api && python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_api.py::test_create_todo -v

# Run with coverage
python -m pytest tests/ --cov=api --cov-report=term-missing

# For frontend tests
cd web && npm test
```

**Common Causes and Solutions**:

#### 1. Database Not Available for Tests

**Error**: `sqlalchemy.exc.OperationalError: connection refused`

**Solutions**:
```bash
# Start test database
docker compose -f docker-compose.test.yml up -d

# Or use in-memory database for tests
# In conftest.py, use SQLite
DATABASE_URL = "sqlite:///./test.db"

# Ensure test database is configured
# In conftest.py
@pytest.fixture(scope="session")
def db_session():
    # Setup test database
    pass
```

#### 2. Test Data Issues

**Error**: `AssertionError: assert response.status_code == 200`

**Solutions**:
```bash
# Check test data setup
# In conftest.py, verify fixtures

# Add debug output to tests
print(f"Response: {response.json()}")

# Check API endpoint manually
curl -v -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Test"}'
```

#### 3. Test Dependencies Missing

**Error**: `ModuleNotFoundError: No module named 'pytest'`

**Solutions**:
```bash
# Install test dependencies
cd api && pip install -r requirements.txt pytest pytest-cov httpx

# Or use uv
uv sync --dev

# For frontend
cd web && npm install
```

#### 4. Test Environment Issues

**Error**: `EnvironmentError: Environment variable not set`

**Solutions**:
```bash
# Set environment variables for tests
# In pytest.ini or pyproject.toml
[pytest]
env =
    DATABASE_URL=sqlite:///./test.db
    ENVIRONMENT=test

# Or use pytest-dotenv
pip install pytest-dotenv

# Create .env.test file
cp .env.example .env.test
```

#### 5. Flaky Tests

**Error**: Tests pass sometimes, fail other times

**Solutions**:
```bash
# Add retries
pip install pytest-rerunfailures

# In pytest.ini
[pytest]
addopts = --reruns 3 --reruns-delay 1

# Or mark specific tests
@pytest.mark.flaky(reruns=3)
def test_flaky():
    pass

# Check for timing issues
# Add waits or retries in tests
```

---

## 🚀 CI/CD Troubleshooting

### Issue: GitHub Actions Failing

**Symptoms**:
- Workflow runs fail
- Red X on PR
- Build or test failures

**Diagnosis**:

```bash
# View workflow runs
gh run list --repo HazelCunuder/briefs-todo-app-starter

# View specific run logs
gh run view <RUN_ID> --repo HazelCunuder/briefs-todo-app-starter --log

# Or view on GitHub
# https://github.com/HazelCunuder/briefs-todo-app-starter/actions
```

**Common Causes and Solutions**:

#### 1. Dependency Installation Failed

**Error**: `pip install failed` or `npm install failed`

**Solutions**:
```yaml
# In workflow file, add retry logic
steps:
  - name: Install dependencies
    run: |
      pip install -r requirements.txt || pip install -r requirements.txt
    retry:
      max-attempts: 3

# Or use uv for more reliable installs
- name: Install with uv
  run: uv sync --frozen-lockfile
```

#### 2. Test Failures in CI

**Error**: Tests pass locally but fail in CI

**Solutions**:
```yaml
# Ensure test database is available
services:
  postgres:
    image: postgres:16-alpine
    env:
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
      POSTGRES_DB: testdb
    ports:
      - 5432:5432

# Set environment variables for tests
env:
  DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
```

#### 3. Docker Build Failed in CI

**Error**: `docker build failed`

**Solutions**:
```yaml
# Use Docker Buildx
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

# Use cache
- name: Build with cache
  uses: docker/build-push-action@v6
  with:
    cache-from: type=gha,scope=api-${{ github.ref_name }}
    cache-to: type=gha,scope=api-${{ github.ref_name }},mode=max
```

#### 4. Permission Issues in CI

**Error**: `Permission denied`

**Solutions**:
```yaml
# Ensure proper permissions
- name: Fix permissions
  run: chmod -R a+r .

# Or use specific user
- name: Run as non-root
  run: |
    useradd -m appuser
    chown -R appuser:appuser .
    su appuser -c "command"
```

#### 5. Secrets Not Available

**Error**: `Secret not found`

**Solutions**:
```yaml
# Ensure secrets are configured in GitHub
# Settings > Secrets and variables > Actions

# Use environment variables
env:
  SECRET_KEY: ${{ secrets.SECRET_KEY }}

# Or use .env file
- name: Create .env
  run: |
    echo "SECRET_KEY=${{ secrets.SECRET_KEY }}" > .env
```

---

## ⚡ Performance Troubleshooting

### Issue: Slow API Responses

**Symptoms**:
- High response times
- Timeouts
- Slow page loads

**Diagnosis**:

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/todos

# Create curl-format.txt
cat > curl-format.txt << 'EOF'
   time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
   time_pretransfer:  %{time_pretransfer}\n
      time_redirect:  %{time_redirect}\n
   time_starttransfer:  %{time_starttransfer}\n
                      ----------\n
         time_total:  %{time_total}\n
EOF

# Use Apache Bench for load testing
ab -n 100 -c 10 http://localhost:8000/api/todos

# Check resource usage
docker stats
```

**Common Causes and Solutions**:

#### 1. Database Query Performance

**Symptoms**: Slow database queries

**Solutions**:
```bash
# Enable query logging
# In PostgreSQL configuration
log_statement = 'all'
log_duration = on

# Check slow queries
docker compose logs postgres | grep "duration:"

# Add indexes
# In models.py
class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)  # Add index
    created_at = Column(DateTime, index=True)  # Add index

# Use EXPLAIN ANALYZE
docker compose exec postgres psql -U appuser -d tododb \
  -c "EXPLAIN ANALYZE SELECT * FROM todos WHERE user_id = 1"
```

#### 2. N+1 Query Problem

**Symptoms**: Many database queries for a single request

**Solutions**:
```python
# Use SQLAlchemy joinedload or selectinload
from sqlalchemy.orm import joinedload, selectinload

# In crud.py or main.py
@router.get("/todos")
def get_todos(db: Session = Depends(get_db)):
    todos = db.query(Todo).options(joinedload(Todo.user)).all()
    return todos
```

#### 3. High Memory Usage

**Symptoms**: Container memory usage high

**Solutions**:
```bash
# Check memory usage
docker stats --no-stream

# Limit container memory
# In docker-compose.yml
api:
  mem_limit: 512m
  memswap_limit: 512m

# Optimize queries
# Use pagination
from fastapi import Query

@router.get("/todos")
def get_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100)
):
    todos = db.query(Todo).offset(skip).limit(limit).all()
    return todos
```

#### 4. High CPU Usage

**Symptoms**: Container CPU usage high

**Solutions**:
```bash
# Check CPU usage
top -c

# Profile Python code
pip install py-spy
py-spy top --pid <API_PID>

# Optimize expensive operations
# Use caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@cache(expire=60)
@router.get("/todos")
def get_todos():
    # Expensive operation
    pass
```

#### 5. Slow Startup

**Symptoms**: Application takes long time to start

**Solutions**:
```bash
# Check startup logs
docker compose logs api | grep -E "Starting|Ready|Loaded"

# Optimize Dockerfile
# Use multi-stage builds
# Minimize layers
# Use smaller base images

# Lazy load dependencies
# In main.py, import heavy modules only when needed
```

---

## 📖 Error Reference

### API Error Codes

| Code | Error | Description | Solution |
|------|-------|-------------|----------|
| 400 | Bad Request | Invalid request data | Check request payload |
| 401 | Unauthorized | Authentication failed | Check credentials |
| 403 | Forbidden | No permission | Check user roles |
| 404 | Not Found | Resource not found | Check URL |
| 405 | Method Not Allowed | Wrong HTTP method | Use correct method |
| 409 | Conflict | Resource already exists | Use different ID |
| 422 | Unprocessable Entity | Validation error | Check request data |
| 429 | Too Many Requests | Rate limit exceeded | Wait and retry |
| 500 | Internal Server Error | Server error | Check logs |
| 502 | Bad Gateway | Gateway error | Check proxy |
| 503 | Service Unavailable | Service down | Check dependencies |

### Database Error Codes

| Code | Error | Description | Solution |
|------|-------|-------------|----------|
| 23505 | unique_violation | Duplicate key | Use different value |
| 23503 | foreign_key_violation | Foreign key constraint | Check references |
| 23502 | not_null_violation | Not null constraint | Provide value |
| 23514 | check_violation | Check constraint | Check data |
| 42P01 | undefined_table | Table doesn't exist | Run migrations |
| 42703 | undefined_column | Column doesn't exist | Check schema |

### Docker Error Codes

| Code | Error | Description | Solution |
|------|-------|-------------|----------|
| 1 | Error | Generic error | Check logs |
| 125 | Cannot connect to Docker daemon | Docker not running | Start Docker |
| 126 | Image not found | Image missing | Pull image |
| 127 | Container not found | Container missing | Create container |
| 137 | Killed | OOM killed | Increase memory |
| 139 | Segmentation fault | Memory error | Check code |
| 143 | Terminated | Graceful shutdown | Normal |

---

## 🎯 Quick Fixes

### Reset Everything (Development Only)

```bash
# Stop all containers
docker compose down

# Remove volumes
docker compose down -v

# Remove all Docker resources
docker system prune -a --volumes

# Rebuild and restart
docker compose build --no-cache
docker compose up -d
```

### Reinstall Dependencies

```bash
# API dependencies
cd api
rm -rf __pycache__ *.egg-info
pip uninstall -y -r requirements.txt
pip install -r requirements.txt

# Web dependencies
cd ../web
rm -rf node_modules package-lock.json
npm install
```

### Clear Caches

```bash
# Docker cache
docker system prune

# Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Node.js cache
rm -rf node_modules/.cache

# Svelte cache
rm -rf .svelte-kit
```

---

## 📞 Getting Help

### Where to Ask for Help

1. **GitHub Issues**: Open an issue with detailed description
2. **GitHub Discussions**: Ask in discussions forum
3. **Stack Overflow**: Tag with `todo-app` and `fastapi` or `svelte`
4. **Discord**: Join the community Discord server

### What to Include in Bug Report

```markdown
## Description

What happened?

## Steps to Reproduce

1. Step 1
2. Step 2
3. Step 3

## Expected Behavior

What should happen?

## Actual Behavior

What actually happened?

## Environment

- OS: [e.g., Ubuntu 22.04]
- Docker version: [e.g., Docker 24.0.7]
- Python version: [e.g., Python 3.12.0]
- Node.js version: [e.g., Node.js 20.0.0]

## Logs

```
Paste relevant logs here
```

## Additional Context

Any other information that might help.
```

---

## 📚 Additional Resources

- [Docker Troubleshooting](https://docs.docker.com/engine/troubleshoot/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SvelteKit Documentation](https://kit.svelte.dev/docs/introduction)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

*Last updated: 2026-04-29*
*Part of the To-Do App troubleshooting documentation*
