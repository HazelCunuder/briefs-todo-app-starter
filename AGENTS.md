# AGENTS.md - AI Assistant Static Context

**Complete static context for AI agents working on this repository.**

This file provides persistent, versioned context that AI agents should consult at the start of every session.

---

## 📌 Repository Overview

| Aspect | Detail |
|--------|--------|
| **Repository** | `HazelCunuder/briefs-todo-app-starter` |
| **Primary Language** | TypeScript (SvelteKit), Python (FastAPI) |
| **License** | MIT |
| **Architecture** | FastAPI + SQLAlchemy (API) + SvelteKit + Tailwind v4 (Frontend) |
| **Database** | SQLite (default), PostgreSQL (optional via `DATABASE_URL`) |
| **Containerization** | Docker Compose with multi-container setup |

---

## 🎯 Project Purpose

A **To-Do application** demonstrating modern full-stack development with:
- **Backend**: FastAPI with SQLAlchemy ORM
- **Frontend**: SvelteKit 2 with Svelte 5 runes
- **Styling**: Tailwind CSS v4
- **DevOps**: Docker Compose orchestration

The project serves as both a functional application and a reference implementation for best practices in:
- API design (REST, Pydantic validation)
- Frontend architecture (typed fetch clients, reactive state)
- Database modeling (SQLAlchemy 2.0)
- Containerization (multi-stage builds, security hardening)

---

## 🏗️ Architecture Diagram

```text
┌─────────────────────────────────────────────────────────────────┐
│                         DEVELOPMENT                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Browser   │───▶│  SvelteKit  │───▶│  FastAPI    │          │
│  │ localhost:5173 │   │ localhost:5173 │   │ localhost:8000 │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                       │                                         │
│                       │ /api/* proxy                             │
│                       ▼                                         │
│                  ┌─────────────┐                                │
│                  │   SQLite    │                                │
│                  │  todo.db    │                                │
│                  └─────────────┘                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         PRODUCTION                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Browser   │───▶│    Nginx    │───▶│  FastAPI    │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                       │                                         │
│                       ▼                                         │
│                  ┌─────────────┐                                │
│                  │  PostgreSQL │                                │
│                  │   (Docker)  │                                │
│                  └─────────────┘                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

### Root Level

```text
briefs-todo-app-starter/
├── AGENTS.md                          # THIS FILE - AI static context
├── README.md                          # Main project documentation
├── CONTRIBUTING.md                    # Contribution guidelines
├── CHANGELOG.md                       # Version history (gitmoji)
├── LICENSE                            # MIT License
├── docker-compose.yml                 # Multi-container orchestration
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── .editorconfig                      # Editor settings
├── package.json                       # Bun tooling (lint, commit)
├── bun.lock                           # Bun lockfile
├── pyproject.toml                     # Python project metadata
├── renovate.json                      # Renovate configuration
│
├── api/                               # FastAPI Backend Service
│   ├── main.py                        # API entry point & routes
│   ├── database.py                    # SQLAlchemy engine & session
│   ├── models.py                      # ORM models (Todo)
│   ├── schemas.py                     # Pydantic validation schemas
│   ├── crud.py                        # Database CRUD operations
│   ├── Dockerfile                     # API container image
│   ├── .env.example                   # API environment variables
│   ├── pyproject.toml                 # Python dependencies (uv)
│   ├── uv.lock                        # uv lockfile
│   └── tests/                         # API unit & integration tests
│
├── web/                               # SvelteKit Frontend
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +layout.svelte         # Root layout
│   │   │   └── +page.svelte           # Main task list page
│   │   ├── lib/
│   │   │   ├── api.ts                 # Typed fetch client
│   │   │   ├── types.ts               # TypeScript interfaces
│   │   │   └── components/
│   │   │       └── TodoItem.svelte    # Task row component
│   │   ├── app.html                   # HTML shell
│   │   ├── app.css                    # Tailwind v4 entry
│   │   └── app.d.ts                   # SvelteKit types
│   ├── package.json                   # Frontend dependencies
│   ├── vite.config.ts                 # Vite + /api proxy config
│   ├── svelte.config.js               # SvelteKit configuration
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── Dockerfile                     # Web container image
│   ├── nginx.conf                     # Nginx reverse proxy config
│   └── tests/                         # Frontend tests
│
└── docs/                              # Documentation
    ├── AGENTS.md                      # Extended AI guide
    ├── PROJECT_STRUCTURE.md           # Directory organization
    ├── CONVENTIONS.md                 # Code style & git conventions
    ├── TECHNICAL_GUIDE.md             # Implementation details
    ├── DESIGN_SYSTEM.md               # Tailwind UI tokens
    ├── COMPONENT_REFERENCE.md         # API & UI component docs
    ├── FEATURES.md                    # Epics & user stories
    ├── SCREEN_FLOW.md                 # Navigation & user flows
    └── TASKS.md                       # Project task tracking
```

---

## 🛠️ Tech Stack Reference

### Backend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | FastAPI | >= 0.115.0 | REST API with auto-docs |
| ASGI Server | Uvicorn | >= 0.34.0 | Production ASGI server |
| ORM | SQLAlchemy | >= 2.0.0 | Database abstraction |
| Validation | Pydantic | >= 2.0.0 | Request/response schemas |
| Database | SQLite | Built-in | Default development DB |
| Database | PostgreSQL | 16 | Optional production DB |

### Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | SvelteKit | ^2.15 | Full-stack framework |
| Language | Svelte | ^5.16 | Reactive components |
| Styling | Tailwind CSS | ^4.0 | Utility-first CSS |
| Bundler | Vite | ^6.0 | Development server & build |
| Type System | TypeScript | ^5.7 | Type safety |

### DevOps Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Container Runtime | Docker | Containerization |
| Orchestration | Docker Compose | Multi-container management |
| Package Manager (Root) | Bun | Fast JavaScript runtime for tooling |
| Package Manager (Web) | npm | Frontend dependencies |
| Package Manager (API) | uv | Python dependency management |
| Git Hooks | Husky | Pre-commit hooks |
| Commit Lint | commitlint | Commit message validation |
| Markdown Lint | markdownlint | Markdown formatting |
| YAML Lint | yamllint | YAML formatting |
| Python Lint | Ruff | Python code quality |
| Dependency Updates | Renovate | Automated dependency updates |
| CI/CD | GitHub Actions | Continuous integration |

---

## 📡 API Contract

### Base URLs

| Environment | URL |
|-------------|-----|
| Development (API direct) | `http://localhost:8000` |
| Development (via proxy) | `/api` (proxied to API) |
| Production | `/api` (via nginx reverse proxy) |

### Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/todos` | List all tasks | - | `TodoResponse[]` |
| GET | `/todos/{id}` | Get task by ID | - | `TodoResponse` |
| POST | `/todos` | Create new task | `TodoCreate` | `TodoResponse` (201) |
| PUT | `/todos/{id}` | Update task | `TodoUpdate` | `TodoResponse` |
| DELETE | `/todos/{id}` | Delete task | - | 204 No Content |

### Schemas

```python
# TodoCreate (Request)
class TodoCreate(BaseModel):
    title: str                      # Required, 1-200 chars
    description: str | None = None  # Optional, max 500 chars
    completed: bool = False         # Default: False

# TodoUpdate (Request)
class TodoUpdate(BaseModel):
    title: str | None = None        # Optional
    description: str | None = None  # Optional
    completed: bool | None = None   # Optional

# TodoResponse (Response)
class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime | None
```

---

## 🎨 Design System Tokens

### Colors

| Role | Tailwind Class | Usage |
|------|----------------|-------|
| Primary | `bg-indigo-600`, `hover:bg-indigo-700` | Buttons, focus rings |
| Background | `bg-slate-50` | Page background |
| Surface | `bg-white` | Cards, list rows |
| Border | `border-slate-200`, `border-slate-300` | Card borders, inputs |
| Text Primary | `text-slate-900` | Titles, body text |
| Text Muted | `text-slate-600` | Descriptions, helper text |
| Text Disabled | `text-slate-400` | Completed task text |
| Danger | `text-red-600`, `bg-red-50` | Delete actions, errors |

### Typography

| Element | Tailwind Class |
|---------|----------------|
| Page Title | `text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl` |
| Section Subtitle | `text-sm text-slate-600` |
| Task Title | `font-medium text-slate-900` |
| Task Description | `text-sm text-slate-600` |
| Stats | `text-xs text-slate-500` |

### Spacing

| Context | Value |
|---------|-------|
| Container Max Width | `max-w-2xl` (~672px) |
| Container Padding (horizontal) | `px-4` |
| Container Padding (vertical) | `py-10` mobile, `py-16` desktop |
| Card Padding | `p-4` to `p-5` |
| Section Spacing | `mb-6` to `mb-8` |
| List Item Spacing | `space-y-2` |

---

## 🚀 Quick Start Commands

### Docker (Recommended)

```bash
# Build and start all services
docker compose up --build

# Build and start in background
docker compose up --build -d

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# View logs
docker compose logs -f

# View API logs only
docker compose logs -f api

# View web logs only
docker compose logs -f web
```

### Local Development

```bash
# API (from api/)
cd api
uv sync                          # Install dependencies
uv run uvicorn main:app --reload  # Start with hot reload

# Frontend (from web/)
cd web
npm install                      # Install dependencies
npm run dev                      # Start dev server (localhost:5173)

# Linting (from root)
bun install                      # Install lint tooling
bun run lint                     # Lint markdown and yaml
bun run lint:md                  # Lint markdown only
bun run lint:md:fix              # Auto-fix markdown
bun run lint:commit              # Validate last commit
bun run commit                   # Interactive gitmoji commit
```

### Testing

```bash
# Frontend type checking
cd web && npm run check

# Frontend build
cd web && npm run build

# API tests
cd api && python -m pytest tests/

# Full test suite
cd api && python -m pytest tests/ && cd ../web && npm run check
```

---

## 📜 Conventions & Rules

### Language Rule

**ALL written content must be in English**, including:
- Documentation (markdown files, comments)
- Commit messages
- Tasks and subtasks
- Epics and user stories
- Code comments and docstrings
- Variable and function names
- Error messages and logs

### Code Style

| Language | Convention |
|----------|------------|
| Python | PEP 8, snake_case, type hints |
| TypeScript | Strict mode, camelCase, explicit types |
| Svelte | Svelte 5 runes (`$state`, `$derived`, `$effect`, `$props`) |
| Tailwind | Utility classes inline, prefer composition |
| Files | kebab-case (config), snake_case (Python), PascalCase (Svelte components) |

### Git Conventions

**Branch Naming:**
```text
feature/short-description
fix/issue-number-description
refactor/component-name
docs/update-readme
hotfix/issue-description
```

**Commit Messages:** Use Gitmoji or Conventional Commits
```bash
# Interactive gitmoji tool
bun run commit
```

**Gitmoji Format:** `<emoji> <description>`
- ✨ New feature
- 🐛 Bug fix
- 📝 Documentation
- 🐳 Docker-related
- 🔒️ Security fix
- ♻️ Refactor
- 🔧 Configuration
- 💄 UI / styling

**Conventional Format:** `<type>(scope): <description>`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

### Branch Strategy

```text
main     --A--B-------------------------------> (production)
                \
develop          C--D--E-----------------------> (integration)
                          \
feature/xxx                F--G----------------> (feature branches)
```

**Rules:**
1. Never commit directly to `main` - only via PR from `develop`
2. Never commit directly to `develop` - always via feature/fix branch
3. Never `git merge main` into `develop` - use `git rebase origin/main`
4. Always rebase your branch on `develop` before opening a PR

---

## 🔒 Security Guidelines

### Secrets Management

**NEVER commit secrets or `.env` files to Git.**

Sensitive files that must NEVER be committed:
- `.env` (use `.env.example` for templates)
- `.env.local`
- `.env.*.local`
- Any file containing passwords, API keys, or database credentials

**Environment Variables:**
- Use `.env.example` to document required variables
- Load from `.env` in development (excluded from Git)
- Use Docker secrets or Kubernetes secrets in production

### Database Security

- PostgreSQL is restricted to internal Docker network only (`internal: true`)
- No direct web-to-database communication
- All database access goes through the FastAPI service
- Use parameterized queries (SQLAlchemy handles this automatically)

### Container Security

- All Dockerfiles use non-root users
- API container: `appuser` (UID 1000)
- Web container: `nginx-unprivileged` image
- PostgreSQL: Default user with restricted permissions
- Resource limits configured in `docker-compose.yml`

### Network Security

- PostgreSQL is not exposed to host or external networks
- API and web services communicate via defined Docker networks
- Production: Use HTTPS with valid certificates
- Development: HTTP is acceptable (localhost only)

---

## 📝 Documentation Index

| File | Purpose | Last Updated |
|------|---------|---------------|
| `AGENTS.md` (root) | AI static context (THIS FILE) | 2026-04-29 |
| `docs/AGENTS.md` | Extended AI guide | 2026-04-29 |
| `README.md` | Main project documentation | 2026-04-29 |
| `CONTRIBUTING.md` | Contribution guidelines | 2026-04-29 |
| `docs/PROJECT_STRUCTURE.md` | Directory organization | 2026-04-29 |
| `docs/CONVENTIONS.md` | Code style & git conventions | 2026-04-29 |
| `docs/TECHNICAL_GUIDE.md` | Implementation details | 2026-04-29 |
| `docs/DESIGN_SYSTEM.md` | Tailwind UI tokens | 2026-04-29 |
| `docs/COMPONENT_REFERENCE.md` | API & UI component docs | 2026-04-29 |
| `docs/FEATURES.md` | Epics & user stories | 2026-04-29 |
| `docs/SCREEN_FLOW.md` | Navigation & user flows | 2026-04-29 |
| `docs/TASKS.md` | Project task tracking | 2026-04-29 |

---

## 🎯 AI Agent Principles

### Fundamental Principles

1. **Read before modifying** - Always read a file before proposing changes
2. **Consult documentation** - Check relevant `docs/` files before any task
3. **Respect existing patterns** - Follow the style and conventions already in place
4. **Minimize changes** - Only modify what is necessary
5. **Document changes** - Update docs if behavior changes
6. **Run checks** - Validate with linting and tests before committing

### Code Generation Preferences

| Language | Preferences |
|----------|-------------|
| Python | PEP 8, type hints, Pydantic models, SQLAlchemy ORM |
| TypeScript | Strict mode, explicit types at module boundaries |
| Svelte | Svelte 5 runes (`$state`, `$derived`, `$effect`, `$props`) — NO legacy `$:` |
| Tailwind | Utility classes inline, prefer composition over `@apply` |
| YAML | Follow yamllint rules, consistent indentation |
| Markdown | Follow markdownlint rules, no trailing spaces |
| SQL | Uppercase keywords, snake_case tables/columns |

### Pre-commit Checklist

- [ ] Code passes `bun run lint`
- [ ] Frontend type-checks: `cd web && npm run check`
- [ ] Frontend builds: `cd web && npm run build`
- [ ] API endpoints respond: `curl http://localhost:8000/todos`
- [ ] Documentation updated if necessary
- [ ] Commit uses gitmoji convention
- [ ] No secrets or `.env` files committed
- [ ] Docker builds succeed: `docker compose up --build`

### Behaviors to Avoid

- ❌ Do not create unnecessary files
- ❌ Do not add dependencies without justification
- ❌ Do not modify project structure without discussion
- ❌ Do not ignore linting errors
- ❌ Do not comment out dead code (delete it)
- ❌ Do not hardcode secrets or database credentials
- ❌ Do not bypass the Vite `/api` proxy with hardcoded `localhost:8000` URLs
- ❌ Do not mix Svelte 5 runes with legacy `$:` reactive syntax

### Priorities

1. **Functionality** - Code must work end-to-end (API + frontend)
2. **Type safety** - TypeScript strict, Pydantic schemas at boundaries
3. **Readability** - Code must be understandable
4. **Consistency** - Follow existing patterns
5. **Simplicity** - Avoid over-engineering

---

## 🔗 External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SvelteKit Documentation](https://kit.svelte.dev/)
- [Tailwind CSS v4](https://tailwindcss.com/)
- [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- [Pydantic v2](https://docs.pydantic.dev/latest/)
- [Gitmoji](https://gitmoji.dev/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

## 📞 Support

For questions or issues:
1. Check the documentation in `docs/`
2. Review existing code for patterns
3. Open a GitHub issue with reproduction steps
4. Include relevant logs and error messages

---

*This file is part of the static context for AI agents. It is versioned in Git and shared across all team members and AI sessions.*
*Last updated: 2026-04-29*
