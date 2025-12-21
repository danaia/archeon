# Constraint-Driven Code Generation

### A Structural Approach to AI-Assisted Development Using Glyph-Based Intermediate Representation and Design Token Propagation

---

## Abstract

This paper presents Archeon, a constraint-driven architecture for AI-assisted software development. The system introduces two key innovations: (1) a closed, glyph-based intermediate representation (IR) that compresses full-stack application architecture into a notation small enough to fit entirely within the context window of parameter-efficient models, and (2) a design token propagation system that enforces visual and interaction consistency from a single source of truth.

The architecture is HCI-first by construction: every feature chain must terminate in observable user feedback, and all visual properties derive from a canonical token specification. This constraint surface eliminates architectural drift in AI-generated code while enabling local models (30B parameters) to produce structurally equivalent output to frontier models.

We describe the formal properties of the glyph system, the token propagation mechanism, the agent decomposition strategy, and present empirical observations on context efficiency and architectural consistency.

---

## 1. Introduction

### 1.1 The Context Window Problem

Large language models generate code by predicting likely continuations given context. When context is insufficient—due to window limits, session boundaries, or retrieval failures—the model reverts to distributional priors. In software development, this manifests as **architectural drift**: syntactically valid code that violates implicit structural assumptions.

Current mitigations focus on context augmentation: larger windows, retrieval-augmented generation, embeddings. These approaches treat context as the scarce resource.

We propose an alternative: **constraint as the primary resource**.

Rather than expanding what the model sees, we compress what the model must reason about. A sufficiently dense representation of architecture—one that fits comfortably in even modest context windows—eliminates the conditions under which drift occurs.

### 1.2 The HCI Enforcement Problem

Software systems frequently implement features that lack observable user feedback. A database write with no confirmation. An API call with no error handling. A state change with no UI update.

These failures are HCI violations, but they are not enforced at the architectural level. They are caught—if at all—in code review, testing, or production incidents.

We propose **structural HCI enforcement**: an architecture where incomplete user journeys are rejected before code generation begins.

### 1.3 The Token Propagation Problem

Design systems typically maintain tokens (colors, typography, spacing) in documentation or design tools. These tokens are then manually translated to CSS, JavaScript, and framework-specific configurations. This translation introduces drift, inconsistency, and maintenance burden.

We propose **single-source token propagation**: a canonical JSON specification that generates all downstream artifacts deterministically.

---

## 2. The Glyph System

### 2.1 Formal Definition

An Archeon glyph is a typed symbol representing a single architectural concern:

```
G = (prefix, name, modifiers, args)
```

Where:
- `prefix ∈ {NED, TSK, OUT, ERR, V, CMP, STO, FNC, EVT, API, MDL}`
- `name` is an identifier
- `modifiers` is a set of behavioral annotations
- `args` is an optional parameter list

The glyph taxonomy is **closed**. No new prefixes can be introduced without modifying the system definition. This closure is the primary constraint mechanism.

### 2.2 Glyph Categories

| Prefix | Layer | Semantic Role |
|--------|-------|---------------|
| `NED` | Meta | User need / motivation |
| `TSK` | Meta | User action / task |
| `OUT` | Meta | Observable outcome |
| `ERR` | Meta | Failure path |
| `V` | View | Structural container |
| `CMP` | Frontend | UI component |
| `STO` | Frontend | Client state |
| `FNC` | Shared | Pure function |
| `EVT` | Shared | Event emitter |
| `API` | Backend | HTTP endpoint |
| `MDL` | Backend | Data model / query |

### 2.3 Edge Types

Glyphs connect via typed edges:

| Operator | Name | Semantics | Cycles |
|----------|------|-----------|--------|
| `=>` | Structural | Compile-time data dependency | Prohibited |
| `~>` | Reactive | Runtime subscription | Permitted |
| `->` | Control | Conditional branching | Prohibited |
| `::` | Containment | Structural composition | Prohibited |

### 2.4 Chain Grammar

A chain is a sequence of glyphs connected by edges:

```
Chain := Glyph (Edge Glyph)*
Edge := '=>' | '~>' | '->' | '::'
Glyph := Prefix ':' Name Modifiers? Args?
```

Chains are versioned and may include framework annotations:

```
@v1 [vue3] NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard
```

### 2.5 Closure Property

The glyph system is **algebraically closed** over the defined operations. Any composition of valid glyphs and edges produces a valid chain. Invalid compositions (e.g., `CMP => MDL`) are rejected by the boundary validator.

This closure guarantees that AI-generated chains are either valid or rejected—never silently malformed.

---

## 3. HCI-First Architecture

### 3.1 The NED-OUT Invariant

Every feature in Archeon must satisfy:

```
∀ chain: ∃ NED ∧ ∃ OUT | ERR
```

A chain that begins with user need (`NED`) must terminate in observable feedback (`OUT`) or explicit error handling (`ERR`). Chains that violate this invariant are rejected at parse time.

This is not a linting rule. It is a **structural requirement**.

### 3.2 Error Path Enforcement

API glyphs require explicit error paths:

```
API:POST/auth -> ERR:auth.invalidCredentials => OUT:toast('Invalid credentials')
```

The `->` edge represents conditional branching. Every `API` glyph must have at least one `ERR` branch defined. The validator enforces this constraint.

### 3.3 Reactivity Annotation

The `~>` edge denotes reactive relationships—runtime subscriptions that update UI when state changes:

```
STO:Auth ~> CMP:NavBar
STO:Theme ~> CMP:*
```

These relationships are explicit in the graph, enabling automatic dependency tracking and test generation.

### 3.4 Observable Outcome Taxonomy

The `OUT` glyph supports typed outcomes:

| Pattern | Semantic |
|---------|----------|
| `OUT:redirect('/path')` | Navigation |
| `OUT:toast('message')` | Notification |
| `OUT:display` | Render data |
| `OUT:download` | File delivery |
| `OUT:refresh` | State reload |

Each outcome type maps to a known UI pattern, ensuring generated code produces observable feedback.

---

## 4. Design Token Propagation

### 4.1 The Single Source of Truth

Archeon maintains design tokens in W3C DTCG (Design Tokens Community Group) format:

```json
{
  "$metadata": {
    "name": "Archeon Design System",
    "version": "1.0.0"
  },
  "color": {
    "primitive": {
      "blue": {
        "500": { "$value": "#3b82f6", "$type": "color" }
      }
    },
    "semantic": {
      "primary": {
        "default": { "$value": "{color.primitive.blue.500}" }
      }
    }
  }
}
```

References (`{path.to.token}`) are resolved at transformation time, enabling semantic aliasing without duplication.

### 4.2 Deterministic Transformation

The token file transforms to platform-specific outputs:

```
design-tokens.json
        │
        ▼
   TKN:transformer
        │
        ├──► tokens.css           (CSS custom properties)
        ├──► tokens.semantic.css  (Component aliases)
        ├──► tokens.tailwind.js   (Tailwind config)
        └──► tokens.js            (Runtime access)
```

This transformation is deterministic: identical input produces identical output. No AI generation occurs in this path.

### 4.3 Glyph Integration

The token transformer is itself a glyph:

```
TKN:transformer :: CSS:variables :: TW:config :: JS:constants
```

Executing `arc run TKN:transformer` regenerates all downstream artifacts. This integrates token propagation into the standard orchestration workflow.

### 4.4 Component Binding

Generated components reference semantic tokens:

```jsx
<button className="bg-primary text-primary-foreground rounded-md">
```

These classes resolve to CSS custom properties:

```css
:root {
  --primary-default: #3b82f6;
  --primary-foreground: #ffffff;
}
```

Changes to `design-tokens.json` propagate to all components via regeneration. No manual synchronization required.

### 4.5 Theme Switching

Light and dark mode tokens are co-located:

```json
{
  "color": {
    "surface": {
      "light": { "default": { "$value": "#ffffff" } },
      "dark": { "default": { "$value": "#0f172a" } }
    }
  }
}
```

The `.dark` class selector activates dark mode values:

```css
.dark {
  --surface-default: #0f172a;
}
```

Theme state is managed via framework-specific stores (`STO:Theme`), which trigger reactive updates to all subscribed components.

---

## 5. Agent Decomposition

### 5.1 The Single-Responsibility Principle

Each agent handles exactly one glyph prefix:

| Agent | Glyph | Responsibility |
|-------|-------|----------------|
| `CMP_agent` | `CMP` | UI component generation |
| `STO_agent` | `STO` | State store generation |
| `API_agent` | `API` | HTTP endpoint generation |
| `MDL_agent` | `MDL` | Data model generation |
| `FNC_agent` | `FNC` | Function generation |
| `EVT_agent` | `EVT` | Event emitter generation |

Agents are stateless. They receive a glyph, context projection, and template—and produce code.

### 5.2 Context Projection

The orchestrator projects only relevant context to each agent:

```python
def project_context(glyph: Glyph, graph: KnowledgeGraph) -> Context:
    """
    Extract minimal context for agent execution.
    
    For CMP:LoginForm, this includes:
    - Upstream chain (NED:login => TSK:submit)
    - Downstream dependencies (STO:Auth)
    - Related tokens (component.button, color.semantic)
    - Existing sibling components
    
    Excludes:
    - Backend implementation details
    - Unrelated feature chains
    - Historical session context
    """
```

This projection keeps agent context under 4K tokens for most operations, well within the efficient reasoning range of parameter-efficient models.

### 5.3 Template Instantiation

Agents do not generate structure. They instantiate templates:

```python
# CMP_agent receives:
{
  "glyph": "CMP:LoginForm",
  "template": "vue3",
  "props": ["username", "password"],
  "emits": ["submit"],
  "store_deps": ["Auth"],
  "tokens": ["component.input", "component.button"]
}

# Agent produces:
# - Component file with correct imports
# - Props/emits matching chain
# - Store bindings matching graph
# - Token-based styling
```

The AI's role is **instantiation**, not **architecture**. Structure is determined by the graph; agents fill in implementation details.

### 5.4 Deterministic Boundaries

Agents cannot:
- Access glyphs outside their prefix
- Modify the knowledge graph
- Communicate with other agents
- Retain state between invocations

These constraints are enforced by the orchestrator, not by agent compliance.

---

## 6. Architectural Properties

### 6.1 Compression Ratio

Empirical observation across multiple projects:

| Metric | Traditional | Archeon | Ratio |
|--------|-------------|---------|-------|
| Lines of architecture docs | 2,000–5,000 | 50–200 | 25–100x |
| Context tokens (full system) | 50,000–200,000 | 2,000–8,000 | 25x |
| Files to understand feature | 8–15 | 1 (chain) | 8–15x |

This compression enables a 30B model to hold the entire system architecture in context—a condition that larger, retrieval-dependent systems cannot guarantee.

### 6.2 Drift Resistance

Architectural drift requires the model to generate structure outside the constraint surface. In Archeon:

1. The glyph taxonomy is closed—new concepts cannot be introduced
2. Layer boundaries are enforced—illegal crossings are rejected
3. Chains are validated before generation—malformed architectures never produce code
4. Templates are deterministic—structure is fixed, only values vary

Drift can only occur within the implementation details of a single agent's output. It cannot propagate to architecture.

### 6.3 Reuse Patterns

Glyphs are reusable across chains:

```
# Multiple features share STO:Auth
NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard
NED:logout => TSK:clickLogout => STO:Auth => API:POST/logout => OUT:home
NED:profile => CMP:ProfileView => STO:Auth => API:GET/users/me => OUT:display
```

The graph tracks these relationships. When `STO:Auth` is modified, all dependent chains are identified for re-validation.

### 6.4 Test Generation

Every chain produces tests by construction:

```python
# Generated from: NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard

def test_login_happy_path():
    """Verifies: NED:login terminates in OUT:dashboard"""
    # Setup
    # Execute chain
    # Assert OUT:dashboard reached

def test_login_error_invalid_credentials():
    """Verifies: API:POST/auth -> ERR:auth.invalidCredentials => OUT:toast"""
    # Setup invalid credentials
    # Execute chain
    # Assert ERR path taken
    # Assert OUT:toast displayed
```

Test coverage is not a discipline—it is a structural property of the system.

---

## 7. Implementation

### 7.1 CLI Interface

```bash
arc init [--frontend vue3|react] [--backend fastapi]
arc parse "<chain>"
arc validate
arc gen
arc run <glyph>
arc tokens build
arc status
```

### 7.2 File Structure

```
project/
├── archeon/
│   ├── ARCHEON.arcon      # Knowledge graph
│   ├── AI_README.md       # Agent provisioning guide
│   └── _config/
│       └── design-tokens.json
├── client/
│   └── src/
│       ├── components/    # CMP: outputs
│       ├── stores/        # STO: outputs
│       └── tokens/        # TKN: outputs
└── server/
    └── src/
        ├── api/routes/    # API: outputs
        └── models/        # MDL: outputs
```

### 7.3 Orchestration Flow

```
User Intent
    │
    ▼
INT:parser ─────► Parse natural language to candidate chains
    │
    ▼
PRS:parser ─────► Parse chain syntax to AST
    │
    ▼
VAL:validator ──► Validate against graph + rules
    │
    ▼
GRF:graph ──────► Update knowledge graph
    │
    ▼
SPW:spawner ────► Dispatch to glyph-specific agents
    │
    ▼
Agent ──────────► Instantiate template with context
    │
    ▼
TST:runner ─────► Generate and execute tests
```

---

## 8. Limitations and Future Work

### 8.1 Current Limitations

1. **Framework coverage**: Currently supports Vue 3, React, and FastAPI. Additional frameworks require template development.

2. **Intent parsing**: Natural language to glyph chain conversion requires frontier model or human approval. Local models perform this task with lower accuracy.

3. **Complex queries**: `MDL` glyph currently maps to single operations. Multi-table joins and complex aggregations require manual implementation.

4. **Real-time features**: WebSocket and streaming patterns are not yet represented in the glyph taxonomy.

### 8.2 Future Directions

1. **Formal verification**: Proving chain properties (termination, error completeness) via SMT solvers.

2. **Visual graph editing**: IDE integration for graphical chain construction.

3. **Cross-project reuse**: Glyph libraries for common patterns (auth, CRUD, search).

4. **Incremental regeneration**: Dependency-aware regeneration when tokens or chains change.

---

## 9. Related Work

### 9.1 Architecture Description Languages

ADLs (AADL, Wright, Darwin) describe system architecture formally but do not integrate with AI code generation or enforce HCI properties.

### 9.2 Model-Driven Development

MDA/MDE approaches generate code from models but typically require heavyweight tooling and do not constrain AI assistants.

### 9.3 Design Systems

Tools like Style Dictionary and Tokens Studio manage design tokens but do not integrate with architectural constraint systems.

### 9.4 AI Coding Assistants

Current AI assistants (Copilot, Cursor, Cody) generate code without persistent architecture representation, leading to drift across sessions.

Archeon differs by introducing an intermediate representation layer that persists across sessions, constrains AI generation, and enforces HCI properties structurally.

---

## 10. Conclusion

Archeon demonstrates that **constraint can substitute for context** in AI-assisted development.

By compressing application architecture into a closed, glyph-based notation—and enforcing HCI properties at the structural level—the system achieves:

1. **Architectural consistency** across sessions, models, and developers
2. **HCI enforcement** by requiring observable outcomes for all features
3. **Design token propagation** from single source to all artifacts
4. **Agent isolation** via single-responsibility decomposition
5. **Model parity** between local (30B) and frontier models for constrained generation

The key insight is that AI code generation fails not from insufficient intelligence, but from insufficient constraint. A well-designed constraint surface transforms the problem from "generate plausible code" to "instantiate within boundaries"—a task that parameter-efficient models perform reliably.

This approach does not replace AI capability. It focuses that capability on the task where it excels: filling in details within a structure that humans define and machines enforce.

---

## Appendix A: Glyph Reference

| Glyph | Name | Layer | Agent | Constraint |
|-------|------|-------|-------|------------|
| `NED` | Need | Meta | — | Must have downstream |
| `TSK` | Task | Meta | — | Must have downstream |
| `OUT` | Outcome | Meta | — | Chain terminator |
| `ERR` | Error | Meta | — | Branch terminator |
| `V` | View | View | — | Contains only `CMP` |
| `CMP` | Component | Frontend | `CMP_agent` | Cannot access `MDL` |
| `STO` | Store | Frontend | `STO_agent` | Cannot access `MDL` |
| `FNC` | Function | Shared | `FNC_agent` | Pure, no side effects |
| `EVT` | Event | Shared | `EVT_agent` | Cannot cross `API` boundary |
| `API` | Endpoint | Backend | `API_agent` | Requires `ERR` path |
| `MDL` | Model | Backend | `MDL_agent` | Data layer only |
| `TKN` | Token | Internal | — | Deterministic transform |

## Appendix B: Edge Semantics

| Edge | Name | Direction | Cycles | Validation |
|------|------|-----------|--------|------------|
| `=>` | Structural | Downstream | No | Type-checked |
| `~>` | Reactive | Subscription | Yes | Store→Component only |
| `->` | Control | Branch | No | Requires `ERR` or conditional |
| `::` | Containment | Parent→Child | No | `V` contains `CMP` only |

## Appendix C: Token Categories

| Category | Purpose | Example |
|----------|---------|---------|
| `color.primitive` | Base palette | `blue.500: #3b82f6` |
| `color.semantic` | Intent mapping | `primary.default: {color.primitive.blue.500}` |
| `color.surface` | Backgrounds | `default`, `raised`, `sunken` |
| `color.content` | Text colors | `primary`, `muted`, `disabled` |
| `typography` | Font properties | `fontSize`, `fontWeight`, `lineHeight` |
| `spacing` | Layout values | `1` (0.25rem) to `96` (24rem) |
| `borderRadius` | Corner rounding | `sm`, `md`, `lg`, `full` |
| `shadow` | Elevation | `sm`, `md`, `lg`, `xl` |
| `component` | Component-specific | `button.height.md`, `input.padding` |

---

*Archeon is open source under the MIT license.*

*Repository: github.com/[redacted]/archeon*
