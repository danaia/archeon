# Archeon

> Glyph-based architecture notation system for AI-orchestrated software development.

Archeon provides a hyper-compressed, human-readable **intermediate representation (IR)** that serves as both documentation and executable specification. It's a **constraint layer** that any LLM can understand, preventing hallucinations and architectural drift.

## Quick Install

```bash
# Clone and install globally
git clone git@github.com:danaia/Archeon.git
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
- `client/src/stores/AuthStore.ts` - Pinia store  
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
✓ Generated STO:Auth → client/src/stores/AuthStore.ts
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

For Archeon to work effectively, your IDE's AI assistant must **always reference the knowledge graph**. 

### Quick Setup

```bash
# Generate all IDE configs (default)
arc ai-setup

# Generate specific IDE configs only
arc ai-setup --cursor              # Only Cursor
arc ai-setup --vscode --copilot    # Only VS Code and Copilot
arc ai-setup --no-cline            # All except Cline
arc ai-setup --aider               # Include Aider (off by default)
```

This generates configuration files with README guides:

| IDE | Config File | README |
|-----|------------|--------|
| Cursor | `.cursorrules` | `.cursor/README.md` |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/COPILOT_README.md` |
| Windsurf | `.windsurfrules` | `.windsurf/README.md` |
| Cline/Claude Dev | `.clinerules` | `.cline/README.md` |
| Aider | `.aider.conf.yml` | `.aider/README.md` |
| VS Code | `.vscode/settings.json` | `.vscode/ARCHEON_README.md` |

### What the Configs Do

Each config file tells the AI assistant to:

### What the Configs Do

Each config file tells the AI assistant to:

1. **Read `archeon/ARCHEON.arcon` first** - Before any code generation
2. **Understand glyph notation** - Know what NED, CMP, STO, API, etc. mean
3. **Respect constraints** - Never create architecture outside the graph
4. **Propose via Archeon** - Suggest `arc intent` for new features

### Manual Configuration

If you prefer to set up manually, here are the configs:

### Cursor

Create `.cursorrules` in your project root:

```markdown
# Archeon Project Rules

Always read `archeon/ARCHEON.arcon` before generating or modifying code.

## Architecture Constraint
This project uses Archeon glyph notation. All features are defined as chains:
- `NED:` = User need/motivation
- `CMP:` = UI Component  
- `STO:` = State store
- `API:` = HTTP endpoint
- `MDL:` = Database model
- `OUT:` = Success outcome
- `ERR:` = Error path

## Rules
1. Never create components, stores, APIs, or models not defined in ARCHEON.arcon
2. Follow the chain flow: NED → CMP → STO → API → MDL → OUT
3. Check existing chains before proposing new architecture
4. Use `arc intent "description"` to propose new features
5. Reference .archeonrc for frontend/backend framework choices

## Before Any Code Generation
1. Read archeon/ARCHEON.arcon
2. Check if the requested feature exists as a chain
3. If not, suggest running `arc intent "feature description"` first
```

### GitHub Copilot

Create `.github/copilot-instructions.md`:

```markdown
# Archeon Project Context

This project uses Archeon, a glyph-based architecture notation system.

## Critical Files to Reference
- `archeon/ARCHEON.arcon` - The knowledge graph (READ THIS FIRST)
- `.archeonrc` - Project configuration

## Glyph Notation
Chains define feature architecture:
```
NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard
```

## Constraints
- Only generate code for glyphs defined in ARCHEON.arcon
- Follow layer boundaries: CMP cannot directly access MDL
- All features must end with OUT: or ERR:
- Propose new features via `arc intent` command, not direct code generation
```

### Windsurf

Create `.windsurfrules` in your project root:

```markdown
# Archeon Architecture Rules

## Required Context
Always read these files before generating code:
1. archeon/ARCHEON.arcon - Knowledge graph with all feature chains
2. .archeonrc - Frontend/backend framework configuration

## Glyph System
Features are defined as chains using these glyphs:
- NED: User need → TSK: Task → CMP: Component → STO: Store → API: Endpoint → MDL: Model → OUT: Output

## Hard Rules
1. Do not create architecture not defined in ARCHEON.arcon
2. Check for existing chains before suggesting new patterns
3. Respect layer boundaries (frontend cannot directly call database)
4. Use `arc intent` for new features, `arc gen` for code generation
```

### Cline / Claude Dev

Create `.clinerules`:

```markdown
# Archeon Project

This uses Archeon glyph notation for architecture.

ALWAYS read archeon/ARCHEON.arcon before any code task.

Chain format: NED:need => CMP:Component => STO:Store => API:endpoint => OUT:result

Do not generate code for features not in the knowledge graph.
Suggest `arc intent "description"` for new features.
```

### Aider

Create `.aider.conf.yml`:

```yaml
read:
  - archeon/ARCHEON.arcon
  - .archeonrc

auto-commits: false

message-template: |
  This project uses Archeon glyph notation.
  Check archeon/ARCHEON.arcon for defined feature chains.
  Do not create architecture outside the knowledge graph.
```

### VS Code Settings (All AI Extensions)

Add to `.vscode/settings.json`:

```json
{
  "files.associations": {
    "*.arcon": "markdown"
  },
  "search.include": {
    "archeon/**": true
  },
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "Always reference archeon/ARCHEON.arcon for architecture. Use Archeon glyph notation."
    }
  ]
}
```

### The Key Principle

**The AI should never invent architecture.** 

The `.arcon` file is the single source of truth. Any AI assistant in your IDE should:

1. **Read first** - Check ARCHEON.arcon before generating code
2. **Propose via Archeon** - Use `arc intent` for new features
3. **Generate from graph** - Use `arc gen` for code, not freeform generation
4. **Respect constraints** - Never violate layer boundaries or glyph rules

This ensures architectural consistency regardless of which AI model or tool you use.

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
