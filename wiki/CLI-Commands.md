# CLI Commands

Complete reference for the Archeon command-line interface.

## Global Options

```bash
arc [COMMAND] [OPTIONS]
```

All commands support:
- `--help` - Show help for command
- `--version` - Show Archeon version

---

## Core Commands

### `arc init`

Initialize a new Archeon project.

```bash
arc init [PATH] [OPTIONS]
```

**Arguments:**
- `PATH` - Directory to initialize (default: current directory)

**Options:**
- `--frontend, -f` - Frontend framework: `react`, `vue`, `vue3` (default: `vue3`)
- `--backend, -b` - Backend framework: `fastapi`, `express` (default: `fastapi`)
- `--arch, -a` - Architecture shape ID (e.g., `vue3-fastapi`). Overrides frontend/backend.
- `--monorepo/--single` - Create client/server separation (default: `--monorepo`)
- `--copilot` - Generate `.github/copilot-instructions.md` for GitHub Copilot
- `--cursor` - Generate `.cursorrules` for Cursor IDE
- `--windsurf` - Generate `.windsurfrules` for Windsurf
- `--cline` - Generate `.clinerules` for Cline/Claude Dev
- `--aider` - Generate `.aider.conf.yml` for Aider
- `--vscode` - Update `.vscode/settings.json`

**Examples:**

```bash
# Initialize with Vue 3 + FastAPI
arc init --frontend vue3 --backend fastapi

# Initialize with architecture shape
arc init --arch nextjs-fastapi

# Initialize with GitHub Copilot rules included
arc init --arch nextjs-fastapi --copilot

# Initialize with multiple IDE rules
arc init --arch nextjs-fastapi --copilot --cline

# Initialize React + FastAPI in specific directory
arc init my-app --frontend react

# Single directory (no client/server split)
arc init --single
```

**What it creates:**

```
my-app/
├── archeon/
│   └── ARCHEON.arcon
├── client/              # Frontend
│   ├── src/
│   │   ├── components/
│   │   ├── stores/
│   │   └── App.vue
│   ├── package.json
│   └── vite.config.js
├── server/              # Backend
│   ├── src/
│   │   ├── api/
│   │   ├── models/
│   │   └── main.py
│   └── requirements.txt
└── README.md
```

---

### `arc parse`

Parse and add a chain to the knowledge graph.

```bash
arc parse "CHAIN_STRING" [OPTIONS]
```

**Arguments:**
- `CHAIN_STRING` - The chain to parse (in quotes)

**Options:**
- `--version, -v` - Version tag (default: `v1`)
- `--validate` - Validate before adding (default: `true`)
- `--dry-run` - Parse without adding to graph

**Examples:**

```bash
# Add a simple chain
arc parse "NED:login => CMP:LoginForm => API:POST/auth => OUT:redirect"

# Add with version
arc parse "@v2 NED:login => CMP:OAuthButton => API:GET/auth/google" --version v2

# Validate only (don't add)
arc parse "NED:test => CMP:Test" --dry-run
```

**Output:**

```
Parsed chain:
  Version: @v1
  Glyphs: 4
  Edges: 3
  
✓ Validation passed
✓ Added to archeon/ARCHEON.arcon
```

---

### `arc intent` (alias: `arc i`)

Generate chains from natural language.

```bash
arc i "NATURAL_LANGUAGE_DESCRIPTION" [OPTIONS]
```

**Arguments:**
- `DESCRIPTION` - What you want to build (in quotes)

**Options:**
- `--file, -f` - Read from file instead of argument
- `--auto-errors` - Auto-suggest error paths
- `--confidence` - Minimum confidence level: `HIGH`, `MEDIUM`, `LOW` (default: `MEDIUM`)

**Examples:**

```bash
# From natural language
arc i "User wants to login with email and password"

# From requirements file
arc i --file requirements.md

# With auto-suggested errors
arc i "User checks out their cart" --auto-errors

# Only high-confidence proposals
arc i "User searches for products" --confidence HIGH
```

**Interactive Flow:**

```
╭─ Proposal 1 ─────────────────────────────────────────╮
│ NED:login => TSK:submit => CMP:LoginForm => STO:Auth │
│     => API:POST/auth/login => MDL:user.verify        │
│     => OUT:redirect('/dashboard')                    │
│                                                      │
│ Confidence: HIGH                                     │
│ Reasoning:                                           │
│   • Detected need: login                             │
│   • Found action: submit                             │
│   • Identified form component                        │
│   • Mapped to auth store                             │
╰──────────────────────────────────────────────────────╯

Suggested error paths:
  → API:POST/auth/login -> ERR:auth.invalidCredentials
  → API:POST/auth/login -> ERR:network.timeout

Action [a/e/r/s]:
```

**Actions:**
- `a` - **Approve** and add to graph
- `e` - **Edit** the chain
- `r` - **Reject** and try again
- `s` - **Suggest** additional error paths

---

### `arc gen`

Generate code from the knowledge graph.

```bash
arc gen [GLYPHS...] [OPTIONS]
```

**Arguments:**
- `GLYPHS` - Specific glyphs to generate (optional, generates all if omitted)

**Options:**
- `--frontend, -f` - Target framework: `react`, `vue`, `vue3`
- `--backend, -b` - Target framework: `fastapi`, `express`
- `--version, -v` - Generate specific version only
- `--force` - Overwrite existing files
- `--dry-run` - Show what would be generated

**Examples:**

```bash
# Generate all files
arc gen

# Generate specific glyphs
arc gen CMP:LoginForm STO:Auth

# Generate with specific framework
arc gen --frontend vue3

# Generate specific version
arc gen --version v1

# Dry run (preview)
arc gen --dry-run

# Force overwrite
arc gen --force
```

**Output:**

```
Generating code...

✓ CMP:LoginForm → client/src/components/LoginForm.vue
✓ STO:Auth → client/src/stores/AuthStore.js  
✓ API:POST/auth/login → server/src/api/routes/auth_login.py
✓ MDL:user → server/src/models/user.py

Generated 4 files
```

---

### `arc status`

Show knowledge graph status.

```bash
arc status [OPTIONS]
```

**Options:**
- `--verbose, -v` - Show detailed information
- `--json` - Output as JSON

**Examples:**

```bash
# Basic status
arc status

# Verbose output
arc status --verbose

# JSON output
arc status --json
```

**Output:**

```
Knowledge Graph Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Chains:  12
Glyphs:  47
Files:   32

Recent Chains:
  @v1 NED:login => TSK:submit => CMP:LoginForm => OUT:redirect
  @v1 NED:register => TSK:submit => CMP:RegisterForm => OUT:redirect
  @v1 NED:search => TSK:query => CMP:SearchBar => OUT:display

Generated Files: 32
Missing Files:   2
  • API:POST/orders → server/src/api/routes/orders.py
  • CMP:OrderCard → client/src/components/OrderCard.vue
```

---

### `arc validate`

Validate the knowledge graph.

```bash
arc validate [OPTIONS]
```

**Options:**
- `--fix` - Auto-fix issues when possible
- `--strict` - Enable strict validation rules

**Examples:**

```bash
# Basic validation
arc validate

# Strict mode
arc validate --strict

# Auto-fix
arc validate --fix
```

**Checks:**

- ✓ Chain syntax
- ✓ Glyph boundary rules
- ✓ HCI completeness (needs → outcomes)
- ✓ Orphaned glyphs
- ✓ Missing error paths
- ✓ Circular dependencies
- ✓ File generation status

**Output:**

```
Validating knowledge graph...

✓ All chains valid
✓ No boundary violations
✓ All user journeys complete
⚠ 2 missing error paths:
  • API:POST/auth/login (suggest: ERR:auth.invalidCredentials)
  • API:POST/orders (suggest: ERR:payment.declined)
  
Run with --strict for additional checks
```

---

### `arc history`

Show version history for a glyph or chain.

```bash
arc history GLYPH [OPTIONS]
```

**Arguments:**
- `GLYPH` - Glyph to show history for

**Options:**
- `--all` - Show all chain history
- `--json` - Output as JSON

**Examples:**

```bash
# Show history for specific glyph
arc history NED:login

# Show all chain history
arc history --all
```

**Output:**

```
History for NED:login
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@v1 (active)
  NED:login => TSK:submit => CMP:LoginForm => OUT:redirect
  Created: 2024-01-15

@v2 (deprecated)
  NED:login => CMP:OAuthButton => API:GET/auth/google => OUT:redirect
  Created: 2024-02-01
  Deprecated: 2024-03-01
  Reason: Switched back to username/password
```

---

### `arc export`

Export knowledge graph in various formats.

```bash
arc export [FORMAT] [OPTIONS]
```

**Arguments:**
- `FORMAT` - Output format: `mermaid`, `dot`, `json`, `markdown`

**Options:**
- `--output, -o` - Output file (default: stdout)
- `--include-deprecated` - Include deprecated chains

**Examples:**

```bash
# Export as Mermaid diagram
arc export mermaid --output graph.mmd

# Export as JSON
arc export json --output graph.json

# Export as Markdown documentation
arc export markdown --output ARCHITECTURE.md

# Export as Graphviz DOT
arc export dot --output graph.dot
```

---

### `arc template`

Manage code templates.

```bash
arc template [COMMAND] [OPTIONS]
```

**Commands:**
- `list` - List available templates
- `show GLYPH` - Show template for glyph type
- `edit GLYPH` - Edit template for glyph type
- `reset GLYPH` - Reset template to default

**Examples:**

```bash
# List all templates
arc template list

# Show Vue3 component template
arc template show CMP --frontend vue3

# Edit React component template
arc template edit CMP --frontend react

# Reset to default
arc template reset CMP
```

---

### `arc index`

Manage the semantic index.

```bash
arc index [COMMAND]
```

**Commands:**
- `code` - ⭐ **One-command setup** - Creates archeon/, index, arcon, and all IDE rules
- `build` - Build index from @archeon:section markers
- `infer` - Auto-index arbitrary codebase by detecting file types
- `show` - Display the current index
- `scan` - Scan a single file for sections
- `check` - Check index consistency / find files missing headers
- `inject` - Add @archeon:file header to an existing file
- `clean` - Remove orphaned entries

---

#### `arc index code`

**⭐ The easiest way to add Archeon to an existing codebase.**

One command does everything:

```bash
cd your-existing-project
arc index code
```

**What it does:**

1. Creates `archeon/` directory
2. Scans and classifies all files to glyphs (CMP, API, STO, MDL, FNC, EVT, V)
3. Auto-detects tech stack from `package.json`, `pyproject.toml`
4. Generates `archeon/ARCHEON.index.json` with file-to-glyph mappings
5. Generates `archeon/ARCHEON.arcon` knowledge graph with inferred chains
6. Creates AI rules for **all IDEs**:
   - `.cursorrules` (Cursor)
   - `.windsurfrules` (Windsurf)
   - `.clinerules` (Cline/Claude Dev)
   - `.github/copilot-instructions.md` (GitHub Copilot)
   - `.aider.conf.yml` (Aider)
   - `.vscode/settings.json` (VS Code)

**Example output:**

```
$ arc index code

╭───────────────────────────────────────────────────────╮
│ ⭐ Archeon One-Command Setup                          │
╰───────────────────────────────────────────────────────╯

✓ Created archeon/ directory
✓ Indexed 47 files
    Glyphs: API:8, CMP:12, STO:4, MDL:6, FNC:15, V:2
✓ Generated ARCHEON.arcon with 5 chains

📝 Generating IDE configurations...
  ✓ .cursorrules
  ✓ .windsurfrules
  ✓ .clinerules
  ✓ .github/copilot-instructions.md
  ✓ .aider.conf.yml
  ✓ .vscode/settings.json

╭──────────────────────────────────────────────────────╮
│ ✅ Archeon setup complete!                           │
│                                                      │
│ Your AI assistant now understands your architecture! │
╰──────────────────────────────────────────────────────╯
```

**Options:**
- `--path, -p` - Directory to index (default: current directory)

---

#### `arc index infer`

Auto-detect and classify files in an arbitrary codebase without Archeon headers.

```bash
arc index infer [--path <directory>] [--output <file>]
```

**What it does:**
- Scans files and classifies by path patterns and code signatures
- Detects tech stack from `package.json`, `pyproject.toml`
- Generates `ARCHEON.index.json` with inferred glyphs
- Does NOT modify source files

**Options:**
- `--path, -p` - Directory to scan (default: current directory)
- `--output, -o` - Output file path

---

#### Other index commands

**Examples:**

```bash
# Rebuild index from annotated files
arc index build

# Check for files missing @archeon:file headers
arc index check

# Show the current index
arc index show

# Show a specific glyph
arc index show --glyph CMP:LoginForm

# Scan a single file
arc index scan --path src/components/LoginForm.vue

# Inject header into existing file
arc index inject --path src/App.vue --glyph CMP:App --intent "Root application component"
```

---

## Advanced Commands

### `arc graph`

Visualize the knowledge graph.

```bash
arc graph [OPTIONS]
```

**Options:**
- `--filter, -f` - Filter by glyph pattern
- `--depth, -d` - Maximum depth to traverse
- `--focus` - Focus on specific glyph and neighbors

**Examples:**

```bash
# Show full graph
arc graph

# Filter to authentication
arc graph --filter "NED:login,NED:register"

# Focus on login form
arc graph --focus CMP:LoginForm
```

---

### `arc migrate`

Migrate chains between versions or frameworks.

```bash
arc migrate [OPTIONS]
```

**Options:**
- `--from-version` - Source version
- `--to-version` - Target version
- `--from-framework` - Source framework
- `--to-framework` - Target framework

**Examples:**

```bash
# Migrate from v1 to v2
arc migrate --from-version v1 --to-version v2

# Migrate from Vue 2 to Vue 3
arc migrate --from-framework vue --to-framework vue3
```

---

## Configuration

### `.archeonrc`

Project configuration file (JSON):

```json
{
  "frontend": {
    "framework": "vue3",
    "srcDir": "client/src",
    "componentsDir": "components",
    "storesDir": "stores"
  },
  "backend": {
    "framework": "fastapi",
    "srcDir": "server/src",
    "apiDir": "api",
    "modelsDir": "models"
  },
  "generation": {
    "overwrite": false,
    "addToGit": true
  },
  "validation": {
    "strict": false,
    "requireErrorPaths": true
  }
}
```

---

## Environment Variables

```bash
# Override arcon file location
export ARCHEON_FILE="/path/to/custom.arcon"

# Set default frontend
export ARCHEON_FRONTEND="vue3"

# Set default backend
export ARCHEON_BACKEND="fastapi"

# Enable debug mode
export ARCHEON_DEBUG="true"
```

---

## Tips and Tricks

### Aliases

Add to your `.zshrc` or `.bashrc`:

```bash
alias a='arc'
alias ai='arc intent'
alias ag='arc gen'
alias as='arc status'
alias av='arc validate'
```

### Chaining Commands

```bash
# Parse and generate in one go
arc parse "NED:login => CMP:Form => OUT:redirect" && arc gen

# Intent, validate, generate
arc i "User wants to login" && arc validate && arc gen
```

### Watch Mode

Use with `entr` for auto-regeneration:

```bash
# Regenerate when arcon changes
echo archeon/ARCHEON.arcon | entr arc gen
```

---

## Next Steps

- 🎨 [Templates](Templates) - Customize code generation
- 🏗️ [Architecture](Architecture) - System design principles
- 🔤 [Glyph Reference](Glyph-Reference) - Glyph documentation
