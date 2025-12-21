# Archeon

> Glyph-based architecture notation system for AI-orchestrated software development.

Archeon provides a hyper-compressed, human-readable **intermediate representation (IR)** that serves as both documentation and executable specification. It's a **constraint layer** that any LLM can understand, preventing hallucinations and architectural drift.

## Quick Install

```bash
# Install globally
pip install -e /path/to/Archeon

# Verify installation
archeon --version

# Uninstall
pip uninstall archeon
```

## Quick Start

```bash
# 1. Create a new project (Vue 3 + FastAPI)
mkdir my-app && cd my-app
archeon init --frontend vue3

# 2. Define a feature chain
archeon parse "NED:login => CMP:LoginForm => STO:Auth => API:POST/auth/login => OUT:dashboard"

# 3. Generate code
archeon gen

# 4. Check status
archeon status
```

That's it. You now have:
- `client/src/components/LoginForm.vue` - Vue 3 component
- `client/src/stores/AuthStore.ts` - Pinia store  
- `server/src/api/routes/auth_login.py` - FastAPI endpoint

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
archeon init [--frontend react|vue3] [--backend fastapi]  # Create project
archeon parse "<chain>"                                    # Add chain to graph
archeon gen                                                # Generate code
archeon validate                                           # Check architecture
archeon status                                             # Show graph stats
archeon legend                                             # Show all glyphs
archeon audit                                              # Check for drift
archeon run "<chain>" [--sandbox]                          # Execute headless
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
