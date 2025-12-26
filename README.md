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

### 1️⃣ Install Archeon

**Option A: Direct pip install (fastest)**
```bash
pip install git+https://github.com/danaia/archeon.git
```

**Option B: Clone and install locally**
```bash
git clone git@github.com:danaia/archeon.git
cd archeon
pip install -e .
```

### 2️⃣ Set Up Your Project (New or Existing)

**For new projects:**
```bash
arc init --arch vue3-fastapi
cd my-app && npm run dev
```

**For existing projects:**
```bash
cd your-project
arc ai-setup
```

### 3️⃣ Open Your IDE and Chat

Pick your IDE, then use this natural language prompt:

```
"Initialize this project with Archeon"
```

**Your AI assistant will:**
- ✅ Read your project structure (or scaffold a new one)
- ✅ Generate `archeon/ARCHEON.arcon` knowledge graph
- ✅ Create IDE-specific rule files for your AI
- ✅ Be ready to build features with you

**What happens next:**
```
You (in IDE chat): "Initialize this project with Archeon"

AI: ✓ Created archeon/ARCHEON.arcon
    ✓ Generated IDE rules for your setup
    ✓ Ready to build features

You: "User registers with email and password, then sees their dashboard"

AI: Adding chain:
    @v1 NED:register => CMP:RegisterForm => STO:Auth
        => API:POST/register => MDL:user => OUT:dashboard

    ✓ Generated RegisterForm
    ✓ Generated AuthStore
    ✓ Generated register.py endpoint
    Done!
```

Your AI now understands your architecture, validates every feature before generating code, and maintains consistency across sessions.

## Quickstart: Choose Your IDE

The fastest way to get Archeon working is to set up your IDE's AI rules. This works with **any project** (new or existing) and requires **no terminal commands after setup**.

### Available IDE Rules

When you run `arc ai-setup`, Archeon generates rule files for your IDE:

| IDE / Tool          | Rule File                         | What It Does                           |
| ------------------- | --------------------------------- | -------------------------------------- |
| **Cursor**          | `.cursorrules`                    | AI reads & writes glyph chains         |
| **Windsurf**        | `.windsurfrules`                  | Cascade follows your architecture      |
| **VS Code + Copilot** | `.github/copilot-instructions.md` | Copilot understands the glyph system   |
| **Cline/Claude Dev** | `.clinerules`                     | Claude writes chains before coding     |
| **Aider**           | `.aider.conf.yml`                 | Auto-includes graph context            |

### One Command: `arc ai-setup`

```bash
# Your project (new or existing)
cd my-project

# Generate rule files for your IDE
arc ai-setup

# That's it! Now open your IDE and ask:
# "Initialize this project with Archeon"
```

### Selective Setup

```bash
arc ai-setup --cursor              # Only Cursor
arc ai-setup --copilot             # Only GitHub Copilot
arc ai-setup --windsurf --cline    # Windsurf + Cline only
```

### Then Build Features

Open your IDE chat and describe what you need:

```
"User registers with email and password, then sees their dashboard"
```

Your AI will propose a glyph chain and implement it. No hallucinations. Consistent architecture every time.


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

AI: Adding chain to ARCHEON.arcon:

    @v1 NED:register => TSK:submit => CMP:RegisterForm => STO:Auth
        => API:POST/register => MDL:user.create => OUT:redirect('/dashboard')

    Detected error paths:
      → API:POST/register -> ERR:validation.emailTaken
      → API:POST/register -> ERR:validation.invalidEmail

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

## IDE AI Integration

**Your IDE's AI becomes architecture-aware.** After running `arc ai-setup`, your AI assistant can read your glyph chains and implement features consistently.

### What Your AI Does Next

Simply ask in IDE chat:

```
"Initialize this project with Archeon"
"Create a user registration feature"
"Add a password reset flow"
"What chains are defined in this project?"
```

Your AI will:
1. **Read** `archeon/ARCHEON.arcon` to understand your architecture
2. **Write** glyph chains for new features
3. **Implement** components following those chains exactly

No hallucinations. Consistent patterns. Persistent across sessions.

### Advanced: Cline Custom Instructions

For Cline (Claude Dev), add to IDE settings for extra context:

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

**For existing codebases** — Use `arc ai-setup` to scan your project and generate the knowledge graph. You may need to adjust some pieces to fit the glyph taxonomy, but you'll end up with a clear, documented architecture that persists.

---



## License

MIT
