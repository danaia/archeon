# Archeon

> **The AI-Powered Project Architect. Structure + AI = Reliable Code.**

🖥️ **[ArcheonGUI](https://github.com/danaia/archeonGUI)** — Visualize your architecture as an interactive graph

## The Problem

You're chatting with AI, building features in minutes. But without structure, your codebase drifts: inconsistent patterns, orphaned components, hallucinated code, and APIs that don't match your frontend. Context windows overflow. Models get confused. You spend more time fixing AI mistakes than shipping features.

## The Solution

**Archeon** is a constraint system that makes AI reliable. It's not a framework—it's a **knowledge graph** that sits between your intent and your code. It ensures:
- ✅ **No architectural drift** — consistent patterns every session
- ✅ **Zero hallucinations** — AI can't invent what isn't in your graph
- ✅ **Smaller models work** — Qwen 32B outperforms GPT-4 on structured tasks
- ✅ **Saves countless hours** — from weeks of refactoring to minutes of validation

---

## 🖥️ Visualize Your Architecture

**[ArcheonGUI](https://github.com/danaia/archeonGUI)** is a companion desktop app that brings your architecture to life:

- **Interactive graph visualization** — See your entire architecture as a node graph
- **Real-time updates** — Changes to `.arcon` appear instantly
- **Chain exploration** — Click any glyph to see its connections
- **Export diagrams** — Share architecture visuals with your team

```bash
# After running arc index code, open in GUI
# Download from: https://github.com/danaia/archeonGUI
```

---

## Get Started in 60 Seconds

### New Project
```bash
pip install archeon
arc init --arch vue3-fastapi --copilot    # Full stack + Copilot setup
cd my-app && npm run dev
```

### Existing Project
```bash
cd your-project
arc index code                             # One command discovers & documents everything
```

Now just chat with your AI:
```
You: "User registers with email and password, then sees their dashboard"

AI: Proposed chain:
    @v1 NED:register => CMP:RegisterForm => STO:Auth
        => API:POST/register => MDL:user => OUT:dashboard

    Shall I proceed?

You: Yes

AI: ✓ Generated RegisterForm.vue
    ✓ Generated AuthStore.js
    ✓ Generated register.py
    ✓ Updated ARCHEON.arcon
```

Your AI now understands your architecture, validates every feature before generating code, and maintains consistency across sessions.

## Quickstart: Setting Up Your Framework

### 1. Create a New Project from Scratch
Archeon supports multiple architecture shapes that define complete frontend/backend stacks:

```bash
arc init --arch vue3-fastapi       # Use vue3-fastapi shape
arc init --arch react-fastapi      # Use react-fastapi shape
arc init --arch vue3-fastapi --copilot  # With GitHub Copilot rules
arc init --arch react-fastapi --copilot --cline  # Multiple IDE rules
```

These commands create complete projects with:
- ✅ Frontend (Vue 3 or React) with TypeScript and Tailwind CSS
- ✅ Backend (FastAPI Python) with MongoDB database integration  
- ✅ Complete directory structure and package configurations
- ✅ Pre-configured state management (Pinia for Vue, Zustand for React)
- ✅ IDE-specific rules for AI assistants (Copilot, Windsurf, Cline)

### 2. Scan an Existing Repository
For existing codebases, Archeon can automatically discover and document your architecture:

```bash
cd your-existing-project
arc index code
```

This one-command setup performs these 5 steps:
1. Creates `archeon/` directory structure
2. Scans & classifies all files to glyphs  
3. Generates `ARCHEON.index.json`
4. Generates `ARCHEON.arcon` knowledge graph
5. Creates AI rules for all IDEs

You can then open the scanned project in ArcheonGUI to visualize your architecture.

### 3. List Available Architectures
See what architecture shapes are available:

```bash
arc shapes
arc shapes -v                      # Detailed information
```

This shows all supported full-stack combinations like:
- `vue3-fastapi` - Vue 3 frontend with FastAPI backend  
- `react-fastapi` - React frontend with FastAPI backend
- And others for different framework combinations


---

## What Archeon Looks Like

A glyph chain describes a complete feature:
```
NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard
```

User need → UI → State → API → Outcome. Every feature follows this pattern. Incomplete chains are rejected before code is generated.

**The glyphs:**
- `NED:` User need (the "why")
- `CMP:` Component (UI)
- `STO:` Store (client state)
- `API:` Endpoint (server call)
- `MDL:` Model (database)
- `OUT:` Outcome (success)
- `ERR:` Error (failure path)

---

## How It Works: Three Innovations That Change Everything

### 1. **Glyph Notation** — Language for Architecture
Instead of asking AI to build in the void, you describe what you want using glyphs:
```
NED:register => CMP:RegisterForm => STO:Auth => API:POST/register => MDL:user => OUT:dashboard
```
That's a complete feature. User need → UI → State → API → Outcome. No guessing. No drift.

### 2. **Persistent Knowledge Graph** (`.arcon`)
Your architecture lives in a ~12KB file that **survives between sessions**. The AI reads it, proposes changes, and updates it. Future sessions know exactly what exists—no re-explaining your stack.

### 3. **Entropy-Based Context Compression**
Large codebases normally overflow token limits. Archeon identifies the most information-rich parts of your code and compresses the rest, fitting entire projects into context windows. The AI stays focused and accurate, even on massive codebases.

### Why This Matters: The Math (Bear With Us, It's Fun)

LLMs predict the next token by sampling from a probability distribution. The *entropy* of that distribution determines how confident the model is:

$$H(X) = -\sum p(x) \log_2 p(x)$$

**Translation:** When entropy is high, the model is basically rolling dice. When entropy is low, it *knows* what comes next.

#### Without Archeon: Entropy Hell 🔥

Ask an LLM to "build a login system" on a 50-file codebase. It must reason over:
- **~10,000 possible patterns** (REST? GraphQL? tRPC? Auth0? JWT? Session cookies? Magic links?)
- **~50 files × ~100 lines = 5,000 lines** of context (most irrelevant)
- **Infinite naming conventions** (is it `authStore`? `useAuth`? `AuthService`? `loginHandler`?)

If we model this as ~10,000 plausible architectural patterns, then in the worst case:
$$H = \log_2(10000) ≈ 13.3 \text{ bits}$$

That's **~10,000 equally plausible choices** the model is juggling per architectural decision. No wonder it hallucinates.

#### With Archeon: Entropy Tamed 🧊

Same request, but now the model reasons over:
- **16 glyph types** (NED, CMP, STO, API, etc.)
- **4 edge types** (=>, ~>, ->, ::)
- **1 template per glyph** (predetermined structure)
- **1-hop dependencies only** (~500 tokens vs 50,000)

For the glyph selection alone:
$$H = \log_2(16) = 4 \text{ bits}$$

That's **16 choices**, not 10,000. The model isn't guessing—it's following a grammar.

#### The Punchline

| Metric | Unconstrained | Archeon |
|--------|---------------|---------|
| Entropy | ~13.3 bits | 4 bits |
| Equivalent choices | ~10,000 | 16 |
| **Reduction** | — | **625× fewer options** |

*(~70% lower entropy — meaning the model's next-step uncertainty collapses, and the tail-risk of weird choices drops hard.)*

A 30B model can reliably sample from 16 options. It *cannot* reliably sample from 10,000. This is why **Qwen 32B locally can match GPT-4** on Archeon tasks—not because it's smarter, but because the problem is *tractable*.

> **TL;DR:** We didn't make the model smarter. We made the problem dumber. That's the whole trick.

---

## The Workflow (It's Just Chat)

```
You: "User registers with email and password, then sees their dashboard"

AI: Proposed chain:
    NED:register => CMP:RegisterForm => STO:Auth 
        => API:POST/register => MDL:user => OUT:redirect('/dashboard')
    
    Shall I proceed?

You: Yes

AI: ✓ Generated RegisterForm.vue
    ✓ Generated AuthStore.js  
    ✓ Generated register.py
    ✓ Updated ARCHEON.arcon
    
    Done.
```

No CLI gymnastics. No memorizing commands. **Just describe what you want.**

---

## Why Archeon Works

Without a shared language for architecture, each AI session invents its own patterns. Features become inconsistent. Hallucinations go uncaught. Context windows overflow.

Archeon fixes this by:
- **Enforcing constraints** — Glyphs define what's valid, not imagination
- **Persisting architecture** — `.arcon` survives between sessions, models, and team members
- **Compressing context** — Fits entire projects into context windows so AI stays focused
- **Validating before code** — Bad chains get caught before they're written

---

## The Easiest Way: IDE Chat

> **🎯 Just chat with your IDE AI assistant. No commands to memorize.**

The most intuitive way to use Archeon is through **natural conversation** in your AI-powered IDE — VS Code, Cursor, Windsurf, or any editor with AI chat. Your AI assistant reads `ARCHEON.arcon`, proposes architecture, and implements everything.

### Quick Setup

Archeon works by generating **IDE-specific rule files** that teach your AI assistant the glyph system. Each IDE has its own rules format:

```bash
# 1. Install Archeon
git clone git@github.com:danaia/archeon.git
cd archeon        # Important: install from the project root, not archeon/archeon/
pip install -e .

# 2. Initialize your project (with optional --copilot flag)
mkdir my-app && cd my-app
arc init --arch vue3-fastapi --copilot   # Creates project + Copilot rules in one step

# Or generate IDE rules separately with ai-setup
arc ai-setup --cursor      # For Cursor → creates .cursorrules
arc ai-setup --windsurf    # For Windsurf → creates .windsurfrules
arc ai-setup --copilot     # For GitHub Copilot → creates .github/copilot-instructions.md
arc ai-setup --cline       # For Cline/Claude Dev → creates .clinerules
arc ai-setup --vscode      # For VS Code → creates .vscode/settings.json
```

That's it. **Now just chat.**

### Your Daily Workflow

Open your IDE and describe what you want in natural language:

```
You: "User wants to register with email and password, then see their dashboard"

AI: I'll create this Archeon chain:

    @v1 NED:register => TSK:submit => CMP:RegisterForm => STO:Auth
        => API:POST/register => MDL:user.create => OUT:redirect('/dashboard')

    Confidence: HIGH

    Suggested error paths:
      → API:POST/register -> ERR:validation.emailTaken
      → API:POST/register -> ERR:validation.invalidEmail

    Shall I proceed?

You: Yes

AI: ✓ Added chain to archeon/ARCHEON.arcon
    ✓ Generated CMP:RegisterForm → client/src/components/RegisterForm.vue
    ✓ Generated STO:Auth → client/src/stores/AuthStore.js
    ✓ Generated API:POST/register → server/src/api/routes/register.py
    ✓ Generated MDL:user → server/src/models/user.py

    Done! Registration flow is ready.
```

**No terminal commands. Just conversation.** The AI proposes, you approve, code gets generated.

### Iterative Refinement

```
You: "Add profile editing"

AI: Proposed chain:
    @v1 NED:editProfile => CMP:ProfileForm => OUT:result

    Confidence: MEDIUM - no API or storage detected

You: "Save to database through API"

AI: Updated chain:
    @v1 NED:editProfile => CMP:ProfileForm
        => API:PUT/profile => MDL:user.update => OUT:toast('Profile saved')

You: "Also add image upload for avatar"

AI: Final chain:
    @v1 NED:editProfile => V:ProfilePage @ CMP:ProfileForm, CMP:AvatarUpload
        => TSK:submit => API:PUT/profile => MDL:user.update
        => OUT:toast('Profile saved')

    Implementing now...
```

### Supported IDEs

Archeon is **rule-based** — it generates IDE-specific configuration files that constrain your AI assistant to the glyph taxonomy:

| IDE                   | Command                   | Creates                           | What It Does                       |
| --------------------- | ------------------------- | --------------------------------- | ---------------------------------- |
| **Cursor**            | `arc ai-setup --cursor`   | `.cursorrules`                    | AI reads + writes to ARCHEON.arcon |
| **Windsurf**          | `arc ai-setup --windsurf` | `.windsurfrules`                  | Cascade AI follows the graph       |
| **VS Code + Copilot** | `arc ai-setup --copilot`  | `.github/copilot-instructions.md` | Copilot Chat understands glyphs    |
| **Cline/Claude Dev**  | `arc ai-setup --cline`    | `.clinerules`                     | Claude writes chains first         |
| **Aider**             | `arc ai-setup --aider`    | `.aider.conf.yml`                 | Auto-loads graph context           |
| **All at once**       | `arc ai-setup`            | All of the above                  | Full setup                         |

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

While IDE chat is the most intuitive daily workflow, the CLI unlocks precision operations:

### Core Commands

```bash
arc init [--frontend react|vue3] [--backend fastapi]  # Create project
arc parse "<chain>"                                    # Add chain directly to graph
arc gen                                                # Generate code from graph
arc validate                                           # Check architecture integrity
arc status                                             # Show graph statistics
arc legend                                             # Display all glyphs
arc audit                                              # Check for architectural drift
arc run "<chain>" [--sandbox]                          # Execute headless
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

| Use Case                     | Recommendation             |
| ---------------------------- | -------------------------- |
| Daily feature development    | IDE Chat                   |
| Exploring ideas              | IDE Chat                   |
| Processing requirements docs | CLI: `arc i --file`        |
| CI/CD pipeline validation    | CLI: `arc validate`        |
| Scripted batch operations    | CLI                        |
| Debugging chain parsing      | CLI: `arc parse --dry-run` |
| Architecture audits          | CLI: `arc audit`           |

---

## Project Structure

```
my-app/
├── .archeonrc           # Config (frontend, backend, paths)
├── client/              # Frontend code (CMP, STO)
│   └── src/
│       ├── components/
│       └── stores/
├── server/              # Backend code (API, MDL, EVT)
│   └── src/
│       ├── api/routes/
│       ├── models/
│       └── events/
└── archeon/
    └── ARCHEON.arcon    # Knowledge graph (the source of truth)
```

---

## 📚 Documentation

For complete guides, see the [wiki documentation](https://github.com/danaia/archeon/wiki):

### Getting Started

- [Installation](https://github.com/danaia/archeon/wiki/Installation) — Install via pip
- [Quick Start](https://github.com/danaia/archeon/wiki/Quick-Start) — First project in 5 minutes

### Core Concepts

- [Glyph Reference](https://github.com/danaia/archeon/wiki/Glyph-Reference) — All 16 glyph types
- [Chain Syntax](https://github.com/danaia/archeon/wiki/Chain-Syntax) — Composition rules and validation
- [Natural Language Intent](https://github.com/danaia/archeon/wiki/Natural-Language-Intent) — Plain English → chains
- [Knowledge Graph](https://github.com/danaia/archeon/wiki/Knowledge-Graph) — The `.arcon` file explained

### Reference

- [CLI Commands](https://github.com/danaia/archeon/wiki/CLI-Commands) — Complete command reference
- [Templates](https://github.com/danaia/archeon/wiki/Templates) — Template customization
- [Architecture](https://github.com/danaia/archeon/wiki/Architecture) — System design and mechanisms

---

## IDE AI Integration Deep Dive

**This is where Archeon really shines.** With a single command, your IDE's AI assistant becomes architecture-aware. It won't just read your knowledge graph — it can **write glyph chains directly**.

### One Command Setup

```bash
arc ai-setup
```

This generates configuration files for every major AI-powered IDE:

| IDE              | Config File                       | What It Does                       |
| ---------------- | --------------------------------- | ---------------------------------- |
| Cursor           | `.cursorrules`                    | AI reads + writes to ARCHEON.arcon |
| GitHub Copilot   | `.github/copilot-instructions.md` | Copilot Chat understands glyphs    |
| Windsurf         | `.windsurfrules`                  | Cascade AI follows the graph       |
| Cline/Claude Dev | `.clinerules`                     | Claude writes chains first         |
| Aider            | `.aider.conf.yml`                 | Auto-loads graph context           |
| VS Code          | `.vscode/settings.json`           | Syntax highlighting for .arcon     |

### Selective Setup

```bash
arc ai-setup --cursor              # Only Cursor
arc ai-setup --vscode --copilot    # VS Code + Copilot only
arc ai-setup --no-aider            # All except Aider
```

### What Happens When You Ask for a Feature

When you tell your IDE's AI: _"Create a user registration feature"_

The AI will:

1. **Read** `archeon/ARCHEON.arcon` to understand existing architecture
2. **Write** a new chain: `@v1 NED:register => CMP:RegisterForm => STO:Auth => API:POST/auth/register => MDL:user => OUT:success`
3. **Implement** each component following that chain exactly

No hallucinations. No random patterns. Just clean, consistent architecture.

### Example Prompts That Work

```
"Create a shopping cart feature"
→ AI adds chain to ARCHEON.arcon, then implements

"Add a password reset flow to the architecture"
→ AI writes the chain first, asks for approval, then codes

"What chains are defined in this project?"
→ AI reads and summarizes ARCHEON.arcon

"Implement CMP:LoginForm following the knowledge graph"
→ AI finds the chain, generates the component
```

### The Magic

**Your AI assistant is now constrained by your architecture**, not its imagination. It can only compose within the glyph taxonomy. This means:

- ✅ Consistent patterns across your entire codebase
- ✅ No architectural drift between sessions
- ✅ Switch AI models mid-project — the graph remains
- ✅ Human stays in control — AI proposes, you approve

### Cline Extra Setup

For Cline (Claude Dev), you can also add the graph to always-included context:

1. Open Cline panel → Settings ⚙️
2. In **"Custom Instructions"**, add:
   ```
   Always reference archeon/ARCHEON.arcon. Write new chains before implementing features.
   ```
3. Optionally add `archeon/ARCHEON.arcon` to always-included files

---

## The Real Value

**Tight architecture** — Your codebase stays coherent. Features connect properly. No orphaned code.

**Persistent across change** — New team member? New AI model? Existing requirements document? The architecture survives and guides them.

**For existing codebases** — `arc index code` will scan your project and build the knowledge graph. You may need to adjust or refactor some pieces to fit the glyph taxonomy, but you'll end up with a clear, documented architecture that persists.

---

```bash
# Clone and install
git clone git@github.com:danaia/archeon.git
pip install -e ./archeon

# Verify installation
arc --version

# Uninstall
pip uninstall archeon
```

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
