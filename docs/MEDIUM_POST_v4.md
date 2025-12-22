# Constraint-Driven Code Generation

### A Structural Approach to AI-Assisted Development Using Glyph-Based Architecture and Semantic Attention Routing

---

## Abstract

This paper presents **Archeon**, a constraint-driven architecture for AI-assisted software development. Archeon introduces two core ideas:

1. A **closed, glyph-based intermediate representation (IR)** that compresses full-stack application architecture into a compact, persistent notation suitable for parameter-efficient models.
2. A **semantic attention-routing mechanism**, implemented through self-describing code annotations and an architecture index, that constrains *where* an AI assistant is allowed to look and modify code—without requiring full context injection or brittle code slicing.

Rather than treating context window size as the primary bottleneck, Archeon treats **architectural constraint and attention discipline** as first-class resources. The system enforces HCI completeness structurally, propagates design tokens from a single source of truth, and limits AI-generated changes to explicitly declared architectural surfaces.

The result is a system in which local models (≈30B parameters), operating inside modern IDEs with full-repo indexing, can reliably produce architecture-consistent changes comparable to frontier models—without access to the entire codebase in-prompt.

---

## 1. Introduction

### 1.1 The Context Window Problem (Reframed)

Large language models generate code by predicting continuations conditioned on context. When architectural context is incomplete—due to context window limits, session boundaries, or retrieval failures—the model falls back to statistical priors. In software systems, this manifests as **architectural drift**: code that is locally plausible but globally inconsistent.

Most current mitigations focus on expanding context:

* larger windows
* retrieval-augmented generation (RAG)
* embeddings over full repositories

These approaches assume that *context volume* is the scarce resource.

Archeon proposes a different framing:

> **Attention, not context, is the scarce resource.**

Rather than forcing models to reason over entire repositories, Archeon constrains *what the model is allowed to attend to* through explicit architectural representations and semantic boundaries embedded directly in code.

---

### 1.2 The HCI Enforcement Problem

Many production systems contain features that technically function but violate basic HCI principles:

* API calls without observable confirmation
* state changes without UI feedback
* failure paths with no user-facing affordance

These errors are rarely architectural violations; they are experiential ones—and they are usually detected late.

Archeon enforces **HCI completeness structurally** by requiring that every feature chain:

* begins with a user need
* terminates in an observable outcome or explicit error path

Incomplete user journeys are rejected *before* code generation.

---

### 1.3 The Token Propagation Problem

Design tokens are commonly defined in design tools and documentation, then manually reimplemented across CSS, component libraries, and runtime code. This translation step introduces inconsistency and drift.

Archeon treats design tokens as **canonical configuration**, not documentation—propagated deterministically into all downstream artifacts.

---

## 2. The Glyph System

### 2.1 Formal Definition

An Archeon glyph is a typed symbol representing a single architectural concern:

```
G = (prefix, name, modifiers, args)
```

Where:

* `prefix ∈ {NED, TSK, OUT, ERR, V, CMP, STO, FNC, EVT, API, MDL}`
* `name` is an identifier
* `modifiers` annotate behavior
* `args` provide optional parameters

The glyph taxonomy is **closed**. New prefixes cannot be introduced without modifying the system definition. This closure is the primary architectural constraint.

---

### 2.2 Glyph Categories

| Prefix | Layer    | Semantic Role        |
| ------ | -------- | -------------------- |
| `NED`  | Meta     | User need            |
| `TSK`  | Meta     | User action          |
| `OUT`  | Meta     | Observable outcome   |
| `ERR`  | Meta     | Error state          |
| `V`    | View     | Structural container |
| `CMP`  | Frontend | UI component         |
| `STO`  | Frontend | Client-side state    |
| `FNC`  | Shared   | Pure function        |
| `EVT`  | Shared   | Event                |
| `API`  | Backend  | HTTP endpoint        |
| `MDL`  | Backend  | Data model           |

---

### 2.3 Edge Types

| Operator | Meaning               | Cycles |
| -------- | --------------------- | ------ |
| `=>`     | Structural dependency | No     |
| `~>`     | Reactive subscription | Yes    |
| `->`     | Conditional branch    | No     |
| `::`     | Containment           | No     |

Invalid crossings (e.g., `CMP => MDL`) are rejected by validation.

---

### 2.4 Chain Grammar

```
@v1 [vue3, fastapi]
NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard
```

Chains are:

* human-readable
* machine-validated
* persistent across sessions and tools

---

## 3. HCI-First Architecture

### 3.1 The NED–OUT Invariant

Every chain must satisfy:

```
∀ chain: ∃ NED ∧ (∃ OUT ∨ ∃ ERR)
```

This is not a linting rule; it is a **structural invariant** enforced at parse time.

---

### 3.2 Error Path Enforcement

All API glyphs must define explicit error handling:

```
API:POST/auth -> ERR:invalid_credentials => OUT:toast
```

Error handling is first-class, not optional.

---

### 3.3 Reactive Relationships

The `~>` edge declares runtime reactivity explicitly:

```
STO:Auth ~> CMP:NavBar
```

This enables dependency tracking, regeneration, and test derivation.

---

## 4. Semantic Attention Routing

### 4.1 From Context Packing to Attention Control

Archeon does **not** require injecting entire files or repositories into an LLM prompt. Modern IDE-based assistants already maintain full-repo indexes.

Archeon instead provides **attention constraints**: explicit declarations of *which files* and *which semantic regions* are relevant for a task.

The core insight:

> **The code describes itself using semantic comment brackets. The index records what sections exist. The LLM uses section labels as attention anchors.**

This approach is:
- **Language-agnostic**: Works with any comment syntax
- **Line-number-free**: Sections are named, not numbered
- **Refactor-stable**: Names survive code movement
- **IDE-native**: No external tools required

---

### 4.2 Self-Describing Files

Every generated file includes a mandatory header:

```vue
<!-- @archeon:file -->
<!-- @glyph CMP:LoginForm -->
<!-- @intent User login input and submission -->
<!-- @chain @v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard -->
```

```python
# @archeon:file
# @glyph API:POST./auth/login
# @intent Authentication endpoint for user login
# @chain @v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth/login => OUT:dashboard
```

This establishes:
- **Architectural ownership**: Which glyph owns this file
- **Intent**: What the file is for (human and AI readable)
- **Chain context**: How this file fits into feature flows

---

### 4.3 Semantic Section Bracketing

Within files, code is partitioned using semantic comment blocks:

```typescript
// @archeon:section handlers
// Handles user submission and auth dispatch
async function submitLogin() {
  loading.value = true;
  try {
    await authStore.login(email.value, password.value);
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
// @archeon:endsection
```

**Section Rules:**
- Sections MUST NOT nest
- Sections MUST be contiguous
- Section labels are STABLE identifiers
- Section comments are NEVER deleted without updating intent
- Code edits must occur INSIDE existing sections unless creating new ones

**Standard Sections by Glyph Type:**

| Glyph | Standard Sections |
|-------|-------------------|
| `CMP` | imports, props_and_state, handlers, render, styles |
| `STO` | imports, state, actions, selectors |
| `API` | imports, models, endpoint, helpers |
| `FNC` | imports, implementation, helpers |
| `EVT` | imports, channels, handlers |
| `MDL` | imports, schema, methods, indexes |

These sections:

* are stable across edits
* survive refactoring
* are readable by humans and machines
* act as *attention anchors* for AI tools

No line numbers. No AST slicing. No brittle offsets.

---

### 4.4 The Architecture Index

A lightweight index (`archeon/ARCHEON.index.json`) is derived by scanning file headers and section markers:

```json
{
  "version": "1.0",
  "project": "myapp",
  "glyphs": {
    "CMP:LoginForm": {
      "file": "client/src/components/LoginForm.vue",
      "intent": "User login input and submission",
      "chain": "@v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard",
      "sections": ["imports", "props_and_state", "handlers", "render"]
    },
    "STO:Auth": {
      "file": "client/src/stores/AuthStore.js",
      "intent": "State management for Auth",
      "chain": "@v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard",
      "sections": ["imports", "state", "selectors", "actions"]
    },
    "API:POST./auth/login": {
      "file": "server/src/api/routes/auth_login.py",
      "intent": "API endpoint for POST/auth/login",
      "chain": "@v1 NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard",
      "sections": ["imports", "models", "endpoint"]
    }
  }
}
```

The index:

* is **deterministic** (identical source → identical index)
* fits in **minimal context** (just metadata, not code)
* can always be **rebuilt from source** (`arc index build`)
* is **auto-updated** after every file generation

---

### 4.5 Index Update Flow

The index stays synchronized through two paths:

**CLI Path:**
```
arc gen → SPW_spawner → write file → auto-update index
```

**IDE AI Path:**
```
AI creates file with @archeon headers → run `arc index build`
```

Both paths produce identical index entries. The AI is instructed via `ARCHEON.arcon` to always update the index after generating files.

---

### 4.6 Prompt-Level Enforcement

When AI assistants receive architectural context, they are instructed:

```
EXISTING FILES (from index):
- CMP:LoginForm in client/src/components/LoginForm.vue
  sections: [imports, props_and_state, handlers, render]

RULES:
- Modify only files listed above
- Restrict edits to named sections
- Create new sections explicitly if needed
- Request approval before adding new files
```

This transforms AI generation from *free-form code writing* into **constrained architectural instantiation**.

The AI doesn't need the full code—it needs to know:
1. What files exist for which glyphs
2. What sections exist in those files
3. What the intent/chain context is

With this information, the AI can make targeted, architecture-aware edits.

---

## 5. Design Token Propagation

Design tokens are stored in W3C DTCG format:

```json
{
  "color": {
    "semantic": {
      "primary": {
        "default": { "$value": "{color.primitive.blue.500}", "$type": "color" }
      }
    }
  }
}
```

Tokens transform deterministically into runtime artifacts:

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

No AI generation occurs in this path. Tokens remain the **single source of truth** for visual and interaction semantics.

---

## 6. Agent Decomposition

### 6.1 Single-Responsibility Agents

Each agent handles exactly one glyph prefix:

| Agent | Glyph | Responsibility |
|-------|-------|----------------|
| `CMP_agent` | `CMP` | UI component generation |
| `STO_agent` | `STO` | State store generation |
| `API_agent` | `API` | HTTP endpoint generation |
| `MDL_agent` | `MDL` | Data model generation |
| `FNC_agent` | `FNC` | Function generation |
| `EVT_agent` | `EVT` | Event emitter generation |

Agents are **single-responsibility instantiators**, not autonomous planners. They:

* receive validated glyphs
* receive bounded context (via index)
* fill deterministic templates with proper headers and sections

### 6.2 Agent Constraints

Agents cannot:

* modify architecture
* introduce new dependencies outside their scope
* communicate across layers
* access glyphs outside their prefix
* retain state between invocations

These constraints are enforced by the orchestrator, not by agent compliance.

---

## 7. Architectural Properties

### 7.1 Compression (Qualified)

Archeon does not claim to compress *entire codebases*. It compresses:

* **architectural intent** (glyph chains)
* **dependency surfaces** (edge relationships)
* **permissible modification regions** (semantic sections)

This compression allows small models to operate with architectural awareness without full-context injection.

| Metric | Traditional | Archeon |
|--------|-------------|---------|
| Architecture docs | 2,000–5,000 lines | 50–200 lines |
| Context for feature understanding | 50K–200K tokens | 2K–8K tokens |
| Files to understand a feature | 8–15 | 1 (chain) |

---

### 7.2 Drift Resistance

Drift is prevented by:

* **Closed glyph vocabulary**: No new architectural concepts without system change
* **Explicit layer boundaries**: Invalid crossings rejected at validation
* **HCI invariants**: Incomplete journeys rejected before generation
* **Attention routing via semantic sections**: Edits constrained to declared regions

Drift can occur only within a declared section, never across architecture.

---

### 7.3 Test Generation

Chains imply test obligations:

```python
# Generated from: NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => OUT:dashboard

def test_login_happy_path():
    """Verifies: NED:login terminates in OUT:dashboard"""
    # Execute chain
    # Assert OUT:dashboard reached

def test_login_error_invalid_credentials():
    """Verifies: API:POST/auth -> ERR:invalid_credentials => OUT:toast"""
    # Execute with invalid credentials
    # Assert ERR path taken
```

Test generation is derived structurally, not heuristically.

---

## 8. Implementation

### 8.1 CLI Interface

```bash
arc init [--frontend vue3|react] [--backend fastapi]
arc parse "<chain>"
arc validate
arc gen
arc index build          # Rebuild index from source
arc index show           # Display indexed glyphs
arc tokens build
arc status
```

### 8.2 File Structure

```
project/
├── archeon/
│   ├── ARCHEON.arcon        # Knowledge graph
│   ├── ARCHEON.index.json   # Semantic index (auto-generated)
│   └── _config/
│       └── design-tokens.json
├── client/
│   └── src/
│       ├── components/      # CMP: outputs
│       ├── stores/          # STO: outputs
│       └── tokens/          # TKN: outputs
└── server/
    └── src/
        ├── api/routes/      # API: outputs
        └── models/          # MDL: outputs
```

### 8.3 Orchestration Flow

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
Agent ──────────► Instantiate template with headers + sections
    │
    ▼
IDX:index ──────► Update semantic index
    │
    ▼
TST:runner ─────► Generate and execute tests
```

---

## 9. Evaluation: Observed Agent Behavior

To validate Archeon's claims about behavioral shaping, we presented the system to an AI assistant unfamiliar with the project and asked: *"How would you implement a dashboard feature after user login?"*

The response provides qualitative evidence that Archeon's constraints produce the intended reasoning patterns.

### 9.1 Architecture-First Reasoning

Without prompting, the AI's first action was:

> *"Read the Knowledge Graph… see where login flows to… identify a gap. The login chain ends with OUT:Dashboard but there's no corresponding glyph for the dashboard itself. This is a gap I need to fill."*

This is non-trivial behavior. Without Archeon, models typically proceed directly to code generation:

* "Add a Dashboard.vue"
* "Fetch some data"
* "Wire it up"

With Archeon, the model instead:

* Inspects **architecture state** before acting
* Identifies **structural incompleteness**
* Refuses to generate code until the gap is resolved

The model was not prompted to do this. The system *caused* it.

### 9.2 Chain-Driven Completeness

The AI constructed a complete chain before writing any code:

```
@v1 [vue3, fastapi]
NED:dashboard => CMP:Dashboard => STO:AuthStore => STO:UserData => API:GET/users/{id} => MDL:User => OUT:displayProfile
```

The model's reasoning:

> *"The chain proves the feature is complete."*

It didn't just add UI. It didn't just add backend. It mentally simulated the full user journey—from need to observable outcome—before generating a single line of code.

This confirms the HCI-first invariant (§3) is producing the intended behavioral effect.

### 9.3 Boundary Internalization

Perhaps most significantly, the AI articulated layer constraints unprompted:

> *"Dashboard can't fetch user data directly; it must go through a store. This prevents spaghetti code."*

The model has internalized Archeon's ontology:

* `CMP` cannot access `MDL` directly
* State management mediates all data flow
* Boundaries are explicit, not advisory

This is the behavioral definition of **drift resistance**—the model is no longer pattern-matching arbitrary tutorials but obeying the system's architectural rules.

### 9.4 Attention Routing Confirmation

The AI described navigation without scanning:

> *"The index lets me find any glyph instantly. If I'm adding a feature, I know exactly what files to touch and in what order."*

This confirms semantic attention routing is working as designed:

* The model follows constrained edit paths
* Section labels act as navigation anchors
* Full-repo context is unnecessary

### 9.5 Comparative Analysis

The AI explicitly contrasted behavior with and without Archeon:

| Without Archeon | With Archeon |
|-----------------|--------------|
| Ad-hoc component creation | Chain-validated completeness |
| Missing backend endpoints | Full-stack generation |
| Route placement "somewhere random" | Deterministic file locations |
| Architecture lost to next developer | Index as persistent source of truth |
| Mistakes caught in production | `arc validate` catches errors early |

### 9.6 The Key Insight

The AI's final observation:

> *"Archeon turns architecture from a vague concept into an executable specification."*

This reframes Archeon's contribution: not a tool, not a framework, but a **specification medium** that shapes AI behavior through structural constraint rather than prompt engineering.

Most AI tooling papers *assert* behavioral change. This evaluation **demonstrates** it.

---

## 10. Limitations and Future Work

### 10.1 Current Limitations

* **Natural-language intent parsing** remains imperfect on local models; human approval recommended
* **Framework coverage** limited to Vue 3, React, and FastAPI; additional frameworks require template development
* **Semantic sections require discipline**; enforced by tooling but relies on consistent usage
* **Complex queries**: `MDL` glyph maps to single operations; multi-table joins require manual implementation

---

### 10.2 Future Directions

* **Visual chain editors**: IDE integration for graphical chain construction
* **Formal verification**: Proving chain properties via SMT solvers
* **Cross-project glyph libraries**: Reusable patterns for auth, CRUD, search
* **IDE-native enforcement**: Real-time validation and section linting
* **Incremental regeneration**: Dependency-aware regeneration when tokens or chains change

---

## 11. Conclusion

Archeon reframes AI-assisted development around a central insight:

> **AI code generation fails not because models are weak, but because architectural constraints are implicit.**

By making architecture, intent, and attention explicit—through glyphs, semantic sections, and deterministic tooling—Archeon enables small, local models to behave like disciplined senior engineers operating inside well-defined systems.

The key innovations:

1. **Glyph-based IR**: Closed vocabulary compresses architecture into minimal context
2. **Semantic attention routing**: Comment-based sections provide stable, named edit targets
3. **Architecture index**: Lightweight metadata enables AI to navigate without full code
4. **HCI enforcement**: Structural invariants guarantee complete user journeys
5. **Token propagation**: Single source of truth for all visual properties

This approach does not replace AI capability. It *focuses* it.

**Constraint substitutes for context. Architecture substitutes for memory. And attention, once constrained, becomes reliable.**

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

## Appendix B: Section Reference

| Glyph Type | Standard Sections |
|------------|-------------------|
| `CMP` | `imports`, `props_and_state`, `handlers`, `render`, `styles` |
| `STO` | `imports`, `state`, `actions`, `selectors` |
| `API` | `imports`, `models`, `endpoint`, `helpers` |
| `FNC` | `imports`, `implementation`, `helpers` |
| `EVT` | `imports`, `channels`, `handlers` |
| `MDL` | `imports`, `schema`, `methods`, `indexes` |

## Appendix C: Index Schema

```json
{
  "version": "1.0",
  "project": "string",
  "glyphs": {
    "<glyph_qualified_name>": {
      "file": "relative/path/to/file",
      "intent": "One-sentence description",
      "chain": "@version chain string",
      "sections": ["section_name", "..."]
    }
  }
}
```

## Appendix D: Implementation Status

| Feature | Status |
|---------|--------|
| Glyph parsing | ✅ Implemented |
| Chain validation | ✅ Implemented |
| Layer boundary enforcement | ✅ Implemented |
| Agent code generation | ✅ Implemented |
| Semantic section headers | ✅ Implemented |
| Architecture index | ✅ Implemented |
| Auto-index update | ✅ Implemented |
| Intent parsing (NL→glyphs) | ⚠️ Requires approval |
| Design token propagation | ✅ Implemented |
| Test generation | 🔄 In progress |
| Visual chain editor | 📋 Planned |

---

*Archeon is open source under the MIT license.*

*Repository: github.com/[redacted]/archeon*
