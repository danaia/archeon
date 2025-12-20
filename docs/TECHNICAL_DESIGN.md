# Archeon Technical Design Document

> **Version:** 1.2  
> **Date:** December 20, 2025  
> **Status:** Draft Specification

---

## 1. Executive Summary

Archeon is a **glyph-based architecture notation system** designed for AI-orchestrated, hallucination-free software development. It provides a hyper-compressed, human-readable shorthand that serves as both documentation and executable specification.

The system enables:
- **One-to-one traceability** between notation and code
- **Modular AI agents** that build code from templates
- **Automated validation** through orchestrator-owned testing
- **Domain memory** as a living knowledge graph
- **Intent parsing** from requirements docs, task tickets, or direct input

---

## 2. Core Philosophy

### 2.1 The UX Foundation
Everything in a user interface is based on:
- **Need (NED)** — User motivation
- **Task (TSK)** — Action taken to satisfy the need
- **Observation (OUT)** — System feedback completing the loop

```
NED:motivation → TSK:action → OUT:feedback
```

### 2.2 Design Principles
1. **Compression over verbosity** — Dense glyphs replace prose
2. **Traceability over abstraction** — Every glyph maps to exactly one code artifact
3. **Validation over trust** — Orchestrator validates all agent output
4. **Templates over generation** — Agents instantiate, not invent
5. **Framework agnostic** — Components work across React, Vue, Angular, Svelte, etc.

---

## 3. Glyph Notation Specification

### 3.1 Core Glyph Set (3-Character Prefixes)

| Prefix | Name | Description | Example |
|--------|------|-------------|---------|
| `NED:` | Need | User intent/motivation | `NED:login` |
| `TSK:` | Task | User action | `TSK:clickSubmit` |
| `V:` | View | Parent view/page container | `V:Dashboard` |
| `CMP:` | Component | UI component (framework agnostic) | `CMP:LoginForm` |
| `STO:` | Store | Client state store/context | `STO:authStore` |
| `FNC:` | Function | Callable logic | `FNC:validateInput` |
| `EVT:` | Event | Emit/broadcast | `EVT:publish('auth')` |
| `API:` | API | Endpoint signature | `API:POST/auth` |
| `MDL:` | Model | Database query/schema | `MDL:findOne(users)` |
| `OUT:` | Output | Feedback layer | `OUT:toast('Success')` |

### 3.2 Orchestrator Notation (Knowledge Graph)

The orchestrator maintains its own deterministic notation for internal coordination:

| Prefix | Name | Description | Example |
|--------|------|-------------|---------|
| `ORC:` | Orchestrator | Core orchestrator node | `ORC:main` |
| `PRS:` | Parser | Chain/intent parser | `PRS:glyph` |
| `VAL:` | Validator | Validation engine | `VAL:chain` |
| `SPW:` | Spawner | Agent spawner | `SPW:agent` |
| `TST:` | Tester | Test runner | `TST:e2e` |
| `GRF:` | Graph | Knowledge graph node | `GRF:domain` |

**Orchestrator Chain:**
```
ORC:main :: PRS:glyph :: VAL:chain :: SPW:agent :: TST:e2e
```

### 3.3 Operators

| Operator | Meaning | Usage |
|----------|---------|-------|
| `=>` | Data flow | `CMP:Form => STO:store` |
| `->` | Control flow (branch/redirect) | `FNC:check -> CMP:Error` |
| `\|` | Parallel execution | `TSK:drag => \| FNC:debounce \| FNC:log` |
| `::` | Orchestrator dependency | `PRS:glyph :: VAL:chain` |
| `@` | View containment | `V:Dashboard @ CMP:Header, CMP:Sidebar` |

### 3.4 Agent Tags

Agents are tagged in square brackets for framework-specific generation:
```
[react] CMP:Dashboard => STO:userStore
[vue] CMP:Dashboard => STO:userStore
[angular] CMP:Dashboard => STO:userStore
[fastapi] API:GET/user => FNC:validate => MDL:findOne(users)
[express] API:GET/user => FNC:validate => MDL:findOne(users)
[mongo] MDL:findOne(users)
[postgres] MDL:findOne(users)
```

### 3.5 Chain Examples

**View with Components:**
```
V:ProfilePage @ CMP:Header, CMP:ProfileCard, CMP:ActivityFeed
```

**Full User Flow:**
```
NED:viewProfile => TSK:clickAvatar => V:ProfilePage => CMP:ProfileCard => FNC:formatDate => STO:userStore => API:GET/user/:id => MDL:findOne(users) => OUT:renderProfile
```

**Authentication Flow:**
```
NED:login => TSK:submitCreds => CMP:LoginForm => API:POST/auth => FNC:validateToken => FNC:hashPassword => MDL:findOne(users) => EVT:authSuccess => OUT:redirect('/dashboard')
```

**Backend Chain:**
```
API:POST/user => FNC:validateUserInput => FNC:hashPassword => MDL:create(users) => FNC:sendWelcomeEmail => OUT:201
```

---

## 4. System Architecture

### 4.1 Two-Layer Model

```
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR LAYER                         │
│  ORC:main :: PRS:glyph :: VAL:chain :: SPW:agent :: TST:e2e │
│                          │                                   │
│              Owns: Knowledge Graph (GRF:domain)              │
│              Owns: Test Generation                           │
│              Owns: Agent Coordination                        │
│              Owns: Intent Parsing (from docs/tasks)          │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │   CMP    │   │   API    │   │   MDL    │
    │  Agent   │   │  Agent   │   │  Agent   │
    └──────────┘   └──────────┘   └──────────┘
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Template │   │ Template │   │ Template │
    │  CMP:*   │   │  API:*   │   │  MDL:*   │
    └──────────┘   └──────────┘   └──────────┘
```

### 4.2 Intent Parsing Sources

The orchestrator accepts input from multiple sources:

| Source | Format | Example |
|--------|--------|---------|
| Direct CLI | Raw chain string | `archeon parse "NED:login => TSK:submit"` |
| Requirements Doc | Markdown link | `archeon import ./docs/requirements.md` |
| Task Ticket | JIRA/Linear/GitHub link | `archeon import https://linear.app/task/ABC-123` |
| Tech Design | Markdown/Notion | `archeon import ./docs/TECH_DESIGN.md` |
| User Story | Natural language | `archeon intent "User wants to reset password"` |

**Intent-to-Chain Conversion:**
```
Input:  "User wants to login with email and password"
Output: NED:login => TSK:submitCreds => CMP:LoginForm => API:POST/auth => MDL:findOne(users) => OUT:redirect
```

### 4.3 Knowledge Graph Structure

The knowledge graph is stored in `ARCHEON.arcon`:

```
# Archeon v1.2
# Orchestrator Layer (Deterministic Reference)
ORC:main :: PRS:glyph
PRS:glyph :: VAL:chain
VAL:chain :: SPW:agent
SPW:agent :: TST:e2e
GRF:domain :: ORC:main

# Agent Chains
[react] NED:chat => TSK:send => V:ChatPage => CMP:MessageBox => FNC:timestamp => OUT:badge(+1)
[fastapi] API:POST/chat => FNC:validate => FNC:rateLimit => MDL:append(messages)
[zustand] STO:chatStore => actions: addMessage, clear
[mongo] MDL:append(messages) => OUT:emit('update')
```

---

## 5. Directory Structure

```
archeon/
├── main.py                    # CLI entry point
├── orchestrator/
│   ├── __init__.py
│   ├── PRS_parser.py          # Glyph chain parser → AST
│   ├── VAL_validator.py       # Chain validation rules
│   ├── GRF_graph.py           # Knowledge graph operations
│   ├── SPW_spawner.py         # Agent instantiation
│   ├── TST_runner.py          # E2E test generation & execution
│   └── INT_intent.py          # Intent parser (docs/tasks → chains)
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py          # Abstract agent interface
│   ├── CMP_agent.py           # CMP: component handler (React/Vue/Angular/etc.)
│   ├── STO_agent.py           # STO: state store handler
│   ├── API_agent.py           # API: endpoint handler
│   ├── MDL_agent.py           # MDL: database model handler
│   ├── FNC_agent.py           # FNC: function handler
│   └── EVT_agent.py           # EVT: event handler
│
├── templates/
│   ├── CMP/                   # Component templates (by framework)
│   │   ├── react.tsx          # React component skeleton
│   │   ├── vue.vue            # Vue component skeleton
│   │   ├── angular.ts         # Angular component skeleton
│   │   └── svelte.svelte      # Svelte component skeleton
│   ├── STO/                   # Store templates
│   │   ├── zustand.ts         # Zustand store skeleton
│   │   ├── redux.ts           # Redux slice skeleton
│   │   ├── pinia.ts           # Pinia store skeleton
│   │   └── ngrx.ts            # NgRx store skeleton
│   ├── API/                   # API templates
│   │   ├── fastapi.py         # FastAPI route skeleton
│   │   ├── express.ts         # Express route skeleton
│   │   └── flask.py           # Flask route skeleton
│   ├── MDL/                   # Model templates
│   │   ├── mongo.py           # MongoDB model skeleton
│   │   ├── postgres.py        # PostgreSQL model skeleton
│   │   └── prisma.ts          # Prisma schema skeleton
│   ├── FNC/                   # Function templates
│   │   ├── typescript.ts      # TypeScript function skeleton
│   │   └── python.py          # Python function skeleton
│   └── EVT/                   # Event templates
│       ├── eventemitter.ts    # Node EventEmitter skeleton
│       └── pubsub.py          # Python pub/sub skeleton
│
├── tests/
│   ├── __init__.py
│   ├── generator.py           # Auto-generate tests from chains
│   └── runner.py              # Pytest wrapper
│
├── utils/
│   ├── tracer.py              # File ↔ glyph mapping
│   └── notifier.py            # Status notifications
│
├── config/
│   └── legend.py              # Global glyph dictionary
│
└── ARCHEON.arcon              # Knowledge graph file
```

---

## 6. Component Specifications

### 6.1 Orchestrator

**Responsibilities:**
1. Parse `ARCHEON.arcon` into in-memory graph
2. Parse user intent from natural language, docs, or task tickets
3. Validate chain integrity (no orphans, no duplicates)
4. Route glyph prefixes to appropriate agents
5. Generate and execute end-to-end tests
6. Maintain single source of truth via deterministic notation

**Orchestrator Internal Graph (Deterministic):**
```
ORC:main          # Entry point
  :: PRS:glyph    # Parse incoming chains
  :: PRS:intent   # Parse natural language / docs
  :: VAL:chain    # Validate structure
  :: VAL:deps     # Validate dependencies
  :: SPW:agent    # Spawn appropriate agent
  :: TST:unit     # Run unit tests
  :: TST:e2e      # Run integration tests
  :: GRF:update   # Update knowledge graph
```

**Validation Rules:**
- Every glyph must resolve to exactly one file path
- No cyclic dependencies (DAG enforcement)
- All `MDL:` queries must have corresponding `API:` endpoints
- All `CMP:` components must have tests
- All `V:` views must contain at least one `CMP:`

### 6.2 Agents

**Agent Contract:**
```python
class BaseAgent(ABC):
    prefix: str  # e.g., 'CMP', 'API', 'MDL'
    
    @abstractmethod
    def generate(self, glyph: str, chain: list, framework: str) -> str:
        """Generate code from glyph and return file path."""
        pass
    
    @abstractmethod
    def get_template(self, framework: str) -> str:
        """Return the code template for this agent and framework."""
        pass
    
    @abstractmethod
    def generate_test(self, glyph: str, framework: str) -> str:
        """Generate test stub for the artifact."""
        pass
```

**Agent Behavior:**
1. Receive glyph + framework tag from orchestrator
2. Look up corresponding template from `templates/{PREFIX}/{framework}`
3. Fill template with chain values
4. Write file to appropriate location
5. Generate companion test
6. Report back to orchestrator for validation

### 6.3 Templates (Structural Guides)

Templates provide the **structure and conventions** that agents must follow. They are not generated—they are reference patterns.

**Template Purpose:**
- Define the skeleton/boilerplate for each artifact type
- Enforce consistent code style across the codebase
- Provide placeholders that agents fill with chain-derived values
- Support multiple frameworks per glyph type

**Component Template (`templates/CMP/react.tsx`):**
```tsx
import React, { FC } from 'react';

interface {COMPONENT_NAME}Props {
  {PROPS}
}

/**
 * @archeon CMP:{COMPONENT_NAME}
 * @chain {CHAIN_CONTEXT}
 */
export const {COMPONENT_NAME}: FC<{COMPONENT_NAME}Props> = ({DESTRUCTURED}) => {
  return (
    <div className="{COMPONENT_NAME_LOWER}">
      {/* Generated by Archeon - CMP:{COMPONENT_NAME} */}
      {children}
    </div>
  );
};
```

**Component Template (`templates/CMP/vue.vue`):**
```vue
<template>
  <div class="{COMPONENT_NAME_LOWER}">
    <!-- Generated by Archeon - CMP:{COMPONENT_NAME} -->
    <slot />
  </div>
</template>

<script setup lang="ts">
/**
 * @archeon CMP:{COMPONENT_NAME}
 * @chain {CHAIN_CONTEXT}
 */
interface Props {
  {PROPS}
}

defineProps<Props>();
</script>
```

**API Template (`templates/API/fastapi.py`):**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class {MODEL_NAME}Request(BaseModel):
    """@archeon API:{METHOD}/{ROUTE} - Request"""
    {REQUEST_FIELDS}

class {MODEL_NAME}Response(BaseModel):
    """@archeon API:{METHOD}/{ROUTE} - Response"""
    {RESPONSE_FIELDS}

@router.{METHOD}("/{ROUTE}")
async def {HANDLER_NAME}(request: {MODEL_NAME}Request) -> {MODEL_NAME}Response:
    """
    @archeon API:{METHOD}/{ROUTE}
    @chain {CHAIN_CONTEXT}
    """
    # Generated by Archeon
    pass
```

**Store Template (`templates/STO/zustand.ts`):**
```typescript
import { create } from 'zustand';

/**
 * @archeon STO:{STORE_NAME}
 * @chain {CHAIN_CONTEXT}
 */
interface {STORE_NAME}State {
  {STATE_FIELDS}
}

interface {STORE_NAME}Actions {
  {ACTION_SIGNATURES}
}

export const use{STORE_NAME} = create<{STORE_NAME}State & {STORE_NAME}Actions>((set, get) => ({
  // State
  {INITIAL_STATE}
  
  // Actions
  {ACTIONS}
}));
```

---

## 7. CLI Interface

```bash
# Initialize new Archeon project
archeon init

# Parse and add chain to knowledge graph
archeon parse "NED:login => TSK:submit => CMP:LoginForm => API:POST/auth"

# Import from requirements/task docs
archeon import ./docs/requirements.md
archeon import ./docs/TECH_DESIGN.md
archeon import https://linear.app/team/issue/ABC-123
archeon import https://github.com/org/repo/issues/42

# Parse natural language intent into chain
archeon intent "User wants to reset their password via email"

# Generate code for all unresolved glyphs
archeon gen

# Generate for specific framework
archeon gen --frontend react --backend fastapi --db mongo

# Run orchestrator workflow
archeon orchestrate

# Execute all tests
archeon test

# Validate knowledge graph integrity
archeon validate

# Export graph visualization (DOT/PNG)
archeon graph --format png

# Audit repository for drift
archeon audit

# Show orchestrator internal state
archeon status
```

---

## 8. Test Generation

### 8.1 Orchestrator-Owned Testing

The orchestrator generates E2E tests from chains:

```python
# Auto-generated from: NED:login => TSK:submit => CMP:LoginForm => API:POST/auth => OUT:redirect
def test_login_journey():
    with TestApp() as app:
        # NED:login - User intent
        user = User()
        
        # TSK:submit - Action
        user.fill('email', 'dana@example.com')
        user.fill('password', 'secret')
        user.click('submit')
        
        # API:POST/auth - API call
        assert api_log.last.status == 200
        
        # OUT:redirect - Feedback
        assert user.current_path == '/dashboard'
```

### 8.2 Test Coverage Rules

| Glyph | Required Test |
|-------|---------------|
| `V:` | View render test + child component presence |
| `CMP:` | Render test + snapshot |
| `STO:` | State mutation test |
| `API:` | Request/response contract |
| `MDL:` | Query result shape |
| `FNC:` | Input/output assertion |
| `EVT:` | Event emission verification |

---

## 9. Headless Execution Mode

### 9.1 Curl-Based Component Testing

Components can be invoked headlessly via HTTP:

```bash
# Trigger component action
curl http://localhost:3000/api/cmp/userprofile?action=load&name=Dana

# Response
{
  "event": "profileLoaded",
  "data": { "name": "Dana", "tier": "pro" },
  "latency_ms": 42,
  "triggered_at": "2025-12-20T15:32:41Z"
}
```

### 9.2 URL Parameter Mapping

```
/api/cmp/{component}?action={task}&from={need}&debug=true

Parameters map to glyphs:
- action=load  → TSK:load
- from=feed    → NED:discover  
- debug=true   → trace all hops
```

### 9.3 Metrics Endpoint

```bash
curl /api/cmp/userprofile/metrics

{
  "fnc_time_ms": 4,
  "sto_write_ms": 2,
  "evt_emit_ms": 1,
  "total_ms": 7
}
```

---

## 10. 3D Canvas Visualization (Future)

### 10.1 Concept

A Three.js-based infinite grid where:
- Each **tile** represents an agent/glyph
- **Lines** between tiles represent `=>` and `->` operators
- The **grid plane** IS the orchestrator
- Click to spawn nodes, drag to connect

### 10.2 Visual Encoding

| Glyph | Color | Shape |
|-------|-------|-------|
| `NED:` | Purple | Sphere |
| `TSK:` | Blue | Cube |
| `V:` | Indigo | Large flat plane |
| `CMP:` | Cyan | Rounded cube |
| `STO:` | Green | Cylinder |
| `FNC:` | Yellow | Octahedron |
| `EVT:` | Orange | Torus |
| `API:` | Red | Cone |
| `MDL:` | Brown | Box |
| `OUT:` | White | Ring |

### 10.3 Spatial Semantics

- **X-axis**: User journey (left to right)
- **Y-axis**: Control flow forks (branching)
- **Z-axis**: Data depth (latency visualization)

---

## 11. Implementation Roadmap

### Phase 1: Core Engine (Week 1-2)
- [ ] Implement glyph parser (PRS_parser.py)
- [ ] Build knowledge graph data structure (GRF_graph.py)
- [ ] Create base agent class
- [ ] Implement CMP agent with React template

### Phase 2: Agent Suite (Week 3-4)
- [ ] STO agent (Zustand, Redux, Pinia)
- [ ] API agent (FastAPI, Express)
- [ ] MDL agent (MongoDB, PostgreSQL)
- [ ] FNC agent
- [ ] EVT agent

### Phase 3: Orchestration (Week 5-6)
- [ ] Chain validation engine (VAL_validator.py)
- [ ] Agent spawner (SPW_spawner.py)
- [ ] Test generator (TST_runner.py)
- [ ] CLI interface

### Phase 4: Intent Parsing (Week 7-8)
- [ ] Natural language → chain conversion (INT_intent.py)
- [ ] Requirements doc parser
- [ ] Task ticket integration (Linear, JIRA, GitHub)
- [ ] Tech design doc parser

### Phase 5: Headless Mode (Week 9-10)
- [ ] HTTP endpoint mapping
- [ ] Curl-based execution
- [ ] Metrics collection
- [ ] Trace logging

### Phase 6: Visualization (Week 11-14)
- [ ] Three.js grid canvas
- [ ] Node spawning/connecting
- [ ] Real-time chain preview
- [ ] Export to ARCHEON.arcon

---

## 12. File Formats

### 12.1 ARCHEON.arcon

```
# Archeon Knowledge Graph
# Version: 1.2
# Project: MyApp

# === ORCHESTRATOR LAYER (Deterministic) ===
ORC:main :: PRS:glyph :: PRS:intent :: VAL:chain :: VAL:deps :: SPW:agent :: TST:e2e
GRF:domain :: ORC:main

# === AGENT CHAINS ===

## Authentication
[react] NED:login => TSK:submitCreds => V:AuthPage => CMP:LoginForm => OUT:showSpinner
[fastapi] API:POST/auth => FNC:validateCreds => FNC:generateToken => MDL:findOne(users)
[zustand] STO:authStore => actions: setToken, clearToken, isAuthenticated

## User Profile
[react] NED:viewProfile => TSK:clickAvatar => V:ProfilePage => CMP:ProfileCard => STO:userStore
[fastapi] API:GET/user/:id => FNC:authorize => MDL:findOne(users)
[mongo] MDL:findOne(users) => schema: { id, name, email, tier }
```

### 12.2 legend.py

```python
GLYPH_LEGEND = {
    # === User Intent Glyphs (Meta) ===
    'NED': {
        'name': 'Need',
        'description': 'User intent or motivation',
        'agent': None,  # Meta-glyph
        'color': '#9B59B6'
    },
    'TSK': {
        'name': 'Task',
        'description': 'User action',
        'agent': None,  # Meta-glyph
        'color': '#3498DB'
    },
    'OUT': {
        'name': 'Output',
        'description': 'Feedback layer',
        'agent': None,  # Meta-glyph
        'color': '#ECF0F1'
    },
    
    # === View/Component Glyphs ===
    'V': {
        'name': 'View',
        'description': 'Parent view/page container',
        'agent': 'CMP_agent',  # Uses same agent, different template
        'color': '#5D3FD3'
    },
    'CMP': {
        'name': 'Component',
        'description': 'UI component (framework agnostic)',
        'agent': 'CMP_agent',
        'color': '#1ABC9C'
    },
    
    # === State/Logic Glyphs ===
    'STO': {
        'name': 'Store',
        'description': 'Client state store',
        'agent': 'STO_agent',
        'color': '#2ECC71'
    },
    'FNC': {
        'name': 'Function',
        'description': 'Callable logic',
        'agent': 'FNC_agent',
        'color': '#F1C40F'
    },
    'EVT': {
        'name': 'Event',
        'description': 'Event emitter',
        'agent': 'EVT_agent',
        'color': '#E67E22'
    },
    
    # === Backend Glyphs ===
    'API': {
        'name': 'API',
        'description': 'HTTP endpoint',
        'agent': 'API_agent',
        'color': '#E74C3C'
    },
    'MDL': {
        'name': 'Model',
        'description': 'Database query/schema',
        'agent': 'MDL_agent',
        'color': '#795548'
    },
    
    # === Orchestrator Glyphs (Internal) ===
    'ORC': {
        'name': 'Orchestrator',
        'description': 'Core orchestrator node',
        'agent': None,  # Internal
        'color': '#2C3E50'
    },
    'PRS': {
        'name': 'Parser',
        'description': 'Chain/intent parser',
        'agent': None,  # Internal
        'color': '#34495E'
    },
    'VAL': {
        'name': 'Validator',
        'description': 'Validation engine',
        'agent': None,  # Internal
        'color': '#7F8C8D'
    },
    'SPW': {
        'name': 'Spawner',
        'description': 'Agent spawner',
        'agent': None,  # Internal
        'color': '#95A5A6'
    },
    'TST': {
        'name': 'Tester',
        'description': 'Test runner',
        'agent': None,  # Internal
        'color': '#BDC3C7'
    },
    'GRF': {
        'name': 'Graph',
        'description': 'Knowledge graph node',
        'agent': None,  # Internal
        'color': '#1A1A2E'
    },
}
```

---

## 13. Glossary

| Term | Definition |
|------|------------|
| **Glyph** | 3-character prefix representing a code artifact type (e.g., `CMP`, `API`, `MDL`) |
| **Chain** | Linear sequence of glyphs connected by operators |
| **View** | Parent container (`V:`) that holds multiple components |
| **Orchestrator** | Central brain that parses, validates, and coordinates |
| **Orchestrator Notation** | Internal deterministic glyphs (`ORC`, `PRS`, `VAL`, `SPW`, `TST`, `GRF`) |
| **Agent** | Specialized code generator for a specific glyph prefix |
| **Template** | Pre-baked code skeleton that agents fill in (structural guide) |
| **Knowledge Graph** | In-memory DAG built from parsed chains |
| **ARCHEON.arcon** | Source file containing all chains |
| **Intent Parsing** | Converting natural language or docs into chains |
| **Headless Mode** | Curl-based execution without browser rendering |

---

## 14. References

- Original brainstorm: [ref/arch.md](../ref/arch.md)
- Inspired by: Mermaid diagrams, LangGraph, CrewAI patterns
- Target stack: Python orchestrator, TypeScript/React/Vue/Angular frontend, FastAPI/Express backend, MongoDB/PostgreSQL

---

*Archeon — The canvas that builds itself.*
