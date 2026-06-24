# .vibe Directory - AI Agent Extensions

This directory contains extensions for AI agents working on the To-Do application project.
These extensions provide static context, auto-triggered skills, MCP servers, hooks, and slash commands.

## 📁 Structure

```text
.vibe/
├── README.md                    # THIS FILE - Extension documentation
├── skills/                      # Auto-triggered skills
│   ├── code-review-skill.yaml   # Code review expertise
│   ├── docker-expert-skill.yaml # Docker/containerization expertise
│   └── fullstack-dev-skill.yaml # Full-stack development expertise
│
├── mcp/                        # Model Context Protocol servers
│   ├── todo-db-mcp.yaml         # Database operations
│   ├── api-test-mcp.yaml        # API testing and validation
│   └── frontend-dev-mcp.yaml    # Frontend development tools
│
├── hooks/                      # Git hooks and event handlers
│   └── secrets-hook.yaml        # Secret detection and prevention
│
└── commands/                   # Slash commands (manual triggers)
    ├── deploy.yaml              # Deployment command
    └── test.yaml                # Testing command
```

---

## 🎯 Overview

### Static Context (Part 1)
- **Root `AGENTS.md`**: Complete static context for AI agents
- **`docs/AGENTS.md`**: Extended hierarchical context
- **Enriched `docs/*.md`**: All documentation files enhanced with AI-specific context

### Extensions (Part 2)
- **3 Skills**: Auto-triggered expertise for code review, Docker, and full-stack development
- **3 MCP Servers**: Tools for database operations, API testing, and frontend development
- **1 Hook**: Security hook for detecting and preventing secret leaks
- **2 Commands**: Slash commands for deployment and testing

---

## 📚 Static Context Files

### Root AGENTS.md
The primary entry point for AI agents. Contains:
- Repository overview and purpose
- Architecture diagrams
- Tech stack reference
- API contract
- Design system tokens
- Quick start commands
- Conventions and rules
- Security guidelines
- Documentation index
- AI agent principles

### docs/AGENTS.md
Extended hierarchical context with:
- Repository metadata
- Project architecture details
- Development environment setup
- Codebase navigation guide
- API and frontend development patterns
- Database and ORM guidance
- Testing strategy
- Deployment information
- AI-specific workflows
- Learning resources

### Enriched Documentation
All files in `docs/` have been enhanced with AI-specific context sections:
- `PROJECT_STRUCTURE.md`: Navigation guide and file patterns
- `CONVENTIONS.md`: Code generation guidelines
- `TECHNICAL_GUIDE.md`: Development workflow and debugging guide
- `DESIGN_SYSTEM.md`: UI development guidelines
- `COMPONENT_REFERENCE.md`: Component usage guide
- `FEATURES.md`: Feature development guide
- `SCREEN_FLOW.md`: User flow analysis
- `TASKS.md`: Task management workflow

---

## 🤖 Skills (Auto-Triggered)

Skills are automatically triggered based on context, file changes, or GitHub events.

### 1. Code Review Skill (`skills/code-review-skill.yaml`)

**Triggers:**
- Pull request events (opened, synchronize, reopened)
- Push to main/develop branches
- Changes to Python, TypeScript, Svelte, or JavaScript files

**Capabilities:**
- Analyze code quality and style
- Check convention compliance
- Review changes and suggest improvements
- Provide severity-based feedback

**Rules Enforced:**
- PEP 8 compliance for Python
- Type hints required
- Svelte 5 runes (no legacy `$:` syntax)
- Explicit types in TypeScript
- Docker best practices

**Usage:**
```yaml
# Automatically triggered on PR
# Provides feedback based on project conventions
```

### 2. Docker Expert Skill (`skills/docker-expert-skill.yaml`)

**Triggers:**
- Changes to Dockerfiles
- Changes to docker-compose files
- Changes to nginx configuration
- Changes to .env files

**Capabilities:**
- Analyze Dockerfiles for best practices
- Optimize layer caching
- Check security configurations
- Validate docker-compose setup
- Suggest improvements

**Rules Enforced:**
- Specific image tags (no `latest`)
- Non-root users required
- Multi-stage builds recommended
- Clean pip cache
- Group RUN commands
- Internal networks for databases
- Healthchecks required
- Resource limits configured

**Templates Provided:**
- Optimized FastAPI Dockerfile
- Multi-stage SvelteKit Dockerfile

**Usage:**
```yaml
# Automatically triggered on Dockerfile changes
# Provides optimization and security suggestions
```

### 3. Full-Stack Dev Skill (`skills/fullstack-dev-skill.yaml`)

**Triggers:**
- Changes to API files (main.py, models.py, schemas.py, crud.py)
- Changes to frontend files (+page.svelte, +layout.svelte, api.ts, types.ts)
- Changes to database files
- Push to feature/fix/refactor branches

**Capabilities:**
- Analyze feature implementation across all layers
- Generate coordinated backend and frontend code
- Validate backend-frontend integration
- Suggest architectural improvements
- Debug integration issues

**Patterns Provided:**
- Complete CRUD implementation pattern
- Svelte component patterns
- API client method patterns
- Optimistic update patterns

**Workflow:**
1. Define schema (schemas.py)
2. Create model (models.py)
3. Implement CRUD (crud.py)
4. Add routes (main.py)
5. Define types (types.ts)
6. Create API client (api.ts)
7. Build components
8. Integrate into page
9. Add tests
10. Update documentation

**Usage:**
```yaml
# Automatically triggered on full-stack development
# Provides coordinated backend and frontend guidance
```

---

## 🔌 MCP Servers

MCP (Model Context Protocol) servers provide external tools and capabilities.

### 1. Todo DB MCP (`mcp/todo-db-mcp.yaml`)

**Type:** Database operations

**Tools:**
- `execute_query`: Execute SQL queries
- `get_table_schema`: Get table schema information
- `list_tables`: List all database tables
- `get_all_todos`: Get all todo items
- `get_todo_by_id`: Get specific todo
- `create_todo`: Create new todo
- `update_todo`: Update existing todo
- `delete_todo`: Delete todo
- `analyze_database`: Analyze database structure
- `get_statistics`: Get todo statistics
- `check_migrations`: Check for pending migrations
- `apply_migrations`: Apply migrations

**Connection:**
- Uses `DATABASE_URL` environment variable
- Defaults to SQLite: `sqlite:///./api/todo.db`
- Supports PostgreSQL in Docker

**Usage:**
```javascript
// Get all todos
const todos = await mcp.callTool('todo-db-mcp', 'get_all_todos', {});

// Create a todo
const newTodo = await mcp.callTool('todo-db-mcp', 'create_todo', {
  title: 'Buy groceries',
  description: 'Milk, eggs, bread'
});

// Get statistics
const stats = await mcp.callTool('todo-db-mcp', 'get_statistics', {});
```

### 2. API Test MCP (`mcp/api-test-mcp.yaml`)

**Type:** API testing and validation

**Tools:**
- `test_endpoint`: Test specific API endpoint
- `validate_response`: Validate response against schema
- `test_all_endpoints`: Test all endpoints
- `get_endpoint_schema`: Get OpenAPI schema
- `list_all_endpoints`: List all endpoints
- `health_check`: Comprehensive health check
- `check_dependencies`: Check API dependencies
- `measure_performance`: Measure API performance
- `load_test`: Perform load testing

**Configuration:**
- Base URL: `http://localhost:8000` (configurable via `API_BASE_URL`)
- Docs: `/docs` and `/redoc` endpoints

**Usage:**
```javascript
// Test an endpoint
const result = await mcp.callTool('api-test-mcp', 'test_endpoint', {
  method: 'GET',
  path: '/todos'
});

// Validate response
const validation = await mcp.callTool('api-test-mcp', 'validate_response', {
  endpoint: '/todos',
  expected_schema: { type: 'array', items: { type: 'object' } }
});

// Health check
const health = await mcp.callTool('api-test-mcp', 'health_check', {});
```

### 3. Frontend Dev MCP (`mcp/frontend-dev-mcp.yaml`)

**Type:** Frontend development tools

**Tools:**
- `generate_component`: Generate new Svelte component
- `analyze_component`: Analyze component for best practices
- `list_components`: List all components
- `check_types`: Run TypeScript type checking
- `generate_types`: Generate TypeScript types
- `validate_types`: Validate type usage
- `analyze_styles`: Analyze Tailwind CSS usage
- `suggest_styles`: Suggest Tailwind classes
- `check_design_system`: Check design system compliance
- `analyze_route`: Analyze SvelteKit route
- `generate_page`: Generate new SvelteKit page
- `check_ssr`: Check SSR configuration

**Configuration:**
- Framework: SvelteKit ^2.15.0
- Language: TypeScript
- Styling: Tailwind CSS ^4.0.0

**Templates:**
- Component templates (empty, card, form, list, button, modal)
- Page templates
- API client templates

**Usage:**
```javascript
// Generate a component
const component = await mcp.callTool('frontend-dev-mcp', 'generate_component', {
  name: 'TodoItem',
  props: { todo: 'Todo', onToggle: 'Function' },
  template: 'card'
});

// Check types
const result = await mcp.callTool('frontend-dev-mcp', 'check_types', {});

// Analyze styles
const analysis = await mcp.callTool('frontend-dev-mcp', 'analyze_styles', {});
```

---

## 🔒 Hooks

### Secrets Hook (`hooks/secrets-hook.yaml`)

**Type:** Pre-commit hook

**Purpose:** Detect and prevent secret leaks before they are committed.

**Events:**
- `git.pre_commit`
- `git.commit_msg`
- `file.create`
- `file.modify`

**Patterns Detected:**
- API keys (generic, GitHub, AWS, Google, Slack, Stripe)
- Database credentials (PostgreSQL, MySQL)
- Generic passwords and secrets
- Private keys (RSA, EC, DSA, SSH)
- JWT tokens
- .env files
- Configuration files with secrets

**Actions:**
- **Block commit** for critical secrets
- **Warn user** for high-risk secrets
- **Suggest fixes** for all detections

**Severity Levels:**
- `critical`: Blocks commit (API keys, passwords, private keys)
- `high`: Warns user (JWT tokens, generic secrets)

**Usage:**
```bash
# The hook runs automatically on git commit
# To manually install:
cp .vibe/hooks/secrets-hook.yaml .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Example Fix:**
```bash
# Remove the secret from the file
git rm file_with_secret.txt

# Add to .gitignore
echo "file_with_secret.txt" >> .gitignore

# Use environment variables instead
echo "API_KEY=your_key_here" >> .env
echo ".env" >> .gitignore
```

---

## ⌨️ Slash Commands

### 1. Deploy Command (`commands/deploy.yaml`)

**Command:** `/deploy`

**Purpose:** Deploy the application to production or staging.

**Usage:**
```
/deploy [environment] [options]
```

**Parameters:**
- `environment`: production (default), staging, development
- `--dry-run, -n`: Perform dry run without deploying
- `--force, -f`: Force deployment even if tests fail
- `--verbose, -v`: Show verbose output
- `--help, -h`: Show help

**Pre-deployment Checks:**
1. Git status (no uncommitted changes)
2. Linting (`bun run lint`)
3. Type checking (`npm run check`)
4. Build test (`npm run build`)
5. API tests (`pytest`)
6. Docker build

**Steps (Production):**
1. Build Docker images
2. Run tests
3. Push images to registry
4. Deploy infrastructure
5. Verify deployment

**Environment Variables:**
- `DOCKER_REGISTRY`: Docker registry URL
- `VERSION`: Version tag
- `PRODUCTION_DB_URL`: Production database URL
- `STAGING_DB_URL`: Staging database URL

**Example:**
```
/deploy production
/deploy staging --dry-run
/deploy --verbose
```

### 2. Test Command (`commands/test.yaml`)

**Command:** `/test`

**Purpose:** Run comprehensive tests on the application.

**Usage:**
```
/test [scope] [options]
```

**Parameters:**
- `scope`: all (default), api, web, lint, docker
- `--verbose, -v`: Show verbose output
- `--watch, -w`: Watch for changes and re-run tests
- `--coverage, -c`: Generate coverage reports
- `--help, -h`: Show help

**Test Suites:**
- `lint`: Markdown and YAML linting
- `api`: FastAPI unit and integration tests
- `web`: SvelteKit type checking and unit tests
- `docker`: Docker build and container health tests
- `all`: All test suites

**Example:**
```
/test
/test api
/test web --verbose
/test all --coverage
```

---

## 🚀 Quick Start

### For AI Agents

1. **Read the static context:**
   ```bash
   cat AGENTS.md
   cat docs/AGENTS.md
   ```

2. **Understand the project structure:**
   ```bash
   cat docs/PROJECT_STRUCTURE.md
   ```

3. **Follow conventions:**
   ```bash
   cat docs/CONVENTIONS.md
   ```

4. **Use the extensions:**
   - Skills are auto-triggered based on context
   - Use MCP servers for external tools
   - Use slash commands for manual operations
   - Hooks run automatically on git events

### For Human Developers

1. **Install the hooks:**
   ```bash
   # Copy hooks to .git/hooks
   cp .vibe/hooks/*.yaml .git/hooks/
   chmod +x .git/hooks/*.yaml
   ```

2. **Use the slash commands:**
   ```bash
   # Run tests
   /test
   
   # Deploy
   /deploy staging
   ```

3. **Explore MCP servers:**
   ```javascript
   // In your AI agent or scripts
   const result = await mcp.callTool('todo-db-mcp', 'get_all_todos', {});
   ```

---

## 📖 Documentation

Each extension file contains detailed documentation including:
- Description and purpose
- Trigger conditions (for skills)
- Available tools and actions (for MCP servers)
- Configuration options
- Usage examples
- Integration with the project
- Response templates

---

## 🔧 Maintenance

### Updating Extensions

1. Modify the YAML files in the appropriate directory
2. Test the changes locally
3. Commit with a descriptive message
4. Update this README if the structure changes

### Adding New Extensions

1. **New Skill:**
   - Add to `skills/` directory
   - Define triggers, actions, and rules
   - Add context files to load

2. **New MCP Server:**
   - Add to `mcp/` directory
   - Define tools and their parameters
   - Add connection configuration

3. **New Hook:**
   - Add to `hooks/` directory
   - Define events to listen for
   - Add patterns to detect
   - Define actions to take

4. **New Command:**
   - Add to `commands/` directory
   - Define command name and parameters
   - Add steps to execute
   - Add response templates

### Testing Extensions

1. **Skills:** Trigger by making changes that match the patterns
2. **MCP Servers:** Call tools programmatically
3. **Hooks:** Test by attempting to commit secrets
4. **Commands:** Run with `/command-name`

---

## 📞 Support

For issues with extensions:
1. Check the extension's YAML file for configuration
2. Review the logs for error messages
3. Check that all dependencies are installed
4. Verify environment variables are set

---

## 🎓 Learning Resources

- [MCP Specification](https://github.com/modelcontextprotocol/specification)
- [Git Hooks Documentation](https://git-scm.com/docs/githooks)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SvelteKit Documentation](https://kit.svelte.dev/)
- [Docker Documentation](https://docs.docker.com/)

---

*Last updated: 2026-04-29*
*Part of the To-Do application AI agent extensions*
