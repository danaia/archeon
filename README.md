# Archeon

> Glyph-based architecture notation system for AI-orchestrated software development.

Archeon provides a hyper-compressed, human-readable **intermediate representation (IR)** that serves as both documentation and executable specification. It's a **constraint layer** that any LLM can understand, preventing hallucinations and architectural drift.

## Quick Install

```bash
# Clone and install globally
git clone git@github.com:danaia/archeon.git
pip install -e ./Archeon

# Verify installation
arc --version

# Uninstall
pip uninstall archeon
```

## Quick Start

```bash
# 1. Create a new project (Vue 3 + FastAPI)
mkdir my-app && cd my-app
arc init --frontend vue3

# 2. Define a feature chain
arc parse "NED:login => CMP:LoginForm => STO:Auth => API:POST/auth/login => OUT:dashboard"

# 3. Generate code
arc gen

# 4. Check status
arc status
```

That's it. You now have:
- `client/src/components/LoginForm.vue` - Vue 3 component
- `client/src/stores/AuthStore.js` - Pinia store  
- `server/src/api/routes/auth_login.py` - FastAPI endpoint

## Natural Language Intent Flow

The primary way to use Archeon is through **natural language**. Describe what you want, and the intent parser proposes glyph chains for your approval.

### Basic Usage

```bash
# From natural language (arc i is shorthand for arc intent)
arc i "User wants to login with email and password"

# From a requirements document
arc i --file requirements.md

# Auto-suggest error paths
arc i "User needs to checkout their cart" --auto-errors
```

### How It Works

```
Natural Language → Intent Parser → Proposed Chain → Human Approval → Graph → Code Generation
```

1. **Parsing** - Keywords (login, register, search, etc.) map to glyphs
2. **Proposal** - Chain generated with confidence level (HIGH/MEDIUM/LOW)
3. **Approval** - You **[a]pprove**, **[e]dit**, **[r]eject**, or **[s]uggest errors**
4. **Graph** - Only approved chains are added to `.arcon`
5. **Generate** - Run `arc gen` to create code

### Example Session

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

### The Key Insight

**The intent parser proposes, humans approve.** This keeps you in control while letting you work in natural language. The constraint layer ensures the AI can't hallucinate — it can only compose within the glyph taxonomy.

## Why Archeon?

```
Without Archeon:  "AI, build me a login"  → Random architecture every time

With Archeon:     NED:login => CMP:LoginForm => API:POST/auth
                  → Same structure, any model, always
```

**Anti-hallucination** - Models can't invent random patterns. Glyphs define what's allowed.  
**Anti-drift** - Context persists in `.arcon` files, not in chat history.  
**Model-portable** - Switch Claude to GPT mid-project. The graph remains.

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

## Commands

```bash
arc init [--frontend react|vue3] [--backend fastapi]  # Create project
arc parse "<chain>"                                    # Add chain to graph
arc gen                                                # Generate code
arc validate                                           # Check architecture
arc status                                             # Show graph stats
arc legend                                             # Show all glyphs
arc audit                                              # Check for drift
arc run "<chain>" [--sandbox]                          # Execute headless
arc i "<text>"                                         # Parse natural language (short)
arc intent "<text>"                                    # Parse natural language (full)
arc intent --file <path>                               # Parse requirements doc
arc ai-setup                                           # Configure IDE AI assistants
```

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
    └── ARCHEON.arcon    # Knowledge graph
```

## IDE AI Integration

**This is where Archeon really shines.** With a single command, your IDE's AI assistant becomes architecture-aware. It won't just read your knowledge graph — it can **write glyph chains directly**.

### Why This Changes Everything

```
Without Archeon:  "AI, build me a login"  → Random files, random patterns, hallucinations

With Archeon:     "AI, build me a login"  
                  → AI writes: @v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard
                  → AI implements each component following that chain
                  → Perfect architectural consistency, every time
```

**Your AI assistant becomes a disciplined architect**, not a random code generator.

### One Command Setup

```bash
arc ai-setup
```

That's it. This generates configuration files for every major AI-powered IDE:

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

### Manual Configuration (Optional)

If you prefer manual setup, `arc ai-setup` creates README files in each config directory (`.cursor/README.md`, `.github/COPILOT_README.md`, etc.) with detailed instructions.

### Cline Extra Setup

For Cline (Claude Dev), you can also add the graph to always-included context:

1. Open Cline panel → Settings ⚙️
2. In **"Custom Instructions"**, add:
   ```
   Always reference archeon/ARCHEON.arcon. Write new chains before implementing features.
   ```
3. Optionally add `archeon/ARCHEON.arcon` to always-included files

## Development

```bash
# Clone and install
git clone <repo>
cd Archeon
pip install -e ".[dev]"

# Run tests
pytest archeon/tests/ -v

# Uninstall
pip uninstall archeon
```

## License

MIT
