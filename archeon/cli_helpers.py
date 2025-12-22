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
        "react": {"CMP": "react.tsx", "STO": "zustand.js"},
        "vue": {"CMP": "vue.vue", "STO": "pinia.js"},
        "vue3": {"CMP": "vue3.vue", "STO": "pinia.js"},
    }
    
    backend_map = {
        "fastapi": {"API": "fastapi.py", "MDL": "mongo.py", "EVT": "pubsub.py", "FNC": "python.py"},
        "express": {"API": "fastapi.py", "MDL": "mongo.py", "EVT": "pubsub.py", "FNC": "python.py"},  # TODO: add express templates
    }
    
    # Theme store map (per framework)
    theme_store_map = {
        "react": "theme-zustand.js",
        "vue": "theme-pinia.js",
        "vue3": "theme-pinia.js",
    }
    
    # Copy frontend templates
    for glyph, filename in frontend_map.get(frontend, frontend_map["react"]).items():
        src = pkg_templates / glyph / filename
        dst = target_templates / glyph / filename
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
    
    # Copy theme store template
    theme_store_file = theme_store_map.get(frontend, "theme-zustand.js")
    src = pkg_templates / "STO" / theme_store_file
    dst = target_templates / "STO" / theme_store_file
    if src.exists() and not dst.exists():
        shutil.copy2(src, dst)
    
    # Copy backend templates  
    for glyph, filename in backend_map.get(backend, backend_map["fastapi"]).items():
        src = pkg_templates / glyph / filename
        dst = target_templates / glyph / filename
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
    
    # Copy Tailwind theming config files
    config_dir = pkg_templates / "_config"
    target_config_dir = target_templates / "_config"
    if config_dir.exists():
        target_config_dir.mkdir(parents=True, exist_ok=True)
        for config_file in config_dir.iterdir():
            if config_file.is_file():
                dst = target_config_dir / config_file.name
                if not dst.exists():
                    shutil.copy2(config_file, dst)


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
- `STO/` - Store templates (zustand.js, pinia.js)  
- `API/` - API route templates (fastapi.py)
- `MDL/` - Model templates (mongo.py)
- `EVT/` - Event templates (pubsub.py)
- `FNC/` - Function templates (python.py)

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
        client_dir / "src" / "types",        client_dir / "src" / "views",
        client_dir / "src" / "router",        client_dir / "public",
    ]
    
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)
    
    # Create package.json based on frontend framework
    package_json = client_dir / "package.json"
    if not package_json.exists():
        if frontend in ("vue", "vue3"):
            # Vue 3 package.json
            package_json.write_text('''{
  "name": "client",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:run": "vitest run"
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
    "tailwindcss": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "jsdom": "^24.0.0"
  }
}
''')
        else:
            # React package.json
            package_json.write_text('''{
  "name": "client",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:run": "vitest run"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "jsdom": "^24.0.0"
  }
}
''')
    
    # Create vite.config for the appropriate framework
    vite_config = client_dir / "vite.config.js"
    if not vite_config.exists():
        if frontend in ("vue", "vue3"):
            vite_config.write_text('''import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
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
})
''')
        else:
            vite_config.write_text('''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
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
})
''')
    
    # Create index.html
    index_html = client_dir / "index.html"
    if not index_html.exists():
        if frontend in ("vue", "vue3"):
            index_html.write_text('''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" type="image/svg+xml" href="/vite.svg">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archeon Vue App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
''')
        else:
            index_html.write_text('''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <link rel="icon" type="image/svg+xml" href="/vite.svg">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Archeon React App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
''')
    
    # Create client files
    if frontend in ("vue", "vue3"):
        # Vue style.css with Tailwind theme
        (client_dir / "src" / "style.css").write_text('''@import "tailwindcss";

/* Archeon Theme Variables */
:root {
  /* Primary palette */
  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-200: #bfdbfe;
  --color-primary-300: #93c5fd;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  --color-primary-800: #1e40af;
  --color-primary-900: #1e3a8a;
  --color-primary-950: #172554;

  /* Surface colors (light mode) */
  --color-surface: #ffffff;
  --color-surface-raised: #f9fafb;
  --color-content: #111827;
  --color-content-secondary: #4b5563;
  --color-content-muted: #9ca3af;
  --color-border: #e5e7eb;
}

.dark {
  --color-surface: #0f172a;
  --color-surface-raised: #1e293b;
  --color-content: #f1f5f9;
  --color-content-secondary: #cbd5e1;
  --color-content-muted: #64748b;
  --color-border: #334155;
}

/* Theme-aware component classes */
@layer components {
  .btn-primary {
    @apply inline-flex items-center justify-center px-4 py-2 font-medium text-sm rounded-md
           bg-[var(--color-primary-500)] text-white
           hover:bg-[var(--color-primary-600)]
           focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)] focus:ring-offset-2
           disabled:opacity-50 disabled:cursor-not-allowed;
  }

  .btn-outline {
    @apply inline-flex items-center justify-center px-4 py-2 font-medium text-sm rounded-md
           border border-[var(--color-border)] bg-transparent text-[var(--color-content)]
           hover:bg-[var(--color-surface-raised)]
           focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)];
  }

  .card {
    @apply bg-[var(--color-surface)] rounded-lg shadow-md border border-[var(--color-border)];
  }

  .input {
    @apply block w-full px-3 py-2 text-sm rounded-md
           bg-[var(--color-surface)] text-[var(--color-content)] border border-[var(--color-border)]
           placeholder:text-[var(--color-content-muted)]
           focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)] focus:border-transparent;
  }
}
''')
        
        # Vue main.js with router
        (client_dir / "src" / "main.js").write_text('''import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')

// Initialize theme from localStorage or system preference
const savedTheme = localStorage.getItem('archeon-theme')
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
  document.documentElement.classList.add('dark')
}
''')
        
        # Vue App.vue - router only
        (client_dir / "src" / "App.vue").write_text('''<!-- @archeon:file -->
<!-- @glyph CMP:App -->
<!-- @intent Root application component with router outlet -->
<!-- @chain @v1 NED:app => CMP:App => OUT:render -->
<template>
  <RouterView />
</template>

<script setup>
// @archeon:section imports
import { RouterView } from 'vue-router'
// @archeon:endsection
</script>
''')
        
        # Create router directory and index.js
        router_dir = client_dir / "src" / "router"
        router_dir.mkdir(parents=True, exist_ok=True)
        
        (router_dir / "index.js").write_text('''// @archeon:file
// @glyph FNC:router
// @intent Application routing configuration
// @chain @v1 NED:navigation => FNC:router => CMP:* => OUT:render

// @archeon:section imports
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
// @archeon:endsection

// @archeon:section implementation
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    // Add more routes here as needed
    // {
    //   path: '/about',
    //   name: 'about',
    //   component: () => import('../views/AboutView.vue')
    // }
  ]
})

export default router
// @archeon:endsection
''')
        
        # Create views directory and HomeView.vue
        views_dir = client_dir / "src" / "views"
        views_dir.mkdir(parents=True, exist_ok=True)
        
        (views_dir / "HomeView.vue").write_text('''<!-- @archeon:file -->
<!-- @glyph CMP:HomeView -->
<!-- @intent Home page with theme toggle -->
<!-- @chain @v1 NED:home => CMP:HomeView => OUT:render -->
<template>
  <!-- @archeon:section render -->
  <div class="min-h-screen bg-[var(--color-surface)] text-[var(--color-content)] transition-colors">
    <header class="p-4 flex justify-between items-center border-b border-[var(--color-border)]">
      <h1 class="text-xl font-bold">Archeon Vue 3</h1>
      <button @click="toggleTheme" class="btn-outline p-2 rounded-md">
        <span v-if="isDark">☀️</span>
        <span v-else>🌙</span>
      </button>
    </header>
    <main class="flex items-center justify-center" style="min-height: calc(100vh - 73px)">
      <div class="text-center">
        <h2 class="text-4xl font-bold mb-4">Welcome</h2>
        <p class="text-[var(--color-content-secondary)]">Add components to /src/components/</p>
        <p class="text-[var(--color-content-muted)] mt-2">Add views to /src/views/</p>
        <div class="mt-8 flex gap-4 justify-center">
          <button class="btn-primary">Primary</button>
          <button class="btn-outline">Outline</button>
        </div>
      </div>
    </main>
  </div>
  <!-- @archeon:endsection -->
</template>

<script setup>
// @archeon:section imports
import { ref, onMounted } from 'vue'
// @archeon:endsection

// @archeon:section props_and_state
const isDark = ref(false)
// @archeon:endsection

// @archeon:section handlers
onMounted(() => {
  isDark.value = document.documentElement.classList.contains('dark')
})

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark')
  localStorage.setItem('archeon-theme', isDark.value ? 'dark' : 'light')
}
// @archeon:endsection
</script>
''')
    else:
        # React index.css with Tailwind theme
        (client_dir / "src" / "index.css").write_text('''@import "tailwindcss";

/* Archeon Theme Variables */
:root {
  /* Primary palette */
  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-200: #bfdbfe;
  --color-primary-300: #93c5fd;
  --color-primary-400: #60a5fa;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;
  --color-primary-800: #1e40af;
  --color-primary-900: #1e3a8a;
  --color-primary-950: #172554;

  /* Surface colors (light mode) */
  --color-surface: #ffffff;
  --color-surface-raised: #f9fafb;
  --color-content: #111827;
  --color-content-secondary: #4b5563;
  --color-content-muted: #9ca3af;
  --color-border: #e5e7eb;
}

.dark {
  --color-surface: #0f172a;
  --color-surface-raised: #1e293b;
  --color-content: #f1f5f9;
  --color-content-secondary: #cbd5e1;
  --color-content-muted: #64748b;
  --color-border: #334155;
}

/* Theme-aware component classes */
@layer components {
  .btn-primary {
    @apply inline-flex items-center justify-center px-4 py-2 font-medium text-sm rounded-md
           bg-[var(--color-primary-500)] text-white
           hover:bg-[var(--color-primary-600)]
           focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)] focus:ring-offset-2
           disabled:opacity-50 disabled:cursor-not-allowed;
  }

  .btn-outline {
    @apply inline-flex items-center justify-center px-4 py-2 font-medium text-sm rounded-md
           border border-[var(--color-border)] bg-transparent text-[var(--color-content)]
           hover:bg-[var(--color-surface-raised)]
           focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)];
  }

  .card {
    @apply bg-[var(--color-surface)] rounded-lg shadow-md border border-[var(--color-border)];
  }

  .input {
    @apply block w-full px-3 py-2 text-sm rounded-md
           bg-[var(--color-surface)] text-[var(--color-content)] border border-[var(--color-border)]
           placeholder:text-[var(--color-content-muted)]
           focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-500)] focus:border-transparent;
  }
}
''')
        
        # React main.tsx with theme init
        (client_dir / "src" / "main.tsx").write_text('''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Initialize theme from localStorage or system preference
const savedTheme = localStorage.getItem('archeon-theme')
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
  document.documentElement.classList.add('dark')
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
''')
        
        # React App.tsx with theme toggle
        (client_dir / "src" / "App.tsx").write_text('''import React, { useState, useEffect } from 'react'

function App() {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains('dark'))
  }, [])

  const toggleTheme = () => {
    setIsDark(!isDark)
    document.documentElement.classList.toggle('dark')
    localStorage.setItem('archeon-theme', !isDark ? 'dark' : 'light')
  }

  return (
    <div className="min-h-screen bg-[var(--color-surface)] text-[var(--color-content)] transition-colors">
      <header className="p-4 flex justify-between items-center border-b border-[var(--color-border)]">
        <h1 className="text-xl font-bold">Archeon React</h1>
        <button onClick={toggleTheme} className="btn-outline p-2 rounded-md">
          {isDark ? '☀️' : '🌙'}
        </button>
      </header>
      <main className="flex items-center justify-center" style={{ minHeight: 'calc(100vh - 73px)' }}>
        <div className="text-center">
          <h2 className="text-4xl font-bold mb-4">Welcome</h2>
          <p className="text-[var(--color-content-secondary)]">Add components to /src/components/</p>
          <div className="mt-8 flex gap-4 justify-center">
            <button className="btn-primary">Primary</button>
            <button className="btn-outline">Outline</button>
          </div>
        </div>
      </main>
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

import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.database import close_connection

# Ensure we can import from server directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import routes here as you create them
# Example:
# from src.api.routes.auth import router


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
# app.include_router(router)
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
    
    # Also create the index file
    create_index_file(archeon_dir, project_name)


def create_index_file(archeon_dir: Path, project_name: str):
    """Create initial ARCHEON.index.json file.
    
    This file is created at provisioning time and updated by scanning
    files for @archeon:file headers and @archeon:section markers.
    The AI must write to this file directly when generating code files.
    """
    import json
    index_path = archeon_dir / "ARCHEON.index.json"
    if not index_path.exists():
        index_data = {
            "version": "1.0",
            "project": project_name,
            "glyphs": {}
        }
        index_path.write_text(json.dumps(index_data, indent=2))


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
