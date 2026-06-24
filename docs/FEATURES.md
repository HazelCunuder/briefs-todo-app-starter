# Features

Application features organized by epics and user stories.
Each item is linked to a GitHub issue for tracking and status.

## Epics

| # | Epic | Description |
|---|------|-------------|
| 1 | Database & Persistence | Persist tasks via SQLAlchemy with SQLite by default and Postgres as an opt-in via `DATABASE_URL` |
| 2 | FastAPI Service | Implement and expose REST CRUD endpoints for todos with Pydantic validation |
| 3 | SvelteKit Frontend | Build a typed, reactive UI consuming the API through a Vite proxy, with Svelte 5 runes |
| 4 | Tailwind v4 Design System | Style the UI with Tailwind utilities and a small set of token roles (slate / indigo / red) |
| 5 | Tooling & DX | Lint, commit conventions, type-check, and CI to keep the repo healthy |

---

## User Stories

### Epic 1: Database & Persistence

| User Story | Priority |
|------------|----------|
| As a developer, I want SQLite as the default database so the app runs with no extra services | High |
| As a developer, I want SQLAlchemy to auto-create tables on API startup so onboarding is trivial | High |
| As a developer, I want to swap to PostgreSQL via `DATABASE_URL` without code changes | Medium |

### Epic 2: FastAPI Service

| User Story | Priority |
|------------|----------|
| As a user, I want CRUD endpoints (create, read, update, delete) for managing tasks | High |
| As a developer, I want Pydantic schemas for request/response validation with min/max length checks | High |
| As a developer, I want auto-generated Swagger UI and ReDoc available at `/docs` and `/redoc` | Medium |
| As a developer, I want a clean separation between routes (`main.py`), models, schemas, and CRUD helpers | Medium |

### Epic 3: SvelteKit Frontend

| User Story | Priority |
|------------|----------|
| As a user, I want to add, toggle, edit, and delete tasks from a single page | High |
| As a user, I want to filter tasks by status (All / Active / Completed) | High |
| As a user, I want to see total / active / completed counts at a glance | Medium |
| As a developer, I want a typed `api.ts` fetch client so frontend calls are checked at build time | High |
| As a developer, I want optimistic UI updates with rollback on error so the app feels responsive | Medium |
| As a developer, I want the dev server to proxy `/api/*` to the FastAPI service so no CORS is needed | High |

### Epic 4: Tailwind v4 Design System

| User Story | Priority |
|------------|----------|
| As a user, I want a clean, accessible interface with clear status indicators | High |
| As a developer, I want Tailwind v4's CSS-first setup (no JS config) so the toolchain stays small | Medium |
| As a developer, I want documented color, spacing, and typography roles in `DESIGN_SYSTEM.md` | Medium |

### Epic 5: Tooling & DX

| User Story | Priority |
|------------|----------|
| As a developer, I want `bun run lint` to validate markdown and yaml on commit | High |
| As a developer, I want commitlint + gitmoji to enforce a consistent commit style | High |
| As a developer, I want `npm run check` to type-check the SvelteKit app | High |
| As a developer, I want CI to lint on every push and PR to `main`/`develop` | Medium |
| As a developer, I want Renovate / Dependabot to keep dependencies up to date | Medium |

---

## Technical Features

| Feature | Description |
|---------|-------------|
| Auto table creation | SQLAlchemy `create_all` on API startup |
| Vite dev proxy | `/api/*` proxied to `http://localhost:8000` — no CORS in dev |
| Svelte 5 runes | `$state`, `$derived`, `$effect`, `$props` for reactive UI |
| Optimistic mutations | Local state mutated before the network round-trip, with rollback on failure |
| API documentation | Auto-generated Swagger UI and ReDoc via FastAPI |

---

## 🤖 AI Agent Context

### Feature Development Guide for AI Agents

When implementing new features, AI agents should follow this process:

#### 1. Understand the Feature
- Review the epic and user stories in this file
- Check `docs/TASKS.md` for implementation tasks
- Review existing similar features for patterns

#### 2. Break Down the Feature
- Identify API changes needed (new endpoints, schemas, models)
- Identify frontend changes needed (new components, pages, state)
- Identify database changes needed (new tables, migrations)
- Identify documentation updates needed

#### 3. Implement the Feature
- Start with backend changes (models, schemas, CRUD, routes)
- Then implement frontend changes (types, API client, components, pages)
- Finally update documentation

#### 4. Test the Feature
- Test API endpoints with curl or Swagger UI
- Test frontend functionality in browser
- Run all tests (`bun run lint`, `npm run check`, `pytest`)
- Test with Docker (`docker compose up --build`)

### Feature Implementation Patterns

#### Adding a New Entity (e.g., Categories)

**Backend (API)**:
1. Add model to `api/models.py`:
   ```python
   class Category(Base):
       __tablename__ = "categories"
       id = Column(Integer, primary_key=True)
       name = Column(String(100), unique=True, nullable=False)
   ```

2. Add schemas to `api/schemas.py`:
   ```python
   class CategoryCreate(BaseModel):
       name: str = Field(..., min_length=1, max_length=100)
   
   class CategoryResponse(CategoryCreate):
       id: int
   ```

3. Add CRUD to `api/crud.py`:
   ```python
   def get_categories(db: Session) -> list[Category]:
       return db.query(Category).all()
   
   def create_category(db: Session, category: CategoryCreate) -> Category:
       db_category = Category(**category.model_dump())
       db.add(db_category)
       db.commit()
       db.refresh(db_category)
       return db_category
   ```

4. Add routes to `api/main.py`:
   ```python
   @app.get("/categories", response_model=list[CategoryResponse])
   def list_categories(db: Session = Depends(get_db)):
       return crud.get_categories(db)
   
   @app.post("/categories", response_model=CategoryResponse, status_code=201)
   def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
       return crud.create_category(db, category)
   ```

**Frontend (Web)**:
1. Add types to `web/src/lib/types.ts`:
   ```typescript
   export interface Category {
       id: number;
       name: string;
   }
   ```

2. Add API methods to `web/src/lib/api.ts`:
   ```typescript
   export const api = {
       // ... existing methods
       listCategories: () => request<Category[]>('/categories'),
       createCategory: (payload: CategoryCreate) =>
           request<Category>('/categories', { method: 'POST', body: JSON.stringify(payload) }),
   };
   ```

3. Create component in `web/src/lib/components/CategoryList.svelte`
4. Use component in appropriate page

#### Adding Authentication

**Backend**:
1. Add user model and auth dependencies
2. Add auth routes (login, register, logout)
3. Add middleware for protected routes
4. Add JWT token handling

**Frontend**:
1. Add auth state management
2. Add login/register forms
3. Add protected route guards
4. Add auth headers to API client

#### Adding Real-time Updates

**Backend**:
1. Add WebSocket endpoint
2. Implement broadcast for changes
3. Add connection management

**Frontend**:
1. Add WebSocket client
2. Handle real-time updates
3. Update UI reactively

### Feature Status Tracking

When working on features, AI agents should:

1. **Check current status** in this file
2. **Update status** when starting work (add `[x]` when complete)
3. **Create implementation tasks** in `docs/TASKS.md`
4. **Link to GitHub issues** when available

### Prioritization Guide

| Priority | When to Use | Examples |
|----------|-------------|----------|
| High | Core functionality, blocking issues | Database setup, CRUD operations |
| Medium | Important but not blocking | Filtering, sorting, search |
| Low | Nice-to-have, enhancements | Animations, advanced styling |

---

*Status is managed directly on GitHub issues.*
