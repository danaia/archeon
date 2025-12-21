"""
Template constants for README and documentation generation.

These templates are used during project initialization to create
guide files for AI assistants and developers.
"""

# This content is written to archeon/orchestrator/README.md during init
ORCHESTRATOR_README_TEMPLATE = '''# Archeon Glyph Reference

This is a living architecture document. All components, stores, APIs, and models
in this project MUST have a corresponding glyph in `ARCHEON.arcon`.

## Glyph Types

{glyph_table}

## Edge Types

{edge_table}

## Usage Example

```
@v1 NED:login => CMP:LoginForm => API:POST/auth/login => MDL:user => OUT:dashboard
```

This chain represents:
1. User need: Login functionality
2. Component: LoginForm to capture credentials
3. API call: POST to /auth/login
4. Model: User model for validation
5. Navigation: Redirect to dashboard

## Rules

1. **Declare Before Implementing**: Add glyphs to ARCHEON.arcon BEFORE writing code
2. **Validate After Every Change**: Run `arc validate` to check integrity
3. **No Orphan Code**: Every file should correspond to a glyph

Run `arc legend` to see the full glyph reference in the terminal.
'''

# This content is written to AI_README.md during init to guide AI assistants
AI_README_TEMPLATE = '''# Archeon AI Provisioning Guide

This file tells AI assistants how to scaffold and provision Archeon projects.

## ⚠️ CRITICAL: The Glyph-Code-Test Workflow

**Every feature MUST follow this exact workflow:**

1. **ADD GLYPH** → Write the chain to `ARCHEON.arcon`
2. **WRITE CODE** → Implement the code for each glyph in the chain
3. **RUN VALIDATE** → Execute `arc validate` to verify architecture

```bash
# After adding glyphs and writing code, ALWAYS run:
arc validate
```

This ensures:
- All glyphs in the knowledge graph have corresponding code
- No code exists outside the architecture
- Layer boundaries are respected (CMP cannot access MDL directly)
- All API endpoints have error paths defined

**Never skip the validation step.** If `arc validate` fails, fix the issues before continuing.

---

## Creating a New Project

When a user asks to create a new application (React, Vue, FastAPI, etc.), use these commands:

### React + FastAPI (Default)
```bash
mkdir project-name && cd project-name
arc init
arc ai-setup
```

### Vue 3 + FastAPI
```bash
mkdir project-name && cd project-name
arc init --frontend vue3
arc ai-setup
```

### Vue 2 + FastAPI
```bash
mkdir project-name && cd project-name
arc init --frontend vue
arc ai-setup
```

### Single Directory (No Monorepo)
```bash
mkdir project-name && cd project-name
arc init --single
arc ai-setup
```

## After Project Creation

Once the project is created, the AI should:

1. **Read** `archeon/ARCHEON.arcon` to understand the empty knowledge graph
2. **Ask** the user what features they want to build
3. **Write** glyph chains to `ARCHEON.arcon` for each feature
4. **Implement** code following those chains
5. **Run `arc validate`** to verify the implementation matches the architecture

## Adding Features - The Complete Workflow

When the user describes a feature, follow these steps IN ORDER:

### Step 1: Add the Glyph Chain
```bash
# Write the chain to ARCHEON.arcon (either manually or via CLI)
arc parse "NED:login => CMP:LoginForm => STO:Auth => API:POST/auth/login => MDL:user => OUT:dashboard"
```

### Step 2: Implement the Code
Write the code for each glyph in the chain:
- `CMP:LoginForm` → `client/src/components/LoginForm.tsx`
- `STO:Auth` → `client/src/stores/Auth.ts`
- `API:POST/auth/login` → `server/src/api/routes/auth_login.py`
- `MDL:user` → `server/src/models/user.py`

### Step 3: Validate the Architecture
```bash
arc validate
```

Expected output on success:
```
✓ All chains valid
✓ No boundary violations
✓ All glyphs resolved
```

If validation fails, fix the issues before proceeding.

### Step 4: Run Tests
```bash
# Frontend tests
cd client && npm test

# Backend tests  
cd server && python -m pytest tests/ -v
```

## Code Generation

After chains are defined:

```bash
# Generate all code from the knowledge graph
arc gen

# Then validate
arc validate

# Or AI implements manually following the chains, then validates
```

## Project Structure After Init

```
project-name/
├── .archeonrc              # Config (frontend: react/vue3, backend: fastapi)
├── client/                 # Frontend (components, stores)
│   └── src/
│       ├── components/     # CMP: glyphs go here
│       └── stores/         # STO: glyphs go here
├── server/                 # Backend (API, models, events)
│   └── src/
│       ├── api/routes/     # API: glyphs go here
│       ├── models/         # MDL: glyphs go here
│       └── events/         # EVT: glyphs go here
└── archeon/
    ├── ARCHEON.arcon       # Knowledge graph (chains go here)
    ├── AI_README.md        # This file (AI provisioning guide)
    ├── orchestrator/       # Reference docs
    │   └── README.md       # Glyph system documentation
    └── templates/          # Code generation templates
        ├── CMP/            # Component templates
        ├── STO/            # Store templates
        ├── API/            # API route templates
        ├── MDL/            # Model templates
        └── EVT/            # Event templates
```

## Framework Options

| Flag | Frontend | Store | Notes |
|------|----------|-------|-------|
| (default) | React | Zustand | Vite + TypeScript |
| `--frontend vue3` | Vue 3 | Pinia | Vite + JavaScript (**NO TypeScript**) |
| `--frontend vue` | Vue 2 | Pinia | Options API (**NO TypeScript**) |

| Flag | Backend | Notes |
|------|---------|-------|
| (default) | FastAPI | Python 3.10+, async |
| `--backend express` | Express | (coming soon) |

## Common Workflows

### "Create a Vue 3 app with user authentication"
```bash
mkdir my-app && cd my-app
arc init --frontend vue3
arc ai-setup
```

**IMPORTANT:** Vue 3 projects use **JavaScript only** - NO TypeScript.

**Step 1: Add glyphs** to ARCHEON.arcon:
```
# User authentication
@v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth/login => MDL:user => OUT:dashboard
@v1 NED:register => CMP:RegisterForm => STO:Auth => API:POST/auth/register => MDL:user => OUT:welcome
@v1 NED:logout => TSK:clickLogout => STO:Auth => API:POST/auth/logout => OUT:home
```

**Step 2: Implement code** for each glyph.

**Step 3: Validate:**
```bash
arc validate
```

### "Create a React app with a todo list"
```bash
mkdir todo-app && cd todo-app
arc init
arc ai-setup
```

**Step 1: Add glyphs** to ARCHEON.arcon:
```
# Todo list feature
@v1 NED:viewTodos => CMP:TodoList => STO:Todos => API:GET/todos => MDL:todo => OUT:display
@v1 NED:addTodo => CMP:TodoForm => STO:Todos => API:POST/todos => MDL:todo => OUT:refresh
@v1 NED:deleteTodo => TSK:clickDelete => STO:Todos => API:DELETE/todos/{id} => OUT:refresh
```

**Step 2: Implement code** for each glyph.

**Step 3: Validate:**
```bash
arc validate
```

## Validation Commands

```bash
arc validate    # Check architecture integrity (REQUIRED after every change)
arc status      # Show graph statistics and unresolved glyphs
arc check       # Quick syntax check on ARCHEON.arcon
```

### What `arc validate` Checks

| Check | Description |
|-------|-------------|
| Chain syntax | All chains parse correctly |
| Glyph resolution | Code exists for each glyph |
| Boundary rules | No illegal layer crossings (e.g., CMP→MDL) |
| Cycle detection | No cycles in structural edges |
| Error paths | API glyphs have ERR: handlers |
| Version integrity | Chain versions are consistent |

## Backend Route Registration (CRITICAL)

When creating API endpoints, you MUST register them in `server/src/main.py`:

### Step 1: Create the route file
```python
# server/src/api/routes/auth_login.py
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(request: LoginRequest):
    # Implementation
    pass
```

### Step 2: Register in main.py
```python
# server/src/main.py
from fastapi import FastAPI
from server.src.api.routes import auth_login  # Add import

app = FastAPI(title="API Server")

app.include_router(auth_login.router)  # Register the router
```

### Step 3: Validate
```bash
arc validate
```

### File Naming Convention
- `API:POST/auth/login` → `server/src/api/routes/auth_login.py`
- `API:GET/users/{id}` → `server/src/api/routes/users.py`
- `API:DELETE/posts/{id}` → `server/src/api/routes/posts.py`

**IMPORTANT:** Every new API route file MUST be imported and registered in `main.py` or the endpoint won't be accessible.

## Key Principles

1. **Glyph First**: Always define architecture in ARCHEON.arcon BEFORE writing code
2. **Validate Always**: Run `arc validate` after EVERY code change
3. **No Orphan Code**: Every file must correspond to a glyph in the knowledge graph
4. **Test Continuously**: Run tests after validation passes

The knowledge graph is the single source of truth. Every component, store, API, and model should be represented as a glyph in a chain before implementation.
'''
