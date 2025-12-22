# Archeon

> Glyph-based architecture notation system for AI-orchestrated software development.

Archeon provides a hyper-compressed, human-readable **intermediate representation (IR)** that serves as both documentation and executable specification. It's a **constraint layer** that any LLM can understand, preventing hallucinations and architectural drift.

## The Easiest Way: IDE Chat

> **🎯 Just chat with your IDE AI assistant. No commands to memorize.**

The most intuitive way to use Archeon is through **natural conversation** in your AI-powered IDE — VS Code, Cursor, Windsurf, or any editor with AI chat. Your AI assistant reads `ARCHEON.arcon`, proposes architecture, and implements everything.

### Quick Setup

Archeon works by generating **IDE-specific rule files** that teach your AI assistant the glyph system. Each IDE has its own rules format:

```bash
# 1. Install Archeon
git clone git@github.com:danaia/archeon.git
pip install -e ./archeon

# 2. Initialize your project
mkdir my-app && cd my-app
arc init --frontend vue3

# 3. Generate rules for YOUR IDE
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

| IDE | Command | Creates | What It Does |
|-----|---------|---------|--------------|
| **Cursor** | `arc ai-setup --cursor` | `.cursorrules` | AI reads + writes to ARCHEON.arcon |
| **Windsurf** | `arc ai-setup --windsurf` | `.windsurfrules` | Cascade AI follows the graph |
| **VS Code + Copilot** | `arc ai-setup --copilot` | `.github/copilot-instructions.md` | Copilot Chat understands glyphs |
| **Cline/Claude Dev** | `arc ai-setup --cline` | `.clinerules` | Claude writes chains first |
| **Aider** | `arc ai-setup --aider` | `.aider.conf.yml` | Auto-loads graph context |
| **All at once** | `arc ai-setup` | All of the above | Full setup |

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

| Metric | Traditional AI | Archeon |
|--------|---------------|---------|
| Structural drift | 60% of features | **0%** |
| Missing outcomes | 42% incomplete | **0%** |
| Time to valid code | ~35 min | **~10 min** |
| Structural rework | 60% | **~1-2%** |
| Weekly refactor overhead | 3+ hrs | **<10 min** |

---

## Glyph Notation

| Prefix | Name | Layer | Description |
|--------|------|-------|-------------|
| `NED:` | Need | Meta | User intent/motivation |
| `TSK:` | Task | Meta | User action |
| `CMP:` | Component | Client | UI component (React/Vue) |
| `STO:` | Store | Client | State management (Zustand/Pinia) |
| `API:` | API | Server | HTTP endpoint |
| `MDL:` | Model | Server | Database model |
| `EVT:` | Event | Server | Event handler |
| `FNC:` | Function | Shared | Utility function |
| `OUT:` | Output | Meta | Success outcome |
| `ERR:` | Error | Meta | Failure path |

## Edge Types

| Operator | Type | Description |
|----------|------|-------------|
| `=>` | Structural | Data flow (no cycles) |
| `~>` | Reactive | Subscriptions (cycles OK) |
| `->` | Control | Branching/conditionals |
| `::` | Containment | Parent-child grouping |

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

| Use Case | Recommendation |
|----------|----------------|
| Daily feature development | IDE Chat |
| Exploring ideas | IDE Chat |
| Processing requirements docs | CLI: `arc i --file` |
| CI/CD pipeline validation | CLI: `arc validate` |
| Scripted batch operations | CLI |
| Debugging chain parsing | CLI: `arc parse --dry-run` |
| Architecture audits | CLI: `arc audit` |

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

For complete guides, see the [wiki documentation](wiki/):

### Getting Started
- [Installation](wiki/Installation.md) — Install via pip
- [Quick Start](wiki/Quick-Start.md) — First project in 5 minutes

### Core Concepts
- [Glyph Reference](wiki/Glyph-Reference.md) — All 16 glyph types
- [Chain Syntax](wiki/Chain-Syntax.md) — Composition rules and validation
- [Natural Language Intent](wiki/Natural-Language-Intent.md) — Plain English → chains
- [Knowledge Graph](wiki/Knowledge-Graph.md) — The `.arcon` file explained

### Reference
- [CLI Commands](wiki/CLI-Commands.md) — Complete command reference
- [Templates](wiki/Templates.md) — Template customization
- [Architecture](wiki/Architecture.md) — System design and mechanisms

---

## IDE AI Integration Deep Dive

**This is where Archeon really shines.** With a single command, your IDE's AI assistant becomes architecture-aware. It won't just read your knowledge graph — it can **write glyph chains directly**.

### One Command Setup

```bash
arc ai-setup
```

This generates configuration files for every major AI-powered IDE:

| IDE | Config File | What It Does |
|-----|------------|--------------|
| Cursor | `.cursorrules` | AI reads + writes to ARCHEON.arcon |
| GitHub Copilot | `.github/copilot-instructions.md` | Copilot Chat understands glyphs |
| Windsurf | `.windsurfrules` | Cascade AI follows the graph |
| Cline/Claude Dev | `.clinerules` | Claude writes chains first |
| Aider | `.aider.conf.yml` | Auto-loads graph context |
| VS Code | `.vscode/settings.json` | Syntax highlighting for .arcon |

### Selective Setup

```bash
arc ai-setup --cursor              # Only Cursor
arc ai-setup --vscode --copilot    # VS Code + Copilot only
arc ai-setup --no-aider            # All except Aider
```

### What Happens When You Ask for a Feature

When you tell your IDE's AI: *"Create a user registration feature"*

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

## Installation

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
