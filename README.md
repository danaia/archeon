# Archeon

> Glyph-based architecture notation system for AI-orchestrated software development.

Archeon provides a hyper-compressed, human-readable **intermediate representation (IR)** that serves as both documentation and executable specification. It's a **constraint layer** that any LLM can understand, preventing hallucinations and architectural drift.

```
Without Archeon:  "AI, build a login"  → Random architecture every time

With Archeon:     "AI, build a login"  → NED:login => CMP:LoginForm => API:POST/auth
                                        → Same structure, any model, always
```

---

## Two Paths to Choose From

Archeon offers **two distinct workflows** depending on how much control and scaffolding you need:

|                  | **IDE AI Rules**                 | **Architecture Shapes**                       |
| ---------------- | -------------------------------- | --------------------------------------------- |
| **Best for**     | Existing projects, minimal setup | New projects, complete scaffolding            |
| **Setup time**   | < 1 minute                       | 2-3 minutes                                   |
| **What you get** | Glyph rules for your IDE         | Full project structure + pre-built components |
| **Command**      | `arc init` + `arc ai-setup`      | `arc init --arch nextjs-express`              |

---

### Path 1: IDE AI Rules (Lightweight)

**Best for:** Experienced developers who want AI assistance within existing projects or prefer minimal scaffolding.

**What you get:**

- IDE-specific configuration files (`.cursorrules`, `.github/copilot-instructions.md`, etc.)
- Your AI assistant learns the glyph system
- Chat-based architecture proposals
- Minimal project structure (just `archeon/ARCHEON.arcon` + templates)

**Setup:**

```bash
# 1. Install Archeon
git clone git@github.com:danaia/archeon.git
cd archeon
pip install -e .

# 2. Initialize minimal structure (in your project directory)
cd ..
mkdir my-app && cd my-app
arc init

# 3. Generate IDE rules
arc ai-setup --cursor      # For Cursor
arc ai-setup --copilot     # For GitHub Copilot
arc ai-setup --windsurf    # For Windsurf
arc ai-setup               # Or all at once
```

**Now just chat with your IDE** — it reads `ARCHEON.arcon` and proposes architecture.

---

### Path 2: Architecture Shapes (Complete Scaffolding)

**Best for:** New projects, teams wanting consistency, or full-stack setup out of the box.

> **Key Insight:** Shapes are **100% customizable JSON files**. You define the exact code patterns, naming conventions, and structure your AI will follow. No more "AI does it differently every time" — your team's coding standards become the AI's training data.

**What you get:**

- **Complete project scaffolding** (client/, server/, pre-configured build tools)
- **Pre-built components** (ThemeToggle, ThemeSelector, design tokens)
- **Framework-specific templates** for every glyph (CMP, STO, API, MDL, EVT, FNC)
- **Full dependency management** (package.json, requirements.txt, pre-configured)
- **Tailwind + theming system** ready to use
- **Test stubs** auto-generated with components
- **Everything the AI needs** to generate production-ready code immediately

**Setup:**

```bash
# 1. Install Archeon
git clone git@github.com:danaia/archeon.git
cd archeon
pip install -e .

# 2. View available shapes
arc shapes

# 3. Initialize with a complete architecture (in your project directory)
cd ..
mkdir my-app && cd my-app
arc init --arch nextjs-express     # Next.js 14 + Express + TypeScript (RECOMMENDED)
arc init --arch vue3-fastapi       # Vue 3 + FastAPI + MongoDB
arc init --arch react-fastapi      # React + FastAPI + MongoDB

# 4. Optional: Add IDE rules too
arc ai-setup
```

**Available Shapes:**

| Shape ID         | Stack                                                  | What's Included                                        |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------ |
| `nextjs-express` | **Next.js 14, Zustand, Express, TypeScript, Mongoose** | **Modern full-stack, App Router, RSC, Zod validation** |
| `vue3-fastapi`   | Vue 3, Pinia, Tailwind, FastAPI, MongoDB               | Complete monorepo, theme system, pre-built components  |
| `react-fastapi`  | React, Zustand, Tailwind, FastAPI, MongoDB             | Complete monorepo, theme system, pre-built components  |

**Project structure after shape initialization (nextjs-express):**

```
my-app/
├── client/                 # Next.js 14 frontend
│   ├── src/
│   │   ├── app/            # App Router pages (RSC)
│   │   ├── components/     # Pre-built: ThemeToggle, ThemeProvider
│   │   ├── stores/         # Zustand stores
│   │   ├── lib/            # Utils (cn helper included)
│   │   └── types/          # TypeScript definitions
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
├── server/                 # Express + TypeScript backend
│   ├── src/
│   │   ├── api/
│   │   │   ├── routes/     # Express routes + Zod validation
│   │   │   └── middleware/
│   │   ├── models/         # Mongoose TypeScript models
│   │   ├── events/         # Event emitters
│   │   └── types/
│   ├── tsconfig.json
│   └── package.json
└── archeon/
    ├── ARCHEON.arcon       # Knowledge graph
    └── architectures/
        └── nextjs-express.shape.json  # Your customizable shape
```

**The difference:** Shapes generate **everything** — not just rules, but actual working code, configs, and dependencies. Your AI assistant can immediately start implementing features using the pre-built patterns.

---

## Quick Comparison

| Feature                   | IDE AI Rules                     | Architecture Shapes                               |
| ------------------------- | -------------------------------- | ------------------------------------------------- |
| **Setup Time**            | < 1 min                          | 2-3 min                                           |
| **Project Scaffolding**   | Minimal (archeon/ only)          | Complete (client/, server/, configs)              |
| **Pre-built Components**  | ❌                               | ✅ ThemeToggle, ThemeSelector                     |
| **Design Tokens**         | ❌                               | ✅ Pre-configured Tailwind theming                |
| **Framework Templates**   | Basic reference only             | ✅ Production-ready glyph snippets                |
| **Dependencies**          | Manual setup                     | ✅ Auto-configured package.json, requirements.txt |
| **Team Coding Standards** | AI improvises                    | ✅ **Enforced via JSON — 100% your rules**        |
| **Best For**              | Existing projects, minimal setup | New projects, teams, full-stack apps              |
| **AI Code Quality**       | Good (with manual refinement)    | Excellent (follows shape blueprints)              |

---

## The Easiest Way: IDE Chat

> **Just chat with your IDE AI assistant. No commands to memorize.**

Whether you choose **IDE rules** or **shapes**, the daily workflow is the same: natural conversation in your AI-powered IDE — VS Code, Cursor, Windsurf, or any editor with AI chat. Your AI assistant reads `ARCHEON.arcon`, proposes architecture, and implements everything.

### Your Daily Workflow

Open your IDE and describe what you want in natural language:

```
You: "User wants to register with email and password, then see their dashboard"

AI: Creating Archeon chain:

    @v1 NED:register => TSK:submit => CMP:RegisterForm => STO:Auth
        => API:POST/register => MDL:user.create => OUT:redirect('/dashboard')

    ✓ Added chain to archeon/ARCHEON.arcon
    ✓ Generated CMP:RegisterForm → client/src/components/RegisterForm.vue
    ✓ Generated STO:Auth → client/src/stores/AuthStore.js
    ✓ Generated API:POST/register → server/src/api/routes/register.py
    ✓ Generated MDL:user → server/src/models/user.py

    Done! Registration flow is ready.
```

**No terminal commands. Just conversation.** The AI executes directly — no approval needed.

### Iterative Refinement

```
You: "Add profile editing"

AI: @v1 NED:editProfile => CMP:ProfileForm => OUT:result
    ✓ Created ProfileForm component

You: "Save to database through API"

AI: Updated chain:
    @v1 NED:editProfile => CMP:ProfileForm
        => API:PUT/profile => MDL:user.update => OUT:toast('Profile saved')

    ✓ Added API endpoint
    ✓ Added user model update method

You: "Also add image upload for avatar"

AI: Final chain:
    @v1 NED:editProfile => V:ProfilePage @ CMP:ProfileForm, CMP:AvatarUpload
        => TSK:submit => API:PUT/profile => MDL:user.update
        => OUT:toast('Profile saved')

    ✓ Added AvatarUpload component
    ✓ Updated ProfilePage view
    Done!
```

**With shapes:** The AI pulls from your shape's pre-built component templates, ensuring consistent patterns across all features.

---

Archeon is **rule-based** — it generates IDE-specific configuration files that constrain your AI assistant to the glyph taxonomy. This works with **both approaches** (IDE rules or shapes):

| IDE                   | Command                   | Creates                           | Works With         |
| --------------------- | ------------------------- | --------------------------------- | ------------------ |
| **Cursor**            | `arc ai-setup --cursor`   | `.cursorrules`                    | IDE Rules + Shapes |
| **Windsurf**          | `arc ai-setup --windsurf` | `.windsurfrules`                  | IDE Rules + Shapes |
| **VS Code + Copilot** | `arc ai-setup --copilot`  | `.github/copilot-instructions.md` | IDE Rules + Shapes |
| **Cline/Claude Dev**  | `arc ai-setup --cline`    | `.clinerules`                     | IDE Rules + Shapes |
| **Aider**             | `arc ai-setup --aider`    | `.aider.conf.yml`                 | IDE Rules + Shapes |
| **All at once**       | `arc ai-setup`            | All of the above                  | IDE Rules + Shapes |

**Shapes + IDE Rules = Maximum Power:** Initialize with a shape for complete scaffolding, then run `arc ai-setup` so your AI assistant understands how to extend it.

---

## Why Archeon?

```
Without Archeon:  "AI, build me a login"  → Random architecture every time

With Archeon:     "AI, build me a login"
                  → AI writes: NED:login => CMP:LoginForm => API:POST/auth => OUT:dashboard
                  → Same structure, any model, always
```

**Anti-hallucination** - Models can't invent random patterns. Glyphs define what's allowed.  
**Anti-drift** - Context persists in `.arcon` files, not in chat history.  
**Model-portable** - Switch Claude to GPT mid-project. The graph remains.

### Measured Impact

| Metric                   | Traditional AI  | Archeon     |
| ------------------------ | --------------- | ----------- |
| Structural drift         | 60% of features | **0%**      |
| Missing outcomes         | 42% incomplete  | **0%**      |
| Time to valid code       | ~35 min         | **~10 min** |
| Structural rework        | 60%             | **~1-2%**   |
| Weekly refactor overhead | 3+ hrs          | **<10 min** |

---

## Glyph Notation

| Prefix | Name      | Layer  | Description                      |
| ------ | --------- | ------ | -------------------------------- |
| `NED:` | Need      | Meta   | User intent/motivation           |
| `TSK:` | Task      | Meta   | User action                      |
| `CMP:` | Component | Client | UI component (React/Vue)         |
| `STO:` | Store     | Client | State management (Zustand/Pinia) |
| `API:` | API       | Server | HTTP endpoint                    |
| `MDL:` | Model     | Server | Database model                   |
| `EVT:` | Event     | Server | Event handler                    |
| `FNC:` | Function  | Shared | Utility function                 |
| `OUT:` | Output    | Meta   | Success outcome                  |
| `ERR:` | Error     | Meta   | Failure path                     |

## Edge Types

| Operator | Type        | Description               |
| -------- | ----------- | ------------------------- |
| `=>`     | Structural  | Data flow (no cycles)     |
| `~>`     | Reactive    | Subscriptions (cycles OK) |
| `->`     | Control     | Branching/conditionals    |
| `::`     | Containment | Parent-child grouping     |

---

## 🔧 CLI Commands: Surgical Precision

> **For automation, CI/CD, scripts, and fine-grained control — the CLI gives you direct access to every Archeon operation.**

While IDE chat is the most intuitive daily workflow, the CLI unlocks precision operations for both IDE rules and shapes workflows:

### Project Initialization

```bash
# First, install Archeon (if not already installed)
git clone git@github.com:danaia/archeon.git
cd archeon && pip install -e .

# Lightweight: IDE rules only (minimal scaffolding)
cd .. && mkdir my-app && cd my-app
arc init
arc ai-setup

# Complete: Architecture shape (full scaffolding)
arc shapes                              # List available shapes
arc init --arch nextjs-express          # Next.js 14 + Express + TypeScript
arc init --arch vue3-fastapi            # Vue 3 + FastAPI + MongoDB
arc init --arch react-fastapi           # React + FastAPI + MongoDB
arc init --arch nextjs-express --copilot  # With IDE rules included

# Manual framework selection (uses shapes behind the scenes)
arc init --frontend vue3 --backend fastapi
```

### Core Commands

```bash
arc parse "<chain>"                                    # Add chain directly to graph
arc gen                                                # Generate code from graph
arc validate                                           # Check architecture integrity
arc status                                             # Show graph statistics
arc legend                                             # Display all glyphs
arc audit                                              # Check for architectural drift
arc run "<chain>" [--sandbox]                          # Execute headless
arc shapes                                             # List available architecture shapes
```

### Natural Language via CLI

```bash
# Intent parsing (same engine the IDE uses)
arc i "User wants to login with email and password"
arc intent --file requirements.md
arc i "User needs to checkout their cart" --auto-errors
```

### Direct Chain Parsing

For maximum control, write chains directly:

```bash
# Parse and add a specific chain
arc parse "NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard"

# Dry run - validate without adding to graph
arc parse "NED:test => CMP:Test" --dry-run

# Parse with version tag
arc parse "@v2 NED:login => CMP:OAuthButton => API:GET/auth/google" --version v2
```

### Example CLI Session

```bash
$ arc i "User needs to register with email and password, then see their dashboard"

╭─ Proposal 1 ─────────────────────────────────────────────────────────────────╮
│ NED:register => TSK:submit => CMP:RegisterForm => STO:Auth                   │
│     => API:POST/register => MDL:user.create => OUT:redirect('/dashboard')    │
│                                                                              │
│ Confidence: HIGH                                                             │
│ Reasoning:                                                                   │
│   • Found need: register                                                     │
│   • Found task: submit                                                       │
│   • Detected form component                                                  │
│   • Found outcome: dashboard redirect                                        │
╰──────────────────────────────────────────────────────────────────────────────╯

Suggested error paths:
  → API:POST/register -> ERR:auth.emailExists
  → API:POST/register -> ERR:validation.invalid

Action [a/e/r/s] (r): a
✓ Added chain to graph

$ arc gen
✓ Generated CMP:RegisterForm → client/src/components/RegisterForm.vue
✓ Generated STO:Auth → client/src/stores/AuthStore.js
✓ Generated API:POST/register → server/src/api/routes/register.py
✓ Generated MDL:user → server/src/models/user.py
```

### When to Use CLI vs IDE Chat

| Use Case                     | Recommendation                 |
| ---------------------------- | ------------------------------ |
| **New project setup**        | CLI: `arc init --arch <shape>` |
| Daily feature development    | IDE Chat                       |
| Exploring ideas              | IDE Chat                       |
| Processing requirements docs | CLI: `arc i --file`            |
| CI/CD pipeline validation    | CLI: `arc validate`            |
| Scripted batch operations    | CLI                            |
| Debugging chain parsing      | CLI: `arc parse --dry-run`     |
| Architecture audits          | CLI: `arc audit`               |
| Browse available stacks      | CLI: `arc shapes`              |

---

## Understanding Architecture Shapes

**Architecture Shapes** are the secret to Archeon's robustness. They're JSON-based blueprints that define **everything** your project needs:

### What's Inside a Shape?

```json
{
  "meta": {
    "id": "vue3-fastapi",
    "name": "Vue 3 + FastAPI",
    "version": "1.0.0"
  },
  "stack": {
    "frontend": { "framework": "vue3", "stateManager": "pinia" },
    "backend": { "framework": "fastapi", "language": "python" }
  },
  "glyphs": {
    "CMP": {
      "extension": ".vue",
      "directory": "client/src/components",
      "snippet": "<!-- Production-ready Vue 3 component template -->"
    },
    "STO": {
      "extension": ".js",
      "directory": "client/src/stores",
      "snippet": "// Pinia store with TypeScript support"
    }
  },
  "prebuilt": {
    "components": ["ThemeToggle.vue", "ThemeSelector.vue"],
    "stores": ["theme.js"]
  },
  "dependencies": {
    "client": { "vue": "^3.3.0", "pinia": "^2.1.0" },
    "server": { "fastapi": "^0.104.0" }
  }
}
```

### Why Shapes Are More Powerful

| Aspect                   | IDE Rules Only            | With Architecture Shapes                         |
| ------------------------ | ------------------------- | ------------------------------------------------ |
| **Project setup**        | Manual directory creation | ✅ Auto-scaffolded client/, server/              |
| **Component templates**  | Generic, AI-generated     | ✅ Framework-specific, production-ready          |
| **Dependencies**         | Manual install            | ✅ Pre-configured package.json, requirements.txt |
| **Theming system**       | Build yourself            | ✅ Tailwind + design tokens ready                |
| **Pre-built components** | None                      | ✅ ThemeToggle, ThemeSelector, theme store       |
| **Build tools**          | Manual config             | ✅ Vite/Webpack pre-configured                   |
| **Code consistency**     | Varies by AI session      | ✅ Enforced by shape templates                   |
| **Customizability**      | AI learns from examples   | ✅ **100% controlled via JSON schema**           |
| **Onboarding speed**     | Hours to days             | ✅ Minutes                                       |

### Creating Custom Shapes — **Train AI to Your Coding Style**

**This is where teams gain true control.** Every shape is just a JSON file that defines:

- Component/API/Store code templates with **your** preferred patterns
- **Your** naming conventions, file structure, import style
- **Your** testing patterns, error handling, validation logic
- **Your** design tokens, theme system, utility functions

**Shapes are training data for your AI.** When you create a custom shape, you're teaching the AI exactly how your team writes code.

**Example: Custom React component style**

```json
{
  "glyphs": {
    "CMP": {
      "snippet": "// YOUR team's component template\nimport { FC } from 'react';\nimport { cn } from '@/lib/utils';  // Your util\n\ninterface {{NAME}}Props {\n  className?: string;\n}\n\nexport const {{NAME}}: FC<{{NAME}}Props> = ({ className }) => {\n  return (\n    <div className={cn('your-base-class', className)}>\n      {/* Your structure */}\n    </div>\n  );\n};"
    }
  }
}
```

**Every component the AI generates will follow this exact pattern.** No variation. No hallucination. Just your team's standards, every time.

**Want your API routes to follow a specific error handling pattern?**

```json
{
  "glyphs": {
    "API": {
      "snippet": "from fastapi import APIRouter, HTTPException\nfrom your_company.middleware import log_request, validate_auth\n\nrouter = APIRouter()\n\n@router.{{METHOD}}('{{PATH}}')\n@log_request  # Your custom decorator\n@validate_auth  # Your auth pattern\nasync def {{NAME}}():\n    try:\n        # Implementation\n        pass\n    except Exception as e:\n        # Your error handling\n        raise HTTPException(status_code=500, detail=str(e))"
    }
  }
}
```

**Every endpoint follows your company's middleware stack, logging, and error patterns.**

Create a `.shape.json` file in `archeon/architectures/` and run `arc init --arch your-shape`. See the [Architecture Shapes wiki](https://github.com/danaia/archeon/wiki/Architecture-Shapes) for complete JSON schema specification.

---

## Project Structure

**With IDE Rules Only (Minimal):**

```
my-app/
├── .archeonrc           # Config
└── archeon/
    ├── ARCHEON.arcon    # Knowledge graph
    └── templates/       # Reference templates only
```

**With Architecture Shape (Complete):**

```
my-app/
├── .archeonrc           # Config (frontend, backend, paths)
├── client/              # Frontend code (CMP, STO)
│   ├── src/
│   │   ├── components/  # Pre-built: ThemeToggle, ThemeSelector
│   │   ├── stores/      # Pre-built: theme store
│   │   └── tokens/      # Design tokens (CSS, JS, Tailwind)
│   ├── package.json     # Dependencies auto-configured
│   └── vite.config.js   # Build tool pre-configured
├── server/              # Backend code (API, MDL, EVT)
│   ├── src/
│   │   ├── api/routes/
│   │   ├── models/
│   │   └── events/
│   └── requirements.txt # Python dependencies ready
└── archeon/
    ├── ARCHEON.arcon    # Knowledge graph
    └── templates/       # Framework-specific glyph templates
```

    └── ARCHEON.arcon    # Knowledge graph (the source of truth)

````

---

## Installation

```bash
# Clone and install from GitHub
git clone git@github.com:danaia/archeon.git
cd archeon
pip install -e .

# Verify installation
arc --version

# Quick start - choose your path:
# Path 1: Lightweight IDE rules
cd ..
mkdir my-app && cd my-app
arc init
arc ai-setup

# Path 2: Complete architecture shape
cd ..
mkdir my-app && cd my-app
arc init --arch nextjs-express
arc ai-setup  # Optional but recommended

# Uninstall
pip uninstall archeon
```

# Verify installation
arc --version

# Quick start - choose your path:
# Path 1: Lightweight IDE rules
mkdir my-app && cd my-app
arc init
arc ai-setup

# Path 2: Complete architecture shape
mkdir my-app && cd my-app
arc init --arch vue3-fastapi
arc ai-setup  # Optional but recommended

# Uninstall
pip uninstall archeon
````

---

## Documentation

For complete guides, see the [wiki documentation](https://github.com/danaia/archeon/wiki):

### Getting Started

- [Installation](https://github.com/danaia/archeon/wiki/Installation) — Install via pip
- [Quick Start](https://github.com/danaia/archeon/wiki/Quick-Start) — First project in 5 minutes

### Core Concepts

- [Glyph Reference](https://github.com/danaia/archeon/wiki/Glyph-Reference) — All 16 glyph types
- [Chain Syntax](https://github.com/danaia/archeon/wiki/Chain-Syntax) — Composition rules and validation
- [Natural Language Intent](https://github.com/danaia/archeon/wiki/Natural-Language-Intent) — Plain English → chains
- [Knowledge Graph](https://github.com/danaia/archeon/wiki/Knowledge-Graph) — The `.arcon` file explained
- [Architecture Shapes](https://github.com/danaia/archeon/wiki/Architecture-Shapes) — **Creating and using shape blueprints**

### Reference

- [CLI Commands](https://github.com/danaia/archeon/wiki/CLI-Commands) — Complete command reference
- [Templates](https://github.com/danaia/archeon/wiki/Templates) — Template customization
- [Architecture](https://github.com/danaia/archeon/wiki/Architecture) — System design and mechanisms

---

## Development

```bash
# Clone and install with dev dependencies
git clone <repo>
cd Archeon
pip install -e ".[dev]"

# Run tests
pytest archeon/tests/ -v
```

## License

MIT
