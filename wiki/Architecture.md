# Architecture

This guide explains Archeon's system design, architectural principles, and how the pieces fit together.

## System Overview

Archeon is a **constraint-driven code generation system** that uses a glyph-based intermediate representation to enforce architectural consistency.

```
┌─────────────────────────────────────────────────────────┐
│                     ARCHEON SYSTEM                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Natural Language → Intent Parser → Chain Proposal      │
│                          ↓                               │
│                    User Approval                         │
│                          ↓                               │
│               Knowledge Graph (.arcon)                   │
│                          ↓                               │
│            Semantic Index (section map)                  │
│                          ↓                               │
│                 Code Generator                           │
│                          ↓                               │
│         Generated Code (with @archeon markers)           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Core Principles

### 1. Constraint Over Context

> **Archeon prioritizes architectural constraint over context size.**

Rather than giving the AI the entire codebase, Archeon constrains *where* the AI can look and *what* it can generate through:

- **Closed vocabulary** - Only 16 glyph types exist
- **Boundary rules** - Frontend can't call backend directly
- **Semantic sections** - Code describes its own structure
- **HCI enforcement** - Every feature needs outcome

### 2. Attention Routing

> **Semantic sections route AI attention to precise locations.**

Instead of searching through thousands of lines, the AI uses section markers as **attention anchors**:

```vue
// @archeon:section handlers
// AI knows: "This is where event handlers live"
function handleClick() { }
// @archeon:endsection
```

The index maps glyphs → files → sections, creating a **semantic affordance map**.

### 3. Small Model Optimization

> **Archeon is designed for 30B parameter models (~60K token context).**

Context budget allocation:

| Allocation | % | Tokens | Purpose |
|------------|---|--------|---------|
| Glyph notation | 10% | 6,000 | Chain definition |
| Template | 20% | 12,000 | Framework template |
| Dependencies | 30% | 18,000 | 1-hop neighbors only |
| Chain context | 20% | 12,000 | Immediate chain |
| Output reserved | 20% | 12,000 | Generated code |

### 4. HCI Completeness

> **Every feature chain must start with a need and end with an observable outcome.**

Incomplete chains are rejected:

❌ **Invalid:**
```
NED:login => CMP:LoginForm  # No outcome!
```

✅ **Valid:**
```
NED:login => CMP:LoginForm => OUT:redirect('/dashboard')
```

## System Layers

### Meta Layer (Orchestrator)

The orchestrator is **deterministic** - it enforces rules without learning:

```
ORC:main :: PRS:glyph :: PRS:intent :: VAL:chain :: VAL:boundary 
    :: SPW:agent :: TST:e2e :: TST:error
```

**Components:**

- **PRS:glyph** - Parses chain syntax
- **PRS:intent** - Parses natural language
- **VAL:chain** - Validates chain structure
- **VAL:boundary** - Enforces separation of concerns
- **SPW:agent** - Spawns specialized agents
- **GRF:domain** - Knowledge graph
- **IDX:index** - Semantic section index

### User Experience Layer

Defines the **what** and **why**:

```
NED:login => TSK:submit => OUT:redirect('/dashboard')
│          │            │
Need       Action       Outcome
```

### View Layer

Structural containers:

```
V:DashboardPage @ CMP:Header, CMP:Stats, CMP:RecentActivity
```

### Frontend Layer

Client-side implementation:

```
CMP:LoginForm => STO:Auth => API:POST/auth/login
```

### Backend Layer

Server-side implementation:

```
API:POST/auth/login => FNC:auth.validate => MDL:user.verify
```

## Knowledge Graph (ARCHEON.arcon)

The `.arcon` file is the **single source of truth**:

```
# Archeon Knowledge Graph
# Version: 3.0

# === ORCHESTRATOR LAYER (Deterministic) ===
ORC:main :: PRS:glyph :: VAL:chain :: SPW:agent

# === AGENT CHAINS (Versioned) ===

# User authentication
@v1 NED:login => TSK:submit => CMP:LoginForm => STO:Auth
    => API:POST/auth/login => MDL:user.verify 
    => OUT:redirect('/dashboard')

# Error paths
API:POST/auth/login -> ERR:auth.invalidCredentials 
    => OUT:toast('Invalid credentials')
```

### Graph Structure

The graph is a **directed acyclic graph (DAG)** with typed edges:

- **Nodes** = Glyphs
- **Edges** = Operators (`=>`, `->`, `~>`, `@`)
- **Attributes** = Modifiers, arguments, versions

### Querying the Graph

```python
from archeon.orchestrator.GRF_graph import load_graph

graph = load_graph("archeon/ARCHEON.arcon")

# Find all chains containing a glyph
chains = graph.find_chain("CMP:LoginForm")

# Find dependencies (upstream)
deps = graph.find_dependencies("API:POST/auth/login")

# Find dependents (downstream)
dependents = graph.find_dependents("STO:Auth")
```

## Semantic Index (ARCHEON.index.json)

The index maps glyphs to file locations and sections:

```json
{
  "CMP:LoginForm": {
    "file": "client/src/components/LoginForm.vue",
    "intent": "User login input and submission",
    "chain": "@v1",
    "sections": ["imports", "props_and_state", "handlers", "render"]
  },
  "STO:Auth": {
    "file": "client/src/stores/AuthStore.js",
    "intent": "Authentication state management",
    "chain": "@v1",
    "sections": ["imports", "state", "actions", "selectors"]
  }
}
```

### Building the Index

```bash
arc index build
```

Or in Python:

```python
from archeon.orchestrator.IDX_index import build_index

build_index(".")
```

## Context Projection

Instead of loading the entire graph, Archeon uses **glyph projection** to load minimal context:

```python
from archeon.orchestrator.CTX_context import GlyphProjection

# Load only target glyph + 1-hop neighbors
projection = GlyphProjection(
    target="CMP:LoginForm",
    graph=graph,
    max_depth=1
)

# Returns:
# - CMP:LoginForm (target)
# - STO:Auth (downstream)
# - NED:login (upstream)
# - TSK:submit (upstream)
```

### Context Budget

```python
from archeon.orchestrator.CTX_context import ContextBudget

budget = ContextBudget(
    total_tokens=60_000,
    allocations={
        "glyph": 0.10,      # 6K
        "template": 0.20,   # 12K
        "deps": 0.30,       # 18K
        "chain": 0.20,      # 12K
        "output": 0.20      # 12K
    }
)

# Check if operation fits budget
if budget.check_allocation("template", template_tokens):
    # Proceed
```

## Micro-Agent Pattern

Archeon uses **micro-agents** - one glyph per invocation:

```python
from archeon.orchestrator.MIC_micro import MicroAgent

agent = MicroAgent(
    glyph="CMP:LoginForm",
    template=vue3_template,
    context=projection,
    budget=budget
)

# Generate code for single glyph
code = agent.execute()
```

**Benefits:**
- Small context payloads
- Parallel generation
- Fault isolation
- Easier debugging

## Agent Spawning

The spawner creates specialized agents per glyph type:

```python
from archeon.orchestrator.SPW_spawner import spawn_agent

# Spawns appropriate agent based on glyph type
agent = spawn_agent(
    glyph="CMP:LoginForm",
    framework="vue3",
    graph=graph
)
```

**Agent Types:**
- **CMP_agent** - Component generation
- **STO_agent** - Store generation
- **API_agent** - Endpoint generation
- **FNC_agent** - Function generation
- **MDL_agent** - Model generation
- **EVT_agent** - Event handler generation

## Validation

Validation happens at multiple levels:

### 1. Syntax Validation

```python
from archeon.orchestrator.PRS_parser import parse_chain

try:
    ast = parse_chain("NED:login => CMP:Form")
except ParseError as e:
    print(f"Syntax error: {e}")
```

### 2. Semantic Validation

```python
from archeon.orchestrator.VAL_validator import validate_chain

errors = validate_chain(ast, graph)
if errors:
    for error in errors:
        print(f"Validation error: {error}")
```

### 3. Boundary Validation

```python
from archeon.orchestrator.VAL_validator import GraphValidator

validator = GraphValidator(graph)
violations = validator.check_boundaries()

if violations:
    print("Boundary violations:")
    for v in violations:
        print(f"  {v.source} -> {v.target}: {v.reason}")
```

### 4. HCI Completeness

```python
incomplete = validator.check_hci_completeness()

if incomplete:
    print("Incomplete user journeys:")
    for chain in incomplete:
        print(f"  {chain}: Missing outcome")
```

## Design Token Propagation

Archeon uses **DTCG (Design Token Community Group)** format:

```
design-tokens.json → token-transformer.js → Multiple outputs
                                           ↓
                          ┌────────────────┼────────────────┐
                          ↓                ↓                ↓
                     tokens.css    tokens.tailwind.js   tokens.js
                          ↓                ↓                ↓
                    CSS variables    Tailwind config   JS constants
```

### Single Source of Truth

All design values defined once:

```json
{
  "color": {
    "primary": {
      "$type": "color",
      "$value": "{color.blue.500}"
    }
  }
}
```

Propagated to:

**CSS:**
```css
:root {
  --color-primary: #3b82f6;
}
```

**Tailwind:**
```js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6'
      }
    }
  }
}
```

**JavaScript:**
```js
export const tokens = {
  color: {
    primary: '#3b82f6'
  }
}
```

## Theme System

Two-layer theme architecture:

### Layer 1: Mode (Standard)
- Light
- Dark
- System

### Layer 2: Color Theme (Project-Specific)
- Example: Blue, Purple, Green (customizable per project)

Managed by `STO:Theme`:

```javascript
const themeStore = defineStore('theme', {
  state: () => ({
    mode: localStorage.getItem('theme-mode') || 'system',
    colorTheme: localStorage.getItem('color-theme') || 'blue'
  }),
  
  actions: {
    setMode(mode) {
      this.mode = mode;
      document.documentElement.classList.toggle('dark', mode === 'dark');
    },
    
    setColorTheme(theme) {
      this.colorTheme = theme;
      document.documentElement.setAttribute('data-theme', theme);
    }
  }
});
```

## Testing

### Test Runner

```bash
arc test
```

Runs:
- **Unit tests** - Individual glyph generation
- **Integration tests** - Chain validation
- **E2E tests** - Full flow from intent to code

### Test Structure

```python
# tests/test_parser.py
def test_parse_simple_chain():
    ast = parse_chain("NED:login => CMP:Form")
    assert len(ast.glyphs) == 2
    assert ast.glyphs[0].type == "NED"
    assert ast.glyphs[1].type == "CMP"
```

## File Structure

```
archeon/
├── config/
│   └── legend.py              # Glyph definitions
├── orchestrator/
│   ├── PRS_parser.py          # Chain parser
│   ├── PRS_intent.py          # Natural language parser
│   ├── GRF_graph.py           # Knowledge graph
│   ├── VAL_validator.py       # Validation
│   ├── SPW_spawner.py         # Agent spawner
│   ├── CTX_context.py         # Context manager
│   ├── MIC_micro.py           # Micro-agent executor
│   ├── IDX_index.py           # Semantic index
│   ├── SCN_scanner.py         # Section scanner
│   ├── GRF_exporter.py        # Graph export
│   └── HED_executor.py        # Headless executor
├── agents/
│   ├── base_agent.py          # Base agent
│   ├── CMP_agent.py           # Component agent
│   ├── STO_agent.py           # Store agent
│   ├── API_agent.py           # API agent
│   ├── FNC_agent.py           # Function agent
│   ├── MDL_agent.py           # Model agent
│   └── EVT_agent.py           # Event agent
├── templates/                 # Code templates
├── tests/                     # Test suite
└── main.py                    # CLI entry point
```

## Design Patterns

### Pattern: Semantic Sections

**Problem:** AI needs to know where to edit code without full context.

**Solution:** Self-describing code with semantic boundaries:

```vue
// @archeon:section handlers
// User interaction event handlers
function handleClick() { }
// @archeon:endsection
```

### Pattern: Glyph Projection

**Problem:** Context window limits prevent loading entire graph.

**Solution:** Load only target + 1-hop neighbors:

```
        NED:login
            ↓
        TSK:submit
            ↓
    → CMP:LoginForm ← (target)
            ↓
        STO:Auth
```

### Pattern: Micro-Agents

**Problem:** Batching multiple glyphs overloads context.

**Solution:** One agent per glyph, execute in parallel:

```
CMP:LoginForm → CMP_agent → code
STO:Auth → STO_agent → code
API:POST/auth → API_agent → code
```

### Pattern: Boundary Enforcement

**Problem:** Frontend calling backend directly breaks architecture.

**Solution:** Validate edges against boundary rules:

```python
BOUNDARY_RULES = [
    {"from": ["CMP", "STO"], "to": ["MDL"], "allowed": False},
    {"from": ["CMP"], "to": ["API"], "allowed": True}
]
```

## Performance

### Benchmarks

- **Parse chain:** <1ms
- **Validate chain:** <5ms
- **Generate component:** <100ms (30B model)
- **Full project init:** <500ms

### Optimization Strategies

1. **Template compression** - 20 lines vs 100+ lines
2. **Glyph projection** - 1-hop only, not full graph
3. **Parallel generation** - Micro-agents run concurrently
4. **Index caching** - Section map loaded once

## Extension Points

### Custom Glyphs

Add new glyph types in `config/legend.py`:

```python
GLYPH_LEGEND["DBQ"] = {
    "name": "Database Query",
    "description": "Direct database query",
    "agent": "DBQ_agent",
    "color": "cyan",
    "layer": "backend"
}
```

### Custom Agents

Create agent in `agents/`:

```python
from archeon.agents.base_agent import BaseAgent

class DBQ_agent(BaseAgent):
    def generate(self, glyph, context):
        # Custom generation logic
        return generated_code
```

### Custom Validators

Add validators in `orchestrator/VAL_validator.py`:

```python
def validate_database_query(chain, graph):
    # Custom validation logic
    return errors
```

## Next Steps

- 📖 [Quick Start](Quick-Start) - Build your first project
- 🔤 [Glyph Reference](Glyph-Reference) - Learn all glyph types
- 💻 [CLI Commands](CLI-Commands) - Master the CLI
- 🎨 [Templates](Templates) - Customize code generation
