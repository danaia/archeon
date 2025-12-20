# Archeon Implementation Roadmap

> Phased build plan for AI-assisted development. Each phase is testable before proceeding.

---

## Phase 1: Project Foundation

### 1.1 Project Structure
- [ ] Create directory scaffold:
  ```
  archeon/
  ├── main.py
  ├── orchestrator/
  │   └── __init__.py
  ├── agents/
  │   └── __init__.py
  ├── templates/
  │   ├── CMP/
  │   ├── STO/
  │   ├── API/
  │   ├── MDL/
  │   ├── FNC/
  │   └── EVT/
  ├── tests/
  │   └── __init__.py
  ├── utils/
  │   └── __init__.py
  ├── config/
  │   └── __init__.py
  └── ARCHEON.arcon
  ```
- [ ] Create `pyproject.toml` with dependencies: `typer`, `pytest`, `pydantic`
- [ ] Create empty `ARCHEON.arcon` with header comment

### 1.2 Glyph Legend (`config/legend.py`)
- [ ] Define `GLYPH_LEGEND` dict with all prefixes:
  - Meta glyphs: `NED`, `TSK`, `OUT`, `ERR`
  - Frontend: `V`, `CMP`, `STO`
  - Shared: `FNC`, `EVT`
  - Backend: `API`, `MDL`
  - Internal: `ORC`, `PRS`, `VAL`, `SPW`, `TST`, `GRF`
- [ ] Each entry: `name`, `description`, `agent`, `color`, `layer`
- [ ] Define `EDGE_TYPES` dict:
  - `=>` structural (no cycles)
  - `~>` reactive (cycles OK)
  - `!>` side-effect (cycles OK)
  - `->` control/branch (no cycles)
  - `::` internal orchestrator
  - `@` containment
- [ ] Define `BOUNDARY_RULES` list for ownership enforcement

**Test:** Import `legend.py`, assert all 16 glyphs defined, all 6 edge types defined.

---

## Phase 2: Chain Parser (`orchestrator/PRS_parser.py`)

### 2.1 Tokenizer
- [ ] Regex patterns for:
  - Version tag: `@v\d+` or `@latest`
  - Framework tag: `\[[\w]+\]`
  - Glyph: `[A-Z]+:[^\s=~!->@]+`
  - Modifiers: `\[stateful\]`, `\[headless\]`, `\[presentational\]`
  - Operators: `=>`, `~>`, `!>`, `->`, `::`, `@`
- [ ] Handle containment syntax: `V:Page @ CMP:A, CMP:B, CMP:C`

### 2.2 Glyph Parser
- [ ] Parse qualified names: `FNC:auth.validateCreds` → `{prefix: 'FNC', namespace: 'auth', action: 'validateCreds'}`
- [ ] Parse modifiers: `CMP:Form[stateful]` → `{prefix: 'CMP', name: 'Form', modifiers: ['stateful']}`
- [ ] Parse API signatures: `API:POST/auth` → `{prefix: 'API', method: 'POST', route: '/auth'}`
- [ ] Parse OUT args: `OUT:toast('message')` → `{prefix: 'OUT', action: 'toast', args: ['message']}`

### 2.3 AST Builder
- [ ] Return structured AST:
  ```python
  {
    'version': 'v1',
    'framework': 'react',
    'nodes': [
      {'prefix': 'NED', 'name': 'login', ...},
      {'prefix': 'CMP', 'name': 'LoginForm', 'modifiers': ['stateful'], ...}
    ],
    'edges': [
      {'from': 0, 'to': 1, 'operator': '=>'},
      ...
    ]
  }
  ```
- [ ] Handle multi-line chains (line continuation)
- [ ] Handle comment lines (`#`)

**Test:** Parse sample chains from TECHNICAL_DESIGN.md §3.8, verify AST structure.

---

## Phase 3: Knowledge Graph (`orchestrator/GRF_graph.py`)

### 3.1 Data Model
- [ ] `Node` dataclass: `id`, `prefix`, `name`, `namespace`, `modifiers`, `metadata`
- [ ] `Edge` dataclass: `source_id`, `target_id`, `operator`
- [ ] `Chain` dataclass: `version`, `framework`, `nodes`, `edges`, `deprecated`
- [ ] `Graph` class: stores all chains, nodes index, edges index

### 3.2 File Operations
- [ ] `load(path)` — Parse `ARCHEON.arcon` line by line
- [ ] `save(path)` — Write graph back to file with sections
- [ ] Preserve comments and section headers

### 3.3 Query Methods
- [ ] `find_chain(glyph)` — All chains containing a glyph
- [ ] `find_dependencies(glyph)` — Upstream nodes
- [ ] `find_dependents(glyph)` — Downstream nodes
- [ ] `get_all_glyphs()` — Unique glyphs across all chains
- [ ] `get_chains_by_version(glyph)` — Version history for a root glyph

### 3.4 Mutation Methods
- [ ] `add_chain(chain_str)` — Parse and add, auto-increment version if exists
- [ ] `remove_chain(version, root_glyph)` — Remove specific version
- [ ] `deprecate_chain(version, root_glyph)` — Mark deprecated

**Test:** Load sample `.arcon`, query for `CMP:LoginForm`, verify dependencies.

---

## Phase 4: Validation Engine (`orchestrator/VAL_validator.py`)

### 4.1 Chain Validation
- [ ] `validate_structure(chain)` — All nodes valid, all edges connect valid nodes
- [ ] `validate_output(chain)` — Chain ends with `OUT:` (warn if missing)
- [ ] `validate_error_paths(chain)` — `API:` glyphs should have `ERR:` branches (warn)

### 4.2 Cycle Detection
- [ ] `validate_cycles(chain)` — DFS for cycles
  - Block cycles through `=>` and `->` edges → `ERR:chain.structuralCycle`
  - Allow cycles through `~>` edges (reactive OK)

### 4.3 Boundary Enforcement
- [ ] `validate_boundary(edge)` — Check ownership rules:
  | From | To | Allowed? | Error Code |
  |------|-----|----------|------------|
  | `V:` | any via `=>`,`~>`,`->`,`!>` | ❌ | `ERR:boundary.viewDataFlow` |
  | `CMP` | `MDL` | ❌ | `ERR:boundary.cmpToMdl` |
  | `STO` | `MDL` | ❌ | `ERR:boundary.stoToMdl` |
  | `EVT` | `API` | ❌ | `ERR:boundary.evtToApi` |
  | `MDL` | `CMP` | ❌ | `ERR:boundary.mdlToCmp` |
  | `FNC:ui.*` | `MDL` | ❌ | `ERR:boundary.uiFncToMdl` |

### 4.4 Duplicate Detection
- [ ] `validate_duplicates(graph)` — Flag duplicate qualified glyphs
  - Two `FNC:auth.validate` in graph → `ERR:glyph.duplicate`

### 4.5 Version Validation
- [ ] `validate_versions(graph)` — No conflicting versions
- [ ] Resolve `@latest` to highest numeric version

### 4.6 Validation Result
- [ ] Return `ValidationResult`:
  ```python
  {
    'valid': bool,
    'errors': [{'code': 'ERR:...', 'message': '...', 'location': ...}],
    'warnings': [{'code': 'WARN:...', 'message': '...'}]
  }
  ```

**Test:** Feed invalid chains (cycle, boundary violation), verify correct error codes.

---

## Phase 5: Base Agent System

### 5.1 Abstract Base (`agents/base_agent.py`)
- [ ] `BaseAgent` ABC:
  ```python
  class BaseAgent(ABC):
      prefix: str
      
      @abstractmethod
      def generate(self, glyph: dict, chain: dict, framework: str) -> str:
          """Generate code, return file path written."""
      
      @abstractmethod
      def get_template(self, framework: str) -> str:
          """Return template string for framework."""
      
      @abstractmethod
      def generate_test(self, glyph: dict, framework: str) -> str:
          """Generate test file, return path."""
      
      @abstractmethod
      def resolve_path(self, glyph: dict, framework: str) -> str:
          """Return output file path for glyph."""
  ```
- [ ] Template loader utility: read from `templates/{prefix}/{framework}.*`
- [ ] Placeholder substitution: `{COMPONENT_NAME}` → actual name

### 5.2 Template Files (Initial Set)
- [ ] `templates/CMP/react.tsx` — React functional component
- [ ] `templates/CMP/vue.vue` — Vue 3 SFC
- [ ] `templates/STO/zustand.ts` — Zustand store
- [ ] `templates/API/fastapi.py` — FastAPI router
- [ ] `templates/MDL/mongo.py` — MongoDB model (motor/pymongo)
- [ ] `templates/FNC/python.py` — Python function stub
- [ ] `templates/FNC/typescript.ts` — TypeScript function stub
- [ ] `templates/EVT/pubsub.py` — Python event emitter

**Test:** Load each template, verify placeholder markers present.

---

## Phase 6: Agent Implementations

### 6.1 CMP Agent (`agents/CMP_agent.py`)
- [ ] Resolve path: `components/{name}.tsx` (React), `components/{name}.vue` (Vue)
- [ ] Handle `[stateful]` modifier — add useState hooks
- [ ] Handle `[headless]` modifier — add `@headless` annotation
- [ ] Handle `[presentational]` modifier — pure render, no hooks
- [ ] Generate companion test: render + snapshot

### 6.2 STO Agent (`agents/STO_agent.py`)
- [ ] Resolve path: `stores/{name}Store.ts`
- [ ] Parse `actions: action1, action2` syntax from chain
- [ ] Generate state interface + actions
- [ ] Generate test: state mutations

### 6.3 API Agent (`agents/API_agent.py`)
- [ ] Resolve path: `api/routes/{route}.py`
- [ ] Parse method + route from `API:POST/auth`
- [ ] Generate request/response Pydantic models
- [ ] Generate error handlers for connected `ERR:` glyphs
- [ ] Generate test: request/response contract

### 6.4 MDL Agent (`agents/MDL_agent.py`)
- [ ] Resolve path: `models/{entity}.py`
- [ ] Parse entity + operation: `MDL:user.findOne` → User model, findOne method
- [ ] Generate schema from `schema: {...}` if present
- [ ] Generate test: query shape validation

### 6.5 FNC Agent (`agents/FNC_agent.py`)
- [ ] Resolve path by namespace:
  - `FNC:auth.*` → `lib/auth.py`
  - `FNC:ui.*` → `lib/ui.ts`
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

### 7.1 Agent Registry
- [ ] Map prefix → agent class:
  ```python
  AGENT_REGISTRY = {
      'CMP': CMPAgent,
      'STO': STOAgent,
      'API': APIAgent,
      'MDL': MDLAgent,
      'FNC': FNCAgent,
      'EVT': EVTAgent,
  }
  ```
- [ ] Skip meta glyphs (`NED`, `TSK`, `OUT`, `ERR`, `V`) — no code gen

### 7.2 Spawn Logic
- [ ] `spawn(glyph, chain, framework)`:
  1. Look up agent by prefix
  2. Check if file already exists (skip or update?)
  3. Call `agent.generate()`
  4. Call `agent.generate_test()`
  5. Return result: `{glyph, file_path, test_path, status}`

### 7.3 Batch Processing
- [ ] `spawn_chain(chain)` — Process all glyphs in a chain
- [ ] `spawn_all(graph)` — Process all unresolved glyphs in graph
- [ ] Track which glyphs have been generated (avoid duplicates)

**Test:** Spawn from sample chain, verify all expected files created.

---

## Phase 8: Test Generation (`orchestrator/TST_runner.py`)

### 8.1 Test Generator
- [ ] `generate_happy_path_test(chain)`:
  - Walk chain from `NED:` to `OUT:`
  - Generate test steps for each glyph
  - Assert on final `OUT:` feedback
- [ ] `generate_error_path_test(chain, error_branch)`:
  - Find `->` edge to `ERR:` glyph
  - Generate test that triggers error condition
  - Assert error `OUT:` response

### 8.2 Test File Structure
- [ ] Output to `tests/generated/test_{chain_name}.py`
- [ ] Pytest format with fixtures
- [ ] Include `@archeon` marker comments for traceability

### 8.3 Test Runner
- [ ] `run_tests()` — Execute all generated tests via pytest
- [ ] `run_tests(chain)` — Execute tests for specific chain
- [ ] Return results: passed, failed, errors

**Test:** Generate tests from sample chains, run them (expect stubs to fail initially).

---

## Phase 9: CLI Interface (`main.py`)

### 9.1 Core Commands
- [ ] `archeon init` — Scaffold new project
  - Create directory structure
  - Create empty `ARCHEON.arcon`
  - Create `config/legend.py` with defaults
- [ ] `archeon parse "<chain>"` — Parse and add chain
  - Parse chain string
  - Validate
  - Add to graph if valid
  - Print errors/warnings
- [ ] `archeon gen` — Generate code
  - Options: `--frontend react|vue`, `--backend fastapi|express`, `--db mongo|postgres`
  - Spawn agents for all unresolved glyphs
  - Report generated files
- [ ] `archeon validate` — Validate graph
  - Options: `--boundaries`, `--cycles`, `--all`
  - Print validation results
- [ ] `archeon test` — Run tests
  - Options: `--errors-only`, `--chain <glyph>`
  - Execute pytest, report results

### 9.2 Graph Commands
- [ ] `archeon status` — Show graph state
  - Total chains, glyphs, unresolved count
  - Validation summary
- [ ] `archeon graph` — Export visualization
  - Options: `--format dot|png|json`
  - Generate DOT file for Graphviz
- [ ] `archeon audit` — Check for drift
  - Compare generated files to graph
  - Report files not in graph, glyphs without files

### 9.3 Version Commands
- [ ] `archeon versions <glyph>` — Show version history
- [ ] `archeon diff @v1 @v2 <glyph>` — Diff two versions
- [ ] `archeon deprecate @v1 <glyph>` — Mark deprecated

### 9.4 Headless Commands
- [ ] `archeon headless enable <glyph>` — Add `[headless]` modifier
- [ ] `archeon headless disable <glyph>` — Remove modifier
- [ ] `archeon headless list` — Show all headless-enabled components

**Test:** Run each CLI command, verify expected output/behavior.

---

## Phase 10: File Tracer (`utils/tracer.py`)

### 10.1 Mapping
- [ ] `glyph_to_path(glyph, framework)` — Return expected file path
- [ ] `path_to_glyph(path)` — Parse `@archeon` comment, return glyph

### 10.2 Drift Detection
- [ ] `find_drift()`:
  - Scan generated files for `@archeon` markers
  - Compare to graph
  - Return: files without glyphs, glyphs without files, modified files

### 10.3 Sync
- [ ] `sync_markers()` — Update `@archeon` comments in files to match graph

**Test:** Modify a generated file, run drift detection, verify detected.

---

## Phase 11: Intent Parsing (`orchestrator/INT_intent.py`)

### 11.1 Natural Language Parser
- [ ] `parse_intent(text)` → proposed chain string
- [ ] Basic heuristics:
  - "user wants to login" → `NED:login`
  - "submit form" → `TSK:submit`
  - "show error" → `OUT:error`
- [ ] Return **proposal only** — never auto-add

### 11.2 Error Path Suggester
- [ ] `suggest_errors(chain)`:
  - Find `API:` glyphs without `ERR:` branches
  - Suggest common errors: `auth.invalidCreds`, `validation.malformed`, `system.rateLimit`
- [ ] Return suggestions, don't auto-add

### 11.3 Document Import
- [ ] `import_markdown(path)`:
  - Scan for code blocks with chain syntax
  - Extract and propose chains
- [ ] `import_url(url)`:
  - Stub for Linear/JIRA/GitHub integration
  - Parse issue description for requirements

### 11.4 Approval Workflow
- [ ] CLI: `archeon intent "<text>"`
  - Show proposed chain
  - Prompt: `[a]pprove [e]dit [r]eject [s]uggest errors`
  - Only add to graph on explicit approval

**Test:** Parse sample intents, verify reasonable chain proposals.

---

## Phase 12: Headless Execution Mode

### 12.1 Opt-In System
- [ ] Only `[headless]` annotated components can execute
- [ ] `VAL:headless` validator — block non-annotated execution

### 12.2 Sandbox Mode (Default)
- [ ] Trace execution without side effects
- [ ] Mock all `API:` calls
- [ ] Return execution trace:
  ```json
  {
    "event": "...",
    "data": {...},
    "trace": [{"glyph": "...", "time_ms": ...}],
    "sandbox": true
  }
  ```

### 12.3 Live Mode
- [ ] Require explicit `mode=live` flag
- [ ] Execute real `API:` calls
- [ ] Log all operations

### 12.4 HTTP Interface
- [ ] `/api/cmp/{component}` endpoint
- [ ] Query params: `action`, `from`, `mode`, `debug`
- [ ] `/api/cmp/{component}/metrics` — Execution metrics

**Test:** Execute headless component in sandbox, verify trace output.

---

## Phase 13: Graph Visualization

### 13.1 DOT Export
- [ ] `export_dot(graph)` — Generate Graphviz DOT format
- [ ] Node shapes by glyph type (from legend colors)
- [ ] Edge styles by operator type

### 13.2 JSON Export
- [ ] `export_json(graph)` — Full graph as JSON
- [ ] For web visualization consumption

### 13.3 PNG Export
- [ ] Shell out to `dot` command
- [ ] `archeon graph --format png --output graph.png`

**Test:** Export sample graph, verify DOT syntax valid.

---

## Phase 14: Polish & Edge Cases

### 14.1 Error Handling
- [ ] Graceful handling of malformed chains
- [ ] Clear error messages with line numbers
- [ ] Suggestions for common mistakes

### 14.2 Performance
- [ ] Lazy loading of graph for large `.arcon` files
- [ ] Incremental validation (only changed chains)

### 14.3 Configuration
- [ ] `.archeonrc` file for project defaults:
  ```yaml
  frontend: react
  backend: fastapi
  db: mongo
  output_dir: ./src
  ```

### 14.4 Documentation
- [ ] `archeon --help` comprehensive help
- [ ] `archeon <command> --help` for each command
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
