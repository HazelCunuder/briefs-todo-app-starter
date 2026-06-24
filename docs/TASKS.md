# Tasks

Project task tracking based on the project brief.

## Part 1: Multi-Container Application

### PostgreSQL Setup

- [x] Pull and configure the official PostgreSQL Docker image
- [x] Create the `tododb` database with dedicated user
- [x] Configure a Docker volume (`pgdata`) for data persistence
- [x] Test database connectivity from a client

### FastAPI API Dockerization

- [x] Adapt `database.py` to connect to PostgreSQL (via `DATABASE_URL` override)
- [x] Create SQLAlchemy models for the Todo entity
- [x] Create Pydantic schemas for request/response validation
- [x] Implement CRUD operations (create, read, update, delete)
- [x] Create `Dockerfile.api` with Python slim base image
- [x] Configure Uvicorn as the ASGI server
- [x] Test API endpoints via Swagger UI
- [ ] Push API image to Docker Hub

### Web (SvelteKit) Dockerization

- [x] Configure SvelteKit with `@sveltejs/adapter-static` and `fallback: 'index.html'`
- [x] Disable SSR in `+layout.ts` (full SPA mode)
- [x] Implement Svelte UI with task list display
- [x] Implement add, edit, delete, and toggle task actions
- [x] Create `Dockerfile.web` (multi-stage: node builder + nginx runtime)
- [x] Add `web/nginx.conf` reverse-proxying `/api/*` to the api service
- [x] Test web-to-API communication through the nginx proxy
- [ ] Push web image to Docker Hub

### Docker Compose Orchestration

- [x] Create `docker-compose.yml` with all three services (db, api, web)
- [x] Configure internal Docker networks (backend, frontend)
- [x] Set up environment variable substitution from `.env`
- [x] Configure service startup dependencies (`depends_on` + healthcheck)
- [x] Create `.env.example` with documented variables
- [x] Test full orchestration with `docker compose up --build`

---

## Part 2: Security and Optimization

### Container Security

- [x] Create non-root users in all Dockerfiles (api: `appuser`; web: `nginx-unprivileged` image)
- [x] Restrict PostgreSQL to internal backend network only (`internal: true`)
- [x] Ensure no direct web-to-database communication (web is only on `frontend`)
- [x] Verify `.env` file is in `.gitignore`
- [x] Use specific image tags (no `latest`) — `postgres:16-alpine`, `node:22-alpine`,
      `nginxinc/nginx-unprivileged:1.27-alpine`, `python:3.12-slim`

### Resource Management

- [x] Define CPU and memory limits for PostgreSQL in Compose
- [x] Define CPU and memory limits for API in Compose
- [x] Define CPU and memory limits for the web in Compose
- [x] Optimize Docker images (slim base, `--no-cache-dir` pip, `npm ci --no-audit --no-fund`,
      multi-stage build)

### Orchestration Security

- [x] Configure `restart: unless-stopped` for all services
- [x] Verify network isolation (test external connection rejection)
- [ ] Run Trivy vulnerability scan on all images

---

## Part 3: Cloud Deployment (Optional)

- [ ] Create Railway account and project
- [ ] Deploy PostgreSQL via Railway plugin
- [ ] Deploy FastAPI service with `DATABASE_URL` from Railway
- [ ] Deploy web service pointing at the public API URL (or co-host behind nginx)
- [ ] Test CRUD operations on deployed application
- [ ] Document deployment steps in README.md
- [ ] Take screenshots of deployed application

---

## Completed (Template Setup)

- [x] Workflow release with changelog and GitHub release
- [x] Clean all docs
- [x] Issue and PR templates
- [x] Dependabot configuration
- [x] Renovate configuration
- [x] Commitlint (gitmoji)
- [x] Changelog (gitmoji + conventional)
- [x] Semantic-release (gitmoji)
- [x] EditorConfig
- [x] CONTRIBUTING.md
- [x] Adapt all documentation files for the SvelteKit stack

---

## 🤖 AI Agent Context

### Task Management for AI Agents

When working on tasks from this file, AI agents should follow this workflow:

#### 1. Select a Task
- Choose an unchecked task (`[ ]`)
- Review the task description
- Check dependencies (other tasks that must be completed first)

#### 2. Understand the Context
- Read relevant documentation in `docs/`
- Review existing code for patterns
- Check related tasks for context

#### 3. Implement the Task
- Follow conventions from `docs/CONVENTIONS.md`
- Use patterns from existing code
- Make minimal, focused changes

#### 4. Test the Implementation
- Run relevant tests
- Test manually if needed
- Verify with Docker if applicable

#### 5. Update Task Status
- Mark task as complete (`[x]`) when done
- Update any related documentation
- Commit changes with proper message

### Task Prioritization

AI agents should prioritize tasks in this order:

1. **Unchecked tasks in Part 1** (Multi-Container Application)
2. **Unchecked tasks in Part 2** (Security and Optimization)
3. **Unchecked tasks in Part 3** (Cloud Deployment - Optional)

### Task Dependencies

Some tasks depend on others. AI agents should:

1. **Check for dependencies** before starting a task
2. **Complete dependencies first** if they're unchecked
3. **Ask for clarification** if dependencies are unclear

#### Dependency Map

```text
PostgreSQL Setup
    └── FastAPI Dockerization (depends on DB)
        └── Web Dockerization (depends on API)
            └── Docker Compose Orchestration (depends on all services)

Container Security
    └── Orchestration Security (both use Docker)

Cloud Deployment
    └── All previous parts (depends on complete local setup)
```

### Task Implementation Patterns

#### Docker-related Tasks

```dockerfile
# ✅ Good Dockerfile pattern
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Security-related Tasks

```yaml
# ✅ Good security pattern in docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    networks:
      - backend
    internal: true  # Not exposed to host or external
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # From .env, not hardcoded
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped
```

#### Testing Tasks

```bash
# ✅ Good testing pattern
# 1. Lint first
bun run lint

# 2. Type check frontend
cd web && npm run check

# 3. Build frontend
cd web && npm run build

# 4. Test API
cd api && python -m pytest tests/

# 5. Test with Docker
docker compose up --build
```

### Task Completion Checklist

Before marking a task as complete (`[x]`), verify:

- [ ] Code follows project conventions
- [ ] All tests pass
- [ ] Documentation is updated (if needed)
- [ ] No secrets are committed
- [ ] No `.env` files are committed
- [ ] Changes are minimal and focused
- [ ] Docker builds succeed (if applicable)

### Common Task Patterns

#### "Create X" Tasks
- Create the file in the appropriate location
- Follow existing patterns in similar files
- Add necessary imports/exports
- Update any references or documentation

#### "Configure X" Tasks
- Modify existing configuration files
- Follow existing configuration patterns
- Ensure security best practices
- Test the configuration

#### "Test X" Tasks
- Write tests in appropriate test file
- Follow existing test patterns
- Test both success and error cases
- Ensure tests pass

#### "Document X" Tasks
- Add documentation to appropriate file
- Follow existing documentation style
- Include code examples where helpful
- Update table of contents if needed

### Task Tracking Tips

1. **Use GitHub issues** for tracking complex tasks
2. **Break large tasks** into smaller subtasks
3. **Update status regularly** in this file
4. **Link to commits/PRs** when available
5. **Review completed tasks** periodically

---

*Last updated: 2026-04-29*
