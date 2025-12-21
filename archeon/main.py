"""
Archeon CLI - Main entry point

Glyph-based architecture notation system for AI-orchestrated software development.

This file contains only CLI command definitions. Helper functions and templates
are in separate modules for better organization:
- cli_helpers.py - Project initialization and setup functions
- cli_templates.py - README and documentation templates

Install globally with:
    pip install -e .
    # or
    pip install archeon
    
Then use from anywhere:
    archeon init
    archeon parse "NED:login => TSK:submit => CMP:LoginForm => OUT:redirect"
    archeon gen --frontend react --backend fastapi
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint

from archeon.orchestrator.PRS_parser import parse_chain, ParseError
from archeon.orchestrator.GRF_graph import KnowledgeGraph, load_graph
from archeon.orchestrator.VAL_validator import validate_chain, validate_graph, GraphValidator
from archeon.config.legend import GLYPH_LEGEND, EDGE_TYPES
from archeon.cli_helpers import (
    create_base_directories,
    create_client_structure,
    create_server_structure,
    create_server_files,
    create_arcon_file,
    create_archeonrc_file,
    create_gitignore,
    create_orchestrator_readme,
    create_ai_readme,
    copy_templates,
)

app = typer.Typer(
    name="archeon",
    help="Glyph-based architecture notation system for AI-orchestrated development.",
    no_args_is_help=False,
    rich_markup_mode="rich",
)
console = Console()

DEFAULT_ARCON = "ARCHEON.arcon"


def get_arcon_path() -> Path:
    """Get path to ARCHEON.arcon in current or parent directories."""
    current = Path.cwd()
    
    # Check current directory
    if (current / DEFAULT_ARCON).exists():
        return current / DEFAULT_ARCON
    
    # Check archeon subdirectory
    if (current / "archeon" / DEFAULT_ARCON).exists():
        return current / "archeon" / DEFAULT_ARCON
    
    # Walk up to find project root
    for parent in current.parents:
        if (parent / DEFAULT_ARCON).exists():
            return parent / DEFAULT_ARCON
        if (parent / "archeon" / DEFAULT_ARCON).exists():
            return parent / "archeon" / DEFAULT_ARCON
    
    # Default to current directory
    return current / DEFAULT_ARCON


# ============================================================================
# CLI COMMANDS
# ============================================================================


@app.command()
def init(
    path: Optional[str] = typer.Argument(None, help="Directory to initialize"),
    monorepo: bool = typer.Option(True, "--monorepo/--single", help="Create client/server separation"),
    frontend: str = typer.Option("react", "--frontend", "-f", help="Frontend framework (react, vue, vue3)"),
    backend: str = typer.Option("fastapi", "--backend", "-b", help="Backend framework (fastapi, express)"),
):
    """Initialize a new Archeon project with client/server structure."""
    target = Path(path) if path else Path.cwd()
    archeon_dir = target / "archeon"
    
    # Normalize frontend option
    if frontend.lower() in ("vue", "vue3"):
        frontend = "vue3"
    
    # Create base archeon directories
    create_base_directories(archeon_dir)
    
    # Copy reference templates from the archeon package
    copy_templates(archeon_dir, frontend, backend)
    
    # Create orchestrator README for AI reference
    create_orchestrator_readme(archeon_dir)
    
    # Create AI provisioning guide
    create_ai_readme(archeon_dir)
    
    if monorepo:
        # Create client and server structures
        create_client_structure(target / "client", frontend)
        create_server_structure(target / "server")
        create_server_files(target / "server", backend)
    
    # Create ARCHEON.arcon
    create_arcon_file(archeon_dir, target.name)
    
    # Create .archeonrc config file
    create_archeonrc_file(target, monorepo, frontend, backend)
    
    # Create .gitignore
    create_gitignore(target)
    
    rprint(f"[green]✓[/green] Initialized Archeon project at [bold]{archeon_dir}[/bold]")
    rprint(f"  Created {DEFAULT_ARCON}")
    rprint(f"  Created .archeonrc")
    rprint(f"  Copied {frontend}/{backend} templates to archeon/templates/")
    rprint(f"  Created orchestrator/README.md (glyph reference)")
    rprint(f"  Created AI_README.md (provisioning guide)")
    
    if monorepo:
        rprint(f"\n  [bold]Project Structure:[/bold]")
        rprint(f"  [cyan]client/[/cyan]  → {frontend.capitalize()} frontend (components, stores)")
        rprint(f"  [cyan]server/[/cyan]  → {backend.capitalize()} backend (API, models, events)")
        rprint(f"  [cyan]archeon/[/cyan] → Knowledge graph and orchestration")
    
    rprint(f"\n  [bold]Next:[/bold] Describe a feature in natural language:")
    rprint(f"  [cyan]arc intent \"user logs in with email and password\"[/cyan]")
    rprint(f"\n  Or use glyph notation directly:")
    rprint(f"  [cyan]arc parse \"NED:login => CMP:LoginForm => API:POST/auth => OUT:dashboard\"[/cyan]")
    
    rprint(f"\n  [bold]Tip:[/bold] Run [cyan]arc ai-setup[/cyan] to configure IDE AI assistants")


@app.command("ai-setup")
def ai_setup(
    cursor: Optional[bool] = typer.Option(None, "--cursor/--no-cursor", help="Generate .cursorrules"),
    copilot: Optional[bool] = typer.Option(None, "--copilot/--no-copilot", help="Generate .github/copilot-instructions.md"),
    windsurf: Optional[bool] = typer.Option(None, "--windsurf/--no-windsurf", help="Generate .windsurfrules"),
    cline: Optional[bool] = typer.Option(None, "--cline/--no-cline", help="Generate .clinerules"),
    aider: Optional[bool] = typer.Option(None, "--aider/--no-aider", help="Generate .aider.conf.yml"),
    vscode: Optional[bool] = typer.Option(None, "--vscode/--no-vscode", help="Update .vscode/settings.json"),
    all_ides: bool = typer.Option(False, "--all", "-a", help="Generate configs for all IDEs"),
):
    """Generate AI assistant configuration files for IDE integration.
    
    By default, generates all configs. Use specific flags to generate only selected ones.
    
    Examples:
        arc ai-setup              # Generate all (default)
        arc ai-setup --cursor     # Only Cursor
        arc ai-setup --vscode --copilot  # Only VS Code and Copilot
        arc ai-setup --no-cline   # All except Cline
    """
    target = Path.cwd()
    created = []
    
    # Determine which to generate:
    # - If --all flag, generate everything
    # - If any positive flag is set (True), only generate those
    # - If only negative flags (False), generate all except those
    # - If no flags, generate all (default behavior)
    
    flags = {'cursor': cursor, 'copilot': copilot, 'windsurf': windsurf, 
             'cline': cline, 'aider': aider, 'vscode': vscode}
    
    has_positive = any(v is True for v in flags.values())
    has_negative = any(v is False for v in flags.values())
    
    if all_ides:
        # --all flag: enable everything
        for key in flags:
            if flags[key] is None:
                flags[key] = True
    elif has_positive:
        # User specified specific IDEs to include
        for key in flags:
            if flags[key] is None:
                flags[key] = False
    else:
        # No positive flags or --all: default to all (unless explicitly disabled)
        for key in flags:
            if flags[key] is None:
                flags[key] = True
    
    # Archeon context block (shared across all configs)
    archeon_context = '''## Archeon Architecture System

This project uses Archeon, a glyph-based architecture notation system.

### ⚠️ MANDATORY: Glyph-Code-Test Workflow

**Every feature MUST follow this exact workflow:**

1. **ADD GLYPH** → Write the chain to `archeon/ARCHEON.arcon`
2. **WRITE CODE** → Implement the code for each glyph
3. **RUN VALIDATE** → Execute `arc validate` to test architecture

```bash
# ALWAYS run after adding glyphs and writing code:
arc validate
```

**Never skip validation.** If it fails, fix issues before continuing.

### Critical Files - READ FIRST
- `archeon/ARCHEON.arcon` - The knowledge graph defining all features
- `archeon/AI_README.md` - **Provisioning guide** (how to create new projects)
- `.archeonrc` - Project configuration (frontend, backend, paths)

### Creating New Projects
If the user asks to create a new application (React, Vue, etc.), read `archeon/AI_README.md` for shell commands:
```bash
mkdir project-name && cd project-name
arc init --frontend vue3  # or react (default)
arc ai-setup
```

### Glyph Notation
Features are defined as chains:
```
NED:login => CMP:LoginForm => STO:Auth => API:POST/auth => MDL:user => OUT:dashboard
```

| Glyph | Meaning |
|-------|---------|
| `NED:` | User need/motivation |
| `TSK:` | User task/action |
| `CMP:` | UI Component |
| `STO:` | State store |
| `API:` | HTTP endpoint |
| `MDL:` | Data model (API schemas + database) |
| `FNC:` | Utility function |
| `EVT:` | Event handler |
| `OUT:` | Success outcome |
| `ERR:` | Error path |

### Edge Types
- `=>` Structural flow (no cycles)
- `~>` Reactive subscription (cycles OK)
- `->` Control/branching
- `::` Containment

### The Complete Workflow (REQUIRED)

**Step 1: Add Glyph Chain**
```bash
arc parse "NED:feature => CMP:Component => STO:Store => API:POST/path => MDL:model => OUT:result"
```
Or write directly to `archeon/ARCHEON.arcon`.

**Step 2: Implement Code**
Write code for each glyph in the chain.

**Step 3: Validate Architecture**
```bash
arc validate
```
This checks:
- All glyphs have corresponding code
- No boundary violations (CMP cannot access MDL)
- No cycles in structural edges
- API endpoints have error handlers

**Step 4: Run Tests**
```bash
cd client && npm test      # Frontend
cd server && pytest        # Backend
```

### Writing Glyph Chains
You CAN and SHOULD write glyph chains directly to `archeon/ARCHEON.arcon`.

**Chain Format:**
```
@v1 NED:feature => CMP:Component => STO:Store => API:METHOD/path => MDL:model => OUT:result
```

**Writing Rules:**
1. Add new chains under `# === AGENT CHAINS ===` section
2. Use incremental version tags: if `@v1 NED:login` exists, next version is `@v2 NED:login`
3. Chains must start with `NED:` or `TSK:` and end with `OUT:` or `ERR:`
4. Use PascalCase for components/stores: `CMP:LoginForm`, `STO:AuthStore`
5. Use METHOD/path for APIs: `API:POST/auth/login`, `API:GET/users/{id}`
6. Add comments above chains to describe the feature

**Example - Adding a new feature:**
```
# User registration with email verification
@v1 NED:register => CMP:RegisterForm => STO:Auth => API:POST/auth/register => MDL:user => EVT:sendVerificationEmail => OUT:checkEmail
```

### Hard Rules
1. **Always read ARCHEON.arcon first** before generating any code
2. **You can add chains** - write new chains following the format above
3. **Never invent architecture outside the graph** - add the chain first, then implement
4. **Respect layer boundaries** - CMP cannot directly access MDL
5. **All features must have outcomes** - chains end with OUT: or ERR:
6. **Increment versions** - when modifying a feature, create `@v2`, `@v3`, etc.
7. **Always validate** - run `arc validate` after every code change

### Backend Route Registration (CRITICAL)
When creating API endpoints, you MUST also update `server/src/main.py`:

```python
# Import the new route module
from server.src.api.routes import auth_login

# Register the router
app.include_router(auth_login.router)
```

**Every API glyph requires:**
1. Create route file: `server/src/api/routes/{name}.py`
2. Import in `server/src/main.py`
3. Call `app.include_router(module.router)`
4. Run `arc validate`

### Commands
- `arc intent "description"` - Propose new feature from natural language
- `arc parse "chain"` - Add glyph chain directly  
- `arc gen` - Generate code from knowledge graph
- `arc status` - Show graph statistics
- `arc validate` - **Check architecture integrity (REQUIRED after every change)**
'''
    
    if flags['cursor']:
        cursor_dir = target / ".cursor"
        cursor_dir.mkdir(exist_ok=True)
        
        # Create .cursorrules in project root (where Cursor looks for it)
        cursor_file = target / ".cursorrules"
        cursor_file.write_text(f'''# Archeon Project Rules for Cursor

{archeon_context}

### Cursor-Specific Instructions
When asked to implement a feature:
1. First, read `archeon/ARCHEON.arcon`
2. Check if the feature exists as a chain
3. If NOT, write a new chain to `archeon/ARCHEON.arcon` under `# === AGENT CHAINS ===`
4. Implement the code following the chain structure exactly
5. **Run `arc validate`** to verify the implementation
6. Fix any validation errors before considering the task complete
7. Do not add components, stores, or APIs not represented in the graph
''')
        
        # Create README in .cursor directory
        (cursor_dir / "README.md").write_text('''# Cursor Configuration for Archeon

## Setup Complete ✓

The `.cursorrules` file in your project root tells Cursor to:
1. Always read `archeon/ARCHEON.arcon` before generating code
2. Write new chains to the knowledge graph for new features
3. Respect the glyph-based architecture
4. **Run `arc validate` after every code change**

## The Glyph-Code-Test Workflow

Every feature follows this mandatory workflow:

```
1. ADD GLYPH    → Write chain to ARCHEON.arcon
2. WRITE CODE   → Implement each glyph
3. RUN VALIDATE → arc validate (REQUIRED)
4. RUN TESTS    → npm test / pytest
```

## How It Works

When you ask Cursor to implement something, it will:
- Check the knowledge graph first
- If the feature doesn't exist, ADD A NEW CHAIN first
- Implement code following that chain
- Run `arc validate` to verify architecture
- Fix any validation errors

## Example Prompts

```
"Create a user registration feature"
→ Cursor adds: @v1 NED:register => CMP:RegisterForm => STO:Auth => API:POST/auth/register => MDL:user => OUT:success
→ Implements the code
→ Runs arc validate
→ Fixes any issues

"Read archeon/ARCHEON.arcon and implement the login feature"
"What chains are defined in this project?"
"Add a password reset flow to the knowledge graph"
```

## More Info

- [Cursor Documentation](https://cursor.sh/docs)
- [Archeon README](../README.md)
''')
        created.append(".cursorrules")
        created.append(".cursor/README.md")
    
    if flags['copilot']:
        github_dir = target / ".github"
        github_dir.mkdir(exist_ok=True)
        copilot_file = github_dir / "copilot-instructions.md"
        copilot_file.write_text(f'''# GitHub Copilot Instructions

{archeon_context}

### For Copilot Chat
When implementing features:
1. Always read `archeon/ARCHEON.arcon` first
2. If the feature doesn't exist, write a new chain to `ARCHEON.arcon`
3. Then implement the code following that chain
''')
        
        # Create README for GitHub Copilot setup
        (github_dir / "COPILOT_README.md").write_text('''# GitHub Copilot Configuration for Archeon

## Setup Complete ✓

The `copilot-instructions.md` file tells GitHub Copilot to:
1. Reference `archeon/ARCHEON.arcon` for architecture context
2. Write new chains to the knowledge graph when needed
3. Understand glyph notation (NED, CMP, STO, API, etc.)

## How It Works

GitHub Copilot Chat reads `copilot-instructions.md` as project context.
When you ask Copilot to generate code, it will:
- Check the knowledge graph first  
- If feature doesn't exist, ADD A NEW CHAIN first
- Then implement code following the chain

## VS Code Setup

1. Ensure GitHub Copilot extension is installed
2. The instructions file is auto-detected from `.github/`
3. In Copilot Chat, the context is applied automatically

## Example Prompts

```
@workspace Create a user profile feature
→ Copilot adds chain to ARCHEON.arcon, then implements

@workspace Read ARCHEON.arcon and implement the login feature
@workspace What chains are defined in this project?
@workspace Add a password reset flow to the architecture
```

## More Info

- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [Archeon README](../README.md)
''')
        created.append(".github/copilot-instructions.md")
        created.append(".github/COPILOT_README.md")
    
    if flags['windsurf']:
        windsurf_dir = target / ".windsurf"
        windsurf_dir.mkdir(exist_ok=True)
        
        # Windsurf rules file in project root
        windsurf_file = target / ".windsurfrules"
        windsurf_file.write_text(f'''# Archeon Rules for Windsurf

{archeon_context}

### Windsurf-Specific
Before any code generation task:
1. Read archeon/ARCHEON.arcon
2. If the feature doesn't exist, write a new chain first
3. Then implement code following the chain structure
''')
        
        # Create README
        (windsurf_dir / "README.md").write_text('''# Windsurf Configuration for Archeon

## Setup Complete ✓

The `.windsurfrules` file tells Windsurf (Codeium) to:
1. Read `archeon/ARCHEON.arcon` before generating code
2. Write new chains when features don't exist
3. Follow the glyph-based architecture

## How It Works

Windsurf's Cascade AI reads the rules file for project context.
When generating code, it will:
- Check existing chains in the knowledge graph
- If feature doesn't exist, ADD A NEW CHAIN first
- Then implement following the chain

## Example Prompts

```
"Create a user settings feature"
→ Windsurf adds chain to ARCHEON.arcon, then implements

"Check ARCHEON.arcon and implement the defined chains"
"Add a notifications system to the architecture"
```

## More Info

- [Windsurf Documentation](https://codeium.com/windsurf)
- [Archeon README](../README.md)
''')
        created.append(".windsurfrules")
        created.append(".windsurf/README.md")
    
    if flags['cline']:
        cline_dir = target / ".cline"
        cline_dir.mkdir(exist_ok=True)
        
        cline_file = target / ".clinerules"
        cline_file.write_text(f'''# Archeon Rules for Cline/Claude Dev

{archeon_context}

IMPORTANT: Always read archeon/ARCHEON.arcon before any task.
If a feature doesn't exist, write a new chain to ARCHEON.arcon first, then implement.
''')
        
        # Create README
        (cline_dir / "README.md").write_text('''# Cline / Claude Dev Configuration for Archeon

## Setup Complete ✓

The `.clinerules` file tells Cline (Claude Dev) to:
1. Read `archeon/ARCHEON.arcon` as first action
2. Write new chains when features don't exist
3. Follow glyph-based architecture constraints

## How It Works

Cline reads `.clinerules` for project-specific instructions.
Before any code task, it will:
- Check the knowledge graph for existing chains
- If feature doesn't exist, ADD A NEW CHAIN first
- Then implement following the chain

## Example Prompts

```
"Create a shopping cart feature"
→ Cline adds chain to ARCHEON.arcon, then implements

"Read ARCHEON.arcon and summarize the architecture"
"Add a checkout flow to the knowledge graph"
"Implement CMP:LoginForm as defined in the graph"
```

## More Info

- [Cline Extension](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
- [Archeon README](../README.md)
''')
        created.append(".clinerules")
        created.append(".cline/README.md")
    
    if flags['aider']:
        aider_dir = target / ".aider"
        aider_dir.mkdir(exist_ok=True)
        
        aider_file = target / ".aider.conf.yml"
        aider_file.write_text('''# Aider configuration for Archeon project

# Always include these files in context
read:
  - archeon/ARCHEON.arcon
  - .archeonrc

# Don't auto-commit so user can review
auto-commits: false

# Model instructions
model-settings-yaml: |
  extra_params:
    system: |
      This project uses Archeon glyph notation.
      Always read archeon/ARCHEON.arcon before generating code.
      If a feature doesn't exist, write a new chain to ARCHEON.arcon first.
      Then implement code following that chain.
''')
        
        # Create README
        (aider_dir / "README.md").write_text('''# Aider Configuration for Archeon

## Setup Complete ✓

The `.aider.conf.yml` configures Aider to:
1. Auto-include `archeon/ARCHEON.arcon` in context
2. Include `.archeonrc` for project config
3. Disable auto-commits for review

## How It Works

When you run `aider`, it will:
- Automatically load the knowledge graph
- If feature doesn't exist, ADD A NEW CHAIN first
- Then implement code following the chain
- Wait for your approval before committing

## Usage

```bash
# Start aider in your project
cd your-project
aider

# Aider will auto-load ARCHEON.arcon
# Just ask it to implement features
```

## Example Session

```
> Create a user settings feature

Aider: I'll add this chain to ARCHEON.arcon:
  @v1 NED:settings => CMP:SettingsForm => STO:UserSettings => API:PUT/user/settings => MDL:user => OUT:saved
  
Now implementing each component...
```

## More Info

- [Aider Documentation](https://aider.chat)
- [Archeon README](../README.md)
''')
        created.append(".aider.conf.yml")
        created.append(".aider/README.md")
    
    if flags['vscode']:
        vscode_dir = target / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        settings_file = vscode_dir / "settings.json"
        
        settings = {}
        if settings_file.exists():
            import json
            try:
                settings = json.loads(settings_file.read_text())
            except:
                pass
        
        # Add Archeon-specific settings
        settings["files.associations"] = settings.get("files.associations", {})
        settings["files.associations"]["*.arcon"] = "markdown"
        
        settings["search.include"] = settings.get("search.include", {})
        settings["search.include"]["archeon/**"] = True
        
        settings["github.copilot.chat.codeGeneration.instructions"] = [
            {"text": "Always reference archeon/ARCHEON.arcon for architecture. This project uses Archeon glyph notation. Do not invent architecture outside the knowledge graph."}
        ]
        
        import json
        settings_file.write_text(json.dumps(settings, indent=2))
        
        # Create README
        (vscode_dir / "ARCHEON_README.md").write_text('''# VS Code Configuration for Archeon

## Setup Complete ✓

The `settings.json` has been updated with:
1. File association: `*.arcon` → Markdown syntax highlighting
2. Search include: `archeon/` folder included in searches  
3. Copilot instructions: Reference knowledge graph for code generation

## What This Enables

### Syntax Highlighting
- `.arcon` files get Markdown highlighting
- Makes chains easier to read

### Search Integration  
- `Ctrl/Cmd + Shift + F` includes archeon folder
- Find chains and glyphs across the project

### Copilot Integration
- Copilot Chat references the knowledge graph
- Better architecture-aware suggestions

## Recommended Extensions

For the best Archeon experience, install:

1. **GitHub Copilot** - AI code completion
2. **Markdown Preview** - Preview .arcon files
3. **Error Lens** - Inline error display

## Useful Shortcuts

- `Ctrl/Cmd + P` → type `ARCHEON.arcon` to open knowledge graph
- `Ctrl/Cmd + Shift + F` → search for glyph names
- `Ctrl/Cmd + Shift + E` → file explorer to browse archeon/

## More Info

- [VS Code Documentation](https://code.visualstudio.com/docs)
- [Archeon README](../README.md)
''')
        created.append(".vscode/settings.json")
        created.append(".vscode/ARCHEON_README.md")
    
    # Always create/update the AI provisioning guide
    archeon_dir = target / "archeon"
    if archeon_dir.exists():
        _create_ai_readme(archeon_dir)
        created.append("archeon/AI_README.md")
    
    if created:
        rprint(f"[green]✓[/green] Created AI assistant configurations:")
        for f in created:
            rprint(f"  [cyan]{f}[/cyan]")
        rprint(f"\n[dim]Your IDE AI will now reference the Archeon knowledge graph.[/dim]")
        rprint(f"[dim]Check the README files in each directory for setup details.[/dim]")
    else:
        rprint("[yellow]No configurations generated. Use --cursor, --copilot, etc.[/yellow]")


@app.command()
def parse(
    chain: str = typer.Argument(..., help="Chain string to parse and add"),
    section: str = typer.Option("", "--section", "-s", help="Section to add chain to"),
):
    """Parse and add a chain to the knowledge graph."""
    arcon_path = get_arcon_path()
    
    try:
        # Parse the chain
        ast = parse_chain(chain)
        
        if not ast.nodes:
            rprint("[red]✗[/red] Empty chain - nothing to add")
            raise typer.Exit(1)
        
        # Validate
        result = validate_chain(ast)
        
        if result.errors:
            rprint("[red]✗[/red] Validation errors:")
            for err in result.errors:
                rprint(f"  [red]•[/red] {err.code}: {err.message}")
            raise typer.Exit(1)
        
        if result.warnings:
            for warn in result.warnings:
                rprint(f"  [yellow]![/yellow] {warn.code}: {warn.message}")
        
        # Load graph and add chain
        graph = load_graph(str(arcon_path))
        stored = graph.add_chain(chain, section=section)
        graph.save()
        
        rprint(f"[green]✓[/green] Added chain: [cyan]{stored.ast.raw}[/cyan]")
        rprint(f"  Nodes: {len(ast.nodes)}, Edges: {len(ast.edges)}")
        if ast.version:
            rprint(f"  Version: {ast.version}")
        if ast.framework:
            rprint(f"  Framework: {ast.framework}")
            
    except ParseError as e:
        rprint(f"[red]✗[/red] Parse error: {e.message}")
        raise typer.Exit(1)
    except ValueError as e:
        rprint(f"[red]✗[/red] Error: {e}")
        raise typer.Exit(1)


@app.command()
def validate(
    boundaries: bool = typer.Option(False, "--boundaries", "-b", help="Check boundaries only"),
    cycles: bool = typer.Option(False, "--cycles", "-c", help="Check cycles only"),
):
    """Validate the knowledge graph."""
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    graph = load_graph(str(arcon_path))
    validator = GraphValidator(graph)
    
    if boundaries:
        result = validator.validate_boundaries_only()
    elif cycles:
        result = validator.validate_cycles_only()
    else:
        result = validator.validate()
    
    if result.errors:
        rprint(f"[red]✗[/red] Validation failed with {len(result.errors)} error(s):")
        for err in result.errors:
            rprint(f"  [red]•[/red] {err.code}: {err.message}")
            if err.node:
                rprint(f"      at {err.node}")
    else:
        rprint("[green]✓[/green] Validation passed")
    
    if result.warnings:
        rprint(f"\n[yellow]![/yellow] {len(result.warnings)} warning(s):")
        for warn in result.warnings:
            rprint(f"  [yellow]•[/yellow] {warn.code}: {warn.message}")
    
    stats = graph.stats()
    rprint(f"\n  Chains: {stats['total_chains']}, Glyphs: {stats['total_glyphs']}")
    
    if not result.valid:
        raise typer.Exit(1)


@app.command()
def status():
    """Show knowledge graph status."""
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    graph = load_graph(str(arcon_path))
    stats = graph.stats()
    
    # Summary panel
    rprint(Panel.fit(
        f"[bold]Archeon Status[/bold]\n"
        f"File: {arcon_path}\n\n"
        f"Chains: [cyan]{stats['total_chains']}[/cyan]\n"
        f"Glyphs: [cyan]{stats['total_glyphs']}[/cyan]\n"
        f"Deprecated: [yellow]{stats['deprecated']}[/yellow]\n"
        f"Sections: {', '.join(stats['sections']) or 'None'}",
        title="📊 Graph Status"
    ))
    
    # Glyphs table
    if graph.chains:
        table = Table(title="Glyphs")
        table.add_column("Glyph", style="cyan")
        table.add_column("Type")
        table.add_column("Chains")
        
        for glyph in sorted(graph.get_all_glyphs()):
            prefix = glyph.split(':')[0]
            glyph_info = GLYPH_LEGEND.get(prefix, {})
            chains = graph.find_chains_by_glyph(glyph)
            table.add_row(
                glyph,
                glyph_info.get('name', 'Unknown'),
                str(len(chains))
            )
        
        console.print(table)


@app.command()
def versions(
    glyph: str = typer.Argument(..., help="Glyph to show versions for"),
):
    """Show version history for a glyph."""
    arcon_path = get_arcon_path()
    graph = load_graph(str(arcon_path))
    
    versions = graph.get_chains_by_version(glyph)
    
    if not versions:
        rprint(f"[yellow]![/yellow] No chains found for {glyph}")
        raise typer.Exit(1)
    
    table = Table(title=f"Versions of {glyph}")
    table.add_column("Version", style="cyan")
    table.add_column("Chain")
    table.add_column("Status")
    
    for version, stored in sorted(versions.items()):
        status = "[red]deprecated[/red]" if stored.ast.deprecated else "[green]active[/green]"
        table.add_row(version, stored.ast.raw[:60] + "..." if len(stored.ast.raw) > 60 else stored.ast.raw, status)
    
    console.print(table)


@app.command()
def deprecate(
    version: str = typer.Argument(..., help="Version tag (e.g., v1)"),
    glyph: str = typer.Argument(..., help="Root glyph of chain"),
):
    """Mark a chain version as deprecated."""
    arcon_path = get_arcon_path()
    graph = load_graph(str(arcon_path))
    
    if graph.deprecate_chain(version, glyph):
        graph.save()
        rprint(f"[green]✓[/green] Deprecated {version} {glyph}")
    else:
        rprint(f"[red]✗[/red] Chain not found: {version} {glyph}")
        raise typer.Exit(1)


@app.command()
def legend():
    """Show the glyph legend."""
    table = Table(title="Archeon Glyph Legend")
    table.add_column("Prefix", style="bold cyan")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Layer")
    table.add_column("Agent")
    
    for prefix, info in GLYPH_LEGEND.items():
        table.add_row(
            prefix,
            info['name'],
            info['description'],
            info['layer'],
            info.get('agent') or "-"
        )
    
    console.print(table)
    
    # Edge types
    rprint("\n[bold]Edge Types:[/bold]")
    for op, info in EDGE_TYPES.items():
        cycles = "[green]yes[/green]" if info['cycles_allowed'] else "[red]no[/red]"
        rprint(f"  [cyan]{op}[/cyan] {info['name']}: {info['description']} (cycles: {cycles})")


@app.command()
def gen(
    frontend: str = typer.Option("", "--frontend", "-f", help="Frontend framework (default: from .archeonrc)"),
    backend: str = typer.Option("", "--backend", "-b", help="Backend framework (default: from .archeonrc)"),
    db: str = typer.Option("", "--db", "-d", help="Database type (default: from .archeonrc)"),
    output: str = typer.Option(".", "--output", "-o", help="Output directory (project root)"),
    force: bool = typer.Option(False, "--force", help="Force regeneration of all glyphs"),
):
    """Generate code for all unresolved glyphs (respects client/server structure)."""
    from archeon.orchestrator.SPW_spawner import AgentSpawner, ProjectConfig
    
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    # Load project config
    config = ProjectConfig.load(Path(output))
    
    # Override config with CLI options if provided
    if frontend:
        config.frontend = frontend
    if backend:
        config.backend = backend
    if db:
        config.db = db
    
    graph = load_graph(str(arcon_path))
    unresolved = graph.get_unresolved_glyphs()
    
    if not unresolved and not force:
        rprint("[green]✓[/green] All glyphs already resolved - nothing to generate")
        return
    
    rprint(f"[cyan]Generating code for {len(unresolved)} glyph(s)...[/cyan]")
    rprint(f"  Frontend: {config.frontend}, Backend: {config.backend}, DB: {config.db}")
    
    if config.monorepo:
        rprint(f"  [bold]Monorepo mode:[/bold]")
        rprint(f"    Client: {config.client_dir}")
        rprint(f"    Server: {config.server_dir}")
    else:
        rprint(f"  Output: {config.output_dir}")
    
    # Create spawner with config
    spawner = AgentSpawner(
        output_dir=output, 
        framework=config.frontend,
        backend=config.backend,
        db=config.db,
        config=config
    )
    
    # Process all unresolved glyphs
    batch = spawner.spawn_all(graph, force=force)
    
    # Display results
    table = Table(title="Generation Results")
    table.add_column("Glyph", style="cyan")
    table.add_column("Target", style="magenta")
    table.add_column("File", style="green")
    table.add_column("Status")
    
    for result in batch.results:
        status_style = {
            "success": "[green]✓[/green]",
            "skipped": "[yellow]○[/yellow]",
            "error": "[red]✗[/red]",
        }.get(result.status, result.status)
        
        target = result.target if result.target else "-"
        file_display = result.file_path or "-"
        if result.error:
            file_display = f"[red]{result.error}[/red]"
        
        table.add_row(result.glyph, target, file_display, status_style)
    
    console.print(table)
    
    rprint(f"\n[green]✓ Generated:[/green] {batch.success_count}")
    if config.monorepo and batch.success_count > 0:
        rprint(f"   [cyan]Client:[/cyan] {batch.client_count}  [magenta]Server:[/magenta] {batch.server_count}")
    rprint(f"[yellow]○ Skipped:[/yellow] {batch.skipped_count}")
    if batch.error_count:
        rprint(f"[red]✗ Errors:[/red] {batch.error_count}")
        raise typer.Exit(1)


@app.command()
def test(
    generate: bool = typer.Option(False, "--generate", "-g", help="Generate tests first"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    errors_only: bool = typer.Option(False, "--errors-only", help="Run only error path tests"),
    chain: Optional[str] = typer.Option(None, "--chain", "-c", help="Test specific chain only"),
):
    """Run generated tests."""
    from archeon.orchestrator.TST_runner import TestGenerator, TestRunner
    
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    test_dir = "tests/generated"
    
    # Generate tests if requested
    if generate:
        rprint("[cyan]Generating tests...[/cyan]")
        graph = load_graph(str(arcon_path))
        generator = TestGenerator(output_dir=test_dir)
        tests = generator.generate_from_graph(graph)
        written = generator.write_tests(tests)
        rprint(f"[green]✓[/green] Generated {len(tests)} test(s) in {len(written)} file(s)")
    
    # Run tests
    runner = TestRunner(test_dir=test_dir)
    
    if chain:
        rprint(f"[cyan]Running tests for {chain}...[/cyan]")
        result = runner.run_chain(chain, verbose=verbose)
    elif errors_only:
        rprint("[cyan]Running error path tests...[/cyan]")
        result = runner.run_errors_only(verbose=verbose)
    else:
        rprint("[cyan]Running all tests...[/cyan]")
        result = runner.run_all(verbose=verbose)
    
    # Display results
    if result.success:
        rprint(f"\n[green]✓ All tests passed[/green]")
        rprint(f"  Passed: {result.passed}, Total: {result.total}")
    else:
        rprint(f"\n[red]✗ Tests failed[/red]")
        rprint(f"  Passed: {result.passed}, Failed: {result.failed}, Errors: {result.errors}")
        raise typer.Exit(1)


@app.command()
def graph(
    format: str = typer.Option("dot", "--format", "-f", help="Output format: dot, json, png, svg, mermaid"),
    output: str = typer.Option("graph", "--output", "-o", help="Output filename (without extension)"),
):
    """Export knowledge graph visualization."""
    from archeon.orchestrator.GRF_exporter import export_dot, export_json, export_png, export_svg, export_mermaid
    
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    graph_data = load_graph(str(arcon_path))
    
    if format == "dot":
        output_path = f"{output}.dot"
        export_dot(graph_data, output_path)
        rprint(f"[green]✓[/green] Exported DOT to {output_path}")
        
    elif format == "json":
        output_path = f"{output}.json"
        export_json(graph_data, output_path)
        rprint(f"[green]✓[/green] Exported JSON to {output_path}")
        
    elif format == "png":
        output_path = f"{output}.png"
        result = export_png(graph_data, output_path)
        if result.success:
            rprint(f"[green]✓[/green] Exported PNG to {output_path}")
            rprint(f"  Nodes: {result.node_count}, Edges: {result.edge_count}")
        else:
            rprint(f"[red]✗[/red] {result.error}")
            raise typer.Exit(1)
            
    elif format == "svg":
        output_path = f"{output}.svg"
        result = export_svg(graph_data, output_path)
        if result.success:
            rprint(f"[green]✓[/green] Exported SVG to {output_path}")
        else:
            rprint(f"[red]✗[/red] {result.error}")
            raise typer.Exit(1)
            
    elif format == "mermaid":
        output_path = f"{output}.md"
        content = export_mermaid(graph_data, output_path)
        rprint(f"[green]✓[/green] Exported Mermaid to {output_path}")
        
    else:
        rprint(f"[red]✗[/red] Unknown format: {format}")
        rprint("  Supported: dot, json, png, svg, mermaid")
        raise typer.Exit(1)


@app.command()
def audit():
    """Check for drift between graph and generated files."""
    from archeon.utils.tracer import find_drift
    
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    graph = load_graph(str(arcon_path))
    
    rprint("[cyan]Scanning for drift...[/cyan]")
    report = find_drift(graph, source_dir=".")
    
    if not report.has_drift:
        rprint("[green]✓[/green] No drift detected")
        rprint(f"  Traced files: {len(report.traced_files)}")
        return
    
    # Display drift items
    table = Table(title="Drift Report")
    table.add_column("Type", style="bold")
    table.add_column("Glyph", style="cyan")
    table.add_column("Path")
    table.add_column("Message")
    
    for item in report.items:
        type_style = {
            'error': '[red]',
            'warning': '[yellow]',
            'info': '[blue]',
        }.get(item.severity, '')
        type_end = '[/]' if type_style else ''
        
        table.add_row(
            f"{type_style}{item.type}{type_end}",
            item.glyph or "-",
            item.file_path or "-",
            item.message
        )
    
    console.print(table)
    
    rprint(f"\n[red]✗ Drift detected:[/red] {len(report.items)} issue(s)")
    rprint(f"  Errors: {report.error_count}, Warnings: {report.warning_count}")
    
    if report.error_count > 0:
        raise typer.Exit(1)


@app.command("i")
@app.command("intent")
def intent(
    text: str = typer.Argument(..., help="Natural language description"),
    auto_errors: bool = typer.Option(False, "--auto-errors", help="Auto-suggest error paths"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Parse from markdown file instead"),
):
    """Parse natural language into proposed chains."""
    from archeon.orchestrator.INT_intent import parse_intent, parse_markdown, suggest_errors, extend_chain
    
    if file:
        rprint(f"[cyan]Parsing markdown file: {file}[/cyan]")
        result = parse_markdown(file)
    else:
        rprint(f"[cyan]Parsing intent...[/cyan]")
        result = parse_intent(text)
    
    if not result.proposals:
        rprint("[yellow]![/yellow] Could not extract any chains from input")
        if result.warnings:
            for warn in result.warnings:
                rprint(f"  [yellow]•[/yellow] {warn}")
        return
    
    arcon_path = get_arcon_path()
    
    # Check for similar existing chains
    similar_chains = []
    if arcon_path.exists():
        graph = load_graph(str(arcon_path))
        for proposal in result.proposals:
            similar = graph.find_similar_chains(proposal.chain, threshold=0.3)
            if similar:
                similar_chains.extend(similar)
    
    # If similar chains found, ask user what to do
    if similar_chains:
        rprint("\n[yellow]Found similar existing chains:[/yellow]")
        unique_chains = []
        seen_raws = set()
        for stored, score, shared in similar_chains:
            if stored.ast.raw not in seen_raws:
                seen_raws.add(stored.ast.raw)
                unique_chains.append((stored, score, shared))
        
        for i, (stored, score, shared) in enumerate(unique_chains[:5], 1):  # Show top 5
            pct = int(score * 100)
            rprint(f"  [dim]{i}.[/dim] [cyan]{stored.ast.raw}[/cyan]")
            rprint(f"     [dim]Similarity: {pct}% | Shared: {', '.join(shared[:3])}{'...' if len(shared) > 3 else ''}[/dim]")
        
        rprint("\n[dim]Options: Enter number to extend that chain, or press Enter to create new[/dim]")
        choice = Prompt.ask("Extend existing chain?", default="")
        
        if choice.isdigit() and 1 <= int(choice) <= len(unique_chains):
            # User wants to extend an existing chain
            selected = unique_chains[int(choice) - 1][0]
            rprint(f"\n[cyan]Extending: {selected.ast.raw}[/cyan]")
            rprint("[dim]Describe what to add (natural language):[/dim]\n")
            
            modification = Prompt.ask("Add")
            extend_result = extend_chain(selected.ast.raw, modification)
            
            if extend_result.proposals:
                # Replace result with the extended proposal
                result.proposals = extend_result.proposals
            else:
                rprint("[yellow]![/yellow] Could not extend chain. Proceeding with original proposal.")
                if extend_result.warnings:
                    for warn in extend_result.warnings:
                        rprint(f"  [yellow]•[/yellow] {warn}")
    
    def process_proposal(proposal, proposal_num):
        """Process a single proposal with approval flow."""
        confidence_style = {
            'high': '[green]HIGH[/green]',
            'medium': '[yellow]MEDIUM[/yellow]',
            'low': '[red]LOW[/red]',
        }.get(proposal.confidence.value, proposal.confidence.value)
        
        rprint(Panel.fit(
            f"[bold cyan]{proposal.chain}[/bold cyan]\n\n"
            f"Confidence: {confidence_style}\n"
            f"Reasoning:\n" + "\n".join(f"  • {r}" for r in proposal.reasoning),
            title=f"Proposal {proposal_num}"
        ))
        
        # Show suggested errors
        if auto_errors or proposal.suggested_errors:
            errors = proposal.suggested_errors or suggest_errors(proposal.chain)
            if errors:
                rprint("\n[yellow]Suggested error paths:[/yellow]")
                for err in errors:
                    rprint(f"  [dim]→[/dim] {err}")
        
        # Prompt for action
        if not arcon_path.exists():
            return
            
        rprint("")
        rprint("[dim]Actions: [a]pprove  [e]dit (natural language)  [r]eject  [s]uggest errors[/dim]")
        action = Prompt.ask(
            "Action",
            choices=["a", "e", "r", "s"],
            default="r",
        )
        
        if action == "a":  # Approve
            graph = load_graph(str(arcon_path))
            try:
                stored = graph.add_chain(proposal.chain)
                graph.save()
                rprint(f"[green]✓[/green] Added chain to graph")
            except Exception as e:
                rprint(f"[red]✗[/red] Failed to add: {e}")
                
        elif action == "e":  # Edit with natural language
            rprint("\n[dim]Describe what to add or change (natural language):[/dim]")
            rprint("[dim]  Examples: 'add a store', 'add API endpoint', 'redirect to dashboard'[/dim]")
            rprint("[dim]  Or type full glyph notation to replace the chain[/dim]\n")
            
            user_input = Prompt.ask("Edit")
            
            # Check if input looks like glyph notation or natural language
            is_glyph_notation = ('=>' in user_input or 
                                 user_input.startswith(('NED:', 'CMP:', 'STO:', 'API:', 'TSK:', 'MDL:', 'FNC:', 'EVT:', 'OUT:', 'ERR:')))
            
            if is_glyph_notation:
                # Treat as direct glyph notation
                try:
                    graph = load_graph(str(arcon_path))
                    stored = graph.add_chain(user_input)
                    graph.save()
                    rprint(f"[green]✓[/green] Added edited chain to graph")
                except Exception as e:
                    rprint(f"[red]✗[/red] Failed to add: {e}")
            else:
                # Treat as natural language modification
                rprint(f"[cyan]Extending chain with: '{user_input}'...[/cyan]")
                extend_result = extend_chain(proposal.chain, user_input)
                
                if extend_result.warnings:
                    for warn in extend_result.warnings:
                        rprint(f"[yellow]![/yellow] {warn}")
                
                if extend_result.proposals:
                    # Recursively process the extended proposal
                    process_proposal(extend_result.proposals[0], proposal_num)
                else:
                    rprint("[yellow]![/yellow] Could not extend chain. Try being more specific.")
                    
        elif action == "s":  # Suggest errors
            errors = suggest_errors(proposal.chain)
            for err in errors:
                error_chain = f"{proposal.chain} -> {err} => OUT:error"
                rprint(f"  [cyan]{error_chain}[/cyan]")
                
        else:  # Reject
            rprint("[dim]Rejected[/dim]")
    
    for i, proposal in enumerate(result.proposals, 1):
        process_proposal(proposal, i)


@app.command("diff")
def diff_versions(
    v1: str = typer.Argument(..., help="First version (e.g., v1)"),
    v2: str = typer.Argument(..., help="Second version (e.g., v2)"),
    glyph: str = typer.Argument(..., help="Root glyph to diff"),
):
    """Diff two versions of a chain."""
    arcon_path = get_arcon_path()
    graph = load_graph(str(arcon_path))
    
    versions_dict = graph.get_chains_by_version(glyph)
    
    # Normalize version format
    v1_key = v1 if v1.startswith('v') else f'v{v1}'
    v2_key = v2 if v2.startswith('v') else f'v{v2}'
    
    if v1_key not in versions_dict:
        rprint(f"[red]✗[/red] Version {v1} not found for {glyph}")
        raise typer.Exit(1)
    
    if v2_key not in versions_dict:
        rprint(f"[red]✗[/red] Version {v2} not found for {glyph}")
        raise typer.Exit(1)
    
    chain1 = versions_dict[v1_key].ast
    chain2 = versions_dict[v2_key].ast
    
    rprint(Panel.fit(
        f"[red]- {v1_key}: {chain1.raw}[/red]\n"
        f"[green]+ {v2_key}: {chain2.raw}[/green]",
        title=f"Diff: {glyph}"
    ))
    
    # Compare nodes
    nodes1 = {n.qualified_name for n in chain1.nodes}
    nodes2 = {n.qualified_name for n in chain2.nodes}
    
    added = nodes2 - nodes1
    removed = nodes1 - nodes2
    
    if added:
        rprint("\n[green]Added nodes:[/green]")
        for n in sorted(added):
            rprint(f"  [green]+[/green] {n}")
    
    if removed:
        rprint("\n[red]Removed nodes:[/red]")
        for n in sorted(removed):
            rprint(f"  [red]-[/red] {n}")
    
    if not added and not removed:
        rprint("\n[dim]No structural changes (same nodes)[/dim]")


@app.command("import")
def import_doc(
    source: str = typer.Argument(..., help="File path or URL to import"),
):
    """Import chains from markdown or external source."""
    from archeon.orchestrator.INT_intent import parse_markdown
    
    if source.startswith('http://') or source.startswith('https://'):
        rprint("[yellow]![/yellow] URL import not yet implemented")
        rprint("  Supported: Linear, JIRA, GitHub (coming soon)")
        raise typer.Exit(1)
    
    path = Path(source)
    if not path.exists():
        rprint(f"[red]✗[/red] File not found: {source}")
        raise typer.Exit(1)
    
    rprint(f"[cyan]Importing from {source}...[/cyan]")
    result = parse_markdown(str(path))
    
    if not result.proposals:
        rprint("[yellow]![/yellow] No chains found in document")
        return
    
    rprint(f"[green]✓[/green] Found {len(result.proposals)} chain(s)")
    
    arcon_path = get_arcon_path()
    
    for proposal in result.proposals:
        rprint(f"\n  [cyan]{proposal.chain}[/cyan]")
        
        if arcon_path.exists() and Confirm.ask("  Add to graph?", default=False):
            try:
                graph = load_graph(str(arcon_path))
                graph.add_chain(proposal.chain)
                graph.save()
                rprint("  [green]✓[/green] Added")
            except Exception as e:
                rprint(f"  [red]✗[/red] {e}")


@app.command()
def run(
    glyph: Optional[str] = typer.Argument(None, help="Component or chain to execute"),
    mode: str = typer.Option("sandbox", "--mode", "-m", help="Execution mode: sandbox or live"),
    input_json: Optional[str] = typer.Option(None, "--input", "-i", help="Input data as JSON"),
    chain: Optional[str] = typer.Option(None, "--chain", "-c", help="Execute a raw chain string"),
    all_chains: bool = typer.Option(False, "--all", "-a", help="Execute all chains"),
):
    """Execute chains in headless mode (sandbox or live)."""
    import json as json_module
    from archeon.orchestrator.HED_executor import (
        HeadlessExecutor,
        ExecutionMode,
        run_sandbox,
    )
    
    arcon_path = get_arcon_path()
    
    # Parse input data
    input_data = {}
    if input_json:
        try:
            input_data = json_module.loads(input_json)
        except json_module.JSONDecodeError as e:
            rprint(f"[red]✗[/red] Invalid JSON input: {e}")
            raise typer.Exit(1)
    
    exec_mode = ExecutionMode.LIVE if mode == "live" else ExecutionMode.SANDBOX
    
    # Execute raw chain string
    if chain:
        try:
            ast = parse_chain(chain)
        except ParseError as e:
            rprint(f"[red]✗[/red] Invalid chain: {e}")
            raise typer.Exit(1)
        
        executor = HeadlessExecutor()
        result = executor.execute(ast, exec_mode, input_data, strict=False)
        _display_execution_result(result, console)
        return
    
    # Need arcon for other modes
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    graph = load_graph(str(arcon_path))
    executor = HeadlessExecutor(graph)
    
    if all_chains:
        # Execute all chains
        rprint(f"[cyan]Executing all {len(graph.chains)} chains in {mode} mode...[/cyan]\n")
        
        for i, stored in enumerate(graph.chains):
            rprint(f"[dim]Chain {i+1}/{len(graph.chains)}:[/dim] {stored.ast.raw[:60]}...")
            result = executor.execute(stored.ast, exec_mode, input_data, strict=False)
            
            if result.success:
                rprint(f"  [green]✓[/green] Success ({len(result.trace.steps)} steps)")
            else:
                rprint(f"  [red]✗[/red] Failed: {result.error}")
        
        # Show metrics summary
        metrics = executor.get_metrics()
        total_exec = sum(m.get('executions', 0) for m in metrics.values())
        total_success = sum(m.get('successes', 0) for m in metrics.values())
        rprint(f"\n[bold]Summary:[/bold] {total_success}/{total_exec} chains succeeded")
        return
    
    if glyph:
        # Execute chains containing this glyph
        results = executor.execute_by_glyph(glyph, exec_mode, input_data)
        
        if not results:
            rprint(f"[yellow]![/yellow] No chains found containing {glyph}")
            raise typer.Exit(1)
        
        rprint(f"[cyan]Found {len(results)} chain(s) containing {glyph}[/cyan]\n")
        for result in results:
            _display_execution_result(result, console)
        return
    
    rprint("[yellow]![/yellow] Specify a glyph, --chain, or --all")
    rprint("  Examples:")
    rprint("    [cyan]archeon run CMP:LoginForm[/cyan]")
    rprint("    [cyan]archeon run --chain \"NED:test => OUT:done\"[/cyan]")
    rprint("    [cyan]archeon run --all --mode sandbox[/cyan]")


def _display_execution_result(result, console):
    """Display execution result with formatting."""
    from rich.json import JSON
    
    trace = result.trace
    status_color = "green" if result.success else "red"
    status_icon = "✓" if result.success else "✗"
    
    rprint(f"[{status_color}]{status_icon}[/{status_color}] {trace.chain_id[:60]}...")
    rprint(f"  Mode: [bold]{trace.mode.value}[/bold] | Status: [{status_color}]{trace.status}[/{status_color}]")
    rprint(f"  Steps: {len(trace.steps)}")
    
    # Show step summary
    for step in trace.steps:
        step_icon = {
            'success': '[green]✓[/green]',
            'mocked': '[blue]◎[/blue]',
            'failed': '[red]✗[/red]',
            'skipped': '[dim]○[/dim]',
        }.get(step.status.value, '[dim]?[/dim]')
        
        duration = f" ({step.duration_ms:.1f}ms)" if step.duration_ms else ""
        rprint(f"    {step_icon} {step.glyph}{duration}")
    
    if result.error:
        rprint(f"  [red]Error:[/red] {result.error}")
    
    if result.output:
        rprint(f"  [dim]Output:[/dim]")
        console.print(JSON.from_data(result.output))
    
    rprint("")


@app.command()
def serve(
    host: str = typer.Option("localhost", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8765, "--port", "-p", help="Port to listen on"),
):
    """Start the headless HTTP server for chain execution."""
    from archeon.server.headless_server import serve as start_server
    
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    start_server(str(arcon_path), host, port)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Show version"),
):
    """Archeon - Glyph-based architecture notation for AI-orchestrated development."""
    if version:
        rprint("[bold]Archeon[/bold] version 0.1.0")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        rprint(ctx.get_help())


if __name__ == "__main__":
    app()
