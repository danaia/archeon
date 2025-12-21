"""
Archeon CLI - Main entry point

Glyph-based architecture notation system for AI-orchestrated software development.

Install globally with:
    pip install -e .
    # or
    pip install archeon
    
Then use from anywhere:
    archeon init
    archeon parse "NED:login => TSK:submit => CMP:LoginForm => OUT:redirect"
    archeon gen --frontend react --backend fastapi
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint

from archeon.orchestrator.PRS_parser import parse_chain, ParseError
from archeon.orchestrator.GRF_graph import KnowledgeGraph, load_graph
from archeon.orchestrator.VAL_validator import validate_chain, validate_graph, GraphValidator
from archeon.config.legend import GLYPH_LEGEND, EDGE_TYPES

app = typer.Typer(
    name="archeon",
    help="Glyph-based architecture notation system for AI-orchestrated development.",
    no_args_is_help=False,
    rich_markup_mode="rich",
)
console = Console()

DEFAULT_ARCON = "ARCHEON.arcon"


def get_arcon_path() -> Path:
    """Get path to ARCHEON.arcon in current or parent directories."""
    current = Path.cwd()
    
    # Check current directory
    if (current / DEFAULT_ARCON).exists():
        return current / DEFAULT_ARCON
    
    # Check archeon subdirectory
    if (current / "archeon" / DEFAULT_ARCON).exists():
        return current / "archeon" / DEFAULT_ARCON
    
    # Walk up to find project root
    for parent in current.parents:
        if (parent / DEFAULT_ARCON).exists():
            return parent / DEFAULT_ARCON
        if (parent / "archeon" / DEFAULT_ARCON).exists():
            return parent / "archeon" / DEFAULT_ARCON
    
    # Default to current directory
    return current / DEFAULT_ARCON


def _get_package_templates_dir() -> Path:
    """Get the path to the templates directory in the installed archeon package."""
    return Path(__file__).parent / "templates"


def _copy_templates(archeon_dir: Path, frontend: str, backend: str):
    """Copy reference templates to the project's archeon/templates folder."""
    pkg_templates = _get_package_templates_dir()
    target_templates = archeon_dir / "templates"
    
    # Map frontend/backend to template files
    frontend_map = {
        "react": {"CMP": "react.tsx", "STO": "zustand.ts"},
        "vue": {"CMP": "vue.vue", "STO": "pinia.ts"},
        "vue3": {"CMP": "vue3.vue", "STO": "pinia.ts"},
    }
    
    backend_map = {
        "fastapi": {"API": "fastapi.py", "MDL": "mongo.py", "EVT": "pubsub.py", "FNC": "python.py"},
        "express": {"API": "fastapi.py", "MDL": "mongo.py", "EVT": "pubsub.py", "FNC": "typescript.ts"},  # TODO: add express templates
    }
    
    # Copy frontend templates
    for glyph, filename in frontend_map.get(frontend, frontend_map["react"]).items():
        src = pkg_templates / glyph / filename
        dst = target_templates / glyph / filename
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
    
    # Copy backend templates  
    for glyph, filename in backend_map.get(backend, backend_map["fastapi"]).items():
        src = pkg_templates / glyph / filename
        dst = target_templates / glyph / filename
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)


def _create_orchestrator_readme(archeon_dir: Path):
    """Create a README in the orchestrator folder explaining the system for AI IDEs."""
    readme_path = archeon_dir / "orchestrator" / "README.md"
    if readme_path.exists():
        return
    
    readme_path.write_text('''# Archeon Orchestrator

This folder contains reference documentation for AI IDE assistants.

## Glyph System

Archeon uses a glyph notation to define architectural components:

| Glyph | Purpose | Output |
|-------|---------|--------|
| `NED` | User Need/Feature entry point | Documentation |
| `TSK` | Task/Action step | Task handler |
| `CMP` | UI Component | React/Vue component |
| `STO` | State Store | Zustand/Pinia store |
| `API` | API Endpoint | Route handler |
| `MDL` | Data Model | API schemas + MongoDB entity |
| `EVT` | Event | Pub/Sub event |
| `FNC` | Function | Utility function |
| `V`   | View/Page | Page component |
| `OUT` | Output/Result | Terminal node |
| `ERR` | Error state | Error handler |

## MDL: (Model) - Unified Data Layer

The `MDL:` glyph handles both **API schemas** and **database models** in one file:

```python
# server/src/models/user.py
from pydantic import BaseModel

# API Schemas (request/response)
class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

# Database Model + Repository
class User:
    collection_name = "users"
    # ... database operations
```

### Chain Example
```
NED:register => CMP:RegisterForm => API:POST/auth/register => MDL:user => OUT:success
```

The flow: Form → API processes → Model validates & saves to DB

## Edge Types

- `=>` Structural flow (data/control)
- `~>` Reactive/subscription flow
- `->` Control flow
- `::` Containment (parent :: child)

## Chain Format

```
@v1 NED:feature => CMP:Component => STO:Store => API:POST/endpoint => MDL:model => OUT:result
```

- Version tag `@v1` tracks chain evolution
- Glyphs are `TYPE:name` format
- Names use PascalCase (components) or lowercase with slashes (APIs)

## Templates

The `../templates/` folder contains code generation templates:

- `CMP/` - Component templates (react.tsx, vue3.vue)
- `STO/` - Store templates (zustand.ts, pinia.ts)  
- `API/` - API route templates (fastapi.py)
- `MDL/` - Model templates (mongo.py)
- `EVT/` - Event templates (pubsub.py)
- `FNC/` - Function templates (python.py, typescript.ts)

Templates use `{PLACEHOLDER}` syntax for code generation.

## Knowledge Graph

The `ARCHEON.arcon` file is the source of truth for all architecture.

### Reading the Graph
AI assistants should read `ARCHEON.arcon` FIRST to understand:
- What features exist
- What components/stores/APIs are defined
- The data flow between layers

### Writing to the Graph
AI assistants CAN and SHOULD write new chains to `ARCHEON.arcon`:

**Where to add chains:**
```
# === AGENT CHAINS ===
# Add new chains below this line
```

**Chain format:**
```
# Feature description comment
@v1 NED:feature => CMP:Component => STO:Store => API:METHOD/path => MDL:model => OUT:result
```

**Versioning:**
- First version: `@v1 NED:login => ...`
- Updated version: `@v2 NED:login => ...` (keep @v1 for history)

**Naming conventions:**
- `CMP:PascalCase` - Components
- `STO:PascalCase` - Stores  
- `API:METHOD/path` - Endpoints (e.g., `API:POST/auth/login`)
- `MDL:lowercase` - Models
- `NED:lowercase` - Needs/features
- `OUT:lowercase` - Outcomes

### Workflow
1. Read `ARCHEON.arcon` to understand existing architecture
2. If feature doesn't exist, ADD a new chain first
3. Use templates from `templates/` for code generation patterns
4. Implement code following the chain structure
5. Never add code that isn't represented in the graph

## Backend Route Registration (CRITICAL)

When creating API endpoints, you MUST register them in `server/src/main.py`.

### FastAPI Route Registration

After creating a route file (e.g., `server/src/api/routes/auth_login.py`):

```python
# In server/src/main.py

from fastapi import FastAPI
from server.src.api.routes import auth_login, auth_register, users  # Import route modules

app = FastAPI(title="API Server", version="0.1.0")

# Register all routes
app.include_router(auth_login.router)
app.include_router(auth_register.router)
app.include_router(users.router)
```

### File Naming Convention

API glyphs map to route files:
- `API:POST/auth/login` → `server/src/api/routes/auth_login.py`
- `API:GET/users/{id}` → `server/src/api/routes/users.py`
- `API:DELETE/posts/{id}` → `server/src/api/routes/posts.py`

### Route Module Structure

Each route file exports a `router`:

```python
# server/src/api/routes/auth_login.py
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(request: LoginRequest):
    ...
```

### IMPORTANT: Always Update main.py

Every time you create a new API route file:
1. Create the route file in `server/src/api/routes/`
2. Import the router in `server/src/main.py`
3. Call `app.include_router(module.router)`

This ensures the endpoint is actually accessible.
''')


def _create_ai_readme(archeon_dir: Path):
    """Create the AI provisioning guide README."""
    ai_readme = archeon_dir / "AI_README.md"
    if ai_readme.exists():
        return
    
    ai_readme.write_text('''# Archeon AI Provisioning Guide

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
| `--frontend vue3` | Vue 3 | Pinia | Vite + JavaScript (no TS) |
| `--frontend vue` | Vue 2 | Pinia | Options API (no TS) |

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
''')


@app.command()
def init(
    path: Optional[str] = typer.Argument(None, help="Directory to initialize"),
    monorepo: bool = typer.Option(True, "--monorepo/--single", help="Create client/server separation"),
    frontend: str = typer.Option("react", "--frontend", "-f", help="Frontend framework (react, vue, vue3)"),
    backend: str = typer.Option("fastapi", "--backend", "-b", help="Backend framework (fastapi, express)"),
):
    """Initialize a new Archeon project with client/server structure."""
    target = Path(path) if path else Path.cwd()
    archeon_dir = target / "archeon"
    
    # Normalize frontend option
    if frontend.lower() in ("vue", "vue3"):
        frontend = "vue3"
    
    # Create base archeon directories
    base_dirs = [
        archeon_dir,
        archeon_dir / "orchestrator",
        archeon_dir / "agents",
        archeon_dir / "templates" / "CMP",
        archeon_dir / "templates" / "STO",
        archeon_dir / "templates" / "API",
        archeon_dir / "templates" / "MDL",
        archeon_dir / "templates" / "FNC",
        archeon_dir / "templates" / "EVT",
        archeon_dir / "tests",
        archeon_dir / "utils",
        archeon_dir / "config",
    ]
    
    for d in base_dirs:
        d.mkdir(parents=True, exist_ok=True)
        init_file = d / "__init__.py"
        if not init_file.exists() and d.name not in ("templates", "CMP", "STO", "API", "MDL", "FNC", "EVT"):
            init_file.write_text(f"# Archeon {d.name.title()}\n")
    
    # Copy reference templates from the archeon package
    _copy_templates(archeon_dir, frontend, backend)
    
    # Create orchestrator README for AI reference
    _create_orchestrator_readme(archeon_dir)
    
    # Create AI provisioning guide
    _create_ai_readme(archeon_dir)
    
    if monorepo:
        # Create client directory structure (frontend)
        client_dirs = [
            target / "client",
            target / "client" / "src",
            target / "client" / "src" / "components",
            target / "client" / "src" / "stores",
            target / "client" / "src" / "lib",
            target / "client" / "src" / "hooks",
            target / "client" / "src" / "types",
            target / "client" / "public",
            target / "client" / "tests",
        ]
        
        for d in client_dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        # Create server directory structure (backend)
        server_dirs = [
            target / "server",
            target / "server" / "src",
            target / "server" / "src" / "api",
            target / "server" / "src" / "api" / "routes",
            target / "server" / "src" / "models",
            target / "server" / "src" / "services",
            target / "server" / "src" / "lib",
            target / "server" / "src" / "events",
            target / "server" / "tests",
        ]
        
        for d in server_dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        # Create client package.json based on frontend framework
        client_package = target / "client" / "package.json"
        if not client_package.exists():
            if frontend == "vue3":
                client_package.write_text('''{
  "name": "client",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:run": "vitest --run",
    "test:ui": "vitest --ui",
    "lint": "eslint . --ext .vue,.ts,.tsx"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "pinia": "^2.1.7",
    "vue-router": "^4.2.5"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "@vue/test-utils": "^2.4.0",
    "@pinia/testing": "^0.1.3",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "jsdom": "^24.0.0",
    "vue-tsc": "^2.0.0",
    "typescript": "^5.0.0"
  }
}
''')
                # Create Vue 3 specific files
                (target / "client" / "src" / "App.vue").write_text('''<script setup>
// App root component - Generated by Archeon
</script>

<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style>
#app {
  font-family: system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
''')
                (target / "client" / "src" / "main.js").write_text('''// Main entry - Generated by Archeon
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.mount('#app');
''')
                (target / "client" / "vite.config.js").write_text('''import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  test: {
    globals: true,
    environment: 'jsdom'
  }
});
''')
            else:
                # React (default)
                client_package.write_text('''{
  "name": "client",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "test": "vitest",
    "test:run": "vitest --run"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "vitest": "^1.0.0",
    "jsdom": "^24.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0"
  }
}
''')
                # Create vite.config.ts for React
                (target / "client" / "vite.config.ts").write_text('''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts']
  }
});
''')
                # Create test setup file for React
                (target / "client" / "tests").mkdir(parents=True, exist_ok=True)
                (target / "client" / "tests" / "setup.ts").write_text('''import '@testing-library/jest-dom';
''')
        
        # Create client .env file
        client_env = target / "client" / ".env"
        if not client_env.exists():
            client_env.write_text('''# Client Environment Variables
# Generated by Archeon

# API Configuration
VITE_API_URL=http://localhost:8000

# Add your environment variables below
# VITE_* variables are exposed to the client
''')
        
        # Create client .env.example file
        client_env_example = target / "client" / ".env.example"
        if not client_env_example.exists():
            client_env_example.write_text('''# Client Environment Variables Template
# Copy this to .env and fill in your values

# API Configuration
VITE_API_URL=http://localhost:8000

# Add your environment variables below
# VITE_* variables are exposed to the client
''')
        
        # Create server pyproject.toml stub
        server_pyproject = target / "server" / "pyproject.toml"
        if not server_pyproject.exists():
            server_pyproject.write_text(f'''[project]
name = "server"
version = "0.1.0"
description = "Backend server for {target.name}"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "pydantic>=2.0.0",
    "motor>=3.3.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "httpx>=0.24.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
''')
        
        # Create server main.py
        server_main = target / "server" / "src" / "main.py"
        if not server_main.exists():
            server_main.write_text('''"""
Server entry point - Generated by Archeon
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import database connection
try:
    from db.database import close_connection
except ImportError:
    async def close_connection(): pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    yield
    # Shutdown
    await close_connection()


app = FastAPI(title="API Server", version="0.1.0", lifespan=lifespan)

# CORS for client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Routes will be imported here by Archeon
''')
        
        # Create MongoDB connection module
        db_module = target / "server" / "src" / "db" / "database.py"
        db_module.parent.mkdir(exist_ok=True)
        (db_module.parent / "__init__.py").touch()
        if not db_module.exists():
            db_template = Path(__file__).parent / "templates" / "_server" / "db.py"
            if db_template.exists():
                shutil.copy2(db_template, db_module)
        
        # Create server .env file
        server_env = target / "server" / ".env"
        if not server_env.exists():
            server_env.write_text('''# Server Environment Variables
# Generated by Archeon

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Database Configuration (MongoDB Atlas)
# Format: mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority&appName=<appname>
MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority&appName=myapp
MONGODB_DB_NAME=app_db

# Security
SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Add your environment variables below
''')
        
        # Create server .env.example file
        server_env_example = target / "server" / ".env.example"
        if not server_env_example.exists():
            server_env_example.write_text('''# Server Environment Variables Template
# Copy this to .env and fill in your values

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Database Configuration
DATABASE_URL=mongodb://localhost:27017
DATABASE_NAME=app_db

# Security (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Add your environment variables below
''')
    
    # Create .gitignore to protect .env files
    gitignore_path = target / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text('''# Environment files (DO NOT COMMIT)
.env
.env.local
.env.*.local

# Dependencies
node_modules/
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/

# Build outputs
dist/
build/
*.egg-info/

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Logs
*.log
npm-debug.log*

# Testing
coverage/
.coverage
htmlcov/

# Archeon generated
tests/generated/
''')
    
    # Create ARCHEON.arcon
    arcon_path = archeon_dir / DEFAULT_ARCON
    if not arcon_path.exists():
        arcon_path.write_text(
            "# Archeon Knowledge Graph\n"
            "# Version: 2.0\n"
            f"# Project: {target.name}\n"
            "\n"
            "# === ORCHESTRATOR LAYER ===\n"
            "ORC:main :: PRS:glyph :: VAL:chain :: SPW:agent :: TST:e2e\n"
            "GRF:domain :: ORC:main\n"
            "\n"
            "# === AGENT CHAINS ===\n"
            "# Add chains using: archeon parse \"<chain>\"\n"
        )
    
    # Create .archeonrc config file with client/server paths
    rc_path = target / ".archeonrc"
    if not rc_path.exists():
        if monorepo:
            rc_path.write_text(
                "# Archeon Configuration\n"
                "\n"
                "# Project structure\n"
                "monorepo: true\n"
                "client_dir: ./client/src\n"
                "server_dir: ./server/src\n"
                "\n"
                "# Frameworks\n"
                f"frontend: {frontend}\n"
                f"backend: {backend}\n"
                "db: mongo\n"
                "\n"
                "# Output mapping\n"
                "# Frontend glyphs (CMP, STO, V) -> client_dir\n"
                "# Backend glyphs (API, MDL, FNC, EVT) -> server_dir\n"
            )
        else:
            rc_path.write_text(
                "# Archeon Configuration\n"
                "monorepo: false\n"
                "frontend: react\n"
                "backend: fastapi\n"
                "db: mongo\n"
                "output_dir: ./src\n"
            )
    
    rprint(f"[green]✓[/green] Initialized Archeon project at [bold]{archeon_dir}[/bold]")
    rprint(f"  Created {DEFAULT_ARCON}")
    rprint(f"  Created .archeonrc")
    rprint(f"  Copied {frontend}/{backend} templates to archeon/templates/")
    rprint(f"  Created orchestrator/README.md (glyph reference)")
    rprint(f"  Created AI_README.md (provisioning guide)")
    
    if monorepo:
        rprint(f"\n  [bold]Project Structure:[/bold]")
        rprint(f"  [cyan]client/[/cyan]  → {frontend.capitalize()} frontend (components, stores)")
        rprint(f"  [cyan]server/[/cyan]  → {backend.capitalize()} backend (API, models, events)")
        rprint(f"  [cyan]archeon/[/cyan] → Knowledge graph and orchestration")
    
    rprint(f"\n  [bold]Next:[/bold] Describe a feature in natural language:")
    rprint(f"  [cyan]arc intent \"user logs in with email and password\"[/cyan]")
    rprint(f"\n  Or use glyph notation directly:")
    rprint(f"  [cyan]arc parse \"NED:login => CMP:LoginForm => API:POST/auth => OUT:dashboard\"[/cyan]")
    
    rprint(f"\n  [bold]Tip:[/bold] Run [cyan]arc ai-setup[/cyan] to configure IDE AI assistants")


@app.command("ai-setup")
def ai_setup(
    cursor: Optional[bool] = typer.Option(None, "--cursor/--no-cursor", help="Generate .cursorrules"),
    copilot: Optional[bool] = typer.Option(None, "--copilot/--no-copilot", help="Generate .github/copilot-instructions.md"),
    windsurf: Optional[bool] = typer.Option(None, "--windsurf/--no-windsurf", help="Generate .windsurfrules"),
    cline: Optional[bool] = typer.Option(None, "--cline/--no-cline", help="Generate .clinerules"),
    aider: Optional[bool] = typer.Option(None, "--aider/--no-aider", help="Generate .aider.conf.yml"),
    vscode: Optional[bool] = typer.Option(None, "--vscode/--no-vscode", help="Update .vscode/settings.json"),
    all_ides: bool = typer.Option(False, "--all", "-a", help="Generate configs for all IDEs"),
):
    """Generate AI assistant configuration files for IDE integration.
    
    By default, generates all configs. Use specific flags to generate only selected ones.
    
    Examples:
        arc ai-setup              # Generate all (default)
        arc ai-setup --cursor     # Only Cursor
        arc ai-setup --vscode --copilot  # Only VS Code and Copilot
        arc ai-setup --no-cline   # All except Cline
    """
    target = Path.cwd()
    created = []
    
    # Determine which to generate:
    # - If --all flag, generate everything
    # - If any positive flag is set (True), only generate those
    # - If only negative flags (False), generate all except those
    # - If no flags, generate all (default behavior)
    
    flags = {'cursor': cursor, 'copilot': copilot, 'windsurf': windsurf, 
             'cline': cline, 'aider': aider, 'vscode': vscode}
    
    has_positive = any(v is True for v in flags.values())
    has_negative = any(v is False for v in flags.values())
    
    if all_ides:
        # --all flag: enable everything
        for key in flags:
            if flags[key] is None:
                flags[key] = True
    elif has_positive:
        # User specified specific IDEs to include
        for key in flags:
            if flags[key] is None:
                flags[key] = False
    else:
        # No positive flags or --all: default to all (unless explicitly disabled)
        for key in flags:
            if flags[key] is None:
                flags[key] = True
    
    # Archeon context block (shared across all configs)
    archeon_context = '''## Archeon Architecture System

This project uses Archeon, a glyph-based architecture notation system.

### ⚠️ MANDATORY: Glyph-Code-Test Workflow

**Every feature MUST follow this exact workflow:**

1. **ADD GLYPH** → Write the chain to `archeon/ARCHEON.arcon`
2. **WRITE CODE** → Implement the code for each glyph
3. **RUN VALIDATE** → Execute `arc validate` to test architecture

```bash
# ALWAYS run after adding glyphs and writing code:
arc validate
```

**Never skip validation.** If it fails, fix issues before continuing.

### Critical Files - READ FIRST
- `archeon/ARCHEON.arcon` - The knowledge graph defining all features
- `archeon/AI_README.md` - **Provisioning guide** (how to create new projects)
- `.archeonrc` - Project configuration (frontend, backend, paths)

### Creating New Projects
If the user asks to create a new application (React, Vue, etc.), read `archeon/AI_README.md` for shell commands:
```bash
mkdir project-name && cd project-name
arc init --frontend vue3  # or react (default)
arc ai-setup
```

### Glyph Notation
Features are defined as chains:
```
NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => MDL:user => OUT:dashboard
```

| Glyph | Meaning |
|-------|---------|
| `NED:` | User need/motivation |
| `TSK:` | User task/action |
| `CMP:` | UI Component |
| `STO:` | State store |
| `API:` | HTTP endpoint |
| `MDL:` | Data model (API schemas + database) |
| `FNC:` | Utility function |
| `EVT:` | Event handler |
| `OUT:` | Success outcome |
| `ERR:` | Error path |

### Edge Types
- `=>` Structural flow (no cycles)
- `~>` Reactive subscription (cycles OK)
- `->` Control/branching
- `::` Containment

### The Complete Workflow (REQUIRED)

**Step 1: Add Glyph Chain**
```bash
arc parse "NED:feature => CMP:Component => STO:Store => API:POST/path => MDL:model => OUT:result"
```
Or write directly to `archeon/ARCHEON.arcon`.

**Step 2: Implement Code**
Write code for each glyph in the chain.

**Step 3: Validate Architecture**
```bash
arc validate
```
This checks:
- All glyphs have corresponding code
- No boundary violations (CMP cannot access MDL)
- No cycles in structural edges
- API endpoints have error handlers

**Step 4: Run Tests**
```bash
cd client && npm test      # Frontend
cd server && pytest        # Backend
```

### Writing Glyph Chains
You CAN and SHOULD write glyph chains directly to `archeon/ARCHEON.arcon`.

**Chain Format:**
```
@v1 NED:feature => CMP:Component => STO:Store => API:METHOD/path => MDL:model => OUT:result
```

**Writing Rules:**
1. Add new chains under `# === AGENT CHAINS ===` section
2. Use incremental version tags: if `@v1 NED:login` exists, next version is `@v2 NED:login`
3. Chains must start with `NED:` or `TSK:` and end with `OUT:` or `ERR:`
4. Use PascalCase for components/stores: `CMP:LoginForm`, `STO:AuthStore`
5. Use METHOD/path for APIs: `API:POST/auth/login`, `API:GET/users/{id}`
6. Add comments above chains to describe the feature

**Example - Adding a new feature:**
```
# User registration with email verification
@v1 NED:register => CMP:RegisterForm => STO:Auth => API:POST/auth/register => MDL:user => EVT:sendVerificationEmail => OUT:checkEmail
```

### Hard Rules
1. **Always read ARCHEON.arcon first** before generating any code
2. **You can add chains** - write new chains following the format above
3. **Never invent architecture outside the graph** - add the chain first, then implement
4. **Respect layer boundaries** - CMP cannot directly access MDL
5. **All features must have outcomes** - chains end with OUT: or ERR:
6. **Increment versions** - when modifying a feature, create `@v2`, `@v3`, etc.
7. **Always validate** - run `arc validate` after every code change

### Backend Route Registration (CRITICAL)
When creating API endpoints, you MUST also update `server/src/main.py`:

```python
# Import the new route module
from server.src.api.routes import auth_login

# Register the router
app.include_router(auth_login.router)
```

**Every API glyph requires:**
1. Create route file: `server/src/api/routes/{name}.py`
2. Import in `server/src/main.py`
3. Call `app.include_router(module.router)`
4. Run `arc validate`

### Commands
- `arc intent "description"` - Propose new feature from natural language
- `arc parse "chain"` - Add glyph chain directly  
- `arc gen` - Generate code from knowledge graph
- `arc status` - Show graph statistics
- `arc validate` - **Check architecture integrity (REQUIRED after every change)**
'''
    
    if flags['cursor']:
        cursor_dir = target / ".cursor"
        cursor_dir.mkdir(exist_ok=True)
        
        # Create .cursorrules in project root (where Cursor looks for it)
        cursor_file = target / ".cursorrules"
        cursor_file.write_text(f'''# Archeon Project Rules for Cursor

{archeon_context}

### Cursor-Specific Instructions
When asked to implement a feature:
1. First, read `archeon/ARCHEON.arcon`
2. Check if the feature exists as a chain
3. If NOT, write a new chain to `archeon/ARCHEON.arcon` under `# === AGENT CHAINS ===`
4. Implement the code following the chain structure exactly
5. **Run `arc validate`** to verify the implementation
6. Fix any validation errors before considering the task complete
7. Do not add components, stores, or APIs not represented in the graph
''')
        
        # Create README in .cursor directory
        (cursor_dir / "README.md").write_text('''# Cursor Configuration for Archeon

## Setup Complete ✓

The `.cursorrules` file in your project root tells Cursor to:
1. Always read `archeon/ARCHEON.arcon` before generating code
2. Write new chains to the knowledge graph for new features
3. Respect the glyph-based architecture
4. **Run `arc validate` after every code change**

## The Glyph-Code-Test Workflow

Every feature follows this mandatory workflow:

```
1. ADD GLYPH    → Write chain to ARCHEON.arcon
2. WRITE CODE   → Implement each glyph
3. RUN VALIDATE → arc validate (REQUIRED)
4. RUN TESTS    → npm test / pytest
```

## How It Works

When you ask Cursor to implement something, it will:
- Check the knowledge graph first
- If the feature doesn't exist, ADD A NEW CHAIN first
- Implement code following that chain
- Run `arc validate` to verify architecture
- Fix any validation errors

## Example Prompts

```
"Create a user registration feature"
→ Cursor adds: @v1 NED:register => CMP:RegisterForm => STO:Auth => API:POST/auth/register => MDL:user => OUT:success
→ Implements the code
→ Runs arc validate
→ Fixes any issues

"Read archeon/ARCHEON.arcon and implement the login feature"
"What chains are defined in this project?"
"Add a password reset flow to the knowledge graph"
```

## More Info

- [Cursor Documentation](https://cursor.sh/docs)
- [Archeon README](../README.md)
''')
        created.append(".cursorrules")
        created.append(".cursor/README.md")
    
    if flags['copilot']:
        github_dir = target / ".github"
        github_dir.mkdir(exist_ok=True)
        copilot_file = github_dir / "copilot-instructions.md"
        copilot_file.write_text(f'''# GitHub Copilot Instructions

{archeon_context}

### For Copilot Chat
When implementing features:
1. Always read `archeon/ARCHEON.arcon` first
2. If the feature doesn't exist, write a new chain to `ARCHEON.arcon`
3. Then implement the code following that chain
''')
        
        # Create README for GitHub Copilot setup
        (github_dir / "COPILOT_README.md").write_text('''# GitHub Copilot Configuration for Archeon

## Setup Complete ✓

The `copilot-instructions.md` file tells GitHub Copilot to:
1. Reference `archeon/ARCHEON.arcon` for architecture context
2. Write new chains to the knowledge graph when needed
3. Understand glyph notation (NED, CMP, STO, API, etc.)

## How It Works

GitHub Copilot Chat reads `copilot-instructions.md` as project context.
When you ask Copilot to generate code, it will:
- Check the knowledge graph first  
- If feature doesn't exist, ADD A NEW CHAIN first
- Then implement code following the chain

## VS Code Setup

1. Ensure GitHub Copilot extension is installed
2. The instructions file is auto-detected from `.github/`
3. In Copilot Chat, the context is applied automatically

## Example Prompts

```
@workspace Create a user profile feature
→ Copilot adds chain to ARCHEON.arcon, then implements

@workspace Read ARCHEON.arcon and implement the login feature
@workspace What chains are defined in this project?
@workspace Add a password reset flow to the architecture
```

## More Info

- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [Archeon README](../README.md)
''')
        created.append(".github/copilot-instructions.md")
        created.append(".github/COPILOT_README.md")
    
    if flags['windsurf']:
        windsurf_dir = target / ".windsurf"
        windsurf_dir.mkdir(exist_ok=True)
        
        # Windsurf rules file in project root
        windsurf_file = target / ".windsurfrules"
        windsurf_file.write_text(f'''# Archeon Rules for Windsurf

{archeon_context}

### Windsurf-Specific
Before any code generation task:
1. Read archeon/ARCHEON.arcon
2. If the feature doesn't exist, write a new chain first
3. Then implement code following the chain structure
''')
        
        # Create README
        (windsurf_dir / "README.md").write_text('''# Windsurf Configuration for Archeon

## Setup Complete ✓

The `.windsurfrules` file tells Windsurf (Codeium) to:
1. Read `archeon/ARCHEON.arcon` before generating code
2. Write new chains when features don't exist
3. Follow the glyph-based architecture

## How It Works

Windsurf's Cascade AI reads the rules file for project context.
When generating code, it will:
- Check existing chains in the knowledge graph
- If feature doesn't exist, ADD A NEW CHAIN first
- Then implement following the chain

## Example Prompts

```
"Create a user settings feature"
→ Windsurf adds chain to ARCHEON.arcon, then implements

"Check ARCHEON.arcon and implement the defined chains"
"Add a notifications system to the architecture"
```

## More Info

- [Windsurf Documentation](https://codeium.com/windsurf)
- [Archeon README](../README.md)
''')
        created.append(".windsurfrules")
        created.append(".windsurf/README.md")
    
    if flags['cline']:
        cline_dir = target / ".cline"
        cline_dir.mkdir(exist_ok=True)
        
        cline_file = target / ".clinerules"
        cline_file.write_text(f'''# Archeon Rules for Cline/Claude Dev

{archeon_context}

IMPORTANT: Always read archeon/ARCHEON.arcon before any task.
If a feature doesn't exist, write a new chain to ARCHEON.arcon first, then implement.
''')
        
        # Create README
        (cline_dir / "README.md").write_text('''# Cline / Claude Dev Configuration for Archeon

## Setup Complete ✓

The `.clinerules` file tells Cline (Claude Dev) to:
1. Read `archeon/ARCHEON.arcon` as first action
2. Write new chains when features don't exist
3. Follow glyph-based architecture constraints

## How It Works

Cline reads `.clinerules` for project-specific instructions.
Before any code task, it will:
- Check the knowledge graph for existing chains
- If feature doesn't exist, ADD A NEW CHAIN first
- Then implement following the chain

## Example Prompts

```
"Create a shopping cart feature"
→ Cline adds chain to ARCHEON.arcon, then implements

"Read ARCHEON.arcon and summarize the architecture"
"Add a checkout flow to the knowledge graph"
"Implement CMP:LoginForm as defined in the graph"
```

## More Info

- [Cline Extension](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
- [Archeon README](../README.md)
''')
        created.append(".clinerules")
        created.append(".cline/README.md")
    
    if flags['aider']:
        aider_dir = target / ".aider"
        aider_dir.mkdir(exist_ok=True)
        
        aider_file = target / ".aider.conf.yml"
        aider_file.write_text('''# Aider configuration for Archeon project

# Always include these files in context
read:
  - archeon/ARCHEON.arcon
  - .archeonrc

# Don't auto-commit so user can review
auto-commits: false

# Model instructions
model-settings-yaml: |
  extra_params:
    system: |
      This project uses Archeon glyph notation.
      Always read archeon/ARCHEON.arcon before generating code.
      If a feature doesn't exist, write a new chain to ARCHEON.arcon first.
      Then implement code following that chain.
''')
        
        # Create README
        (aider_dir / "README.md").write_text('''# Aider Configuration for Archeon

## Setup Complete ✓

The `.aider.conf.yml` configures Aider to:
1. Auto-include `archeon/ARCHEON.arcon` in context
2. Include `.archeonrc` for project config
3. Disable auto-commits for review

## How It Works

When you run `aider`, it will:
- Automatically load the knowledge graph
- If feature doesn't exist, ADD A NEW CHAIN first
- Then implement code following the chain
- Wait for your approval before committing

## Usage

```bash
# Start aider in your project
cd your-project
aider

# Aider will auto-load ARCHEON.arcon
# Just ask it to implement features
```

## Example Session

```
> Create a user settings feature

Aider: I'll add this chain to ARCHEON.arcon:
  @v1 NED:settings => CMP:SettingsForm => STO:UserSettings => API:PUT/user/settings => MDL:user => OUT:saved
  
Now implementing each component...
```

## More Info

- [Aider Documentation](https://aider.chat)
- [Archeon README](../README.md)
''')
        created.append(".aider.conf.yml")
        created.append(".aider/README.md")
    
    if flags['vscode']:
        vscode_dir = target / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        settings_file = vscode_dir / "settings.json"
        
        settings = {}
        if settings_file.exists():
            import json
            try:
                settings = json.loads(settings_file.read_text())
            except:
                pass
        
        # Add Archeon-specific settings
        settings["files.associations"] = settings.get("files.associations", {})
        settings["files.associations"]["*.arcon"] = "markdown"
        
        settings["search.include"] = settings.get("search.include", {})
        settings["search.include"]["archeon/**"] = True
        
        settings["github.copilot.chat.codeGeneration.instructions"] = [
            {"text": "Always reference archeon/ARCHEON.arcon for architecture. This project uses Archeon glyph notation. Do not invent architecture outside the knowledge graph."}
        ]
        
        import json
        settings_file.write_text(json.dumps(settings, indent=2))
        
        # Create README
        (vscode_dir / "ARCHEON_README.md").write_text('''# VS Code Configuration for Archeon

## Setup Complete ✓

The `settings.json` has been updated with:
1. File association: `*.arcon` → Markdown syntax highlighting
2. Search include: `archeon/` folder included in searches  
3. Copilot instructions: Reference knowledge graph for code generation

## What This Enables

### Syntax Highlighting
- `.arcon` files get Markdown highlighting
- Makes chains easier to read

### Search Integration  
- `Ctrl/Cmd + Shift + F` includes archeon folder
- Find chains and glyphs across the project

### Copilot Integration
- Copilot Chat references the knowledge graph
- Better architecture-aware suggestions

## Recommended Extensions

For the best Archeon experience, install:

1. **GitHub Copilot** - AI code completion
2. **Markdown Preview** - Preview .arcon files
3. **Error Lens** - Inline error display

## Useful Shortcuts

- `Ctrl/Cmd + P` → type `ARCHEON.arcon` to open knowledge graph
- `Ctrl/Cmd + Shift + F` → search for glyph names
- `Ctrl/Cmd + Shift + E` → file explorer to browse archeon/

## More Info

- [VS Code Documentation](https://code.visualstudio.com/docs)
- [Archeon README](../README.md)
''')
        created.append(".vscode/settings.json")
        created.append(".vscode/ARCHEON_README.md")
    
    # Always create/update the AI provisioning guide
    archeon_dir = target / "archeon"
    if archeon_dir.exists():
        _create_ai_readme(archeon_dir)
        created.append("archeon/AI_README.md")
    
    if created:
        rprint(f"[green]✓[/green] Created AI assistant configurations:")
        for f in created:
            rprint(f"  [cyan]{f}[/cyan]")
        rprint(f"\n[dim]Your IDE AI will now reference the Archeon knowledge graph.[/dim]")
        rprint(f"[dim]Check the README files in each directory for setup details.[/dim]")
    else:
        rprint("[yellow]No configurations generated. Use --cursor, --copilot, etc.[/yellow]")


@app.command()
def parse(
    chain: str = typer.Argument(..., help="Chain string to parse and add"),
    section: str = typer.Option("", "--section", "-s", help="Section to add chain to"),
):
    """Parse and add a chain to the knowledge graph."""
    arcon_path = get_arcon_path()
    
    try:
        # Parse the chain
        ast = parse_chain(chain)
        
        if not ast.nodes:
            rprint("[red]✗[/red] Empty chain - nothing to add")
            raise typer.Exit(1)
        
        # Validate
        result = validate_chain(ast)
        
        if result.errors:
            rprint("[red]✗[/red] Validation errors:")
            for err in result.errors:
                rprint(f"  [red]•[/red] {err.code}: {err.message}")
            raise typer.Exit(1)
        
        if result.warnings:
            for warn in result.warnings:
                rprint(f"  [yellow]![/yellow] {warn.code}: {warn.message}")
        
        # Load graph and add chain
        graph = load_graph(str(arcon_path))
        stored = graph.add_chain(chain, section=section)
        graph.save()
        
        rprint(f"[green]✓[/green] Added chain: [cyan]{stored.ast.raw}[/cyan]")
        rprint(f"  Nodes: {len(ast.nodes)}, Edges: {len(ast.edges)}")
        if ast.version:
            rprint(f"  Version: {ast.version}")
        if ast.framework:
            rprint(f"  Framework: {ast.framework}")
            
    except ParseError as e:
        rprint(f"[red]✗[/red] Parse error: {e.message}")
        raise typer.Exit(1)
    except ValueError as e:
        rprint(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1)


@app.command()
def validate(
    boundaries: bool = typer.Option(False, "--boundaries", "-b", help="Check boundaries only"),
    cycles: bool = typer.Option(False, "--cycles", "-c", help="Check cycles only"),
):
    """Validate the knowledge graph."""
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    graph = load_graph(str(arcon_path))
    validator = GraphValidator(graph)
    
    if boundaries:
        result = validator.validate_boundaries_only()
    elif cycles:
        result = validator.validate_cycles_only()
    else:
        result = validator.validate()
    
    if result.errors:
        rprint(f"[red]✗[/red] Validation failed with {len(result.errors)} error(s):")
        for err in result.errors:
            rprint(f"  [red]•[/red] {err.code}: {err.message}")
            if err.node:
                rprint(f"      at {err.node}")
    else:
        rprint("[green]✓[/green] Validation passed")
    
    if result.warnings:
        rprint(f"\n[yellow]![/yellow] {len(result.warnings)} warning(s):")
        for warn in result.warnings:
            rprint(f"  [yellow]•[/yellow] {warn.code}: {warn.message}")
    
    stats = graph.stats()
    rprint(f"\n  Chains: {stats['total_chains']}, Glyphs: {stats['total_glyphs']}")
    
    if not result.valid:
        raise typer.Exit(1)


@app.command()
def status():
    """Show knowledge graph status."""
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    graph = load_graph(str(arcon_path))
    stats = graph.stats()
    
    # Summary panel
    rprint(Panel.fit(
        f"[bold]Archeon Status[/bold]\n"
        f"File: {arcon_path}\n\n"
        f"Chains: [cyan]{stats['total_chains']}[/cyan]\n"
        f"Glyphs: [cyan]{stats['total_glyphs']}[/cyan]\n"
        f"Deprecated: [yellow]{stats['deprecated']}[/yellow]\n"
        f"Sections: {', '.join(stats['sections']) or 'None'}",
        title="📊 Graph Status"
    ))
    
    # Glyphs table
    if graph.chains:
        table = Table(title="Glyphs")
        table.add_column("Glyph", style="cyan")
        table.add_column("Type")
        table.add_column("Chains")
        
        for glyph in sorted(graph.get_all_glyphs()):
            prefix = glyph.split(':')[0]
            glyph_info = GLYPH_LEGEND.get(prefix, {})
            chains = graph.find_chains_by_glyph(glyph)
            table.add_row(
                glyph,
                glyph_info.get('name', 'Unknown'),
                str(len(chains))
            )
        
        console.print(table)


@app.command()
def versions(
    glyph: str = typer.Argument(..., help="Glyph to show versions for"),
):
    """Show version history for a glyph."""
    arcon_path = get_arcon_path()
    graph = load_graph(str(arcon_path))
    
    versions = graph.get_chains_by_version(glyph)
    
    if not versions:
        rprint(f"[yellow]![/yellow] No chains found for {glyph}")
        raise typer.Exit(1)
    
    table = Table(title=f"Versions of {glyph}")
    table.add_column("Version", style="cyan")
    table.add_column("Chain")
    table.add_column("Status")
    
    for version, stored in sorted(versions.items()):
        status = "[red]deprecated[/red]" if stored.ast.deprecated else "[green]active[/green]"
        table.add_row(version, stored.ast.raw[:60] + "..." if len(stored.ast.raw) > 60 else stored.ast.raw, status)
    
    console.print(table)


@app.command()
def deprecate(
    version: str = typer.Argument(..., help="Version tag (e.g., v1)"),
    glyph: str = typer.Argument(..., help="Root glyph of chain"),
):
    """Mark a chain version as deprecated."""
    arcon_path = get_arcon_path()
    graph = load_graph(str(arcon_path))
    
    if graph.deprecate_chain(version, glyph):
        graph.save()
        rprint(f"[green]✓[/green] Deprecated {version} {glyph}")
    else:
        rprint(f"[red]✗[/red] Chain not found: {version} {glyph}")
        raise typer.Exit(1)


@app.command()
def legend():
    """Show the glyph legend."""
    table = Table(title="Archeon Glyph Legend")
    table.add_column("Prefix", style="bold cyan")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Layer")
    table.add_column("Agent")
    
    for prefix, info in GLYPH_LEGEND.items():
        table.add_row(
            prefix,
            info['name'],
            info['description'],
            info['layer'],
            info.get('agent') or "-"
        )
    
    console.print(table)
    
    # Edge types
    rprint("\n[bold]Edge Types:[/bold]")
    for op, info in EDGE_TYPES.items():
        cycles = "[green]yes[/green]" if info['cycles_allowed'] else "[red]no[/red]"
        rprint(f"  [cyan]{op}[/cyan] {info['name']}: {info['description']} (cycles: {cycles})")


@app.command()
def gen(
    frontend: str = typer.Option("", "--frontend", "-f", help="Frontend framework (default: from .archeonrc)"),
    backend: str = typer.Option("", "--backend", "-b", help="Backend framework (default: from .archeonrc)"),
    db: str = typer.Option("", "--db", "-d", help="Database type (default: from .archeonrc)"),
    output: str = typer.Option(".", "--output", "-o", help="Output directory (project root)"),
    force: bool = typer.Option(False, "--force", help="Force regeneration of all glyphs"),
):
    """Generate code for all unresolved glyphs (respects client/server structure)."""
    from archeon.orchestrator.SPW_spawner import AgentSpawner, ProjectConfig
    
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    # Load project config
    config = ProjectConfig.load(Path(output))
    
    # Override config with CLI options if provided
    if frontend:
        config.frontend = frontend
    if backend:
        config.backend = backend
    if db:
        config.db = db
    
    graph = load_graph(str(arcon_path))
    unresolved = graph.get_unresolved_glyphs()
    
    if not unresolved and not force:
        rprint("[green]✓[/green] All glyphs already resolved - nothing to generate")
        return
    
    rprint(f"[cyan]Generating code for {len(unresolved)} glyph(s)...[/cyan]")
    rprint(f"  Frontend: {config.frontend}, Backend: {config.backend}, DB: {config.db}")
    
    if config.monorepo:
        rprint(f"  [bold]Monorepo mode:[/bold]")
        rprint(f"    Client: {config.client_dir}")
        rprint(f"    Server: {config.server_dir}")
    else:
        rprint(f"  Output: {config.output_dir}")
    
    # Create spawner with config
    spawner = AgentSpawner(
        output_dir=output, 
        framework=config.frontend,
        backend=config.backend,
        db=config.db,
        config=config
    )
    
    # Process all unresolved glyphs
    batch = spawner.spawn_all(graph, force=force)
    
    # Display results
    table = Table(title="Generation Results")
    table.add_column("Glyph", style="cyan")
    table.add_column("Target", style="magenta")
    table.add_column("File", style="green")
    table.add_column("Status")
    
    for result in batch.results:
        status_style = {
            "success": "[green]✓[/green]",
            "skipped": "[yellow]○[/yellow]",
            "error": "[red]✗[/red]",
        }.get(result.status, result.status)
        
        target = result.target if result.target else "-"
        file_display = result.file_path or "-"
        if result.error:
            file_display = f"[red]{result.error}[/red]"
        
        table.add_row(result.glyph, target, file_display, status_style)
    
    console.print(table)
    
    rprint(f"\n[green]✓ Generated:[/green] {batch.success_count}")
    if config.monorepo and batch.success_count > 0:
        rprint(f"   [cyan]Client:[/cyan] {batch.client_count}  [magenta]Server:[/magenta] {batch.server_count}")
    rprint(f"[yellow]○ Skipped:[/yellow] {batch.skipped_count}")
    if batch.error_count:
        rprint(f"[red]✗ Errors:[/red] {batch.error_count}")
        raise typer.Exit(1)


@app.command()
def test(
    generate: bool = typer.Option(False, "--generate", "-g", help="Generate tests first"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    errors_only: bool = typer.Option(False, "--errors-only", help="Run only error path tests"),
    chain: Optional[str] = typer.Option(None, "--chain", "-c", help="Test specific chain only"),
):
    """Run generated tests."""
    from archeon.orchestrator.TST_runner import TestGenerator, TestRunner
    
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    test_dir = "tests/generated"
    
    # Generate tests if requested
    if generate:
        rprint("[cyan]Generating tests...[/cyan]")
        graph = load_graph(str(arcon_path))
        generator = TestGenerator(output_dir=test_dir)
        tests = generator.generate_from_graph(graph)
        written = generator.write_tests(tests)
        rprint(f"[green]✓[/green] Generated {len(tests)} test(s) in {len(written)} file(s)")
    
    # Run tests
    runner = TestRunner(test_dir=test_dir)
    
    if chain:
        rprint(f"[cyan]Running tests for {chain}...[/cyan]")
        result = runner.run_chain(chain, verbose=verbose)
    elif errors_only:
        rprint("[cyan]Running error path tests...[/cyan]")
        result = runner.run_errors_only(verbose=verbose)
    else:
        rprint("[cyan]Running all tests...[/cyan]")
        result = runner.run_all(verbose=verbose)
    
    # Display results
    if result.success:
        rprint(f"\n[green]✓ All tests passed[/green]")
        rprint(f"  Passed: {result.passed}, Total: {result.total}")
    else:
        rprint(f"\n[red]✗ Tests failed[/red]")
        rprint(f"  Passed: {result.passed}, Failed: {result.failed}, Errors: {result.errors}")
        raise typer.Exit(1)


@app.command()
def graph(
    format: str = typer.Option("dot", "--format", "-f", help="Output format: dot, json, png, svg, mermaid"),
    output: str = typer.Option("graph", "--output", "-o", help="Output filename (without extension)"),
):
    """Export knowledge graph visualization."""
    from archeon.orchestrator.GRF_exporter import export_dot, export_json, export_png, export_svg, export_mermaid
    
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    graph_data = load_graph(str(arcon_path))
    
    if format == "dot":
        output_path = f"{output}.dot"
        export_dot(graph_data, output_path)
        rprint(f"[green]✓[/green] Exported DOT to {output_path}")
        
    elif format == "json":
        output_path = f"{output}.json"
        export_json(graph_data, output_path)
        rprint(f"[green]✓[/green] Exported JSON to {output_path}")
        
    elif format == "png":
        output_path = f"{output}.png"
        result = export_png(graph_data, output_path)
        if result.success:
            rprint(f"[green]✓[/green] Exported PNG to {output_path}")
            rprint(f"  Nodes: {result.node_count}, Edges: {result.edge_count}")
        else:
            rprint(f"[red]✗[/red] {result.error}")
            raise typer.Exit(1)
            
    elif format == "svg":
        output_path = f"{output}.svg"
        result = export_svg(graph_data, output_path)
        if result.success:
            rprint(f"[green]✓[/green] Exported SVG to {output_path}")
        else:
            rprint(f"[red]✗[/red] {result.error}")
            raise typer.Exit(1)
            
    elif format == "mermaid":
        output_path = f"{output}.md"
        content = export_mermaid(graph_data, output_path)
        rprint(f"[green]✓[/green] Exported Mermaid to {output_path}")
        
    else:
        rprint(f"[red]✗[/red] Unknown format: {format}")
        rprint("  Supported: dot, json, png, svg, mermaid")
        raise typer.Exit(1)


@app.command()
def audit():
    """Check for drift between graph and generated files."""
    from archeon.utils.tracer import find_drift
    
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    graph = load_graph(str(arcon_path))
    
    rprint("[cyan]Scanning for drift...[/cyan]")
    report = find_drift(graph, source_dir=".")
    
    if not report.has_drift:
        rprint("[green]✓[/green] No drift detected")
        rprint(f"  Traced files: {len(report.traced_files)}")
        return
    
    # Display drift items
    table = Table(title="Drift Report")
    table.add_column("Type", style="bold")
    table.add_column("Glyph", style="cyan")
    table.add_column("Path")
    table.add_column("Message")
    
    for item in report.items:
        type_style = {
            'error': '[red]',
            'warning': '[yellow]',
            'info': '[blue]',
        }.get(item.severity, '')
        type_end = '[/]' if type_style else ''
        
        table.add_row(
            f"{type_style}{item.type}{type_end}",
            item.glyph or "-",
            item.file_path or "-",
            item.message
        )
    
    console.print(table)
    
    rprint(f"\n[red]✗ Drift detected:[/red] {len(report.items)} issue(s)")
    rprint(f"  Errors: {report.error_count}, Warnings: {report.warning_count}")
    
    if report.error_count > 0:
        raise typer.Exit(1)


@app.command("i")
@app.command("intent")
def intent(
    text: str = typer.Argument(..., help="Natural language description"),
    auto_errors: bool = typer.Option(False, "--auto-errors", help="Auto-suggest error paths"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Parse from markdown file instead"),
):
    """Parse natural language into proposed chains."""
    from archeon.orchestrator.INT_intent import parse_intent, parse_markdown, suggest_errors, extend_chain
    
    if file:
        rprint(f"[cyan]Parsing markdown file: {file}[/cyan]")
        result = parse_markdown(file)
    else:
        rprint(f"[cyan]Parsing intent...[/cyan]")
        result = parse_intent(text)
    
    if not result.proposals:
        rprint("[yellow]![/yellow] Could not extract any chains from input")
        if result.warnings:
            for warn in result.warnings:
                rprint(f"  [yellow]•[/yellow] {warn}")
        return
    
    arcon_path = get_arcon_path()
    
    # Check for similar existing chains
    similar_chains = []
    if arcon_path.exists():
        graph = load_graph(str(arcon_path))
        for proposal in result.proposals:
            similar = graph.find_similar_chains(proposal.chain, threshold=0.3)
            if similar:
                similar_chains.extend(similar)
    
    # If similar chains found, ask user what to do
    if similar_chains:
        rprint("\n[yellow]Found similar existing chains:[/yellow]")
        unique_chains = []
        seen_raws = set()
        for stored, score, shared in similar_chains:
            if stored.ast.raw not in seen_raws:
                seen_raws.add(stored.ast.raw)
                unique_chains.append((stored, score, shared))
        
        for i, (stored, score, shared) in enumerate(unique_chains[:5], 1):  # Show top 5
            pct = int(score * 100)
            rprint(f"  [dim]{i}.[/dim] [cyan]{stored.ast.raw}[/cyan]")
            rprint(f"     [dim]Similarity: {pct}% | Shared: {', '.join(shared[:3])}{'...' if len(shared) > 3 else ''}[/dim]")
        
        rprint("\n[dim]Options: Enter number to extend that chain, or press Enter to create new[/dim]")
        choice = Prompt.ask("Extend existing chain?", default="")
        
        if choice.isdigit() and 1 <= int(choice) <= len(unique_chains):
            # User wants to extend an existing chain
            selected = unique_chains[int(choice) - 1][0]
            rprint(f"\n[cyan]Extending: {selected.ast.raw}[/cyan]")
            rprint("[dim]Describe what to add (natural language):[/dim]\n")
            
            modification = Prompt.ask("Add")
            extend_result = extend_chain(selected.ast.raw, modification)
            
            if extend_result.proposals:
                # Replace result with the extended proposal
                result.proposals = extend_result.proposals
            else:
                rprint("[yellow]![/yellow] Could not extend chain. Proceeding with original proposal.")
                if extend_result.warnings:
                    for warn in extend_result.warnings:
                        rprint(f"  [yellow]•[/yellow] {warn}")
    
    def process_proposal(proposal, proposal_num):
        """Process a single proposal with approval flow."""
        confidence_style = {
            'high': '[green]HIGH[/green]',
            'medium': '[yellow]MEDIUM[/yellow]',
            'low': '[red]LOW[/red]',
        }.get(proposal.confidence.value, proposal.confidence.value)
        
        rprint(Panel.fit(
            f"[bold cyan]{proposal.chain}[/bold cyan]\n\n"
            f"Confidence: {confidence_style}\n"
            f"Reasoning:\n" + "\n".join(f"  • {r}" for r in proposal.reasoning),
            title=f"Proposal {proposal_num}"
        ))
        
        # Show suggested errors
        if auto_errors or proposal.suggested_errors:
            errors = proposal.suggested_errors or suggest_errors(proposal.chain)
            if errors:
                rprint("\n[yellow]Suggested error paths:[/yellow]")
                for err in errors:
                    rprint(f"  [dim]→[/dim] {err}")
        
        # Prompt for action
        if not arcon_path.exists():
            return
            
        rprint("")
        rprint("[dim]Actions: [a]pprove  [e]dit (natural language)  [r]eject  [s]uggest errors[/dim]")
        action = Prompt.ask(
            "Action",
            choices=["a", "e", "r", "s"],
            default="r",
        )
        
        if action == "a":  # Approve
            graph = load_graph(str(arcon_path))
            try:
                stored = graph.add_chain(proposal.chain)
                graph.save()
                rprint(f"[green]✓[/green] Added chain to graph")
            except Exception as e:
                rprint(f"[red]✗[/red] Failed to add: {e}")
                
        elif action == "e":  # Edit with natural language
            rprint("\n[dim]Describe what to add or change (natural language):[/dim]")
            rprint("[dim]  Examples: 'add a store', 'add API endpoint', 'redirect to dashboard'[/dim]")
            rprint("[dim]  Or type full glyph notation to replace the chain[/dim]\n")
            
            user_input = Prompt.ask("Edit")
            
            # Check if input looks like glyph notation or natural language
            is_glyph_notation = ('=>' in user_input or 
                                 user_input.startswith(('NED:', 'CMP:', 'STO:', 'API:', 'TSK:', 'MDL:', 'FNC:', 'EVT:', 'OUT:', 'ERR:')))
            
            if is_glyph_notation:
                # Treat as direct glyph notation
                try:
                    graph = load_graph(str(arcon_path))
                    stored = graph.add_chain(user_input)
                    graph.save()
                    rprint(f"[green]✓[/green] Added edited chain to graph")
                except Exception as e:
                    rprint(f"[red]✗[/red] Failed to add: {e}")
            else:
                # Treat as natural language modification
                rprint(f"[cyan]Extending chain with: '{user_input}'...[/cyan]")
                extend_result = extend_chain(proposal.chain, user_input)
                
                if extend_result.warnings:
                    for warn in extend_result.warnings:
                        rprint(f"[yellow]![/yellow] {warn}")
                
                if extend_result.proposals:
                    # Recursively process the extended proposal
                    process_proposal(extend_result.proposals[0], proposal_num)
                else:
                    rprint("[yellow]![/yellow] Could not extend chain. Try being more specific.")
                    
        elif action == "s":  # Suggest errors
            errors = suggest_errors(proposal.chain)
            for err in errors:
                error_chain = f"{proposal.chain} -> {err} => OUT:error"
                rprint(f"  [cyan]{error_chain}[/cyan]")
                
        else:  # Reject
            rprint("[dim]Rejected[/dim]")
    
    for i, proposal in enumerate(result.proposals, 1):
        process_proposal(proposal, i)


@app.command("diff")
def diff_versions(
    v1: str = typer.Argument(..., help="First version (e.g., v1)"),
    v2: str = typer.Argument(..., help="Second version (e.g., v2)"),
    glyph: str = typer.Argument(..., help="Root glyph to diff"),
):
    """Diff two versions of a chain."""
    arcon_path = get_arcon_path()
    graph = load_graph(str(arcon_path))
    
    versions_dict = graph.get_chains_by_version(glyph)
    
    # Normalize version format
    v1_key = v1 if v1.startswith('v') else f'v{v1}'
    v2_key = v2 if v2.startswith('v') else f'v{v2}'
    
    if v1_key not in versions_dict:
        rprint(f"[red]✗[/red] Version {v1} not found for {glyph}")
        raise typer.Exit(1)
    
    if v2_key not in versions_dict:
        rprint(f"[red]✗[/red] Version {v2} not found for {glyph}")
        raise typer.Exit(1)
    
    chain1 = versions_dict[v1_key].ast
    chain2 = versions_dict[v2_key].ast
    
    rprint(Panel.fit(
        f"[red]- {v1_key}: {chain1.raw}[/red]\n"
        f"[green]+ {v2_key}: {chain2.raw}[/green]",
        title=f"Diff: {glyph}"
    ))
    
    # Compare nodes
    nodes1 = {n.qualified_name for n in chain1.nodes}
    nodes2 = {n.qualified_name for n in chain2.nodes}
    
    added = nodes2 - nodes1
    removed = nodes1 - nodes2
    
    if added:
        rprint("\n[green]Added nodes:[/green]")
        for n in sorted(added):
            rprint(f"  [green]+[/green] {n}")
    
    if removed:
        rprint("\n[red]Removed nodes:[/red]")
        for n in sorted(removed):
            rprint(f"  [red]-[/red] {n}")
    
    if not added and not removed:
        rprint("\n[dim]No structural changes (same nodes)[/dim]")


@app.command("import")
def import_doc(
    source: str = typer.Argument(..., help="File path or URL to import"),
):
    """Import chains from markdown or external source."""
    from archeon.orchestrator.INT_intent import parse_markdown
    
    if source.startswith('http://') or source.startswith('https://'):
        rprint("[yellow]![/yellow] URL import not yet implemented")
        rprint("  Supported: Linear, JIRA, GitHub (coming soon)")
        raise typer.Exit(1)
    
    path = Path(source)
    if not path.exists():
        rprint(f"[red]✗[/red] File not found: {source}")
        raise typer.Exit(1)
    
    rprint(f"[cyan]Importing from {source}...[/cyan]")
    result = parse_markdown(str(path))
    
    if not result.proposals:
        rprint("[yellow]![/yellow] No chains found in document")
        return
    
    rprint(f"[green]✓[/green] Found {len(result.proposals)} chain(s)")
    
    arcon_path = get_arcon_path()
    
    for proposal in result.proposals:
        rprint(f"\n  [cyan]{proposal.chain}[/cyan]")
        
        if arcon_path.exists() and Confirm.ask("  Add to graph?", default=False):
            try:
                graph = load_graph(str(arcon_path))
                graph.add_chain(proposal.chain)
                graph.save()
                rprint("  [green]✓[/green] Added")
            except Exception as e:
                rprint(f"  [red]✗[/red] {e}")


@app.command()
def run(
    glyph: Optional[str] = typer.Argument(None, help="Component or chain to execute"),
    mode: str = typer.Option("sandbox", "--mode", "-m", help="Execution mode: sandbox or live"),
    input_json: Optional[str] = typer.Option(None, "--input", "-i", help="Input data as JSON"),
    chain: Optional[str] = typer.Option(None, "--chain", "-c", help="Execute a raw chain string"),
    all_chains: bool = typer.Option(False, "--all", "-a", help="Execute all chains"),
):
    """Execute chains in headless mode (sandbox or live)."""
    import json as json_module
    from archeon.orchestrator.HED_executor import (
        HeadlessExecutor,
        ExecutionMode,
        run_sandbox,
    )
    
    arcon_path = get_arcon_path()
    
    # Parse input data
    input_data = {}
    if input_json:
        try:
            input_data = json_module.loads(input_json)
        except json_module.JSONDecodeError as e:
            rprint(f"[red]✗[/red] Invalid JSON input: {e}")
            raise typer.Exit(1)
    
    exec_mode = ExecutionMode.LIVE if mode == "live" else ExecutionMode.SANDBOX
    
    # Execute raw chain string
    if chain:
        try:
            ast = parse_chain(chain)
        except ParseError as e:
            rprint(f"[red]✗[/red] Invalid chain: {e}")
            raise typer.Exit(1)
        
        executor = HeadlessExecutor()
        result = executor.execute(ast, exec_mode, input_data, strict=False)
        _display_execution_result(result, console)
        return
    
    # Need arcon for other modes
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    graph = load_graph(str(arcon_path))
    executor = HeadlessExecutor(graph)
    
    if all_chains:
        # Execute all chains
        rprint(f"[cyan]Executing all {len(graph.chains)} chains in {mode} mode...[/cyan]\n")
        
        for i, stored in enumerate(graph.chains):
            rprint(f"[dim]Chain {i+1}/{len(graph.chains)}:[/dim] {stored.ast.raw[:60]}...")
            result = executor.execute(stored.ast, exec_mode, input_data, strict=False)
            
            if result.success:
                rprint(f"  [green]✓[/green] Success ({len(result.trace.steps)} steps)")
            else:
                rprint(f"  [red]✗[/red] Failed: {result.error}")
        
        # Show metrics summary
        metrics = executor.get_metrics()
        total_exec = sum(m.get('executions', 0) for m in metrics.values())
        total_success = sum(m.get('successes', 0) for m in metrics.values())
        rprint(f"\n[bold]Summary:[/bold] {total_success}/{total_exec} chains succeeded")
        return
    
    if glyph:
        # Execute chains containing this glyph
        results = executor.execute_by_glyph(glyph, exec_mode, input_data)
        
        if not results:
            rprint(f"[yellow]![/yellow] No chains found containing {glyph}")
            raise typer.Exit(1)
        
        rprint(f"[cyan]Found {len(results)} chain(s) containing {glyph}[/cyan]\n")
        for result in results:
            _display_execution_result(result, console)
        return
    
    rprint("[yellow]![/yellow] Specify a glyph, --chain, or --all")
    rprint("  Examples:")
    rprint("    [cyan]archeon run CMP:LoginForm[/cyan]")
    rprint("    [cyan]archeon run --chain \"NED:test => OUT:done\"[/cyan]")
    rprint("    [cyan]archeon run --all --mode sandbox[/cyan]")


def _display_execution_result(result, console):
    """Display execution result with formatting."""
    from rich.json import JSON
    
    trace = result.trace
    status_color = "green" if result.success else "red"
    status_icon = "✓" if result.success else "✗"
    
    rprint(f"[{status_color}]{status_icon}[/{status_color}] {trace.chain_id[:60]}...")
    rprint(f"  Mode: [bold]{trace.mode.value}[/bold] | Status: [{status_color}]{trace.status}[/{status_color}]")
    rprint(f"  Steps: {len(trace.steps)}")
    
    # Show step summary
    for step in trace.steps:
        step_icon = {
            'success': '[green]✓[/green]',
            'mocked': '[blue]◎[/blue]',
            'failed': '[red]✗[/red]',
            'skipped': '[dim]○[/dim]',
        }.get(step.status.value, '[dim]?[/dim]')
        
        duration = f" ({step.duration_ms:.1f}ms)" if step.duration_ms else ""
        rprint(f"    {step_icon} {step.glyph}{duration}")
    
    if result.error:
        rprint(f"  [red]Error:[/red] {result.error}")
    
    if result.output:
        rprint(f"  [dim]Output:[/dim]")
        console.print(JSON.from_data(result.output))
    
    rprint("")


@app.command()
def serve(
    host: str = typer.Option("localhost", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8765, "--port", "-p", help="Port to listen on"),
):
    """Start the headless HTTP server for chain execution."""
    from archeon.server.headless_server import serve as start_server
    
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    start_server(str(arcon_path), host, port)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Show version"),
):
    """Archeon - Glyph-based architecture notation for AI-orchestrated development."""
    if version:
        rprint("[bold]Archeon[/bold] version 0.1.0")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        rprint(ctx.get_help())


if __name__ == "__main__":
    app()
