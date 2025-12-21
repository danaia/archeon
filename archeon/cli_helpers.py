"""
CLI helper functions for project initialization and setup.

This module contains all the utility functions used by the main CLI
to set up new Archeon projects, copy templates, and generate documentation.
"""

import shutil
from pathlib import Path
from rich import print as rprint

from archeon.cli_templates import ORCHESTRATOR_README_TEMPLATE, AI_README_TEMPLATE


def get_package_templates_dir() -> Path:
    """Get the path to the templates directory in the installed archeon package."""
    return Path(__file__).parent / "templates"


def copy_templates(archeon_dir: Path, frontend: str, backend: str):
    """Copy reference templates to the project's archeon/templates folder."""
    pkg_templates = get_package_templates_dir()
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


def create_orchestrator_readme(archeon_dir: Path):
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


def create_ai_readme(archeon_dir: Path):
    """Create the AI provisioning guide README using template constant."""
    ai_readme = archeon_dir / "AI_README.md"
    if ai_readme.exists():
        return
    
    ai_readme.write_text(AI_README_TEMPLATE)


def create_base_directories(archeon_dir: Path):
    """Create base archeon directory structure."""
    base_dirs = [
        archeon_dir,
        archeon_dir / "orchestrator",
        archeon_dir / "agents",
        archeon_dir / "templates" / "CMP",
        archeon_dir / "templates" / "STO",
        archeon_dir / "templates" / "API",
        archeon_dir / "templates" / "MDL",
        archeon_dir / "templates" / "EVT",
        archeon_dir / "templates" / "FNC",
    ]
    
    for d in base_dirs:
        d.mkdir(parents=True, exist_ok=True)


def create_client_structure(client_dir: Path, frontend: str):
    """Create client directory structure."""
    dirs_to_create = [
        client_dir / "src" / "components",
        client_dir / "src" / "stores",
        client_dir / "src" / "views",
        client_dir / "src" / "lib",
        client_dir / "src" / "hooks",
        client_dir / "src" / "types",
        client_dir / "public",
    ]
    
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)
    
    # Create client files
    if frontend in ("vue", "vue3"):
        # Vue main.js
        (client_dir / "src" / "main.js").write_text('''import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.mount('#app')
''')
        
        # Vue App.vue
        (client_dir / "src" / "App.vue").write_text('''<template>
  <div id="app">
    <h1>Archeon Vue 3 App</h1>
    <p>Add components to /src/components/</p>
  </div>
</template>

<script setup>
// Add imports here
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
''')
    else:
        # React main.tsx
        (client_dir / "src" / "main.tsx").write_text('''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
''')
        
        # React App.tsx
        (client_dir / "src" / "App.tsx").write_text('''import React from 'react'

function App() {
  return (
    <div className="App">
      <h1>Archeon React App</h1>
      <p>Add components to /src/components/</p>
    </div>
  )
}

export default App
''')


def create_server_structure(server_dir: Path):
    """Create server directory structure."""
    dirs_to_create = [
        server_dir / "src" / "api" / "routes",
        server_dir / "src" / "models",
        server_dir / "src" / "db",
        server_dir / "src" / "events",
        server_dir / "src" / "lib",
        server_dir / "src" / "services",
        server_dir / "tests",
    ]
    
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)


def create_server_files(server_dir: Path, backend: str):
    """Create initial server files."""
    # .env file
    (server_dir / ".env").write_text(
        "# Database Configuration\n"
        "MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<dbname>?retryWrites=true&w=majority\n"
        "DB_NAME=myapp\n"
        "\n"
        "# API Configuration\n"
        "API_PORT=8000\n"
        "JWT_SECRET=change-this-secret-key\n"
    )
    
    # Copy database module
    pkg_templates = get_package_templates_dir()
    db_src = pkg_templates / "_server" / "db.py"
    db_dst = server_dir / "src" / "db" / "database.py"
    
    if db_src.exists() and not db_dst.exists():
        shutil.copy2(db_src, db_dst)
    
    # FastAPI main.py
    if backend == "fastapi":
        (server_dir / "src" / "main.py").write_text(
            '''"""
FastAPI Backend Server
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.database import close_connection

# Import routes here as you create them
# Example:
# from src.api.routes import auth_login


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager to handle startup and shutdown events."""
    # Startup
    yield
    # Shutdown
    await close_connection()


app = FastAPI(
    title="API Server",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Register route modules here
# Example:
# app.include_router(auth_login.router)
'''
        )
        
        # requirements.txt
        (server_dir / "requirements.txt").write_text(
            "fastapi>=0.104.0\n"
            "uvicorn[standard]>=0.24.0\n"
            "motor>=3.3.0\n"
            "pydantic>=2.0.0\n"
            "python-dotenv>=1.0.0\n"
            "python-jose[cryptography]>=3.3.0\n"
            "passlib[bcrypt]>=1.7.4\n"
            "python-multipart>=0.0.6\n"
        )


def create_arcon_file(archeon_dir: Path, project_name: str):
    """Create initial ARCHEON.arcon file."""
    arcon_path = archeon_dir / "ARCHEON.arcon"
    if not arcon_path.exists():
        arcon_path.write_text(
            "# Archeon Knowledge Graph\n"
            "# Version: 2.0\n"
            f"# Project: {project_name}\n"
            "\n"
            "# === ORCHESTRATOR LAYER ===\n"
            "ORC:main :: PRS:glyph :: VAL:chain :: SPW:agent :: TST:e2e\n"
            "GRF:domain :: ORC:main\n"
            "\n"
            "# === AGENT CHAINS ===\n"
            "# Add chains using: archeon parse \"<chain>\"\n"
        )


def create_archeonrc_file(target: Path, monorepo: bool, frontend: str, backend: str):
    """Create .archeonrc configuration file."""
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
                f"frontend: {frontend}\n"
                f"backend: {backend}\n"
                "db: mongo\n"
                "output_dir: ./src\n"
            )


def create_gitignore(target: Path):
    """Create .gitignore file."""
    gitignore_path = target / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text('''# Dependencies
node_modules/
.pnp
.pnp.js

# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
ENV/
env/
*.egg-info/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Build outputs
dist/
build/
*.log

# Testing
coverage/
.coverage
htmlcov/

# Archeon generated
tests/generated/
''')
