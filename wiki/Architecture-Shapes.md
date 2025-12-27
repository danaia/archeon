# Architecture Shapes

Architecture Shapes are JSON-based blueprints that define complete technology stacks for Archeon projects. They contain glyph templates, configuration files, prebuilt components, and dependency specifications.

---

## Quick Start

```bash
# 1. List available shapes
arc shapes

# 2. Create a new project with a shape
arc init --arch vue3-fastapi

# 3. That's it! Your project structure:
#    client/     → Vue 3 frontend with ThemeToggle, ThemeSelector
#    server/     → FastAPI backend ready for API, models, events
#    archeon/    → Knowledge graph + shape definition
```

**Available Shapes:**

| Shape                 | Command                          | Stack                                                                |
| --------------------- | -------------------------------- | -------------------------------------------------------------------- |
| **Next.js + Express** | `arc init --arch nextjs-express` | **Next.js 14, Zustand, Express, TypeScript, Mongoose (RECOMMENDED)** |
| Vue 3 + FastAPI       | `arc init --arch vue3-fastapi`   | Vue 3, Pinia, TailwindCSS, FastAPI, MongoDB                          |
| React + FastAPI       | `arc init --arch react-fastapi`  | React, Zustand, TailwindCSS, FastAPI, MongoDB                        |

---

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE SHAPE                           │
├─────────────────────────────────────────────────────────────────┤
│  meta        → id, name, version, description, tags             │
│  stack       → frontend, backend, database, state management    │
│  directories → project structure blueprint                      │
│  glyphs      → CMP, STO, API, MDL, EVT, FNC, V templates       │
│  config      → tailwind, theme store, vite/webpack configs      │
│  prebuilt    → ready-to-use components (ThemeToggle, etc.)     │
│  dependencies→ npm packages, pip requirements                   │
└─────────────────────────────────────────────────────────────────┘
```

## File Location

```
archeon/
└── architectures/
    ├── _schema.json           # JSON Schema for validation
    ├── vue3-fastapi.shape.json
    ├── react-fastapi.shape.json
    └── [future].shape.json
```

## CLI Commands

```bash
# List available shapes
arc shapes

# Initialize project with specific shape
arc init --arch nextjs-express     # Next.js 14 + Express + TypeScript (RECOMMENDED)
arc init --arch vue3-fastapi       # Vue 3 + FastAPI + MongoDB
arc init --arch react-fastapi      # React + FastAPI + MongoDB

# Default behavior (uses vue3-fastapi)
arc init
```

---

## Shape Structure Reference

### 1. Meta Section

```json
{
  "meta": {
    "id": "vue3-fastapi",
    "name": "Vue 3 + FastAPI",
    "description": "Full-stack architecture with Vue 3 and FastAPI",
    "version": "1.0.0",
    "author": "Archeon",
    "tags": ["fullstack", "spa", "python", "vue", "mongodb"]
  }
}
```

| Field         | Type     | Required | Description                    |
| ------------- | -------- | -------- | ------------------------------ |
| `id`          | string   | ✅       | Unique identifier (kebab-case) |
| `name`        | string   | ✅       | Human-readable name            |
| `description` | string   | ✅       | Brief description              |
| `version`     | string   | ✅       | Semver version                 |
| `author`      | string   | ❌       | Shape author                   |
| `tags`        | string[] | ❌       | Searchable tags                |

### 2. Stack Section

Defines the technology choices. Can be simple strings or detailed objects:

**Simple format (react-fastapi):**

```json
{
  "stack": {
    "frontend": "react",
    "backend": "fastapi",
    "database": "mongodb",
    "state": "zustand"
  }
}
```

**Detailed format (vue3-fastapi):**

```json
{
  "stack": {
    "frontend": {
      "framework": "vue3",
      "language": "typescript",
      "stateManagement": "pinia",
      "styling": "tailwind",
      "buildTool": "vite"
    },
    "backend": {
      "framework": "fastapi",
      "language": "python",
      "database": "mongodb",
      "orm": "motor"
    }
  }
}
```

### 3. Directories Section

Defines project folder structure:

```json
{
  "directories": {
    "frontend": {
      "src": {
        "components": {},
        "stores": {},
        "views": {},
        "hooks": {},
        "types": {},
        "utils": {}
      },
      "public": {}
    },
    "backend": {
      "app": {
        "api": {},
        "models": {},
        "events": {},
        "services": {}
      }
    }
  }
}
```

### 4. Glyphs Section

Each glyph type has a template definition:

```json
{
  "glyphs": {
    "CMP": {
      "description": "Vue 3 component with Composition API",
      "fileExtension": ".vue",
      "targetDir": "src/components",
      "layer": "frontend",
      "sections": ["imports", "props_and_state", "handlers", "render"],
      "snippet": "<!-- @archeon:file -->\n<!-- @glyph {GLYPH_NAME} -->\n...",
      "placeholders": {
        "GLYPH_NAME": {
          "description": "Full glyph name (e.g., CMP:LoginForm)",
          "required": true
        },
        "IMPORTS": {
          "description": "Additional imports",
          "default": ""
        }
      }
    }
  }
}
```

**Supported Glyph Types:**

| Glyph | Purpose                 | Frontend         | Backend     |
| ----- | ----------------------- | ---------------- | ----------- |
| `CMP` | UI Component            | ✅ React/Vue     | -           |
| `STO` | State Store             | ✅ Zustand/Pinia | -           |
| `API` | API Endpoint            | -                | ✅ FastAPI  |
| `MDL` | Data Model              | -                | ✅ Pydantic |
| `EVT` | Event System            | -                | ✅ Pub/Sub  |
| `FNC` | Utility Function        | ✅               | ✅          |
| `V`   | View/Page or Validation | ✅               | ✅          |

### 5. Config Section

Static configuration files to generate:

```json
{
  "config": {
    "tailwind": {
      "targetPath": "tailwind.config.js",
      "content": "/** @type {import('tailwindcss').Config} */\n..."
    },
    "themeStore": {
      "targetPath": "src/stores/themeStore.js",
      "content": "// @archeon:file\n// @glyph STO:Theme\n..."
    }
  }
}
```

### 6. Prebuilt Section

Ready-to-use components that ship with the shape:

```json
{
  "prebuilt": {
    "ThemeToggle": {
      "description": "Theme toggle button with light/dark/system modes",
      "targetPath": "src/components/ThemeToggle.vue",
      "content": "<!-- @archeon:file -->\n<!-- @glyph CMP:ThemeToggle -->..."
    },
    "ThemeSelector": {
      "description": "Full theme selector dropdown",
      "targetPath": "src/components/ThemeSelector.vue",
      "content": "..."
    }
  }
}
```

### 7. Dependencies Section

Package dependencies for both frontend and backend:

```json
{
  "dependencies": {
    "frontend": {
      "vue": "^3.4.0",
      "pinia": "^2.1.0",
      "tailwindcss": "^3.4.0"
    },
    "backend": {
      "fastapi": ">=0.109.0",
      "uvicorn": ">=0.27.0",
      "motor": ">=3.3.0"
    }
  }
}
```

---

## Creating New Shapes

### Step 1: Copy an existing shape

```bash
cp archeon/architectures/vue3-fastapi.shape.json \
   archeon/architectures/angular-nestjs.shape.json
```

### Step 2: Update meta section

```json
{
  "meta": {
    "id": "angular-nestjs",
    "name": "Angular + NestJS",
    "description": "Enterprise Angular frontend with NestJS TypeScript backend",
    "version": "1.0.0",
    "tags": ["fullstack", "enterprise", "typescript", "angular"]
  }
}
```

### Step 3: Define stack

```json
{
  "stack": {
    "frontend": "angular",
    "backend": "nestjs",
    "database": "postgresql",
    "state": "ngrx"
  }
}
```

### Step 4: Create glyph templates

Write templates for each glyph type using the target framework's idioms.

### Step 5: Validate against schema

```bash
# The shape loader validates automatically
python -c "from archeon.orchestrator.SHP_shape import load_architecture; print(load_architecture('angular-nestjs'))"
```

---

## GUI Development Guide

This section provides specifications for building a Shape Management GUI.

### API Endpoints (Suggested)

```
GET    /api/shapes              → List all shapes
GET    /api/shapes/:id          → Get shape details
POST   /api/shapes              → Create new shape
PUT    /api/shapes/:id          → Update shape
DELETE /api/shapes/:id          → Delete shape
POST   /api/shapes/:id/validate → Validate shape JSON
GET    /api/shapes/:id/preview  → Preview generated files
```

### Data Model for GUI

```typescript
// Shape list item (minimal)
interface ShapeListItem {
  id: string;
  name: string;
  description: string;
  version: string;
  tags: string[];
  stack: {
    frontend: string;
    backend: string;
    database?: string;
  };
  glyphCount: number;
  prebuiltCount: number;
}

// Full shape for editing
interface Shape {
  meta: ShapeMeta;
  stack: Record<string, string | object>;
  directories: NestedObject;
  glyphs: Record<string, GlyphDefinition>;
  config: Record<string, ConfigFile>;
  prebuilt: Record<string, PrebuiltComponent>;
  dependencies: {
    frontend: Record<string, string>;
    backend: Record<string, string>;
  };
}

interface GlyphDefinition {
  description: string;
  fileExtension: string;
  targetDir: string;
  layer: "frontend" | "backend" | "shared";
  sections: string[];
  snippet: string;
  placeholders: Record<string, PlaceholderDef>;
}

interface PlaceholderDef {
  description: string;
  required?: boolean;
  default?: string;
  transform?: "pascalCase" | "camelCase" | "snake_case" | "kebab-case";
}

interface PrebuiltComponent {
  description: string;
  targetPath: string;
  content: string;
  glyph?: string; // e.g., "CMP:ThemeToggle"
}
```

### GUI Views

#### 1. Shape Browser (List View)

```
┌─────────────────────────────────────────────────────────────────┐
│ Architecture Shapes                            [+ New Shape]    │
├─────────────────────────────────────────────────────────────────┤
│ 🔍 Search...                    Filter: [All ▼] [Frontend ▼]   │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🟢 vue3-fastapi                                    v1.0.0   │ │
│ │ Vue 3 + FastAPI                                             │ │
│ │ Tags: fullstack, spa, python, vue                           │ │
│ │ Glyphs: 7 │ Prebuilt: 2 │ Stack: Vue3/FastAPI/MongoDB       │ │
│ │                                    [View] [Edit] [Clone]    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 🔵 react-fastapi                                   v1.0.0   │ │
│ │ React + FastAPI                                             │ │
│ │ Tags: fullstack, typescript, react                          │ │
│ │ Glyphs: 7 │ Prebuilt: 2 │ Stack: React/FastAPI/MongoDB      │ │
│ │                                    [View] [Edit] [Clone]    │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

#### 2. Shape Detail View

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back    vue3-fastapi                          [Edit] [Clone] │
├─────────────────────────────────────────────────────────────────┤
│ Vue 3 + FastAPI                                                 │
│ Full-stack architecture with Vue 3 Composition API...           │
│ Version: 1.0.0 │ Author: Archeon                                │
│ Tags: [fullstack] [spa] [python] [vue] [mongodb]               │
├─────────────────────────────────────────────────────────────────┤
│ [Stack] [Glyphs] [Config] [Prebuilt] [Dependencies] [Preview]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STACK                                                          │
│  ┌──────────────┬────────────────────────────────────────────┐ │
│  │ Frontend     │ Vue 3 + TypeScript + Pinia + Tailwind      │ │
│  │ Backend      │ FastAPI + Python + Motor                   │ │
│  │ Database     │ MongoDB                                     │ │
│  └──────────────┴────────────────────────────────────────────┘ │
│                                                                 │
│  GLYPHS (7)                                                     │
│  ┌────────┬─────────────────────────────────────────┬────────┐ │
│  │ CMP    │ Vue 3 component with Composition API    │ .vue   │ │
│  │ STO    │ Pinia store with TypeScript             │ .js    │ │
│  │ API    │ FastAPI router endpoint                 │ .py    │ │
│  │ MDL    │ Pydantic model for MongoDB              │ .py    │ │
│  │ EVT    │ Python async event pub/sub              │ .py    │ │
│  │ FNC    │ Python utility function                 │ .py    │ │
│  │ V      │ Vue view/page component                 │ .vue   │ │
│  └────────┴─────────────────────────────────────────┴────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 3. Glyph Template Editor

```
┌─────────────────────────────────────────────────────────────────┐
│ Editing: CMP (Component) Template                               │
├─────────────────────────────────────────────────────────────────┤
│ Description: [Vue 3 component with Composition API           ]  │
│ Extension:   [.vue    ]  Target Dir: [src/components         ]  │
│ Layer:       [frontend ▼]                                       │
├─────────────────────────────────────────────────────────────────┤
│ Sections: [imports] [props_and_state] [handlers] [render] [+]  │
├─────────────────────────────────────────────────────────────────┤
│ Template Snippet:                                               │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ <!-- @archeon:file -->                                      │ │
│ │ <!-- @glyph {GLYPH_QUALIFIED_NAME} -->                      │ │
│ │ <!-- @intent {COMPONENT_INTENT} -->                         │ │
│ │ <script setup lang="ts">                                    │ │
│ │ {STORE_IMPORT}                                              │ │
│ │ {IMPORTS}                                                   │ │
│ │ // @archeon:section props_and_state                         │ │
│ │ ...                                                         │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Placeholders:                                                   │
│ ┌────────────────────┬────────────┬─────────────┬────────────┐ │
│ │ Name               │ Required   │ Default     │ Transform  │ │
│ ├────────────────────┼────────────┼─────────────┼────────────┤ │
│ │ GLYPH_QUALIFIED... │ ✅         │ -           │ -          │ │
│ │ COMPONENT_INTENT   │ ✅         │ -           │ -          │ │
│ │ STORE_IMPORT       │ ❌         │ ""          │ -          │ │
│ │ IMPORTS            │ ❌         │ ""          │ -          │ │
│ └────────────────────┴────────────┴─────────────┴────────────┘ │
│                                              [+ Add Placeholder]│
├─────────────────────────────────────────────────────────────────┤
│                                         [Cancel] [Save Glyph]   │
└─────────────────────────────────────────────────────────────────┘
```

#### 4. File Preview Panel

```
┌─────────────────────────────────────────────────────────────────┐
│ Preview: Generated Files                                        │
├─────────────────────────────────────────────────────────────────┤
│ 📁 client/                                                      │
│   📁 src/                                                       │
│     📁 components/                                              │
│       📄 ThemeToggle.vue ←──────────────────────────────────┐  │
│       📄 ThemeSelector.vue                                   │  │
│     📁 stores/                                               │  │
│       📄 themeStore.js                                       │  │
│   📄 tailwind.config.js                                      │  │
│   📄 vite.config.js                                          │  │
│ 📁 server/                                                   │  │
│   📁 app/                                                    │  │
│     📁 api/                                                  │  │
│     📁 models/                                               │  │
│                                                              │  │
├──────────────────────────────────────────────────────────────┤  │
│ ThemeToggle.vue                                              │  │
│ ─────────────────────────────────────────────────────────────│  │
│ <!-- @archeon:file -->                                       │  │
│ <!-- @glyph CMP:ThemeToggle -->                              │  │
│ <!-- @intent Dark/light mode toggle button... -->            │  │
│ <script setup lang="ts">                                     │  │
│ import { useThemeStore } from '@/stores/themeStore';         │  │
│ ...                                                          │◄─┘
└─────────────────────────────────────────────────────────────────┘
```

### GUI Component Hierarchy

```
ShapeManager/
├── ShapeBrowser/
│   ├── SearchBar
│   ├── FilterDropdowns
│   └── ShapeCard (list)
│       ├── ShapeIcon
│       ├── ShapeMeta
│       ├── TagList
│       └── ActionButtons
├── ShapeDetail/
│   ├── ShapeHeader
│   ├── TabNavigation
│   ├── StackView
│   ├── GlyphList/
│   │   └── GlyphCard
│   ├── ConfigList/
│   │   └── ConfigCard
│   ├── PrebuiltList/
│   │   └── PrebuiltCard
│   ├── DependencyView
│   └── FilePreview
├── ShapeEditor/
│   ├── MetaEditor
│   ├── StackEditor
│   ├── DirectoryTreeEditor
│   ├── GlyphEditor/
│   │   ├── SnippetEditor (Monaco/CodeMirror)
│   │   └── PlaceholderTable
│   ├── ConfigEditor
│   ├── PrebuiltEditor
│   └── DependencyEditor
└── ShapeWizard/
    ├── StackSelector
    ├── GlyphSelector
    ├── TemplateGenerator
    └── ReviewStep
```

### Reading Shapes Programmatically

```python
from archeon.orchestrator.SHP_shape import (
    list_architectures,
    load_architecture,
    get_loader
)

# List all available shapes
shapes = list_architectures()
for shape_id in shapes:
    shape = load_architecture(shape_id)
    print(f"{shape.id}: {shape.name}")
    print(f"  Glyphs: {list(shape.glyphs.keys())}")
    print(f"  Prebuilt: {list(shape.prebuilt.keys()) if shape.prebuilt else []}")

# Load specific shape
shape = load_architecture("vue3-fastapi")

# Access shape data
print(shape.meta)           # {'id': 'vue3-fastapi', ...}
print(shape.stack)          # {'frontend': {...}, 'backend': {...}}
print(shape.glyphs['CMP'])  # GlyphShape object
print(shape.config)         # {'tailwind': {...}, 'themeStore': {...}}
print(shape.prebuilt)       # {'ThemeToggle': {...}, ...}
print(shape.dependencies)   # {'frontend': {...}, 'backend': {...}}
```

### JSON Schema Location

The JSON Schema for validating shapes is at:

```
archeon/architectures/_schema.json
```

Use it for:

- Editor autocomplete (VS Code, etc.)
- Runtime validation
- GUI form generation

---

## Training AI Developers to Build Shapes

### Key Concepts to Understand

1. **Glyphs are semantic markers** - They tag code with architectural meaning
2. **Placeholders use Mustache-style syntax** - `{PLACEHOLDER_NAME}`
3. **Sections mark editable regions** - `// @archeon:section name`
4. **Each shape is self-contained** - All templates, configs, and deps in one file

### Shape Building Checklist

```markdown
□ Meta section complete with unique ID
□ Stack technologies defined
□ Directory structure matches framework conventions
□ All 7 core glyph types defined (CMP, STO, API, MDL, EVT, FNC, V)
□ Each glyph has:
□ Appropriate file extension
□ Correct target directory
□ Layer assignment (frontend/backend/shared)
□ Section markers in snippet
□ Placeholder definitions
□ Config files for build tools (tailwind, vite/webpack)
□ Theme store with light/dark/system support
□ At least ThemeToggle prebuilt component
□ Dependencies list is complete and version-pinned
□ Shape validates against \_schema.json
```

### Common Patterns

**Frontend Frameworks:**

- React: `.tsx`, Zustand/Redux, Zod validation
- Vue 3: `.vue`, Pinia, Composition API
- Angular: `.ts`, NgRx, Services
- Svelte: `.svelte`, Svelte stores

**Backend Frameworks:**

- FastAPI: Python, Pydantic, async
- NestJS: TypeScript, decorators, DI
- Express: JavaScript/TypeScript
- Django: Python, ORM, class-based

**State Management:**

- Zustand (React): `create()`, middleware
- Pinia (Vue): `defineStore()`, actions
- NgRx (Angular): Actions, Reducers, Effects

### Example: Creating a Svelte Shape

```json
{
  "meta": {
    "id": "svelte-fastapi",
    "name": "Svelte + FastAPI"
  },
  "stack": {
    "frontend": "svelte",
    "backend": "fastapi"
  },
  "glyphs": {
    "CMP": {
      "description": "Svelte component",
      "fileExtension": ".svelte",
      "targetDir": "src/lib/components",
      "snippet": "<!-- @archeon:file -->\n<script lang=\"ts\">\n  // @archeon:section imports\n  {IMPORTS}\n  // @archeon:end imports\n</script>\n\n{TEMPLATE}\n\n<style>\n  {STYLES}\n</style>"
    },
    "STO": {
      "description": "Svelte writable store",
      "fileExtension": ".ts",
      "targetDir": "src/lib/stores",
      "snippet": "// @archeon:file\nimport { writable } from 'svelte/store';\n\nexport const {STORE_NAME} = writable({INITIAL_STATE});"
    }
  }
}
```

---

## Browsing Shapes in Your GUI

### Recommended User Flows

**1. Discovery Flow**

```
Browse Shapes → Filter by Stack → View Details → Preview Files → Clone to Project
```

**2. Creation Flow**

```
New Shape → Select Base Template → Configure Stack → Edit Glyphs → Add Prebuilt → Save
```

**3. Editing Flow**

```
Select Shape → Edit Section → Live Preview → Validate → Save → Test Init
```

### Search & Filter Capabilities

```typescript
interface ShapeFilters {
  search?: string; // Full-text search
  frontend?: string[]; // ['react', 'vue', 'angular']
  backend?: string[]; // ['fastapi', 'nestjs', 'express']
  database?: string[]; // ['mongodb', 'postgresql', 'mysql']
  tags?: string[]; // ['fullstack', 'spa', 'enterprise']
  hasPrebuilt?: boolean; // Has prebuilt components
}
```

### Integration Points

Your GUI should integrate with:

1. **File System** - Read/write `.shape.json` files
2. **CLI** - Call `arc shapes` and `arc init --arch`
3. **Validation** - Use `_schema.json` for validation
4. **Preview** - Generate file tree preview before init

### WebSocket Events (for real-time updates)

```typescript
// Shape events
'shape:created'   → { shapeId: string }
'shape:updated'   → { shapeId: string, changes: string[] }
'shape:deleted'   → { shapeId: string }
'shape:validated' → { shapeId: string, valid: boolean, errors?: string[] }
```

---

## Future Shape Ideas

| Shape ID         | Frontend | Backend  | Database   | Status     |
| ---------------- | -------- | -------- | ---------- | ---------- |
| `vue3-fastapi`   | Vue 3    | FastAPI  | MongoDB    | ✅ Done    |
| `react-fastapi`  | React    | FastAPI  | MongoDB    | ✅ Done    |
| `angular-nestjs` | Angular  | NestJS   | PostgreSQL | 📋 Planned |
| `svelte-fastapi` | Svelte   | FastAPI  | MongoDB    | 📋 Planned |
| `react-express`  | React    | Express  | MongoDB    | 📋 Planned |
| `vue3-django`    | Vue 3    | Django   | PostgreSQL | 📋 Planned |
| `nextjs-prisma`  | Next.js  | Next API | PostgreSQL | 📋 Planned |
| `nuxt-nitro`     | Nuxt 3   | Nitro    | MongoDB    | 📋 Planned |

---

## Related Documentation

- [Glyph-Reference](Glyph-Reference.md) - All glyph types and syntax
- [Chain-Syntax](Chain-Syntax.md) - How chains connect glyphs
- [Templates](Templates.md) - Template system overview
- [CLI-Commands](CLI-Commands.md) - Full CLI reference
