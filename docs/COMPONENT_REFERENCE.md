# Component Reference

Complete technical reference for API endpoints and Svelte components.

## Table of Contents

- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Svelte Components](#svelte-components)

---

## API Endpoints

Base URL: `http://localhost:8000` (proxied via `/api` from the SvelteKit dev server).

### GET /todos

List all tasks.

| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| - | - | - | No parameters |

**Response** `200 OK`:

```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-04-25T10:00:00Z",
    "updated_at": null
  }
]
```

---

### GET /todos/{todo_id}

Get a specific task by ID.

| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| `todo_id` | `int` | Path | Task ID |

**Response** `200 OK`: Single todo object.

**Response** `404 Not Found`:

```json
{ "detail": "Todo not found" }
```

---

### POST /todos

Create a new task.

**Request body**:

```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `title` | `string` | Yes | - | Task title (max 200 chars) |
| `description` | `string` | No | `null` | Task description (max 500 chars) |
| `completed` | `boolean` | No | `false` | Task completion status |

**Response** `201 Created`: Created todo object.

---

### PUT /todos/{todo_id}

Update an existing task.

| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| `todo_id` | `int` | Path | Task ID |

**Request body** (all fields optional):

```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}
```

**Response** `200 OK`: Updated todo object.

**Response** `404 Not Found`:

```json
{ "detail": "Todo not found" }
```

---

### DELETE /todos/{todo_id}

Delete a task.

| Parameter | Type | Location | Description |
|-----------|------|----------|-------------|
| `todo_id` | `int` | Path | Task ID |

**Response** `204 No Content`: Task deleted (no body).

**Response** `404 Not Found`:

```json
{ "detail": "Todo not found" }
```

---

## Data Models

### SQLAlchemy Model (Todo)

```python
class Todo(Base):
    __tablename__ = "todos"

    id: int              # Primary key, auto-increment
    title: str           # Max 200 chars, not null
    description: str     # Max 500 chars, nullable
    completed: bool      # Default: False
    created_at: datetime # Auto-set on creation
    updated_at: datetime # Auto-set on update
```

### Pydantic Schemas

#### TodoCreate (Request)

```python
class TodoCreate(BaseModel):
    title: str                       # Required, 1..200 chars
    description: str | None = None   # Optional, max 500 chars
    completed: bool = False          # Default: False
```

#### TodoUpdate (Request)

```python
class TodoUpdate(BaseModel):
    title: str | None = None         # Optional
    description: str | None = None   # Optional
    completed: bool | None = None    # Optional
```

#### TodoResponse (Response)

```python
class TodoResponse(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
```

### TypeScript Types (`web/src/lib/types.ts`)

```ts
export interface Todo {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface TodoCreate {
  title: string;
  description?: string | null;
  completed?: boolean;
}

export interface TodoUpdate {
  title?: string;
  description?: string | null;
  completed?: boolean;
}

export type Filter = 'all' | 'active' | 'completed';
```

---

## Svelte Components

### Page Layout (`web/src/routes/+page.svelte`)

The main page owns the list state and orchestrates filters, the create form, and per-item actions.

```svelte
<script lang="ts">
  import { api } from '$lib/api';
  import TodoItem from '$lib/components/TodoItem.svelte';
  import type { Filter, Todo, TodoUpdate } from '$lib/types';

  let todos = $state<Todo[]>([]);
  let filter = $state<Filter>('all');
  let newTitle = $state('');

  const visibleTodos = $derived.by(() => {
    if (filter === 'active') return todos.filter((t) => !t.completed);
    if (filter === 'completed') return todos.filter((t) => t.completed);
    return todos;
  });

  async function createTodo(e: Event) {
    e.preventDefault();
    const title = newTitle.trim();
    if (!title) return;
    const created = await api.createTodo({ title });
    todos = [created, ...todos];
    newTitle = '';
  }

  async function toggleTodo(id: number, completed: boolean) {
    todos = todos.map((t) => (t.id === id ? { ...t, completed } : t));
    await api.updateTodo(id, { completed });
  }

  async function deleteTodo(id: number) {
    todos = todos.filter((t) => t.id !== id);
    await api.deleteTodo(id);
  }

  $effect(() => {
    api.listTodos().then((list) => (todos = list));
  });
</script>

<form onsubmit={createTodo}>
  <input bind:value={newTitle} placeholder="What needs to be done?" required />
  <button type="submit">Add</button>
</form>

<ul>
  {#each visibleTodos as todo (todo.id)}
    <TodoItem
      {todo}
      onToggle={toggleTodo}
      onSave={(id, patch) => api.updateTodo(id, patch)}
      onDelete={deleteTodo}
    />
  {/each}
</ul>
```

### Task Row (`web/src/lib/components/TodoItem.svelte`)

Owns the inline-edit state for a single task. Receives the parent's mutation callbacks via `$props`.

```svelte
<script lang="ts">
  import type { Todo, TodoUpdate } from '$lib/types';

  interface Props {
    todo: Todo;
    onToggle: (id: number, completed: boolean) => void | Promise<void>;
    onSave: (id: number, patch: TodoUpdate) => void | Promise<void>;
    onDelete: (id: number) => void | Promise<void>;
  }

  let { todo, onToggle, onSave, onDelete }: Props = $props();

  let editing = $state(false);
  let titleDraft = $state('');
  let descriptionDraft = $state('');

  function startEdit() {
    titleDraft = todo.title;
    descriptionDraft = todo.description ?? '';
    editing = true;
  }
</script>
```

### Typed Fetch Client (`web/src/lib/api.ts`)

```ts
import type { Todo, TodoCreate, TodoUpdate } from './types';

const BASE = '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  listTodos: () => request<Todo[]>('/todos'),
  getTodo: (id: number) => request<Todo>(`/todos/${id}`),
  createTodo: (payload: TodoCreate) =>
    request<Todo>('/todos', { method: 'POST', body: JSON.stringify(payload) }),
  updateTodo: (id: number, payload: TodoUpdate) =>
    request<Todo>(`/todos/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteTodo: (id: number) => request<void>(`/todos/${id}`, { method: 'DELETE' })
};
```

---

## 🤖 AI Agent Context

### Component Usage Guide for AI Agents

This reference provides AI agents with quick access to all API endpoints and UI components in the project.

#### API Endpoints Quick Reference

| Method | Endpoint | Request | Response | Use Case |
|--------|----------|---------|----------|----------|
| GET | `/todos` | - | `TodoResponse[]` | List all tasks |
| GET | `/todos/{id}` | - | `TodoResponse` | Get specific task |
| POST | `/todos` | `TodoCreate` | `TodoResponse` | Create new task |
| PUT | `/todos/{id}` | `TodoUpdate` | `TodoResponse` | Update task |
| DELETE | `/todos/{id}` | - | 204 | Delete task |

#### Common API Patterns

##### Fetching all todos
```typescript
// Using the typed client
import { api } from '$lib/api';

const todos = await api.listTodos();

// Direct fetch (not recommended)
const response = await fetch('/api/todos');
const todos = await response.json();
```

##### Creating a todo
```typescript
import { api } from '$lib/api';

const newTodo = await api.createTodo({
  title: 'Buy groceries',
  description: 'Milk, eggs, bread'
});
```

##### Updating a todo
```typescript
import { api } from '$lib/api';

const updated = await api.updateTodo(1, {
  completed: true
});
```

##### Deleting a todo
```typescript
import { api } from '$lib/api';

await api.deleteTodo(1);
```

#### Svelte Component Reference

##### TodoItem Component

**Location**: `web/src/lib/components/TodoItem.svelte`

**Props**:
```typescript
interface Props {
  todo: Todo;                    // The todo item to display
  onToggle: (id: number, completed: boolean) => void | Promise<void>;
  onSave: (id: number, patch: TodoUpdate) => void | Promise<void>;
  onDelete: (id: number) => void | Promise<void>;
}
```

**Usage**:
```svelte
<script lang="ts">
  import TodoItem from '$lib/components/TodoItem.svelte';
  import type { Todo, TodoUpdate } from '$lib/types';
  
  let todos: Todo[] = [];
  
  async function toggleTodo(id: number, completed: boolean) {
    // Update logic
  }
  
  async function saveTodo(id: number, patch: TodoUpdate) {
    // Save logic
  }
  
  async function deleteTodo(id: number) {
    // Delete logic
  }
</script>

<ul>
  {#each todos as todo (todo.id)}
    <TodoItem
      todo={todo}
      onToggle={toggleTodo}
      onSave={saveTodo}
      onDelete={deleteTodo}
    />
  {/each}
</ul>
```

##### Page Layout Component

**Location**: `web/src/routes/+layout.svelte`

**Purpose**: Root layout that wraps all pages

**Key Features**:
- Imports Tailwind CSS (`app.css`)
- Provides consistent page structure
- Handles global state if needed

##### Main Page Component

**Location**: `web/src/routes/+page.svelte`

**State Management**:
- `todos`: Array of all todo items
- `filter`: Current filter ('all' | 'active' | 'completed')
- `newTitle`: Input for new todo title

**Derived Values**:
- `visibleTodos`: Filtered list based on current filter

**Effects**:
- Load todos on mount

**Handlers**:
- `createTodo`: Add new todo
- `toggleTodo`: Toggle completion status
- `deleteTodo`: Remove todo

#### TypeScript Types Reference

**Location**: `web/src/lib/types.ts`

**Core Types**:
```typescript
export interface Todo {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface TodoCreate {
  title: string;
  description?: string | null;
  completed?: boolean;
}

export interface TodoUpdate {
  title?: string;
  description?: string | null;
  completed?: boolean;
}

export type Filter = 'all' | 'active' | 'completed';
```

**Usage Patterns**:
```typescript
// Typing state
let todos = $state<Todo[]>([]);

// Typing props
let { todo }: { todo: Todo } = $props();

// Typing function parameters
function handleTodo(todo: Todo) { ... }
```

#### Python Model Reference

**Location**: `api/models.py`

**Todo Model**:
```python
class Todo(Base):
    __tablename__ = "todos"
    
    id: int              # Primary key
    title: str           # Required, max 200 chars
    description: str     # Optional, max 500 chars
    completed: bool      # Default: False
    created_at: datetime # Auto-set on creation
    updated_at: datetime # Auto-set on update
```

**Common Queries**:
```python
# Get all todos (most recent first)
todos = db.query(Todo).order_by(Todo.created_at.desc()).all()

# Get todo by ID
todo = db.query(Todo).filter(Todo.id == todo_id).first()

# Get incomplete todos
todos = db.query(Todo).filter(Todo.completed == False).all()

# Get todos by title search
todos = db.query(Todo).filter(Todo.title.ilike(f"%{search}%")).all()
```

#### Pydantic Schema Reference

**Location**: `api/schemas.py`

**Schemas**:
```python
# Base schema (shared fields)
class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool = False

# Create schema (all fields optional except title)
class TodoCreate(TodoBase):
    pass

# Update schema (all fields optional)
class TodoUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool | None = None

# Response schema (includes ID and timestamps)
class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    
    model_config = {"from_attributes": True}
```

**Validation**:
```python
# Automatic validation in FastAPI
@app.post("/todos")
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    # todo is already validated by Pydantic
    return crud.create_todo(db, todo)

# Manual validation
try:
    todo = TodoCreate(title="Test", description="Desc")
except ValidationError as e:
    print(e.errors())
```

---

*Last updated: 2026-04-29*
