# Archeon Implementation Roadmap

> Phased build plan for AI-assisted development. Each phase is testable before proceeding.

---

## 🎯 CRITICAL: Small Model Context Optimization

> **Target:** 30B parameter models (Qwen3) on RTX 5090 with ~60K token context window.
> **Goal:** Never overload context. Keep agent prompts under 10K tokens each.

### Core Principles
1. **Glyph Projection** - Only load 1-hop neighbors, not entire graph
2. **Micro-Agent Pattern** - One glyph per invocation, never batch
3. **Template Compression** - Templates (~20 lines) not full code (~100+ lines)
4. **Context Budgeting** - Track and enforce token limits per operation

### Implemented Components
- [x] `CTX_context.py` - Context budget manager with tier support
- [x] `MIC_micro.py` - Micro-agent executor for single-glyph operations
- [x] `GlyphProjection` - Minimal context projection (target + 1-hop deps)
- [x] `ContextBudget` - Token tracking with allocation percentages

### Token Budget Allocation (60K total)
| Allocation | % | Tokens | Purpose |
|------------|---|--------|---------|
| Glyph notation | 10% | 6,000 | Chain definition |
| Template | 20% | 12,000 | Framework template |
| Dependencies | 30% | 18,000 | 1-hop neighbors only |
| Chain context | 20% | 12,000 | Immediate chain |
| Output reserved | 20% | 12,000 | Generated code |

### Anti-Patterns to Avoid
- ❌ Loading entire `.arcon` file into context
- ❌ Batching multiple glyphs in one prompt
- ❌ Including 2+ hop dependencies
- ❌ Full file reads instead of projections

---

## Phase 1: Project Foundation ✅

### 1.1 Project Structure
- [x] Create directory scaffold
- [x] Create `pyproject.toml` with dependencies: `typer`, `pytest`, `pydantic`
- [x] Create empty `ARCHEON.arcon` with header comment

### 1.2 Glyph Legend (`config/legend.py`)
- [x] Define `GLYPH_LEGEND` dict with all 16 prefixes
- [x] Each entry: `name`, `description`, `agent`, `color`, `layer`
- [x] Define `EDGE_TYPES` dict (6 types)
- [x] Define `BOUNDARY_RULES` list for ownership enforcement

**Test:** ✅ 16 tests passing (legend integrity)

---

## Phase 2: Chain Parser (`orchestrator/PRS_parser.py`) ✅

### 2.1 Tokenizer
- [x] Regex patterns for version, framework, glyph, modifiers, operators
- [x] Handle containment syntax: `V:Page @ CMP:A, CMP:B, CMP:C`

### 2.2 Glyph Parser
- [x] Parse qualified names: `FNC:auth.validateCreds`
- [x] Parse modifiers: `CMP:Form[stateful]`
- [x] Parse API signatures: `API:POST/auth`
- [x] Parse OUT args: `OUT:toast('message')`

### 2.3 AST Builder
- [x] Return structured `ChainAST` dataclass
- [x] Handle comment lines (`#`)

**Test:** ✅ 18 tests passing (parser coverage)

---

## Phase 3: Knowledge Graph (`orchestrator/GRF_graph.py`) ✅

### 3.1 Data Model
- [x] `StoredChain` dataclass with AST, section, line number
- [x] `KnowledgeGraph` class: stores chains, provides queries

### 3.2 File Operations
- [x] `load(path)` — Parse `ARCHEON.arcon` line by line
- [x] `save(path)` — Write graph back to file with sections

### 3.3 Query Methods
- [x] `find_chain(glyph)` — All chains containing a glyph
- [x] `find_dependencies(glyph)` — Upstream nodes
- [x] `find_dependents(glyph)` — Downstream nodes
- [x] `get_all_glyphs()` — Unique glyphs across all chains

### 3.4 Mutation Methods
- [x] `add_chain(chain_str)` — Parse and add with version conflict detection
- [x] `deprecate_chain(version, root_glyph)` — Mark deprecated

**Test:** ✅ Graph tests passing

---

## Phase 4: Validation Engine (`orchestrator/VAL_validator.py`) ✅

### 4.1 Chain Validation
- [x] `validate_structure(chain)` — All nodes valid, edges connect valid nodes
- [x] `validate_output(chain)` — Warn if no `OUT:` terminal
- [x] `validate_error_paths(chain)` — Warn if `API:` has no `ERR:` branch

### 4.2 Cycle Detection
- [x] `validate_cycles(chain)` — DFS for cycles
- [x] Block cycles through `=>` and `->` edges
- [x] Allow cycles through `~>` and `!>` edges

### 4.3 Boundary Enforcement
- [x] `validate_boundary(edge)` — Check ownership rules
- [x] CMP↛MDL, STO↛MDL, V↛data flow blocked

### 4.4 Validation Result
- [x] Return `ValidationResult` with errors and warnings

**Test:** ✅ 19 tests passing (validation coverage)

---

## Phase 5: Base Agent System ✅

### 5.1 Abstract Base (`agents/base_agent.py`)
- [x] `BaseAgent` ABC with `generate`, `get_template`, `generate_test`, `resolve_path`
- [x] Template loader utility: read from `templates/{prefix}/{framework}.*`
- [x] Placeholder substitution: `{COMPONENT_NAME}` → actual name

### 5.2 Template Files (Initial Set)
- [x] `templates/CMP/react.tsx` — React functional component
- [x] `templates/CMP/vue.vue` — Vue 3 SFC
- [x] `templates/STO/zustand.js` — Zustand store
- [x] `templates/API/fastapi.py` — FastAPI router
- [x] `templates/MDL/mongo.py` — MongoDB model (motor/pymongo)
- [x] `templates/FNC/python.py` — Python function stub
- [x] `templates/EVT/pubsub.py` — Python event emitter

**Test:** ✅ Templates loaded and used in generation

---

## Phase 6: Agent Implementations ✅

### 6.1 CMP Agent (`agents/CMP_agent.py`)
- [x] Resolve path: `components/{name}.tsx` (React), `components/{name}.vue` (Vue)
- [x] Handle `[stateful]` modifier — add useState hooks
- [x] Handle `[headless]` modifier — add `@headless` annotation
- [x] Generate companion test: render + snapshot

### 6.2 STO Agent (`agents/STO_agent.py`)
- [x] Resolve path: `stores/{name}Store.js`
- [x] Parse actions from chain context
- [x] Generate state interface + actions
- [x] Generate test: state mutations

### 6.3 API Agent (`agents/API_agent.py`)
- [x] Resolve path: `api/routes/{route}.py`
- [x] Parse method + route from `API:POST/auth`
- [x] Generate request/response Pydantic models
- [x] Generate error handlers for connected `ERR:` glyphs
- [x] Generate test: request/response contract

### 6.4 MDL Agent (`agents/MDL_agent.py`)
- [x] Resolve path: `models/{entity}.py`
- [x] Parse entity + operation: `MDL:user.findOne` → User model, findOne method
- [x] Generate CRUD repository methods
- [x] Generate test: query shape validation

### 6.5 FNC Agent (`agents/FNC_agent.py`)
- [ ] Resolve path by namespace:
  - `FNC:auth.*` → `lib/auth.py`
  - `FNC:ui.*` → `lib/ui.js`
  - `FNC:validation.*` → `lib/validation.py`
- [ ] Generate function stub with docstring
- [ ] Generate test: input/output assertion

### 6.6 EVT Agent (`agents/EVT_agent.py`)
- [ ] Resolve path: `events/{name}.py`
- [ ] Generate event class + emit/subscribe methods
- [ ] Generate test: emission verification

**Test:** Generate code from sample chains, verify files created with correct content.

---

## Phase 7: Agent Spawner (`orchestrator/SPW_spawner.py`)

- [x] Resolve path by namespace: `FNC:auth.*` → `lib/auth.py`
- [x] Generate function stub with docstring
- [x] Generate test: input/output assertion

### 6.6 EVT Agent (`agents/EVT_agent.py`)
- [x] Resolve path: `events/{name}.py`
- [x] Generate event class + emit/subscribe methods
- [x] Generate test: emission verification

**Test:** ✅ End-to-end generation verified

---

## Phase 7: Agent Spawner (`orchestrator/SPW_spawner.py`) ✅

### 7.1 Agent Registry
- [x] Map prefix → agent class (`AGENT_REGISTRY`)
- [x] Skip meta glyphs (`NED`, `TSK`, `OUT`, `ERR`, `V`) — no code gen
- [x] Auto-select framework per glyph type (frontend/backend/db)

### 7.2 Spawn Logic
- [x] `spawn(glyph, chain, framework)`:
  1. Look up agent by prefix
  2. Check if file already exists (skip or force)
  3. Call `agent.generate()`
  4. Call `agent.generate_test()`
  5. Return `SpawnResult`

### 7.3 Batch Processing
- [x] `spawn_chain(chain)` — Process all glyphs in a chain
- [x] `spawn_all(graph)` — Process all unresolved glyphs in graph
- [x] Track resolution status in graph

**Test:** ✅ Spawned from sample chain, all files created correctly

---

## Phase 8: Test Generation (`orchestrator/TST_runner.py`) ✅

### 8.1 Test Generator
- [x] `generate_happy_path_test(chain)`:
  - Walk chain from `NED:` to `OUT:`
  - Generate test steps for each glyph
  - Assert on final `OUT:` feedback
- [x] `generate_error_path_test(chain, error_branch)`:
  - Find `->` edge to `ERR:` glyph
  - Generate test that triggers error condition
  - Assert error `OUT:` response

### 8.2 Test File Structure
- [x] Output to `tests/generated/test_{glyph_name}.py` (per-glyph tests)
- [x] Include `@archeon` marker comments for traceability
- [x] Pytest format with fixtures for chain-level tests

### 8.3 Test Runner
- [x] `run_tests()` — Execute all generated tests via pytest
- [x] `run_tests(chain)` — Execute tests for specific chain
- [x] Return results: passed, failed, errors

**Test:** ✅ Test generation and runner implemented

---

## Phase 9: CLI Interface (`main.py`) ✅

### 9.1 Core Commands
- [x] `archeon init` — Scaffold new project + .archeonrc
- [x] `archeon parse "<chain>"` — Parse and add chain
- [x] `archeon gen` — Generate code with framework options
- [x] `archeon validate` — Validate graph
- [x] `archeon test` — Run tests with --generate, --errors-only options

### 9.2 Graph Commands
- [x] `archeon status` — Show graph state
- [x] `archeon graph` — Export visualization (dot, json, png, svg, mermaid)
- [x] `archeon audit` — Check for drift

### 9.3 Version Commands
- [x] `archeon versions <glyph>` — Show version history
- [x] `archeon diff @v1 @v2 <glyph>` — Diff two versions
- [x] `archeon deprecate @v1 <glyph>` — Mark deprecated

### 9.4 Utility Commands
- [x] `archeon legend` — Show glyph legend table
- [x] `archeon intent` — Natural language to chain proposals
- [x] `archeon import` — Import from markdown files

**Test:** ✅ All CLI commands verified working

---

## Phase 10: File Tracer (`utils/tracer.py`) ✅

### 10.1 Mapping
- [x] `glyph_to_path(glyph, framework)` — Return expected file path
- [x] `path_to_glyph(path)` — Parse `@archeon` comment, return glyph

### 10.2 Drift Detection
- [x] `find_drift()`:
  - Scan generated files for `@archeon` markers
  - Compare to graph
  - Return: orphan files, missing files, version mismatches

### 10.3 Sync
- [x] `sync_markers()` — Update `@archeon` comments in files to match graph

**Test:** ✅ Drift detection verified via `archeon audit`

---

## Phase 11: Intent Parsing (`orchestrator/INT_intent.py`) ✅

### 11.1 Natural Language Parser
- [x] `parse_intent(text)` → proposed chain string
- [x] Basic heuristics:
  - "user wants to login" → `NED:login`
  - "submit form" → `TSK:submit`
  - "show error" → `OUT:error`
- [x] Return **proposal only** — never auto-add

### 11.2 Error Path Suggester
- [x] `suggest_errors(chain)`:
  - Context-aware error suggestions (auth, validation, payment, etc.)
  - Suggest common errors: `auth.invalidCreds`, `validation.malformed`, `system.rateLimit`
- [x] Return suggestions, don't auto-add

### 11.3 Document Import
- [x] `import_markdown(path)`:
  - Scan for code blocks with chain syntax
  - Extract user stories and requirements
  - Propose chains with confidence levels
- [ ] `import_url(url)`:
  - Stub for Linear/JIRA/GitHub integration (not yet implemented)

### 11.4 Approval Workflow
- [ ] CLI: `archeon intent "<text>"`
  - Show proposed chain
  - Prompt: `[a]pprove [e]dit [r]eject [s]uggest errors`
  - Only add to graph on explicit approval

**Test:** Parse sample intents, verify reasonable chain proposals.

---

## Phase 12: Headless Execution Mode ✅

### 12.1 Opt-In System
- [x] Only `[headless]` annotated components can execute (strict mode)
- [x] `validate_headless()` validator — block non-annotated execution
- [x] `HeadlessValidator.can_execute()` — check headless capability

### 12.2 Sandbox Mode (Default)
- [x] Trace execution without side effects
- [x] Mock all `API:` calls via `MockRegistry`
- [x] Return execution trace with timing, status, I/O:
  ```json
  {
    "chain_id": "...",
    "mode": "sandbox",
    "status": "completed",
    "steps": [{"glyph": "...", "duration_ms": ..., "mocked": true}],
    "final_output": {...}
  }
  ```

### 12.3 Live Mode
- [x] Require explicit `mode=live` flag
- [x] Strict headless validation for live mode
- [x] Placeholder for real code execution

### 12.4 HTTP Interface
- [x] `/api/cmp/{component}` endpoint — Execute component
- [x] `/api/chain/{id}` endpoint — Execute by chain ID
- [x] `/api/execute` endpoint — Execute raw chain string
- [x] Query params: `mode=sandbox|live`
- [x] `/api/cmp/{component}/metrics` — Execution metrics
- [x] `/api/status`, `/api/chains`, `/health` endpoints
- [x] WSGI-compatible `create_app()` for production servers

### 12.5 CLI Commands
- [x] `archeon run <glyph>` — Execute chains containing glyph
- [x] `archeon run --chain "<chain>"` — Execute raw chain
- [x] `archeon run --all` — Execute all chains
- [x] `archeon run --mode live` — Live execution mode
- [x] `archeon serve [--port] [--host]` — Start HTTP server

**Test:** ✅ Execute headless component in sandbox, verify trace output.

---

## Phase 13: Graph Visualization ✅

### 13.1 DOT Export
- [x] `export_dot(graph)` — Generate Graphviz DOT format
- [x] Node shapes by glyph type (from legend colors)
- [x] Edge styles by operator type

### 13.2 JSON Export
- [x] `export_json(graph)` — Full graph as JSON
- [x] For web visualization consumption

### 13.3 PNG/SVG Export
- [x] Shell out to `dot` command
- [x] `archeon graph --format png|svg --output graph.png`

### 13.4 Mermaid Export
- [x] `export_mermaid(graph)` — Generate Mermaid diagram

**Test:** ✅ All export formats verified working

---

## Phase 14: Polish & Edge Cases ✅ (mostly)

### 14.1 Error Handling
- [x] Graceful handling of malformed chains
- [x] Clear error messages with line numbers
- [ ] Suggestions for common mistakes

### 14.2 Performance
- [ ] Lazy loading of graph for large `.arcon` files
- [ ] Incremental validation (only changed chains)

### 14.3 Configuration
- [x] `.archeonrc` file for project defaults:
  ```yaml
  frontend: react
  backend: fastapi
  db: mongo
  output_dir: ./src
  ```

### 14.4 Documentation
- [x] `archeon --help` comprehensive help
- [x] `archeon <command> --help` for each command
- [ ] README with quick start

---

## Implementation Order (Quick Start)

**Week 1-2: Foundation**
1. Phase 1 — Project structure + legend
2. Phase 2 — Chain parser
3. Phase 3 — Knowledge graph

**Week 3-4: Validation**
4. Phase 4 — Validation engine
5. Phase 9.1 — Basic CLI (`init`, `parse`, `validate`)

**Week 5-6: Code Generation**
6. Phase 5 — Base agent system
7. Phase 6.1 — CMP agent (React only)
8. Phase 7 — Agent spawner
9. Phase 9.1 — CLI `gen` command

**Week 7-8: Full Agent Suite**
10. Phase 6.2-6.6 — Remaining agents
11. Phase 8 — Test generation
12. Phase 9.1 — CLI `test` command

**Week 9-10: Utilities**
13. Phase 10 — File tracer
14. Phase 9.2-9.4 — Remaining CLI commands
15. Phase 13 — Graph visualization

**Week 11-12: Advanced Features**
16. Phase 11 — Intent parsing
17. Phase 12 — Headless mode

**Week 13+: Polish**
18. Phase 14 — Edge cases, config, docs

---

## Testing Strategy

| Phase | Test Focus |
|-------|-----------|
| 1-2 | Unit: parser tokenization, AST structure |
| 3 | Unit: graph load/save, queries |
| 4 | Unit: each validation rule with positive/negative cases |
| 5-7 | Integration: chain → generated files |
| 8 | Integration: chain → test files → pytest execution |
| 9 | E2E: CLI commands with real `.arcon` files |
| 10-14 | E2E: full workflows |

---

## Dependencies

```toml
[project]
dependencies = [
    "typer>=0.9.0",      # CLI framework
    "pydantic>=2.0",     # Data validation
    "pytest>=7.0",       # Testing
]

[project.optional-dependencies]
dev = [
    "pytest-cov",        # Coverage
    "ruff",              # Linting
]
```

---

## Notes

- **Start with one framework** (React + FastAPI + MongoDB), add variants after core works
- **Templates are simple string substitution** — no Jinja complexity
- **Validation is strict** — better to reject than generate bad code
- **Intent parsing is proposal-only** — humans approve all chains
- **Headless is opt-in** — security by default
