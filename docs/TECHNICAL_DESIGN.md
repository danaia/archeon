# Archeon Technical Design Document

> **Version:** 2.0  
> **Date:** December 20, 2025  
> **Status:** Specification (Hardened)

---

## 1. Executive Summary

Archeon is a **glyph-based architecture notation system** designed for AI-orchestrated, hallucination-free software development. It provides a hyper-compressed, human-readable **intermediate representation (IR)** that serves as both documentation and executable specification.

The system enables:
- **One-to-one traceability** between notation and code
- **Modular AI agents** that build code from templates (instantiate, never invent)
- **Automated validation** through orchestrator-owned testing
- **Domain memory** as a living, versioned knowledge graph
- **Intent parsing** that proposes chains (never auto-executes)
- **Error path modeling** for realistic failure handling

**Core Invariant:** Archeon is a compiler + build system, not an "AI framework". Determinism wins.

---

## 2. Core Philosophy

### 2.1 The UX Foundation
Everything in a user interface is based on:
- **Need (NED)** — User motivation
- **Task (TSK)** — Action taken to satisfy the need
- **Observation (OUT)** — System feedback completing the loop (must exist)

```
NED:motivation → TSK:action → OUT:feedback
```

This is Archeon's strongest constraint: **every chain must close with observable feedback**. If `OUT:` doesn't exist, the chain is incomplete—and hallucination is blocked.

### 2.2 Design Principles
1. **Compression over verbosity** — Dense glyphs replace prose
2. **Traceability over abstraction** — Every glyph maps to exactly one code artifact
3. **Validation over trust** — Orchestrator validates all agent output
4. **Templates over generation** — Agents instantiate, not invent
5. **Framework agnostic** — Components work across React, Vue, Angular, Svelte, etc.
6. **Explicit over magic** — Intent parsing proposes, humans approve
7. **Failure paths are first-class** — Errors are modeled, not afterthoughts

---

## 3. Glyph Notation Specification

### 3.1 Core Glyph Set (3-Character Prefixes)

| Prefix | Name | Description | Example |
|--------|------|-------------|---------|
| `NED:` | Need | User intent/motivation | `NED:login` |
| `TSK:` | Task | User action | `TSK:clickSubmit` |
| `V:` | View | Structural container → `App.vue`, `Page.tsx`, `_layout.tsx` | `V:Dashboard` |
| `CMP:` | Component | UI component (framework agnostic) | `CMP:LoginForm` |
| `STO:` | Store | Client state store/context | `STO:authStore` |
| `FNC:` | Function | Callable logic | `FNC:auth.validateCreds` |
| `EVT:` | Event | Emit/broadcast | `EVT:publish('auth')` |
| `API:` | API | Endpoint signature | `API:POST/auth` |
| `MDL:` | Model | Database query/schema | `MDL:user.findOne` |
| `OUT:` | Output | Feedback layer | `OUT:toast('Success')` |
| `ERR:` | Error | Failure/exception path | `ERR:authFailed` |

### 3.2 Secondary Qualifiers (Namespace.Action)

To prevent ambiguity as systems scale, glyphs use **dot-notation qualifiers**:

```
# Functions by domain
FNC:auth.validateCreds       # Authentication logic
FNC:auth.hashPassword        # Security function
FNC:ui.formatDate            # Presentation helper
FNC:domain.calculateTier     # Business logic

# Models by entity
MDL:user.findOne             # User queries
MDL:user.updateTier          # User mutations
MDL:chat.append              # Chat operations

# Components by behavior
CMP:LoginForm[stateful]      # Has internal state
CMP:ProfileCard[presentational]  # Pure render
CMP:DataGrid[headless]       # Opt-in for headless mode

# Errors by category
ERR:auth.invalidCreds        # Auth failures
ERR:auth.tokenExpired        # Token issues
ERR:validation.malformed     # Input errors
ERR:system.rateLimit         # Infrastructure errors
```

**Rule:** Qualifiers are optional for simple cases but required when ambiguity exists. Validator flags duplicates.

### 3.3 Orchestrator Notation (Knowledge Graph)

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

### 3.4 Edge Types (Operators)

Archeon distinguishes between **structural dependencies** and **runtime flows**:

| Operator | Type | Meaning | Cycles Allowed? |
|----------|------|---------|-----------------|
| `=>` | Structural | Data flow (compile-time dependency) | ❌ No |
| `~>` | Reactive | Runtime feedback loop | ✅ Yes |
| `!>` | Side-effect | External effect (email, webhook, log) | ✅ Yes |
| `->` | Control | Branch/redirect (conditional) | ❌ No |
| `::` | Internal | Orchestrator dependency | ❌ No |
| `@` | Containment | View contains components | N/A |

**Examples:**
```
# Structural (no cycles allowed)
CMP:Form => STO:formStore => API:POST/submit

# Reactive (cycles allowed - this is normal UI)
CMP:Form => STO:formStore ~> CMP:Form

# Side-effect (doesn't block, doesn't cycle)
API:POST/user => MDL:user.create !> FNC:email.sendWelcome

# Control flow (branching)
FNC:auth.check -> ERR:auth.denied => OUT:toast('Access denied')
FNC:auth.check -> CMP:Dashboard
```

### 3.5 View Containment Invariant

> **Invariant:**  
> `V:` is a structural container only.  
> It never executes, never owns logic, never spawns an agent, and never participates in data flow.  
> All behavior lives in `CMP:` and below.

**Framework File Mapping:**

| Framework | `V:` Maps To | Example |
|-----------|--------------|--------|
| Vue | `App.vue`, `views/*.vue` | `V:Dashboard` → `views/Dashboard.vue` |
| React | `Page.tsx`, `_layout.tsx` | `V:Profile` → `pages/Profile.tsx` |
| Next.js | `app/*/page.tsx`, `layout.tsx` | `V:Settings` → `app/settings/page.tsx` |
| Angular | `*.component.ts` (routed) | `V:Home` → `home/home.component.ts` |
| Svelte | `+page.svelte`, `+layout.svelte` | `V:About` → `routes/about/+page.svelte` |

`V:` files are **structural shells** — they import and compose `CMP:` components but contain no logic themselves.

**Valid:**
```
V:ProfilePage @ CMP:Header, CMP:ProfileCard, CMP:ActivityFeed
```

**Invalid (blocked by VAL:boundary):**
```
V:ProfilePage => STO:userStore        # ❌ V cannot access stores
V:ProfilePage => API:GET/user         # ❌ V cannot access APIs
V:ProfilePage ~> CMP:ProfileCard      # ❌ V cannot have reactive edges
```

### 3.6 Chain Versioning

All chains are versioned for audit, regression, and historical reasoning:

```
@v1 NED:login => TSK:submitCreds => CMP:LoginForm => API:POST/auth
@v2 NED:login => TSK:submitCreds => CMP:LoginForm => FNC:auth.validate => API:POST/auth
@v3 NED:login => TSK:submitCreds => CMP:LoginForm => FNC:auth.validate => API:POST/auth -> ERR:auth.failed
```

**Version Rules:**
- `@v1` is always the original chain
- New versions are appended, old versions preserved
- Orchestrator can diff versions for regression testing
- `@latest` alias points to highest version
- Deprecation: `@v1 [deprecated]`

### 3.7 Agent Tags

Agents are tagged in square brackets for framework-specific generation:
```
[react] CMP:Dashboard => STO:userStore
[vue] CMP:Dashboard => STO:userStore
[angular] CMP:Dashboard => STO:userStore
[fastapi] API:GET/user => FNC:auth.validate => MDL:user.findOne
[express] API:GET/user => FNC:auth.validate => MDL:user.findOne
[mongo] MDL:user.findOne
[postgres] MDL:user.findOne
```

### 3.8 Chain Examples

**View with Components (Containment Only):**
```
V:ProfilePage @ CMP:Header, CMP:ProfileCard, CMP:ActivityFeed
```

**Full User Flow (Happy Path):**
```
@v1 NED:viewProfile => TSK:clickAvatar => V:ProfilePage => CMP:ProfileCard => FNC:ui.formatDate => STO:userStore => API:GET/user/:id => MDL:user.findOne => OUT:renderProfile
```

**Authentication Flow (with Error Handling):**
```
@v1 NED:login => TSK:submitCreds => CMP:LoginForm => API:POST/auth => FNC:auth.validateToken => MDL:user.findOne => EVT:authSuccess => OUT:redirect('/dashboard')
@v1 API:POST/auth -> ERR:auth.invalidCreds => OUT:toast('Invalid credentials')
@v1 API:POST/auth -> ERR:auth.rateLimited => OUT:toast('Too many attempts')
```

**Backend Chain (with Side-Effects):**
```
@v1 API:POST/user => FNC:validation.userInput => FNC:auth.hashPassword => MDL:user.create !> FNC:email.sendWelcome => OUT:201
@v1 API:POST/user -> ERR:validation.malformed => OUT:400
@v1 API:POST/user -> ERR:system.dbError => OUT:500
```

**Reactive UI Pattern (feedback loop allowed):**
```
@v1 CMP:SearchInput => STO:searchStore ~> CMP:SearchResults
@v1 STO:searchStore => API:GET/search => MDL:search.query ~> STO:searchStore
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
│              Owns: Intent Parsing (PROPOSE ONLY)             │
│              Owns: Chain Versioning                          │
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

### 4.2 Intent Parsing (Proposal Mode Only)

**Critical Constraint:** Intent parsing is **lossy by definition**. The orchestrator:
- ✅ **Proposes** chains from natural language
- ✅ **Requires explicit approval** before adding to graph
- ❌ **Never auto-writes** code without a resolved, approved chain

| Source | Format | Workflow |
|--------|--------|----------|
| Direct CLI | Raw chain string | Parse → Validate → Add (if valid) |
| Requirements Doc | Markdown link | Parse → **Propose** → Human Approval → Add |
| Task Ticket | JIRA/Linear/GitHub link | Parse → **Propose** → Human Approval → Add |
| Tech Design | Markdown/Notion | Parse → **Propose** → Human Approval → Add |
| User Story | Natural language | Parse → **Propose** → Human Approval → Add |

**Intent-to-Chain Conversion (Proposal):**
```bash
$ archeon intent "User wants to login with email and password"

PROPOSED CHAIN (requires approval):
  @v1 NED:login => TSK:submitCreds => CMP:LoginForm => API:POST/auth => MDL:user.findOne => OUT:redirect

  Missing error paths detected. Suggest adding:
  - API:POST/auth -> ERR:auth.invalidCreds
  - API:POST/auth -> ERR:auth.rateLimited

  [a]pprove  [e]dit  [r]eject  [s]uggest errors
```

### 4.3 Ownership Boundaries (Layer Enforcement)

The orchestrator enforces strict architectural boundaries:

| Rule | Constraint | Rationale |
|------|------------|-----------|
| `CMP` ↛ `MDL` | Components cannot directly access models | Prevents data layer leakage |
| `STO` ↛ `MDL` | Stores cannot directly access models | Must go through API |
| `EVT` ↛ `API` | Events cannot cross trust boundaries directly | Security isolation |
| `FNC:ui.*` ↛ `MDL` | UI functions cannot touch data | Presentation/data separation |
| `MDL` ↛ `CMP` | Models cannot reference components | Backend independence |

**Valid Flow:**
```
CMP:Form => STO:formStore => API:POST/data => FNC:validation.input => MDL:data.create
```

**Invalid Flow (blocked by validator):**
```
CMP:Form => MDL:data.create  # ❌ VAL:boundary - CMP cannot directly access MDL
```

### 4.4 Knowledge Graph Structure

The knowledge graph is stored in `ARCHEON.arcon`:

```
# Archeon v2.0
# Orchestrator Layer (Deterministic Reference)
ORC:main :: PRS:glyph
PRS:glyph :: VAL:chain
VAL:chain :: VAL:boundary
VAL:boundary :: SPW:agent
SPW:agent :: TST:e2e
GRF:domain :: ORC:main

# Agent Chains (Versioned)
@v1 [react] NED:chat => TSK:send => V:ChatPage => CMP:MessageBox => FNC:ui.timestamp => OUT:badge(+1)
@v1 [fastapi] API:POST/chat => FNC:validation.message => FNC:auth.rateLimit => MDL:chat.append
@v1 [fastapi] API:POST/chat -> ERR:auth.rateLimited => OUT:429
@v1 [zustand] STO:chatStore => actions: addMessage, clear
@v1 [mongo] MDL:chat.append !> EVT:emit('update')
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
2. Parse user intent from natural language, docs, or task tickets (**propose only**)
3. Validate chain integrity (no orphans, no duplicates, no boundary violations)
4. Enforce ownership boundaries between layers
5. Route glyph prefixes to appropriate agents
6. Generate and execute end-to-end tests (including error paths)
7. Maintain single source of truth via deterministic notation
8. Track chain versions and enable regression testing

**Orchestrator Internal Graph (Deterministic):**
```
ORC:main          # Entry point
  :: PRS:glyph    # Parse incoming chains
  :: PRS:intent   # Parse natural language / docs (PROPOSE ONLY)
  :: VAL:chain    # Validate structure
  :: VAL:deps     # Validate dependencies
  :: VAL:boundary # Enforce ownership rules
  :: VAL:version  # Check version conflicts
  :: SPW:agent    # Spawn appropriate agent
  :: TST:unit     # Run unit tests
  :: TST:e2e      # Run integration tests
  :: TST:error    # Run error path tests
  :: GRF:update   # Update knowledge graph
```

**Validation Rules:**
- Every glyph must resolve to exactly one file path
- No structural cycles (`=>`, `->`) — reactive cycles (`~>`) allowed
- All `MDL:` queries must have corresponding `API:` endpoints
- All `CMP:` components must have tests
- All `V:` views must contain at least one `CMP:`
- All `API:` endpoints should have at least one `ERR:` path
- Ownership boundaries are enforced (see 4.3)
- Duplicate qualifiers are flagged (e.g., two `FNC:auth.validate`)

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
    
    @abstractmethod
    def generate_error_test(self, glyph: str, error: str, framework: str) -> str:
        """Generate test for error path."""
        pass
```

**Agent Behavior:**
1. Receive glyph + framework tag from orchestrator
2. Look up corresponding template from `templates/{PREFIX}/{framework}`
3. Fill template with chain values
4. Write file to appropriate location
5. Generate companion test (happy path + error paths)
6. Report back to orchestrator for validation

### 6.3 Templates (Structural Guides)

Templates provide the **structure and conventions** that agents must follow. They are not generated—they are reference patterns.

**Template Purpose:**
- Define the skeleton/boilerplate for each artifact type
- Enforce consistent code style across the codebase
- Provide placeholders that agents fill with chain-derived values
- Support multiple frameworks per glyph type
- Include error handling scaffolding

**Component Template (`templates/CMP/react.tsx`):**
```tsx
import React, { FC } from 'react';

interface {COMPONENT_NAME}Props {
  {PROPS}
}

/**
 * @archeon CMP:{COMPONENT_NAME}
 * @chain {CHAIN_CONTEXT}
 * @version {VERSION}
 * @headless {HEADLESS_ENABLED}
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
 * @version {VERSION}
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

class {MODEL_NAME}Error(BaseModel):
    """@archeon ERR:{ERROR_CODES} - Error responses"""
    code: str
    message: str

@router.{METHOD}("/{ROUTE}")
async def {HANDLER_NAME}(request: {MODEL_NAME}Request) -> {MODEL_NAME}Response:
    """
    @archeon API:{METHOD}/{ROUTE}
    @chain {CHAIN_CONTEXT}
    @version {VERSION}
    @errors {ERROR_PATHS}
    """
    # Generated by Archeon
    try:
        # Happy path
        pass
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
```

**Store Template (`templates/STO/zustand.ts`):**
```typescript
import { create } from 'zustand';

/**
 * @archeon STO:{STORE_NAME}
 * @chain {CHAIN_CONTEXT}
 * @version {VERSION}
 */
interface {STORE_NAME}State {
  {STATE_FIELDS}
  error: string | null;
}

interface {STORE_NAME}Actions {
  {ACTION_SIGNATURES}
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const use{STORE_NAME} = create<{STORE_NAME}State & {STORE_NAME}Actions>((set, get) => ({
  // State
  {INITIAL_STATE}
  error: null,
  
  // Actions
  {ACTIONS}
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),
}));
```

---

## 7. CLI Interface

```bash
# Initialize new Archeon project
archeon init

# Parse and add chain to knowledge graph (direct, no approval needed)
archeon parse "NED:login => TSK:submit => CMP:LoginForm => API:POST/auth"

# Parse with version tag
archeon parse "@v2 NED:login => TSK:submit => CMP:LoginForm[stateful] => API:POST/auth"

# Import from requirements/task docs (PROPOSAL MODE - requires approval)
archeon import ./docs/requirements.md
archeon import ./docs/TECH_DESIGN.md
archeon import https://linear.app/team/issue/ABC-123
archeon import https://github.com/org/repo/issues/42

# Parse natural language intent (PROPOSAL MODE - requires approval)
archeon intent "User wants to reset their password via email"
archeon intent --auto-errors "User wants to login"  # Auto-suggest error paths

# Generate code for all unresolved glyphs
archeon gen

# Generate for specific framework
archeon gen --frontend react --backend fastapi --db mongo

# Run orchestrator workflow
archeon orchestrate

# Execute all tests (happy + error paths)
archeon test
archeon test --errors-only  # Just error path tests

# Validate knowledge graph integrity
archeon validate
archeon validate --boundaries  # Check ownership rules only
archeon validate --cycles      # Check for illegal cycles

# Export graph visualization (DOT/PNG)
archeon graph --format png

# Audit repository for drift
archeon audit

# Show orchestrator internal state
archeon status

# Version management
archeon versions NED:login        # Show all versions of a chain
archeon diff @v1 @v2 NED:login   # Diff two versions
archeon deprecate @v1 NED:login  # Mark version as deprecated

# Headless mode control
archeon headless enable CMP:UserProfile   # Opt-in component
archeon headless disable CMP:UserProfile  # Opt-out
archeon headless list                     # Show all headless-enabled
```

---

## 8. Test Generation

### 8.1 Orchestrator-Owned Testing

The orchestrator generates E2E tests from chains, including **error paths**:

**Happy Path Test:**
```python
# Auto-generated from: @v1 NED:login => TSK:submit => CMP:LoginForm => API:POST/auth => OUT:redirect
def test_login_journey_happy():
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

**Error Path Tests:**
```python
# Auto-generated from: @v1 API:POST/auth -> ERR:auth.invalidCreds => OUT:toast('Invalid')
def test_login_journey_invalid_creds():
    with TestApp() as app:
        user = User()
        user.fill('email', 'dana@example.com')
        user.fill('password', 'wrong')
        user.click('submit')
        
        # ERR:auth.invalidCreds
        assert api_log.last.status == 401
        
        # OUT:toast
        assert user.toast.text == 'Invalid credentials'
        assert user.current_path == '/login'  # Did not redirect

# Auto-generated from: @v1 API:POST/auth -> ERR:auth.rateLimited => OUT:toast('Too many')
def test_login_journey_rate_limited():
    with TestApp() as app:
        user = User()
        
        # Trigger rate limit
        for _ in range(10):
            user.fill('email', 'dana@example.com')
            user.fill('password', 'wrong')
            user.click('submit')
        
        # ERR:auth.rateLimited
        assert api_log.last.status == 429
        assert user.toast.text == 'Too many attempts'
```

### 8.2 Test Coverage Rules

| Glyph | Required Test |
|-------|---------------|
| `V:` | Structural validation only (child CMP presence, no rendering) |
| `CMP:` | Render test + snapshot |
| `CMP:[stateful]` | Render + state mutation test |
| `STO:` | State mutation test + error state test |
| `API:` | Request/response contract + all `ERR:` paths |
| `MDL:` | Query result shape |
| `FNC:` | Input/output assertion |
| `EVT:` | Event emission verification |
| `ERR:` | Error handling verification + OUT assertion |

---

## 9. Headless Execution Mode

### 9.1 Opt-In Requirement

Headless mode is **explicitly opt-in per component**. Components must be annotated:

```
CMP:UserProfile[headless]    # Enabled
CMP:LoginForm                # NOT enabled (default)
```

**Why?** Prevents:
- Components acting like controllers
- Security boundary leakage
- "Magic" APIs bypassing normal flows

### 9.2 Sandbox Mode (Default)

Headless execution runs in **sandbox/trace mode by default**:

```bash
# Trace mode (default) - logs everything, no side effects
curl http://localhost:3000/api/cmp/userprofile?action=load&name=Dana&mode=trace

# Response includes full trace
{
  "event": "profileLoaded",
  "data": { "name": "Dana", "tier": "pro" },
  "latency_ms": 42,
  "trace": [
    { "glyph": "FNC:ui.formatDate", "time_ms": 2 },
    { "glyph": "STO:userStore.get", "time_ms": 1 },
    { "glyph": "API:GET/user/123", "time_ms": 38, "mocked": true }
  ],
  "sandbox": true
}
```

### 9.3 Live Mode (Explicit)

```bash
# Live mode - requires explicit flag
curl http://localhost:3000/api/cmp/userprofile?action=load&name=Dana&mode=live

# Must also have @headless annotation in template
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
| `ERR:` | Magenta | Spike/Warning |

### 10.3 Edge Visualization

| Operator | Visual |
|----------|--------|
| `=>` | Solid line (structural) |
| `~>` | Dashed line (reactive) |
| `!>` | Dotted line (side-effect) |
| `->` | Arrow with branch node |

### 10.4 Spatial Semantics

- **X-axis**: User journey (left to right)
- **Y-axis**: Control flow forks (branching, error paths)
- **Z-axis**: Data depth (latency visualization)

---

## 11. Implementation Roadmap

### Phase 1: Core Engine (Week 1-2)
- [ ] Implement glyph parser with qualifier support (PRS_parser.py)
- [ ] Build knowledge graph data structure (GRF_graph.py)
- [ ] Implement edge type detection (`=>`, `~>`, `!>`, `->`)
- [ ] Create base agent class
- [ ] Implement CMP agent with React template

### Phase 2: Validation Engine (Week 3-4)
- [ ] Chain validation (VAL_validator.py)
- [ ] Ownership boundary enforcement
- [ ] Cycle detection (structural vs reactive)
- [ ] Duplicate qualifier detection
- [ ] Version conflict detection

### Phase 3: Agent Suite (Week 5-6)
- [ ] STO agent (Zustand, Redux, Pinia)
- [ ] API agent (FastAPI, Express) with error scaffolding
- [ ] MDL agent (MongoDB, PostgreSQL)
- [ ] FNC agent with domain qualifiers
- [ ] EVT agent
- [ ] ERR agent (error path generation)

### Phase 4: Orchestration (Week 7-8)
- [ ] Agent spawner (SPW_spawner.py)
- [ ] Test generator with error paths (TST_runner.py)
- [ ] CLI interface with proposal mode
- [ ] Version management commands

### Phase 5: Intent Parsing (Week 9-10)
- [ ] Natural language → chain conversion (INT_intent.py)
- [ ] **Proposal-only mode** (no auto-execute)
- [ ] Error path suggestion engine
- [ ] Requirements doc parser
- [ ] Task ticket integration (Linear, JIRA, GitHub)

### Phase 6: Headless Mode (Week 11-12)
- [ ] Opt-in annotation system
- [ ] Sandbox/trace mode (default)
- [ ] Live mode (explicit)
- [ ] Metrics collection

### Phase 7: Visualization (Week 13-16)
- [ ] Three.js grid canvas
- [ ] Node spawning/connecting
- [ ] Edge type visualization
- [ ] Real-time chain preview
- [ ] Export to ARCHEON.arcon

---

## 12. File Formats

### 12.1 ARCHEON.arcon

```
# Archeon Knowledge Graph
# Version: 2.0
# Project: MyApp

# === ORCHESTRATOR LAYER (Deterministic) ===
ORC:main :: PRS:glyph :: PRS:intent :: VAL:chain :: VAL:boundary :: VAL:version :: SPW:agent :: TST:e2e :: TST:error
GRF:domain :: ORC:main

# === AGENT CHAINS (Versioned) ===

## Authentication
@v1 [react] NED:login => TSK:submitCreds => V:AuthPage => CMP:LoginForm[stateful] => OUT:showSpinner
@v1 [fastapi] API:POST/auth => FNC:auth.validateCreds => FNC:auth.generateToken => MDL:user.findOne
@v1 [fastapi] API:POST/auth -> ERR:auth.invalidCreds => OUT:401
@v1 [fastapi] API:POST/auth -> ERR:auth.rateLimited => OUT:429
@v1 [zustand] STO:authStore => actions: setToken, clearToken, isAuthenticated

## User Profile
@v1 [react] NED:viewProfile => TSK:clickAvatar => V:ProfilePage => CMP:ProfileCard[headless] => STO:userStore
@v1 [fastapi] API:GET/user/:id => FNC:auth.authorize => MDL:user.findOne
@v1 [fastapi] API:GET/user/:id -> ERR:auth.forbidden => OUT:403
@v1 [mongo] MDL:user.findOne => schema: { id, name, email, tier }

## Chat (with reactive loop)
@v1 [react] CMP:ChatInput => STO:chatStore ~> CMP:ChatMessages
@v1 [fastapi] API:POST/chat => FNC:validation.message => FNC:auth.rateLimit => MDL:chat.append !> EVT:broadcast('newMessage')
```

### 12.2 legend.py

```python
GLYPH_LEGEND = {
    # === User Intent Glyphs (Meta) ===
    'NED': {
        'name': 'Need',
        'description': 'User intent or motivation',
        'agent': None,  # Meta-glyph
        'color': '#9B59B6',
        'layer': 'meta'
    },
    'TSK': {
        'name': 'Task',
        'description': 'User action',
        'agent': None,  # Meta-glyph
        'color': '#3498DB',
        'layer': 'meta'
    },
    'OUT': {
        'name': 'Output',
        'description': 'Feedback layer (must exist to close chain)',
        'agent': None,  # Meta-glyph
        'color': '#ECF0F1',
        'layer': 'meta'
    },
    
    # === Error Glyph ===
    'ERR': {
        'name': 'Error',
        'description': 'Failure/exception path',
        'agent': 'ERR_agent',
        'color': '#E91E63',
        'layer': 'meta',
        'qualifiers': ['auth', 'validation', 'system', 'domain']
    },
    
    # === View Glyph (Structural Only) ===
    'V': {
        'name': 'View',
        'description': 'Structural container (no logic, no agent)',
        'agent': None,              # V: never spawns an agent
        'color': '#5D3FD3',
        'layer': 'frontend',
        'contains': ['CMP'],        # Only valid relationship
        'cannot_execute': True,     # Never runs headless
        'allowed_operators': ['@'], # Containment only
        'file_patterns': {          # Framework → file mapping
            'vue': 'views/{name}.vue',
            'react': 'pages/{name}.tsx',
            'nextjs': 'app/{name}/page.tsx',
            'angular': '{name}/{name}.component.ts',
            'svelte': 'routes/{name}/+page.svelte'
        }
    },
    
    # === Component Glyphs ===
    'CMP': {
        'name': 'Component',
        'description': 'UI component (framework agnostic)',
        'agent': 'CMP_agent',
        'color': '#1ABC9C',
        'layer': 'frontend',
        'modifiers': ['stateful', 'presentational', 'headless']
    },
    
    # === State/Logic Glyphs ===
    'STO': {
        'name': 'Store',
        'description': 'Client state store',
        'agent': 'STO_agent',
        'color': '#2ECC71',
        'layer': 'frontend',
        'cannot_access': ['MDL']  # Ownership boundary
    },
    'FNC': {
        'name': 'Function',
        'description': 'Callable logic',
        'agent': 'FNC_agent',
        'color': '#F1C40F',
        'layer': 'shared',
        'qualifiers': ['auth', 'ui', 'domain', 'validation', 'email']
    },
    'EVT': {
        'name': 'Event',
        'description': 'Event emitter',
        'agent': 'EVT_agent',
        'color': '#E67E22',
        'layer': 'shared',
        'cannot_cross': ['API']  # Without API bridge
    },
    
    # === Backend Glyphs ===
    'API': {
        'name': 'API',
        'description': 'HTTP endpoint',
        'agent': 'API_agent',
        'color': '#E74C3C',
        'layer': 'backend',
        'requires_error_paths': True
    },
    'MDL': {
        'name': 'Model',
        'description': 'Database query/schema',
        'agent': 'MDL_agent',
        'color': '#795548',
        'layer': 'backend',
        'qualifiers': ['user', 'chat', 'search', 'analytics']
    },
    
    # === Orchestrator Glyphs (Internal) ===
    'ORC': {
        'name': 'Orchestrator',
        'description': 'Core orchestrator node',
        'agent': None,
        'color': '#2C3E50',
        'layer': 'internal'
    },
    'PRS': {
        'name': 'Parser',
        'description': 'Chain/intent parser',
        'agent': None,
        'color': '#34495E',
        'layer': 'internal'
    },
    'VAL': {
        'name': 'Validator',
        'description': 'Validation engine',
        'agent': None,
        'color': '#7F8C8D',
        'layer': 'internal'
    },
    'SPW': {
        'name': 'Spawner',
        'description': 'Agent spawner',
        'agent': None,
        'color': '#95A5A6',
        'layer': 'internal'
    },
    'TST': {
        'name': 'Tester',
        'description': 'Test runner',
        'agent': None,
        'color': '#BDC3C7',
        'layer': 'internal'
    },
    'GRF': {
        'name': 'Graph',
        'description': 'Knowledge graph node',
        'agent': None,
        'color': '#1A1A2E',
        'layer': 'internal'
    },
}

# Edge type definitions
EDGE_TYPES = {
    '=>': {
        'name': 'structural',
        'description': 'Compile-time data dependency',
        'cycles_allowed': False,
        'visual': 'solid'
    },
    '~>': {
        'name': 'reactive',
        'description': 'Runtime feedback loop',
        'cycles_allowed': True,
        'visual': 'dashed'
    },
    '!>': {
        'name': 'side-effect',
        'description': 'External effect (non-blocking)',
        'cycles_allowed': True,
        'visual': 'dotted'
    },
    '->': {
        'name': 'control',
        'description': 'Branch/conditional flow',
        'cycles_allowed': False,
        'visual': 'arrow-branch'
    },
    '::': {
        'name': 'internal',
        'description': 'Orchestrator dependency',
        'cycles_allowed': False,
        'visual': 'thick'
    }
}

# Ownership boundary rules
BOUNDARY_RULES = [
    # V: is structural only - no data flow operators allowed
    {'from': 'V', 'operator': '=>', 'allowed': False, 'reason': 'Views cannot participate in data flow'},
    {'from': 'V', 'operator': '~>', 'allowed': False, 'reason': 'Views cannot have reactive edges'},
    {'from': 'V', 'operator': '->', 'allowed': False, 'reason': 'Views cannot have control flow'},
    {'from': 'V', 'operator': '!>', 'allowed': False, 'reason': 'Views cannot trigger side-effects'},
    
    # CMP/STO/EVT boundaries
    {'from': 'CMP', 'to': 'MDL', 'allowed': False, 'reason': 'Components cannot directly access models'},
    {'from': 'STO', 'to': 'MDL', 'allowed': False, 'reason': 'Stores must go through API'},
    {'from': 'EVT', 'to': 'API', 'allowed': False, 'reason': 'Events cannot cross trust boundaries directly'},
    {'from': 'MDL', 'to': 'CMP', 'allowed': False, 'reason': 'Backend cannot reference frontend'},
    {'from': 'FNC:ui', 'to': 'MDL', 'allowed': False, 'reason': 'UI functions cannot touch data layer'},
]
```

---

## 13. Glossary

| Term | Definition |
|------|------------|
| **Glyph** | 3-character prefix representing a code artifact type (e.g., `CMP`, `API`, `MDL`) |
| **Qualifier** | Dot-notation suffix for disambiguation (e.g., `FNC:auth.validate`, `MDL:user.findOne`) |
| **Modifier** | Bracket annotation for behavior (e.g., `CMP:Form[stateful]`, `CMP:Card[headless]`) |
| **Chain** | Linear sequence of glyphs connected by operators |
| **Edge Type** | Operator defining relationship: `=>` structural, `~>` reactive, `!>` side-effect, `->` control |
| **View** | Parent container (`V:`) that holds multiple components |
| **Orchestrator** | Central brain that parses, validates, and coordinates |
| **Orchestrator Notation** | Internal deterministic glyphs (`ORC`, `PRS`, `VAL`, `SPW`, `TST`, `GRF`) |
| **Agent** | Specialized code generator for a specific glyph prefix |
| **Template** | Pre-baked code skeleton that agents fill in (structural guide) |
| **Knowledge Graph** | In-memory DAG built from parsed chains |
| **ARCHEON.arcon** | Source file containing all versioned chains |
| **Intent Parsing** | Converting natural language or docs into **proposed** chains (requires approval) |
| **Proposal Mode** | Intent parsing workflow where chains must be explicitly approved |
| **Headless Mode** | Curl-based execution (opt-in only, sandbox by default) |
| **Ownership Boundary** | Layer enforcement rules (e.g., `CMP` cannot access `MDL` directly) |
| **Error Path** | `ERR:` glyph representing failure/exception handling |
| **Version Tag** | Chain version prefix (e.g., `@v1`, `@v2`, `@latest`) |
| **Structural Cycle** | Illegal circular dependency via `=>` or `->` operators |
| **Reactive Cycle** | Allowed feedback loop via `~>` operator (normal UI pattern) |

---

## 14. Validation Rules Summary

| Rule | Enforced By | Error Code |
|------|-------------|------------|
| `V:` can only use `@` operator (containment) | `VAL:boundary` | `ERR:boundary.viewDataFlow` |
| Every chain must end with `OUT:` | `VAL:chain` | `ERR:chain.noOutput` |
| No structural cycles (`=>`, `->`) | `VAL:chain` | `ERR:chain.structuralCycle` |
| Reactive cycles (`~>`) are allowed | `VAL:chain` | N/A |
| `CMP` cannot directly access `MDL` | `VAL:boundary` | `ERR:boundary.cmpToMdl` |
| `STO` cannot directly access `MDL` | `VAL:boundary` | `ERR:boundary.stoToMdl` |
| `EVT` cannot cross to `API` without bridge | `VAL:boundary` | `ERR:boundary.evtToApi` |
| All `API:` should have at least one `ERR:` | `VAL:chain` | `WARN:api.noErrorPath` |
| Duplicate qualifiers are flagged | `VAL:chain` | `ERR:glyph.duplicate` |
| Version conflicts are blocked | `VAL:version` | `ERR:version.conflict` |
| Headless requires `[headless]` modifier | `VAL:headless` | `ERR:headless.notEnabled` |

---

## 15. References

- Original brainstorm: [ref/arch.md](../ref/arch.md)
- Inspired by: Mermaid diagrams, LangGraph, CrewAI patterns
- Target stack: Python orchestrator, TypeScript/React/Vue/Angular frontend, FastAPI/Express backend, MongoDB/PostgreSQL

---

*Archeon — A human-readable IR for software systems that happens to be AI-operable.*
*The canvas that builds itself.*
