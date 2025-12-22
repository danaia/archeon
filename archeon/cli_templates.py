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
- `STO:Auth` → `client/src/stores/Auth.js`
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

## Code Generation - Two Paths

There are TWO ways to create Archeon-compatible files. Both require updating the index.

### Path 1: Use `arc gen` (Recommended for CLI)

```bash
# First, add chains to ARCHEON.arcon
arc parse "NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard"

# Generate all code from the knowledge graph (auto-updates index)
arc gen

# Validate architecture
arc validate
```

`arc gen` automatically:
- Creates files with proper `@archeon:file` headers
- Adds `@archeon:section` markers
- Updates `archeon/ARCHEON.index.json`

### Path 2: Manual File Creation (For IDE AI like Copilot/Claude)

When the AI creates files manually:

```bash
# Step 1: AI creates files WITH headers and sections (see format below)
# Step 2: ALWAYS update the index after creating/modifying files:
arc index build

# Step 3: Validate
arc validate
```

**⚠️ CRITICAL:** If you create files manually without running `arc index build`, the files will be INVISIBLE to the Archeon system. The index is how Archeon knows what files exist and what sections they contain.

### Quick Reference

| Action | Command |
|--------|---------|
| Generate files from chains | `arc gen` (auto-updates index) |
| After manually creating files | `arc index build` |
| Check for files missing headers | `arc index check` |
| Add header to existing file | `arc index inject --path <file> --glyph <GLYPH> ...` |
| View current index | `arc index show` |

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
| (default) | React | Zustand | Vite + React |
| `--frontend vue3` | Vue 3 | Pinia | Vite + JavaScript |
| `--frontend vue` | Vue 2 | Pinia | Options API |

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

## Design Tokens (Theming)

Archeon uses **W3C DTCG (Design Tokens Community Group)** format for design tokens - a single source of truth for all design system values (colors, typography, spacing, etc.).

### Token Workflow

```
design-tokens.json (Source of Truth)
        │
        ▼
   arc tokens build   OR   arc run TKN:transformer
        │
        ├──► tokens.css          (CSS custom properties)
        ├──► tokens.semantic.css (Component-ready aliases)
        ├──► tokens.tailwind.js  (Tailwind extend config)
        └──► tokens.js           (JS module export)
```

### When a User Wants to Change Theme/Colors

1. **Edit the design tokens file:**
   ```bash
   # Location: archeon/_config/design-tokens.json
   # Or: client/src/tokens/design-tokens.json
   ```

2. **Change values in the JSON:**
   ```json
   {
     "color": {
       "semantic": {
         "primary": {
           "default": { "$value": "#8b5cf6" }  // Changed from blue to purple
         }
       }
     }
   }
   ```

3. **Regenerate outputs via TKN glyph:**
   ```bash
   arc run TKN:transformer
   # Or use CLI directly:
   arc tokens build
   ```

4. **Changes propagate to all generated files** - CSS variables, Tailwind config, and JS exports all update automatically.

### Token Commands

```bash
arc tokens init       # Create default design-tokens.json in project
arc tokens build      # Transform tokens to CSS/Tailwind/JS
arc tokens validate   # Verify token file format
arc tokens build -f css -o ./styles  # Only CSS to custom directory
```

### Token Categories

| Category | Purpose | Example |
|----------|---------|---------|
| `color.primitive` | Base palette | `blue.500`, `gray.100` |
| `color.semantic` | Intent colors | `primary`, `success`, `danger` |
| `color.surface` | Backgrounds | `default`, `raised`, `sunken` |
| `color.content` | Text colors | `primary`, `secondary`, `muted` |
| `typography` | Font settings | `fontSize`, `fontWeight`, `lineHeight` |
| `spacing` | Layout spacing | `1` (0.25rem) to `96` (24rem) |
| `borderRadius` | Corner rounding | `sm`, `md`, `lg`, `full` |
| `shadow` | Box shadows | `sm`, `md`, `lg`, `xl` |
| `component` | Component-specific | `button.height.md`, `input.padding` |

### Theme-Aware Components

Generated components use semantic CSS classes that respond to tokens:

```jsx
// Uses CSS variables that update when tokens change
<button className="bg-primary text-primary-foreground rounded-md">
  Click me
</button>
```

```css
/* In tokens.semantic.css */
:root {
  --primary-default: #3b82f6;
  --primary-foreground: #ffffff;
}
.dark {
  --primary-default: #60a5fa;
}
```

### Dark Mode

Dark mode values are defined alongside light mode in the tokens:

```json
{
  "color": {
    "surface": {
      "light": { "default": { "$value": "#ffffff" } },
      "dark": { "default": { "$value": "#0f172a" } }
    }
  }
}
```

Toggle dark mode by adding/removing the `dark` class on `<html>` or `<body>`.

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

---

## ⚠️ CRITICAL: File Headers and Semantic Sections

**EVERY generated file MUST include Archeon headers and section markers.** This enables AI-native code navigation via the semantic index.

### File Header Format (REQUIRED at top of every file)

**Vue/HTML files:**
```vue
<!-- @archeon:file -->
<!-- @glyph CMP:LoginForm -->
<!-- @intent User login input and submission -->
<!-- @chain @v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard -->
```

**JavaScript/TypeScript files:**
```javascript
// @archeon:file
// @glyph STO:Auth
// @intent Authentication state management
// @chain @v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard
```

**Python files:**
```python
# @archeon:file
# @glyph API:POST./auth/login
# @intent Authentication endpoint for user login
# @chain @v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth/login => OUT:dashboard
```

### Section Markers (REQUIRED to wrap code blocks)

Wrap logical code blocks in section markers:

```javascript
// @archeon:section imports
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
// @archeon:endsection

// @archeon:section props_and_state
const email = ref('');
const password = ref('');
const loading = ref(false);
// @archeon:endsection

// @archeon:section handlers
async function submitLogin() {
  // implementation
}
// @archeon:endsection
```

### Standard Sections by Glyph Type

| Glyph Type | Required Sections |
|------------|-------------------|
| `CMP` | `imports`, `props_and_state`, `handlers`, `render`, `styles` |
| `STO` | `imports`, `state`, `actions`, `selectors` |
| `API` | `imports`, `models`, `endpoint`, `helpers` |
| `FNC` | `imports`, `implementation`, `helpers` |
| `EVT` | `imports`, `channels`, `handlers` |
| `MDL` | `imports`, `schema`, `methods`, `indexes` |

### Section Rules

1. **Sections MUST NOT nest** - no section inside another section
2. **Sections MUST be contiguous** - no gaps between start and end
3. **Section labels are STABLE** - don't rename without updating index
4. **Code edits occur INSIDE sections** - unless creating a new section

### ⚠️ MANDATORY: Update the Index After Creating Files

**Every time you create or modify a file with `@archeon:file` headers, you MUST run:**

```bash
# ALWAYS run after generating files to update ARCHEON.index.json
arc index build
```

This scans all files for `@archeon:file` headers and section markers, building the semantic index that enables AI navigation.

### Checking for Missing Headers

```bash
# Find files that should have headers but don't
arc index check

# Inject a header into an existing file
arc index inject --path <file> --glyph <GLYPH> --intent "<intent>" --chain "<chain>"
```

### Why This Matters

The semantic index (`archeon/ARCHEON.index.json`) enables:
- **AI attention routing** - LLMs know exactly which files/sections to read
- **Architecture awareness** - Every file declares its glyph ownership
- **Refactor stability** - Section names survive code movement (unlike line numbers)
- **Minimal context** - AI reads index metadata instead of entire files

**Without headers and sections, files are invisible to the Archeon system.**
'''
