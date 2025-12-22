# Archeon Wiki

> Glyph-based architecture notation system for AI-orchestrated software development

Archeon provides a hyper-compressed, human-readable **intermediate representation (IR)** that serves as both documentation and executable specification. It's a **constraint layer** that any LLM can understand, preventing hallucinations and architectural drift.

## 📚 Documentation

### Getting Started
- **[Installation](Installation)** - Install Archeon globally via pip
- **[Quick Start](Quick-Start)** - Create your first project in 5 minutes
- **[Tutorial](Tutorial)** - Step-by-step guide building a real application

### Core Concepts
- **[Glyph Reference](Glyph-Reference)** - Complete guide to all 16 glyph types
- **[Chain Syntax](Chain-Syntax)** - How to write and compose chains
- **[Natural Language Intent](Natural-Language-Intent)** - Using plain English to generate chains
- **[Knowledge Graph](Knowledge-Graph)** - Understanding the `.arcon` file

### Guides
- **[CLI Commands](CLI-Commands)** - Complete command reference
- **[Templates](Templates)** - Template system and customization
- **[Architecture](Architecture)** - System design and principles
- **[Context Optimization](Context-Optimization)** - Working with small models (30B parameters)

### Integration
- **[IDE Setup](IDE-Setup)** - Configure VS Code, Cursor, and other editors
- **[CI/CD Integration](CI-CD)** - Validation in pipelines
- **[Design Tokens](Design-Tokens)** - Single source of truth for design systems

## 🎯 What is Archeon?

Archeon is a **constraint-driven code generation system** that uses a glyph-based intermediate representation to:

1. **Prevent architectural drift** - Closed vocabulary ensures consistency
2. **Enforce HCI completeness** - Every feature must start with a user need and end with an observable outcome
3. **Enable small model usage** - Context optimization for 30B parameter models
4. **Provide single source of truth** - Design tokens propagate deterministically

## 🔤 The Glyph System

Archeon uses 16 typed symbols representing architectural concerns:

| Glyph | Layer | Purpose |
|-------|-------|---------|
| `NED` | Meta | User need |
| `TSK` | Meta | User action |
| `OUT` | Meta | Observable outcome |
| `ERR` | Meta | Error state |
| `V` | View | Container component |
| `CMP` | Frontend | UI component |
| `STO` | Frontend | Client state |
| `FNC` | Backend | Function |
| `EVT` | Backend | Event handler |
| `API` | Backend | HTTP endpoint |
| `MDL` | Backend | Data model |

## 🔗 Example Chain

```
NED:login => TSK:submit => CMP:LoginForm => STO:Auth 
    => API:POST/auth/login => MDL:user.verify => OUT:redirect('/dashboard')
```

This single line defines:
- ✅ User intent (need to login)
- ✅ UI component (login form)
- ✅ State management (auth store)
- ✅ Backend endpoint (POST /auth/login)
- ✅ Data operation (user verification)
- ✅ Observable outcome (redirect to dashboard)

Run `arc gen` and Archeon generates all the code automatically.

## 🚀 Quick Example

```bash
# Install
pip install -e .

# Initialize project
arc init --frontend vue3 --backend fastapi

# Define feature
arc i "User wants to login with email and password"

# Review proposed chain, approve with 'a'
# Then generate code
arc gen

# All files created:
# ✓ client/src/components/LoginForm.vue
# ✓ client/src/stores/AuthStore.js
# ✓ server/src/api/routes/auth_login.py
```

## 🤝 Contributing

See [Contributing Guide](Contributing) for development setup and guidelines.

## 📄 License

MIT - See LICENSE file for details.
