# Architecture Shapes

Architecture Shapes are JSON-based blueprints that define complete technology stacks for Archeon projects. They contain glyph templates, configuration files, prebuilt components, and dependency specifications.

> **Key Insight:** Shapes are **100% customizable**. Create your own shape to enforce your team's exact coding standards, patterns, and architecture. **Your shape = Your AI's training data.**

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
| Next.js + FastAPI     | `arc init --arch nextjs-fastapi` | Next.js 15, Zustand, TailwindCSS, FastAPI, MongoDB                   |

---

## Creating Your Team's Custom Shape

**This is the most powerful feature of Archeon.** Custom shapes let you codify your team's exact coding standards into a JSON file that the AI must follow.

### Why Create a Custom Shape?

| Problem                                      | Custom Shape Solution                                                     |
| -------------------------------------------- | ------------------------------------------------------------------------- |
| "AI uses different patterns every time"      | ✅ Define exact templates for CMP, API, STO — AI follows them always      |
| "Every dev has their own style"              | ✅ One shape = one standard = zero style drift                            |
| "Onboarding takes weeks"                     | ✅ New devs run `arc init --arch yourcompany` → instant setup             |
| "AI doesn't know our error handling pattern" | ✅ Embed your try/catch, logging, middleware in API template              |
| "We need custom auth middleware on routes"   | ✅ Put it in the API snippet — every endpoint gets it                     |
| "Design system isn't consistent"             | ✅ Pre-build components with your utility classes, tokens, theme patterns |

### The Power of Custom Shapes

**Example: Your team uses a specific React component pattern:**

```json
{
  "glyphs": {
    "CMP": {
      "snippet": "// @archeon:file\n// @glyph {{GLYPH_NAME}}\nimport { FC } from 'react';\nimport { cn } from '@/lib/utils';\nimport { useAnalytics } from '@/hooks/useAnalytics'; // Your custom hook\n\ninterface {{COMPONENT_NAME}}Props {\n  className?: string;\n  // Add props\n}\n\nexport const {{COMPONENT_NAME}}: FC<{{COMPONENT_NAME}}Props> = ({ className }) => {\n  const analytics = useAnalytics(); // Auto-included\n  \n  return (\n    <div className={cn('your-base-class', className)} data-component=\"{{COMPONENT_NAME}}\">\n      {/* Your structure */}\n    </div>\n  );\n};\n\n// @archeon:test\nimport { render } from '@testing-library/react';\nimport { {{COMPONENT_NAME}} } from './{{COMPONENT_NAME}}';\n\ndescribe('{{COMPONENT_NAME}}', () => {\n  it('renders', () => {\n    const { container } = render(<{{COMPONENT_NAME}} />);\n    expect(container).toMatchSnapshot();\n  });\n});"
    }
  }
}
```

**Every component the AI generates will:**

- Import your `cn` utility
- Include your analytics hook
- Use your base CSS class
- Have a data attribute for debugging
- Include a snapshot test

**No variation. No hallucination. Zero deviation.**

### Step-by-Step: Create Your Shape

#### 1. Start with a Template

Copy an existing shape as your starting point:

```bash
# Navigate to Archeon installation
cd archeon/architectures

# Copy the shape closest to your stack
cp nextjs-express.shape.json yourcompany.shape.json
```

#### 2. Update Meta Information

```json
{
  "meta": {
    "id": "yourcompany",
    "name": "YourCompany Stack",
    "description": "Next.js 14 + tRPC + Prisma + Tailwind (YourCompany Standards)",
    "version": "1.0.0",
    "author": "YourCompany Engineering",
    "tags": ["fullstack", "nextjs", "trpc", "prisma", "typescript"]
  }
}
```

#### 3. Define Your Stack

```json
{
  "stack": {
    "frontend": {
      "framework": "nextjs",
      "version": "14.0",
      "stateManagement": "zustand",
      "styling": "tailwind",
      "api": "trpc"
    },
    "backend": {
      "framework": "nextjs-api",
      "language": "typescript",
      "database": "postgresql",
      "orm": "prisma"
    }
  }
}
```

#### 4. Customize Glyph Templates

This is where you encode your team's patterns. Here's a complete example:

```json
{
  "glyphs": {
    "CMP": {
      "description": "Next.js React Server/Client Component with company standards",
      "fileExtension": ".tsx",
      "targetDir": "src/components",
      "layer": "frontend",
      "sections": ["imports", "types", "component", "tests"],
      "snippet": "// @archeon:file\n// @glyph {{GLYPH_NAME}}\n'use client'; // Remove if RSC\n\nimport { FC } from 'react';\nimport { cn } from '@/lib/utils';\nimport { logger } from '@/lib/logger'; // Your logger\n\n// @archeon:section types\ninterface {{COMPONENT_NAME}}Props {\n  className?: string;\n}\n// @archeon:endsection\n\n// @archeon:section component\nexport const {{COMPONENT_NAME}}: FC<{{COMPONENT_NAME}}Props> = ({\n  className,\n}) => {\n  logger.component('{{COMPONENT_NAME}}', 'rendered'); // Your logging pattern\n  \n  return (\n    <div className={cn('base-component', className)}>\n      {/* Implementation */}\n    </div>\n  );\n};\n// @archeon:endsection",
      "placeholders": {
        "GLYPH_NAME": {
          "description": "Full glyph reference (e.g., CMP:LoginButton)",
          "required": true
        },
        "COMPONENT_NAME": {
          "description": "PascalCase component name extracted from glyph",
          "required": true
        }
      }
    },
    "API": {
      "description": "tRPC procedure with Zod validation and company middleware",
      "fileExtension": ".ts",
      "targetDir": "src/server/api/routers",
      "layer": "backend",
      "snippet": "// @archeon:file\n// @glyph {{GLYPH_NAME}}\nimport { z } from 'zod';\nimport { router, protectedProcedure } from '@/server/api/trpc';\nimport { logger } from '@/lib/logger';\nimport { TRPCError } from '@trpc/server';\n\n// @archeon:section schema\nconst {{PROCEDURE_NAME}}Schema = z.object({\n  // Define input schema\n});\n// @archeon:endsection\n\n// @archeon:section procedure\nexport const {{ROUTER_NAME}}Router = router({\n  {{PROCEDURE_NAME}}: protectedProcedure // Your auth middleware\n    .input({{PROCEDURE_NAME}}Schema)\n    .mutation(async ({ ctx, input }) => {\n      try {\n        logger.api('{{PROCEDURE_NAME}}', { userId: ctx.user.id, input });\n        \n        // Implementation\n        \n        return { success: true };\n      } catch (error) {\n        logger.error('{{PROCEDURE_NAME}} failed', error);\n        throw new TRPCError({\n          code: 'INTERNAL_SERVER_ERROR',\n          message: 'Operation failed',\n        });\n      }\n    }),\n});\n// @archeon:endsection"
    },
    "STO": {
      "description": "Zustand store with company patterns",
      "fileExtension": ".ts",
      "targetDir": "src/stores",
      "layer": "frontend",
      "snippet": "// @archeon:file\n// @glyph {{GLYPH_NAME}}\nimport { create } from 'zustand';\nimport { devtools, persist } from 'zustand/middleware';\nimport { logger } from '@/lib/logger';\n\ninterface {{STORE_NAME}}State {\n  // State properties\n}\n\ninterface {{STORE_NAME}}Actions {\n  // Action methods\n}\n\nexport const use{{STORE_NAME}} = create<{{STORE_NAME}}State & {{STORE_NAME}}Actions>()(\n  devtools(\n    persist(\n      (set, get) => ({\n        // Initial state\n        \n        // Actions with logging\n      }),\n      {\n        name: '{{STORE_NAME}}-storage',\n        onRehydrateStorage: () => (state) => {\n          logger.store('{{STORE_NAME}}', 'rehydrated');\n        },\n      }\n    ),\n    { name: '{{STORE_NAME}}' }\n  )\n);"
    }
  }
}
```

#### 5. Add Pre-built Components

Include your design system components:

```json
{
  "prebuilt": {
    "Button": {
      "description": "Company button component with all variants",
      "targetPath": "src/components/ui/Button.tsx",
      "content": "// Your complete button implementation with all your variants"
    },
    "Input": {
      "description": "Form input with validation",
      "targetPath": "src/components/ui/Input.tsx",
      "content": "// Your input component"
    },
    "Toast": {
      "description": "Toast notification system",
      "targetPath": "src/components/ui/Toast.tsx",
      "content": "// Your toast implementation"
    }
  }
}
```

#### 6. Define Configuration Files

```json
{
  "config": {
    "tailwind": {
      "targetPath": "tailwind.config.ts",
      "content": "import type { Config } from 'tailwindcss';\n\nconst config: Config = {\n  // Your company's Tailwind config\n  theme: {\n    extend: {\n      colors: {\n        brand: {\n          // Your brand colors\n        }\n      }\n    }\n  }\n};\n\nexport default config;"
    },
    "prettier": {
      "targetPath": ".prettierrc",
      "content": "{\n  \"semi\": true,\n  \"singleQuote\": true,\n  \"tabWidth\": 2\n  // Your formatting rules\n}"
    },
    "eslint": {
      "targetPath": ".eslintrc.json",
      "content": "{\n  \"extends\": [\"next/core-web-vitals\"],\n  \"rules\": {\n    // Your linting rules\n  }\n}"
    }
  }
}
```

#### 7. Specify Dependencies

```json
{
  "dependencies": {
    "frontend": {
      "@trpc/client": "^10.45.0",
      "@trpc/server": "^10.45.0",
      "next": "^14.0.0",
      "react": "^18.2.0",
      "zustand": "^4.4.0",
      "zod": "^3.22.0",
      "tailwindcss": "^3.4.0",
      "@your-company/ui-kit": "^2.0.0"
    },
    "backend": {
      "@prisma/client": "^5.7.0",
      "prisma": "^5.7.0"
    }
  }
}
```

#### 8. Validate Your Shape

```bash
# Test your shape
arc init --arch yourcompany

# Check the generated structure
tree my-app

# Validate it works
cd my-app
arc validate
```

#### 9. Share with Your Team

```bash
# Commit the shape file
git add archeon/architectures/yourcompany.shape.json
git commit -m "Add company architecture shape"
git push

# Team members clone and use it
git clone <your-archeon-fork>
cd archeon && pip install -e .
cd .. && mkdir new-project && cd new-project
arc init --arch yourcompany
```

### Complete Shape Schema Reference

For full JSON schema specification, see `archeon/architectures/_schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["meta", "stack", "glyphs"],
  "properties": {
    "meta": {
      "type": "object",
      "required": ["id", "name", "version"],
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" },
        "description": { "type": "string" },
        "version": { "type": "string" },
        "author": { "type": "string" },
        "tags": { "type": "array", "items": { "type": "string" } }
      }
    },
    "stack": { "type": "object" },
    "directories": { "type": "object" },
    "glyphs": {
      "type": "object",
      "properties": {
        "CMP": { "$ref": "#/definitions/glyphTemplate" },
        "STO": { "$ref": "#/definitions/glyphTemplate" },
        "API": { "$ref": "#/definitions/glyphTemplate" },
        "MDL": { "$ref": "#/definitions/glyphTemplate" },
        "EVT": { "$ref": "#/definitions/glyphTemplate" },
        "FNC": { "$ref": "#/definitions/glyphTemplate" },
        "V": { "$ref": "#/definitions/glyphTemplate" }
      }
    },
    "config": { "type": "object" },
    "prebuilt": { "type": "object" },
    "dependencies": {
      "type": "object",
      "properties": {
        "frontend": { "type": "object" },
        "backend": { "type": "object" }
      }
    }
  },
  "definitions": {
    "glyphTemplate": {
      "type": "object",
      "required": ["fileExtension", "targetDir", "snippet"],
      "properties": {
        "description": { "type": "string" },
        "fileExtension": { "type": "string" },
        "targetDir": { "type": "string" },
        "layer": { "enum": ["frontend", "backend", "shared"] },
        "sections": { "type": "array", "items": { "type": "string" } },
        "snippet": { "type": "string" },
        "placeholders": { "type": "object" }
      }
    }
  }
}
```

### Pro Tips

1. **Start small** — Copy a base shape and modify one glyph at a time
2. **Test frequently** — Run `arc init --arch yourshape` after each change
3. **Use placeholders** — `{{COMPONENT_NAME}}`, `{{GLYPH_NAME}}` are auto-replaced
4. **Include tests** — Put test stubs in your glyph snippets
5. **Version your shapes** — Use semver in meta.version for tracking changes
6. **Document patterns** — Use description fields to explain your decisions
7. **Share internally** — Fork Archeon, add company shape, use in all projects

### Real-World Examples

**Startup (Move Fast):**

- Minimal templates, get started quickly
- Pre-built auth, payments, email components
- Supabase + Next.js for rapid prototyping

**Enterprise (Compliance & Standards):**

- Detailed error handling, logging, audit trails in every template
- Custom middleware for auth, rate limiting, monitoring
- Pre-built components that meet accessibility standards
- Strict TypeScript, ESLint, testing requirements

**Agency (Client Variety):**

- Multiple shapes for different client tech preferences
- Reusable design system components
- Consistent project structure across all client work

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
    ├── nextjs-fastapi.shape.json
    └── [future].shape.json
```

## CLI Commands

```bash
# List available shapes
arc shapes

# Initialize project with specific shape
arc init --arch nextjs-express     # Next.js 14 + Express + TypeScript (RECOMMENDED)
arc init --arch vue3-fastapi       # Vue 3 + FastAPI + MongoDB
arc init --arch nextjs-fastapi      # Next.js + FastAPI + MongoDB

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

**Simple format (nextjs-fastapi):**

```json
{
  "stack": {
    "frontend": "nextjs",
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
│ │ 🔵 nextjs-fastapi                                  v1.0.0   │ │
│ │ Next.js 15 + FastAPI                                        │ │
│ │ Tags: fullstack, typescript, nextjs, python                 │ │
│ │ Glyphs: 8 │ Prebuilt: 4 │ Stack: Next.js/FastAPI/MongoDB    │ │
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
| `nextjs-fastapi`  | Next.js  | FastAPI  | MongoDB    | ✅ Done    |
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
