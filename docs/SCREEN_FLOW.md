# Screen Flow

SvelteKit web application screen flow and navigation.

## Overview

The app is a single-page experience: one route (`/`) holds the task list, the create form,
filter tabs, and inline edit forms.

```text
┌──────────────────────────────────────────────┐
│  To-Do (single page)                         │
│                                              │
│  ┌──────────────────────────────────────┐    │
│  │  Add task form (title + description) │    │
│  └──────────────────────────────────────┘    │
│  ┌──────────────────────┬─────────────────┐  │
│  │ Filter tabs          │ Stats           │  │
│  │ [All|Active|Done]    │ total / active  │  │
│  └──────────────────────┴─────────────────┘  │
│  ┌──────────────────────────────────────┐    │
│  │ TodoItem rows (toggle / edit / del)  │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
```

---

## Sections

### Add Task Form

- **Purpose**: Create a new task
- **Components**:
  - Title input (required, max 200 chars)
  - Description textarea (optional, max 500 chars)
  - Add button (disabled while submitting or empty title)
- **Behavior**: Optimistic prepend to the list on success; form clears

### Filter Tabs

- **Purpose**: Filter the list by status
- **Options**: All / Active / Completed
- **Behavior**: Re-renders the visible list via a `$derived` selector — no network call

### Stats

- **Purpose**: Show total / active / completed counts
- **Behavior**: Derived from `todos` (`$derived`), updates instantly on any mutation

### Task Row (`TodoItem`)

- **Purpose**: Display and mutate a single task
- **Components**:
  - Checkbox (toggle completed)
  - Title (strikethrough when completed)
  - Description (optional, secondary text)
  - Edit button (reveals inline edit form)
  - Delete button
- **Inline edit form**: Title input, description textarea, Save / Cancel buttons

---

## User Flows

### Flow 1: Add a Task

1. User types a title (and optionally a description) in the Add form
2. User submits the form
3. Frontend calls `POST /api/todos`
4. On success, the new task is prepended to the list and the form clears
5. On error, an inline alert is displayed and the form keeps its values

### Flow 2: Toggle a Task

1. User clicks the checkbox on a task row
2. UI updates optimistically (strikethrough applied/removed instantly)
3. Frontend calls `PUT /api/todos/{id}` with `{ completed }`
4. On error, the optimistic change is rolled back and an alert is shown

### Flow 3: Edit a Task

1. User clicks the edit button on a task
2. The row swaps to an inline form pre-filled with the current values
3. User edits and clicks Save
4. Frontend calls `PUT /api/todos/{id}` with the patch
5. On success, the row returns to read mode with updated values
6. Cancel discards changes without an API call

### Flow 4: Delete a Task

1. User clicks the delete button on a task
2. UI removes the row immediately (optimistic)
3. Frontend calls `DELETE /api/todos/{id}`
4. On error, the row is restored and an alert is shown

### Flow 5: Filter Tasks

1. User clicks one of the filter tabs (All / Active / Completed)
2. The visible list updates instantly via the `$derived` selector
3. Stats remain unchanged (always derived from the full list)

---

## API Communication Flow

```text
User action → SvelteKit UI → fetch /api/* → Vite proxy → FastAPI → SQLAlchemy → Database
                                  ↓
Database → SQLAlchemy → FastAPI → fetch response → SvelteKit state update → re-render
```

| User Action | HTTP Method | Endpoint | UI Update |
|-------------|-------------|----------|-----------|
| View tasks | GET | `/todos` | Render task list |
| Add task | POST | `/todos` | Prepend to list |
| Edit task | PUT | `/todos/{id}` | Update row |
| Delete task | DELETE | `/todos/{id}` | Remove row |
| Toggle status | PUT | `/todos/{id}` | Toggle checkbox |

---

## 🤖 AI Agent Context

### User Flow Analysis for AI Agents

When implementing or modifying user flows, AI agents should analyze the current flows and ensure consistency.

#### Flow Implementation Checklist

1. **Identify the user action** (click, submit, navigate)
2. **Trace the flow** through all layers (UI → API → DB)
3. **Identify state changes** at each step
4. **Identify side effects** (API calls, DB updates)
5. **Ensure optimistic updates** where appropriate
6. **Handle errors** gracefully with rollback

#### Flow 1: Add a Task - Detailed Breakdown

```text
User Action: Submit add form
    │
    ▼
SvelteKit (+page.svelte)
    ├── State: newTitle (string)
    ├── Action: createTodo() function
    │   ├── Validate: title.trim() !== ""
    │   ├── Call: api.createTodo({ title })
    │   ├── Optimistic: Prepend to todos array
    │   └── Clear: newTitle = ""
    │
    ▼
API Client (api.ts)
    ├── Method: POST /api/todos
    ├── Headers: Content-Type: application/json
    ├── Body: JSON.stringify({ title })
    └── Return: Todo object
    │
    ▼
FastAPI (main.py)
    ├── Route: @app.post("/todos")
    ├── Validate: TodoCreate schema
    ├── Call: crud.create_todo(db, todo)
    └── Return: 201 Created with TodoResponse
    │
    ▼
CRUD (crud.py)
    ├── Create: Todo(**todo.model_dump())
    ├── Add: db.add(db_todo)
    ├── Commit: db.commit()
    ├── Refresh: db.refresh(db_todo)
    └── Return: db_todo
    │
    ▼
Database (SQLite/PostgreSQL)
    ├── Insert: INTO todos (title, description, completed, created_at)
    └── Return: Generated ID
```

#### Flow 2: Toggle a Task - Detailed Breakdown

```text
User Action: Click checkbox
    │
    ▼
TodoItem Component
    ├── State: todo.completed (boolean)
    ├── Action: onToggle(todo.id, !todo.completed)
    │   ├── Optimistic: Update local state immediately
    │   └── Call: parent handler
    │
    ▼
Page Component (+page.svelte)
    ├── Handler: toggleTodo(id, completed)
    │   ├── Optimistic: Map over todos, update matching item
    │   └── Call: api.updateTodo(id, { completed })
    │
    ▼
API Client (api.ts)
    ├── Method: PUT /api/todos/{id}
    ├── Body: JSON.stringify({ completed })
    └── Return: Updated Todo object
    │
    ▼
FastAPI (main.py)
    ├── Route: @app.put("/todos/{todo_id}")
    ├── Validate: TodoUpdate schema
    ├── Call: crud.update_todo(db, todo_id, todo)
    └── Return: 200 OK with TodoResponse
    │
    ▼
CRUD (crud.py)
    ├── Get: db_todo = get_todo(db, todo_id)
    ├── Update: for key, value in todo.model_dump().items()
    ├── Commit: db.commit()
    ├── Refresh: db.refresh(db_todo)
    └── Return: db_todo or None
    │
    ▼
Database
    ├── Update: UPDATE todos SET completed = ? WHERE id = ?
    └── Return: Row count
```

#### Error Handling in Flows

All flows should handle errors gracefully:

```typescript
// ✅ Good - Error handling with rollback
async function toggleTodo(id: number, completed: boolean) {
  const previousState = todos.find(t => t.id === id)?.completed;
  
  // Optimistic update
  todos = todos.map((t) => (t.id === id ? { ...t, completed } : t));
  
  try {
    await api.updateTodo(id, { completed });
  } catch (error) {
    // Rollback on error
    todos = todos.map((t) => (t.id === id ? { ...t, completed: previousState } : t));
    // Show error to user
    showError("Failed to update task");
  }
}

// ❌ Avoid - No error handling
async function toggleTodo(id: number, completed: boolean) {
  todos = todos.map((t) => (t.id === id ? { ...t, completed } : t));
  await api.updateTodo(id, { completed });  // Might fail silently
}
```

#### Navigation Patterns

The app uses a **single-page architecture** with client-side routing:

```text
URL Structure:
/
  └── (single page with all functionality)

Navigation:
- No page-to-page navigation
- All state managed in single page
- Filter changes via state (not URL)
- Form submissions handled inline
```

For future multi-page support:

```text
Suggested URL Structure:
/
├── /todos           (main list - current)
├── /todos/new       (add form)
├── /todos/{id}      (single todo detail)
└── /settings         (app settings)
```

#### State Management Patterns

```svelte
<!-- ✅ Good - Centralized state in page -->
<script lang="ts">
  // State in page component
  let todos = $state<Todo[]>([]);
  let filter = $state<Filter>('all');
  
  // Derived state
  const visibleTodos = $derived.by(() => {
    if (filter === 'active') return todos.filter(t => !t.completed);
    if (filter === 'completed') return todos.filter(t => t.completed);
    return todos;
  });
  
  // Computed stats
  const stats = $derived.by(() => ({
    total: todos.length,
    active: todos.filter(t => !t.completed).length,
    completed: todos.filter(t => t.completed).length
  }));
</script>

<!-- ❌ Avoid - Duplicated state -->
<script lang="ts">
  // State in multiple places
  let todos = $state<Todo[]>([]);
  let activeTodos = $state<Todo[]>([]);
  let completedTodos = $state<Todo[]>([]);
  
  // Manual updates required
  $effect(() => {
    activeTodos = todos.filter(t => !t.completed);
    completedTodos = todos.filter(t => t.completed);
  });
</script>
```

#### Data Flow Patterns

```text
Unidirectional Data Flow:

User Action → Component → Page State → API Call → Server → Database
                                    ↓
                              Response → Page State → Re-render

Example: Add Task
1. User types in input (bind:value)
2. User submits form (onsubmit)
3. Page handler validates input
4. Page optimistically updates state
5. Page calls api.createTodo()
6. API sends POST /api/todos
7. Server validates with Pydantic
8. Server calls crud.create_todo()
9. CRUD creates and saves Todo
10. Server returns 201 with Todo
11. Page receives response
12. Page updates state (if not already optimistic)
13. Svelte re-renders with new state
```

---

*Last updated: 2026-04-29*
