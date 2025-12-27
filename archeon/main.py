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
    get_shape_id,
    list_architectures,
    load_architecture,
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
    frontend: str = typer.Option("vue3", "--frontend", "-f", help="Frontend framework (react/vue/vue3)"),
    backend: str = typer.Option("fastapi", "--backend", "-b", help="Backend framework (fastapi, express)"),
    arch: Optional[str] = typer.Option(None, "--arch", "-a", help="Architecture shape ID (e.g., vue3-fastapi). Overrides frontend/backend."),
    copilot: bool = typer.Option(False, "--copilot", help="Generate .github/copilot-instructions.md for GitHub Copilot"),
    cursor: bool = typer.Option(False, "--cursor", help="Generate .cursorrules for Cursor IDE"),
    windsurf: bool = typer.Option(False, "--windsurf", help="Generate .windsurfrules for Windsurf"),
    cline: bool = typer.Option(False, "--cline", help="Generate .clinerules for Cline/Claude Dev"),
    aider: bool = typer.Option(False, "--aider", help="Generate .aider.conf.yml for Aider"),
    vscode: bool = typer.Option(False, "--vscode", help="Update .vscode/settings.json"),
):
    """Initialize a new Archeon project with client/server structure.
    
    Uses JSON-based architecture shapes (.shape.json) to define the stack.
    
    Examples:
        arc init                           # Vue 3 + FastAPI (default)
        arc init --arch vue3-fastapi       # Explicit shape selection
        arc init -f react -b fastapi       # React + FastAPI
        arc init --arch react-fastapi --copilot  # With GitHub Copilot rules
        arc init --arch react-fastapi --copilot --cline  # Multiple IDE rules
        
    Run 'arc shapes' to list available architecture shapes.
    """
    target = Path(path) if path else Path.cwd()
    archeon_dir = target / "archeon"
    
    # Determine shape from arch option or frontend/backend combo
    if arch:
        shape_id = arch
        shape = load_architecture(shape_id)
        if shape:
            # Extract frontend/backend from shape stack (handles both nested dict and simple string)
            fe = shape.stack.get("frontend", "vue3")
            be = shape.stack.get("backend", "fastapi")
            frontend = fe.get("framework", fe) if isinstance(fe, dict) else fe
            backend = be.get("framework", be) if isinstance(be, dict) else be
        else:
            rprint(f"[red]✗[/red] Unknown architecture shape: {arch}")
            rprint(f"  Run [cyan]arc shapes[/cyan] to list available shapes.")
            raise typer.Exit(1)
    else:
        # Normalize frontend option
        if frontend.lower() in ("vue", "vue3"):
            frontend = "vue3"
        shape_id = get_shape_id(frontend, backend)
    
    # Create base archeon directories
    create_base_directories(archeon_dir)
    
    # Copy reference templates from the archeon package (uses shapes)
    used_shape = copy_templates(archeon_dir, frontend, backend, arch=shape_id)
    
    # Create orchestrator README for AI reference
    create_orchestrator_readme(archeon_dir)
    
    # Create AI provisioning guide
    create_ai_readme(archeon_dir)
    
    if monorepo:
        # Create client and server structures
        create_client_structure(target / "client", frontend)
        create_server_structure(target / "server")
        create_server_files(target / "server", backend)
        
        # Generate design tokens to client/src/tokens for immediate use
        from archeon.orchestrator.TKN_tokens import TokenTransformer
        tokens_source = archeon_dir / "templates" / "_config" / "design-tokens.json"
        tokens_output = target / "client" / "src" / "tokens"
        if tokens_source.exists():
            try:
                transformer = TokenTransformer(tokens_source)
                transformer.generate_all(tokens_output)
            except Exception:
                pass  # Non-fatal: tokens can be generated later with `arc tokens build`
    
    # Create ARCHEON.arcon (also creates ARCHEON.index.json)
    # Pass shape_id to add default ready glyph
    create_arcon_file(archeon_dir, target.name, shape_id=shape_id if used_shape else None)
    
    # Create .archeonrc config file
    create_archeonrc_file(target, monorepo, frontend, backend)
    
    # Create .gitignore
    create_gitignore(target)
    
    # Generate IDE rule files
    # Default behavior: if no IDE flags are set, generate all
    # If any flags are set, only generate those that are True
    ide_files_created = []
    ide_flags = {'copilot': copilot, 'cursor': cursor, 'windsurf': windsurf, 
                 'cline': cline, 'aider': aider, 'vscode': vscode}
    
    # Determine which IDEs to generate
    has_any_flag = any(ide_flags.values())
    if not has_any_flag:
        # No flags set: generate all by default
        ide_flags = {key: True for key in ide_flags}
    
    if any(ide_flags.values()):
        # Load AI rules from template
        rules_file = Path(__file__).parent / "templates" / "_config" / "ai-rules.md"
        if rules_file.exists():
            archeon_rules = rules_file.read_text()
        else:
            archeon_rules = "# Archeon AI Rules\n\nSee archeon/ARCHEON.arcon for architecture.\n"
        
        if ide_flags.get('copilot'):
            github_dir = target / ".github"
            github_dir.mkdir(exist_ok=True)
            (github_dir / "copilot-instructions.md").write_text(f'''# GitHub Copilot Instructions

{archeon_rules}
''')
            ide_files_created.append(".github/copilot-instructions.md")
        
        if ide_flags.get('cursor'):
            (target / ".cursorrules").write_text(f'''# Archeon Project Rules for Cursor

{archeon_rules}
''')
            ide_files_created.append(".cursorrules")
        
        if ide_flags.get('windsurf'):
            (target / ".windsurfrules").write_text(f'''# Archeon Rules for Windsurf

{archeon_rules}
''')
            ide_files_created.append(".windsurfrules")
        
        if ide_flags.get('cline'):
            (target / ".clinerules").write_text(f'''# Archeon Rules for Cline/Claude Dev

{archeon_rules}
''')
            ide_files_created.append(".clinerules")
        
        if ide_flags.get('aider'):
            (target / ".aider.conf.yml").write_text('''# Aider configuration for Archeon project

# Always include these files in context
read:
  - archeon/ARCHEON.arcon
  - archeon/ARCHEON.index.json
  - archeon/templates/_config/ai-rules.md
  - .archeonrc

# Don't auto-commit so user can review
auto-commits: false

# Model instructions
model-settings-yaml: |
  extra_params:
    system: |
      This project uses Archeon glyph notation.
      Read archeon/templates/_config/ai-rules.md for the complete rules.
      
      Key rules:
      - Always read archeon/ARCHEON.arcon before generating code
      - If a feature doesn't exist, write a new chain to ARCHEON.arcon first
      - EVERY file MUST have @archeon:file headers at top with @glyph, @intent, @chain
      - EVERY file MUST use @archeon:section / @archeon:endsection markers
      - ALWAYS update archeon/ARCHEON.index.json when creating files or adding sections
      - The index MUST stay in sync with the code
      - Run arc validate after implementation
''')
            ide_files_created.append(".aider.conf.yml")
        
        if ide_flags.get('vscode'):
            import json
            vscode_dir = target / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
            settings_file = vscode_dir / "settings.json"
            
            settings = {}
            if settings_file.exists():
                try:
                    settings = json.loads(settings_file.read_text())
                except:
                    pass
            
            settings["files.associations"] = settings.get("files.associations", {})
            settings["files.associations"]["*.arcon"] = "markdown"
            settings["search.include"] = settings.get("search.include", {})
            settings["search.include"]["archeon/**"] = True
            settings["github.copilot.chat.codeGeneration.instructions"] = [
                {"text": "Always reference archeon/ARCHEON.arcon for architecture and archeon/templates/_config/ai-rules.md for complete rules. This project uses Archeon glyph notation. Do not invent architecture outside the knowledge graph. EVERY file MUST have @archeon:file headers and @archeon:section markers. ALWAYS update archeon/ARCHEON.index.json when creating files or adding sections."}
            ]
            settings_file.write_text(json.dumps(settings, indent=2))
            ide_files_created.append(".vscode/settings.json")
    
    rprint(f"[green]✓[/green] Initialized Archeon project at [bold]{archeon_dir}[/bold]")
    rprint(f"  Architecture shape: [cyan]{shape_id}[/cyan]")
    rprint(f"  Created {DEFAULT_ARCON}")
    rprint(f"  Created ARCHEON.index.json (semantic index)")
    rprint(f"  Created .archeonrc")
    if used_shape:
        rprint(f"  Copied [cyan]{shape_id}.shape.json[/cyan] (architecture definition)")
    rprint(f"  Created templates from shape ({frontend}/{backend})")
    rprint(f"  Created orchestrator/README.md (glyph reference)")
    rprint(f"  Created AI_README.md (provisioning guide)")
    if ide_files_created:
        for ide_file in ide_files_created:
            rprint(f"  Created [cyan]{ide_file}[/cyan] (AI rules)")
    
    if monorepo:
        rprint(f"  Generated design tokens to client/src/tokens/")
        rprint(f"\n  [bold]Project Structure:[/bold]")
        rprint(f"  [cyan]client/[/cyan]  → {frontend.capitalize()} frontend")
        rprint(f"  [cyan]server/[/cyan]  → {backend.capitalize()} backend (API, models, events)")
        rprint(f"  [cyan]archeon/[/cyan] → Knowledge graph and orchestration")
        
        rprint(f"\n  [bold]Install Dependencies:[/bold]")
        rprint(f"  [cyan]cd client && npm install[/cyan]")
        rprint(f"  [cyan]cd server && pip install -r requirements.txt[/cyan]")
    
    rprint(f"\n  You use glyph notation directly if you like:")
    rprint(f"  [cyan]arc parse \"NED:login => CMP:LoginForm => API:POST/auth => OUT:dashboard\"[/cyan]")
    
    rprint(f"\n  [bold]Next Up:[/bold] [cyan]Talk with your AI![/cyan] Go build something awesome!")


@app.command("shapes")
def shapes_cmd(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed shape information"),
):
    """List available architecture shapes.
    
    Architecture shapes define complete project stacks including:
    - Glyph snippets (CMP, STO, API, MDL, etc.)
    - Directory structures
    - Framework configurations
    - Dependencies
    
    Examples:
        arc shapes           # List all shapes
        arc shapes -v        # Show detailed info
        arc init --arch vue3-fastapi  # Use a specific shape
    """
    from archeon.orchestrator.SHP_shape import list_architectures, load_architecture
    
    available = list_architectures()
    
    if not available:
        rprint("[yellow]No architecture shapes found.[/yellow]")
        rprint("  Shapes should be in archeon/architectures/*.shape.json")
        return
    
    rprint(f"\n[bold]Available Architecture Shapes[/bold]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("ID", style="green")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Tags", style="dim")
    
    for shape_info in available:
        tags = ", ".join(shape_info.get("tags", []))
        table.add_row(
            shape_info["id"],
            shape_info["name"],
            shape_info.get("description", "")[:50],
            tags
        )
    
    console.print(table)
    
    if verbose:
        rprint(f"\n[bold]Shape Details[/bold]")
        for shape_info in available:
            shape = load_architecture(shape_info["id"])
            if shape:
                rprint(f"\n[cyan]{shape.id}[/cyan] - {shape.name} v{shape.version}")
                rprint(f"  Stack: {shape.stack.get('frontend', {}).get('framework', 'N/A')} + {shape.stack.get('backend', {}).get('framework', 'N/A')}")
                rprint(f"  Glyphs: {', '.join(shape.glyphs.keys())}")
    
    rprint(f"\n[dim]Use: arc init --arch <shape-id>[/dim]")


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
    
    # Load shared AI rules from template file
    rules_file = Path(__file__).parent / "templates" / "_config" / "ai-rules.md"
    if rules_file.exists():
        archeon_rules = rules_file.read_text()
    else:
        # Fallback if rules file not found
        archeon_rules = "# Archeon AI Rules\n\nSee archeon/ARCHEON.arcon for architecture.\n"
        rprint(f"[yellow]![/yellow] Rules template not found at {rules_file}, using fallback")
    
    if flags['cursor']:
        cursor_dir = target / ".cursor"
        cursor_dir.mkdir(exist_ok=True)
        
        # Create .cursorrules in project root (where Cursor looks for it)
        cursor_file = target / ".cursorrules"
        cursor_file.write_text(f'''# Archeon Project Rules for Cursor

{archeon_rules}
''')
        
        # Create README in .cursor directory
        (cursor_dir / "README.md").write_text('''# Cursor Configuration for Archeon

## Setup Complete ✓

The `.cursorrules` file in your project root tells Cursor to:
1. Always read `archeon/ARCHEON.arcon` before generating code
2. Write new chains to the knowledge graph for new features
3. Respect the glyph-based architecture
4. Update `archeon/ARCHEON.index.json` when creating files or sections
5. **Run `arc validate` after every code change**

## The Glyph-Code-Test Workflow

Every feature follows this mandatory workflow:

```
1. ADD GLYPH    → Write chain to ARCHEON.arcon
2. WRITE CODE   → Implement each glyph (with headers + sections)
3. UPDATE INDEX → Add glyphs/sections to ARCHEON.index.json
4. RUN VALIDATE → arc validate (REQUIRED)
5. RUN TESTS    → npm test / pytest
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

{archeon_rules}
''')
        
        # Create README for GitHub Copilot setup
        (github_dir / "COPILOT_README.md").write_text('''# GitHub Copilot Configuration for Archeon

## Setup Complete ✓

The `copilot-instructions.md` file tells GitHub Copilot to:
1. Reference `archeon/ARCHEON.arcon` for architecture context
2. Write new chains to the knowledge graph when needed
3. Add @archeon:file headers and @archeon:section markers to all files
4. Update `archeon/ARCHEON.index.json` when creating files or sections
5. Understand glyph notation (NED, CMP, STO, API, etc.)

## How It Works

GitHub Copilot Chat reads `copilot-instructions.md` as project context.
When you ask Copilot to generate code, it will:
- Check the knowledge graph first  
- If feature doesn't exist, ADD A NEW CHAIN first
- Then implement code following the chain
- Update the index with new glyphs and sections

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

{archeon_rules}
''')
        
        # Create README
        (windsurf_dir / "README.md").write_text('''# Windsurf Configuration for Archeon

## Setup Complete ✓

The `.windsurfrules` file tells Windsurf (Codeium) to:
1. Read `archeon/ARCHEON.arcon` before generating code
2. Write new chains when features don't exist
3. Add @archeon:file headers and @archeon:section markers to all files
4. Update `archeon/ARCHEON.index.json` when creating files or sections
5. Follow the glyph-based architecture

## How It Works

Windsurf's Cascade AI reads the rules file for project context.
When generating code, it will:
- Check existing chains in the knowledge graph
- If feature doesn't exist, ADD A NEW CHAIN first
- Then implement following the chain
- Update the index with new glyphs and sections

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

{archeon_rules}
''')
        
        # Create README
        (cline_dir / "README.md").write_text('''# Cline / Claude Dev Configuration for Archeon

## Setup Complete ✓

The `.clinerules` file tells Cline (Claude Dev) to:
1. Read `archeon/ARCHEON.arcon` as first action
2. Write new chains when features don't exist
3. Add @archeon:file headers and @archeon:section markers to all files
4. Update `archeon/ARCHEON.index.json` when creating files or sections
5. Follow glyph-based architecture constraints

## How It Works

Cline reads `.clinerules` for project-specific instructions.
Before any code task, it will:
- Check the knowledge graph for existing chains
- If feature doesn't exist, ADD A NEW CHAIN first
- Then implement following the chain
- Update the index with new glyphs and sections

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
  - archeon/ARCHEON.index.json
  - archeon/templates/_config/ai-rules.md
  - .archeonrc

# Don't auto-commit so user can review
auto-commits: false

# Model instructions
model-settings-yaml: |
  extra_params:
    system: |
      This project uses Archeon glyph notation.
      Read archeon/templates/_config/ai-rules.md for the complete rules.
      
      Key rules:
      - Always read archeon/ARCHEON.arcon before generating code
      - If a feature doesn't exist, write a new chain to ARCHEON.arcon first
      - EVERY file MUST have @archeon:file headers at top with @glyph, @intent, @chain
      - EVERY file MUST use @archeon:section / @archeon:endsection markers
      - ALWAYS update archeon/ARCHEON.index.json when creating files or adding sections
      - The index MUST stay in sync with the code
      - Run arc validate after implementation
''')
        
        # Create README
        (aider_dir / "README.md").write_text('''# Aider Configuration for Archeon

## Setup Complete ✓

The `.aider.conf.yml` configures Aider to:
1. Auto-include `archeon/ARCHEON.arcon` in context
2. Auto-include `archeon/templates/_config/ai-rules.md` for rules
3. Include `.archeonrc` for project config
4. Disable auto-commits for review

## How It Works

When you run `aider`, it will:
- Automatically load the knowledge graph and rules
- If feature doesn't exist, ADD A NEW CHAIN first
- Then implement code following the chain
- Update the index with new glyphs and sections
- Wait for your approval before committing

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
            {"text": "Always reference archeon/ARCHEON.arcon for architecture and archeon/templates/_config/ai-rules.md for complete rules. This project uses Archeon glyph notation. Do not invent architecture outside the knowledge graph. EVERY file MUST have @archeon:file headers and @archeon:section markers. ALWAYS update archeon/ARCHEON.index.json when creating files or adding sections."}
        ]
        
        import json
        settings_file.write_text(json.dumps(settings, indent=2))
        
        # Create README
        (vscode_dir / "ARCHEON_README.md").write_text('''# VS Code Configuration for Archeon

## Setup Complete ✓

The `settings.json` has been updated with:
1. File association: `*.arcon` → Markdown syntax highlighting
2. Search include: `archeon/` folder included in searches  
3. Copilot instructions: Reference knowledge graph and rules for code generation

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

## Key Files

- `archeon/ARCHEON.arcon` - Knowledge graph (chains)
- `archeon/ARCHEON.index.json` - Semantic index (glyph→file mapping)
- `archeon/templates/_config/ai-rules.md` - Complete AI rules

## More Info

- [VS Code Documentation](https://code.visualstudio.com/docs)
- [Archeon README](../README.md)
''')
        created.append(".vscode/settings.json")
        created.append(".vscode/ARCHEON_README.md")
    
    # Always create/update the AI provisioning guide
    archeon_dir = target / "archeon"
    if archeon_dir.exists():
        create_ai_readme(archeon_dir)
        created.append("archeon/AI_README.md")
    
    if created:
        rprint(f"[green]✓[/green] Created AI assistant configurations:")
        for f in created:
            rprint(f"  [cyan]{f}[/cyan]")
        rprint(f"\n[dim]Your IDE AI will now reference the Archeon knowledge graph.[/dim]")
        rprint(f"[dim]Rules loaded from: archeon/templates/_config/ai-rules.md[/dim]")
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
                
                # Ask if user wants to generate code now
                should_gen = Confirm.ask("Generate code now?", default=True)
                if should_gen:
                    from archeon.orchestrator.SPW_spawner import AgentSpawner, ProjectConfig
                    
                    # Load config
                    project_root = arcon_path.parent.parent if arcon_path.parent.name == "archeon" else arcon_path.parent
                    config = ProjectConfig.load(project_root)
                    
                    rprint(f"\n[cyan]Generating code...[/cyan]")
                    spawner = AgentSpawner(
                        output_dir=str(project_root),
                        framework=config.frontend,
                        backend=config.backend,
                        db=config.db,
                        config=config
                    )
                    
                    # Spawn just the glyphs in this chain
                    batch = spawner.spawn_chain(stored.ast)
                    
                    for result in batch.results:
                        if result.status == "success":
                            rprint(f"  [green]✓[/green] {result.glyph} → {result.file_path}")
                        elif result.status == "skipped":
                            rprint(f"  [yellow]○[/yellow] {result.glyph} (skipped)")
                    
                    rprint(f"\n[green]✓ Generated {batch.success_count} files[/green]")
                    rprint(f"[dim]Index updated at ARCHEON.index.json[/dim]")
                    
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


# ═══════════════════════════════════════════════════════════════════════════════
# TOKENS - Design Token Transformation
# ═══════════════════════════════════════════════════════════════════════════════


@app.command()
def tokens(
    action: str = typer.Argument(
        "build",
        help="Action: build (transform tokens), init (create default), validate (check format)"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o",
        help="Output directory for generated files (default: client/src/tokens)"
    ),
    source: Optional[Path] = typer.Option(
        None, "--source", "-s",
        help="Path to design-tokens.json (default: archeon/templates/_config/design-tokens.json)"
    ),
    format_type: str = typer.Option(
        "all", "--format", "-f",
        help="Output format: all, css, tailwind, js"
    ),
):
    """
    Transform design tokens to CSS/Tailwind/JS.
    
    The design tokens follow the W3C DTCG (Design Tokens Community Group) format
    for a single source of truth. This command transforms them into platform-specific
    outputs for use in your application.
    
    Examples:
        archeon tokens           # Build all outputs to client/src/tokens
        archeon tokens build     # Same as above
        archeon tokens init      # Create default design-tokens.json
        archeon tokens validate  # Validate token file format
        archeon tokens build -f css -o ./styles  # Only CSS to custom dir
    """
    from archeon.orchestrator.TKN_tokens import TokenTransformer, generate_css, generate_tailwind_extension, generate_js_tokens
    
    console = Console()
    
    # Determine source path
    if source:
        tokens_path = source
    else:
        # Look in project's archeon config, then package templates
        project_tokens = Path("archeon/_config/design-tokens.json")
        client_tokens = Path("client/src/tokens/design-tokens.json")
        package_tokens = Path(__file__).parent / "templates" / "_config" / "design-tokens.json"
        
        if project_tokens.exists():
            tokens_path = project_tokens
        elif client_tokens.exists():
            tokens_path = client_tokens
        elif package_tokens.exists():
            tokens_path = package_tokens
        else:
            tokens_path = package_tokens  # Will fail with helpful error
    
    # Determine output path
    output_dir = output or Path("client/src/tokens")
    
    if action == "init":
        # Create default design-tokens.json in the project
        init_path = output or Path("archeon/_config")
        init_path.mkdir(parents=True, exist_ok=True)
        dest_file = init_path / "design-tokens.json"
        
        package_tokens = Path(__file__).parent / "templates" / "_config" / "design-tokens.json"
        
        if dest_file.exists():
            if not Confirm.ask(f"[yellow]![/yellow] {dest_file} already exists. Overwrite?"):
                raise typer.Exit(0)
        
        if package_tokens.exists():
            shutil.copy(package_tokens, dest_file)
            rprint(f"[green]✓[/green] Created {dest_file}")
            rprint(f"  Edit this file to customize your design tokens")
            rprint(f"  Then run [cyan]archeon tokens build[/cyan] to generate outputs")
        else:
            rprint(f"[red]✗[/red] Package design-tokens.json not found")
            raise typer.Exit(1)
        return
    
    if action == "validate":
        # Validate the token file format
        try:
            transformer = TokenTransformer(tokens_path)
            metadata = transformer.get_metadata()
            
            rprint(f"[green]✓[/green] Valid design tokens: {tokens_path}")
            
            if metadata:
                rprint(f"\n[bold]Metadata:[/bold]")
                if 'name' in metadata:
                    rprint(f"  Name: {metadata['name']}")
                if 'version' in metadata:
                    rprint(f"  Version: {metadata['version']}")
                if 'description' in metadata:
                    rprint(f"  Description: {metadata['description']}")
            
            # Count tokens by category
            tokens_data = transformer.tokens
            categories = [k for k in tokens_data.keys() if not k.startswith('$')]
            rprint(f"\n[bold]Categories:[/bold] {', '.join(categories)}")
            
        except FileNotFoundError:
            rprint(f"[red]✗[/red] File not found: {tokens_path}")
            raise typer.Exit(1)
        except Exception as e:
            rprint(f"[red]✗[/red] Invalid token file: {e}")
            raise typer.Exit(1)
        return
    
    if action == "build":
        # Transform tokens
        try:
            transformer = TokenTransformer(tokens_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            rprint(f"[cyan]◈[/cyan] Transforming tokens from: {tokens_path}")
            rprint(f"[cyan]◈[/cyan] Output directory: {output_dir}\n")
            
            if format_type == "all":
                generated = transformer.generate_all(output_dir)
                for path in generated:
                    rprint(f"  [green]✓[/green] Generated {path.name}")
            elif format_type == "css":
                css_path = output_dir / "tokens.css"
                css_path.write_text(generate_css(transformer.tokens))
                rprint(f"  [green]✓[/green] Generated {css_path.name}")
            elif format_type == "tailwind":
                tw_path = output_dir / "tokens.tailwind.js"
                tw_path.write_text(generate_tailwind_extension(transformer.tokens))
                rprint(f"  [green]✓[/green] Generated {tw_path.name}")
            elif format_type == "js":
                js_path = output_dir / "tokens.js"
                js_path.write_text(generate_js_tokens(transformer.tokens))
                rprint(f"  [green]✓[/green] Generated {js_path.name}")
            else:
                rprint(f"[red]✗[/red] Unknown format: {format_type}")
                rprint(f"  Available: all, css, tailwind, js")
                raise typer.Exit(1)
            
            rprint(f"\n[green]✓[/green] Token transformation complete!")
            rprint(f"  Import tokens in your app:")
            rprint(f'    [dim]import "./tokens/tokens.css"[/dim]')
            rprint(f'    [dim]import {{ themeExtend }} from "./tokens/tokens.tailwind.js"[/dim]')
            
        except FileNotFoundError:
            rprint(f"[red]✗[/red] Design tokens not found: {tokens_path}")
            rprint(f"  Run [cyan]archeon tokens init[/cyan] to create default tokens")
            raise typer.Exit(1)
        except Exception as e:
            rprint(f"[red]✗[/red] Error transforming tokens: {e}")
            raise typer.Exit(1)
        return
    
    rprint(f"[red]✗[/red] Unknown action: {action}")
    rprint(f"  Available actions: build, init, validate")
    raise typer.Exit(1)


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


@app.command()
def index(
    action: str = typer.Argument("build", help="Action: build, show, scan, check, inject, infer, code"),
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Directory or file to scan"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    glyph: Optional[str] = typer.Option(None, "--glyph", "-g", help="Glyph for show/inject"),
    intent: Optional[str] = typer.Option(None, "--intent", "-i", help="Intent for inject"),
    chain: Optional[str] = typer.Option(None, "--chain", "-c", help="Chain reference for inject"),
):
    """Build and manage the semantic section index (ARCHEON.index.json).
    
    The index enables AI-native code navigation by tracking:
    - Which file each glyph lives in
    - What sections exist in each file
    - Intent metadata for each glyph
    
    Actions:
    - build: Scan files and rebuild ARCHEON.index.json
    - show: Display the current index
    - scan: Scan a single file for sections
    - check: Find files that are missing @archeon:file headers
    - inject: Add @archeon:file header to an existing file
    - infer: Auto-index arbitrary codebase by detecting file types and relationships
    - code: ⭐ One-command setup - creates archeon/, index, arcon, and all IDE rules
    """
    from archeon.orchestrator.IDX_index import (
        IndexBuilder,
        build_index,
        load_index,
        format_index_for_prompt,
    )
    from archeon.orchestrator.SCN_scanner import (
        scan_file,
        validate_sections,
        find_files_missing_headers,
        inject_header,
    )
    
    project_root = Path(path) if path and Path(path).is_dir() else Path.cwd()
    
    if action == "build":
        # Build the index
        index_path = build_index(str(project_root), output)
        rprint(f"[green]✓[/green] Built index at [bold]{index_path}[/bold]")
        
        # Show summary
        idx = load_index(str(project_root))
        rprint(f"  Indexed [cyan]{len(idx.entries)}[/cyan] glyphs")
        
        if idx.entries:
            table = Table(title="Indexed Glyphs", show_lines=True)
            table.add_column("Glyph", style="cyan")
            table.add_column("File", style="green")
            table.add_column("Sections")
            
            for g, entry in sorted(idx.entries.items()):
                table.add_row(g, entry.file, ", ".join(entry.sections))
            
            console.print(table)
    
    elif action == "show":
        # Show the index
        idx = load_index(str(project_root))
        
        if not idx.entries:
            rprint("[yellow]No index found.[/yellow] Run [cyan]archeon index build[/cyan] first.")
            raise typer.Exit(1)
        
        if glyph:
            # Show specific glyph
            entry = idx.entries.get(glyph)
            if not entry:
                rprint(f"[red]✗[/red] Glyph [cyan]{glyph}[/cyan] not found in index")
                raise typer.Exit(1)
            
            rprint(Panel(
                f"[bold]File:[/bold] {entry.file}\n"
                f"[bold]Intent:[/bold] {entry.intent}\n"
                f"[bold]Chain:[/bold] {entry.chain}\n"
                f"[bold]Sections:[/bold] {', '.join(entry.sections)}",
                title=f"[cyan]{glyph}[/cyan]",
            ))
        else:
            # Show all - formatted for LLM prompt
            rprint(Panel(
                format_index_for_prompt(idx),
                title="Semantic Index",
            ))
    
    elif action == "scan":
        # Scan a single file
        if not path:
            rprint("[red]✗[/red] --path required for scan action")
            raise typer.Exit(1)
        
        scanned = scan_file(path)
        errors = validate_sections(scanned)
        
        if not scanned.is_archeon_file:
            rprint(f"[yellow]⚠[/yellow] {path} is not an Archeon file (no @archeon:file header)")
            raise typer.Exit(1)
        
        rprint(Panel(
            f"[bold]Glyph:[/bold] {scanned.header.glyph}\n"
            f"[bold]Intent:[/bold] {scanned.header.intent}\n"
            f"[bold]Chain:[/bold] {scanned.header.chain}\n"
            f"[bold]Sections:[/bold] {', '.join(s.name for s in scanned.sections)}",
            title=f"Scanned: [cyan]{path}[/cyan]",
        ))
        
        if errors:
            rprint("\n[yellow]Warnings:[/yellow]")
            for err in errors:
                rprint(f"  [yellow]⚠[/yellow] {err}")
    
    elif action == "check":
        # Find files missing headers
        rprint(f"[cyan]Checking for files missing @archeon:file headers...[/cyan]\n")
        
        missing = find_files_missing_headers(str(project_root))
        
        if not missing:
            rprint("[green]✓[/green] All files in Archeon paths have headers!")
        else:
            rprint(f"[yellow]⚠[/yellow] Found [bold]{len(missing)}[/bold] files without @archeon:file headers:\n")
            for f in missing:
                rel_path = Path(f).relative_to(project_root) if project_root in Path(f).parents else f
                rprint(f"  [yellow]•[/yellow] {rel_path}")
            
            rprint(f"\n[bold]To add headers, use:[/bold]")
            rprint(f"  [cyan]arc index inject --path <file> --glyph <GLYPH> --intent '<intent>' --chain '<chain>'[/cyan]")
    
    elif action == "infer":
        # Auto-infer glyphs from arbitrary codebase
        from archeon.orchestrator.IDX_orchestrator import IndexOrchestrator
        
        infer_path = Path(path) if path else Path.cwd()
        if not infer_path.exists():
            rprint(f"[red]✗[/red] Path not found: {infer_path}")
            raise typer.Exit(1)
        
        rprint(f"[cyan]🔍 Indexing codebase: {infer_path}[/cyan]\n")
        
        try:
            orchestrator = IndexOrchestrator(
                str(infer_path),
                output_file=output
            )
            index = orchestrator.run(verbose=True)
            
            # Show statistics
            stats = orchestrator.get_stats()
            rprint(f"\n[green]✓[/green] Indexing complete!")
            rprint(f"\n[bold]Tech Stack Detected:[/bold]")
            rprint(f"  Frontend: {stats['tech_stack']['frontend'] or '(not detected)'}")
            rprint(f"  Backend: {stats['tech_stack']['backend'] or '(not detected)'}")
            rprint(f"\n[bold]Glyph Coverage:[/bold]")
            
            coverage = stats.get('glyph_coverage', {})
            if coverage:
                for glyph in sorted(coverage.keys()):
                    count = coverage[glyph]
                    rprint(f"  {glyph}: {count} file{'s' if count != 1 else ''}")
            
            rprint(f"\n[cyan]Index written to: {stats['output_file']}[/cyan]")
            
        except Exception as e:
            rprint(f"[red]✗[/red] Error during indexing: {e}")
            import traceback
            rprint(f"[dim]{traceback.format_exc()}[/dim]")
            raise typer.Exit(1)
    
    elif action == "code":
        # ⭐ ONE-COMMAND SETUP: Prep entire codebase for Archeon
        from archeon.orchestrator.IDX_orchestrator import IndexOrchestrator
        
        project_root = Path(path) if path else Path.cwd()
        if not project_root.exists():
            rprint(f"[red]✗[/red] Path not found: {project_root}")
            raise typer.Exit(1)
        
        project_name = project_root.name
        
        rprint(Panel.fit(
            "[bold cyan]⭐ Archeon One-Command Setup[/bold cyan]\n\n"
            "This will prepare your existing codebase for Archeon:\n"
            "  1. Create archeon/ directory\n"
            "  2. Scan & classify all files to glyphs\n"
            "  3. Generate ARCHEON.index.json\n"
            "  4. Generate ARCHEON.arcon knowledge graph\n"
            "  5. Create AI rules for all IDEs\n",
            border_style="cyan"
        ))
        
        try:
            # Step 1: Create archeon directory
            archeon_dir = project_root / "archeon"
            archeon_dir.mkdir(exist_ok=True)
            rprint(f"\n[green]✓[/green] Created [bold]archeon/[/bold] directory")
            
            # Step 2 & 3: Run the index inference
            rprint(f"\n[cyan]🔍 Scanning codebase...[/cyan]")
            orchestrator = IndexOrchestrator(
                str(project_root),
                output_file=str(archeon_dir / "ARCHEON.index.json")
            )
            index = orchestrator.run(verbose=False)
            
            stats = orchestrator.get_stats()
            coverage = stats.get('glyph_coverage', {})
            total_files = stats.get('total_files', 0)
            
            rprint(f"[green]✓[/green] Indexed [bold]{total_files}[/bold] files")
            if coverage:
                glyph_summary = ", ".join(f"{g}:{c}" for g, c in sorted(coverage.items()))
                rprint(f"    Glyphs: {glyph_summary}")
            
            # Step 4: Generate ARCHEON.arcon from inferred chains
            arcon_path = archeon_dir / "ARCHEON.arcon"
            
            # Get structural chains from imports
            structural_chains = orchestrator.inferrer.infer_chains()
            
            # Get data flow chains (STO -> API connections)
            data_flow_chains = orchestrator.data_flow_analyzer.get_data_flow_chains()
            
            # Build arcon content
            frontend_fw = stats['tech_stack'].get('frontend') or 'unknown'
            backend_fw = stats['tech_stack'].get('backend') or 'unknown'
            state_mgmt = stats['tech_stack'].get('state_management') or 'unknown'
            
            arcon_content = f'''# Archeon Knowledge Graph
# Version: 2.0
# Project: {project_name}
# Generated by: arc index code

# === DETECTED STACK ===
# Frontend: {frontend_fw}
# Backend: {backend_fw}
# State Management: {state_mgmt}

# === ORCHESTRATOR LAYER ===
ORC:main :: PRS:glyph :: VAL:chain :: SPW:agent :: TST:e2e
GRF:domain :: ORC:main

# === AGENT CHAINS ===
# Add chains using: arc parse "<chain>"

'''
            
            # Group glyphs by type for intelligent chain generation
            api_glyphs = {}
            store_glyphs = {}
            component_glyphs = {}
            model_glyphs = {}
            function_glyphs = {}
            view_glyphs = {}
            
            for qualified_name, glyph_info in index.glyphs.items():
                # Extract glyph type from qualified_name (e.g., "API:GET/" -> "API")
                glyph_type = qualified_name.split(':')[0] if ':' in qualified_name else ''
                if glyph_type == 'API':
                    api_glyphs[qualified_name] = glyph_info
                elif glyph_type == 'STO':
                    store_glyphs[qualified_name] = glyph_info
                elif glyph_type == 'CMP':
                    component_glyphs[qualified_name] = glyph_info
                elif glyph_type == 'MDL':
                    model_glyphs[qualified_name] = glyph_info
                elif glyph_type == 'FNC':
                    function_glyphs[qualified_name] = glyph_info
                elif glyph_type == 'V':
                    view_glyphs[qualified_name] = glyph_info
            
            # Generate proper chains from data flow analysis
            chains_generated = []
            
            # Build chains from Store -> API connections
            if orchestrator.data_flow_analyzer.data_flows:
                arcon_content += "# Detected API Flows\n"
                
                # Group by store
                store_flows = {}
                for flow in orchestrator.data_flow_analyzer.data_flows:
                    store = flow.source_glyph
                    if store not in store_flows:
                        store_flows[store] = []
                    store_flows[store].append(flow)
                
                for store_name, flows in store_flows.items():
                    for flow in flows:
                        # Extract operation name from API path
                        api_path = flow.target_glyph.replace('API:', '')
                        method_path = api_path.split('/')
                        operation = method_path[-1] if len(method_path) > 1 else 'action'
                        
                        # Determine outcome based on method
                        if 'POST' in flow.target_glyph:
                            outcome = 'success'
                            errors = ['validation.invalid', 'server.error']
                        elif 'PUT' in flow.target_glyph or 'PATCH' in flow.target_glyph:
                            outcome = 'updated'
                            errors = ['notFound', 'validation.invalid', 'server.error']
                        elif 'DELETE' in flow.target_glyph:
                            outcome = 'deleted'
                            errors = ['notFound', 'server.error']
                        else:  # GET
                            outcome = 'loaded'
                            errors = ['notFound', 'server.error']
                        
                        # Build full chain with error paths
                        chain = f"@v1 NED:{operation} => {store_name} => {flow.target_glyph}"
                        arcon_content += f"{chain}\n"
                        for err in errors:
                            arcon_content += f"    -> ERR:{err}\n"
                        arcon_content += f"    => OUT:{outcome}\n"
                        arcon_content += "\n"
                        chains_generated.append(chain)
            
            # Generate standalone API chains for endpoints not connected to stores
            orphan_apis = [api for api in api_glyphs.keys() 
                          if not any(flow.target_glyph == api for flow in orchestrator.data_flow_analyzer.data_flows)]
            
            if orphan_apis:
                arcon_content += "# Standalone API Endpoints\n"
                for api_name in orphan_apis:
                    api_info = api_glyphs[api_name]
                    endpoint = api_info.get('endpoint', {})
                    method = endpoint.get('method', 'GET')
                    path = endpoint.get('path', '/')
                    operation = path.split('/')[-1] if path != '/' else 'root'
                    
                    if method == 'POST':
                        chain = f"@v1 NED:{operation} => {api_name}\n    -> ERR:validation.invalid\n    -> ERR:server.error\n    => OUT:created\n"
                    elif method in ('PUT', 'PATCH'):
                        chain = f"@v1 NED:{operation} => {api_name}\n    -> ERR:notFound\n    -> ERR:server.error\n    => OUT:updated\n"
                    elif method == 'DELETE':
                        chain = f"@v1 NED:{operation} => {api_name}\n    -> ERR:notFound\n    -> ERR:server.error\n    => OUT:deleted\n"
                    else:  # GET
                        chain = f"@v1 NED:{operation} => {api_name}\n    -> ERR:notFound\n    => OUT:loaded\n"
                    
                    arcon_content += chain
                    arcon_content += "\n"
                    chains_generated.append(api_name)
            
            # Add component definitions
            if component_glyphs:
                arcon_content += "# Components\n"
                for cmp_name in sorted(component_glyphs.keys()):
                    arcon_content += f"@v1 {cmp_name}\n"
                    chains_generated.append(cmp_name)
                arcon_content += "\n"
            
            # Add view definitions
            if view_glyphs:
                arcon_content += "# Views\n"
                for v_name in sorted(view_glyphs.keys()):
                    arcon_content += f"@v1 {v_name}\n"
                    chains_generated.append(v_name)
                arcon_content += "\n"
            
            # Add store definitions with their model connections
            if store_glyphs:
                arcon_content += "# Stores\n"
                for sto_name in sorted(store_glyphs.keys()):
                    arcon_content += f"@v1 {sto_name}\n"
                    chains_generated.append(sto_name)
                arcon_content += "\n"
            
            # Add model definitions
            if model_glyphs:
                arcon_content += "# Models\n"
                for mdl_name in sorted(model_glyphs.keys()):
                    arcon_content += f"@v1 {mdl_name}\n"
                    chains_generated.append(mdl_name)
                arcon_content += "\n"
            
            # Add function definitions
            if function_glyphs:
                arcon_content += "# Functions\n"
                for fnc_name in sorted(function_glyphs.keys()):
                    arcon_content += f"@v1 {fnc_name}\n"
                    chains_generated.append(fnc_name)
                arcon_content += "\n"
            
            if not chains_generated:
                arcon_content += "# No glyphs detected yet.\n"
                arcon_content += "# Add chains using: arc parse \"NED:feature => CMP:Component => OUT:result\"\n"
            
            arcon_path.write_text(arcon_content)
            all_chains = chains_generated
            rprint(f"[green]✓[/green] Generated [bold]ARCHEON.arcon[/bold] with {len(all_chains)} chains")
            
            # Step 5: Generate ALL IDE rules
            rprint(f"\n[cyan]📝 Generating IDE configurations...[/cyan]")
            
            # Load shared AI rules
            rules_file = Path(__file__).parent / "templates" / "_config" / "ai-rules.md"
            if rules_file.exists():
                archeon_rules = rules_file.read_text()
            else:
                archeon_rules = "# Archeon AI Rules\n\nSee archeon/ARCHEON.arcon for architecture.\n"
            
            # Cursor
            cursor_dir = project_root / ".cursor"
            cursor_dir.mkdir(exist_ok=True)
            (project_root / ".cursorrules").write_text(f"# Archeon Project Rules for Cursor\n\n{archeon_rules}\n")
            rprint(f"  [green]✓[/green] .cursorrules")
            
            # Windsurf
            (project_root / ".windsurfrules").write_text(f"# Archeon Project Rules for Windsurf\n\n{archeon_rules}\n")
            rprint(f"  [green]✓[/green] .windsurfrules")
            
            # Cline
            (project_root / ".clinerules").write_text(f"# Archeon Project Rules for Cline\n\n{archeon_rules}\n")
            rprint(f"  [green]✓[/green] .clinerules")
            
            # GitHub Copilot
            github_dir = project_root / ".github"
            github_dir.mkdir(exist_ok=True)
            (github_dir / "copilot-instructions.md").write_text(f"# Archeon Project Rules for GitHub Copilot\n\n{archeon_rules}\n")
            rprint(f"  [green]✓[/green] .github/copilot-instructions.md")
            
            # Aider
            (project_root / ".aider.conf.yml").write_text(f'''# Archeon configuration for Aider
read:
  - archeon/ARCHEON.arcon
  - archeon/ARCHEON.index.json
''')
            rprint(f"  [green]✓[/green] .aider.conf.yml")
            
            # VS Code settings
            vscode_dir = project_root / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
            import json
            vscode_settings_path = vscode_dir / "settings.json"
            vscode_settings = {}
            if vscode_settings_path.exists():
                try:
                    vscode_settings = json.loads(vscode_settings_path.read_text())
                except:
                    pass
            vscode_settings["files.associations"] = vscode_settings.get("files.associations", {})
            vscode_settings["files.associations"]["*.arcon"] = "markdown"
            vscode_settings_path.write_text(json.dumps(vscode_settings, indent=2))
            rprint(f"  [green]✓[/green] .vscode/settings.json")
            
            # Final summary
            data_flow_count = len(orchestrator.data_flow_analyzer.data_flows)
            rprint(Panel.fit(
                f"[bold green]✅ Archeon setup complete![/bold green]\n\n"
                f"[bold]Project:[/bold] {project_name}\n"
                f"[bold]Files indexed:[/bold] {total_files}\n"
                f"[bold]Chains detected:[/bold] {len(all_chains)} ({len(structural_chains)} structural, {len(data_flow_chains)} data flow)\n"
                f"[bold]Data flows:[/bold] {data_flow_count} (Store → API connections)\n\n"
                f"[bold]Created:[/bold]\n"
                f"  • archeon/ARCHEON.arcon\n"
                f"  • archeon/ARCHEON.index.json\n"
                f"  • .cursorrules, .windsurfrules, .clinerules\n"
                f"  • .github/copilot-instructions.md\n"
                f"  • .aider.conf.yml, .vscode/settings.json\n\n"
                f"[dim]Your AI assistant now understands your architecture![/dim]",
                border_style="green"
            ))
            
        except Exception as e:
            rprint(f"[red]✗[/red] Error during setup: {e}")
            import traceback
            rprint(f"[dim]{traceback.format_exc()}[/dim]")
            raise typer.Exit(1)
    
    elif action == "inject":
        # Inject header into a file
        if not path:
            rprint("[red]✗[/red] --path required for inject action")
            raise typer.Exit(1)
        if not glyph:
            rprint("[red]✗[/red] --glyph required for inject action")
            rprint("  Example: --glyph CMP:LoginForm")
            raise typer.Exit(1)
        
        file_path = Path(path)
        if not file_path.exists():
            rprint(f"[red]✗[/red] File not found: {path}")
            raise typer.Exit(1)
        
        # Default intent and chain if not provided
        intent_str = intent or f"{glyph.split(':')[1]} implementation"
        chain_str = chain or glyph
        
        # Inject the header
        new_content = inject_header(str(file_path), glyph, intent_str, chain_str)
        file_path.write_text(new_content)
        
        rprint(f"[green]✓[/green] Injected header into [bold]{path}[/bold]")
        rprint(f"  [bold]Glyph:[/bold] {glyph}")
        rprint(f"  [bold]Intent:[/bold] {intent_str}")
        rprint(f"  [bold]Chain:[/bold] {chain_str}")
        rprint(f"\n[cyan]Run 'arc index build' to update the index[/cyan]")
    
    else:
        rprint(f"[red]✗[/red] Unknown action: {action}")
        rprint(f"  Available actions: build, show, scan, check, inject, infer, code")
        raise typer.Exit(1)


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
