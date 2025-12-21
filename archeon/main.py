"""
Archeon CLI - Main entry point

Glyph-based architecture notation system for AI-orchestrated software development.

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


@app.command()
def init(
    path: Optional[str] = typer.Argument(None, help="Directory to initialize"),
):
    """Initialize a new Archeon project."""
    target = Path(path) if path else Path.cwd()
    archeon_dir = target / "archeon"
    
    # Create directories
    dirs = [
        archeon_dir,
        archeon_dir / "orchestrator",
        archeon_dir / "agents",
        archeon_dir / "templates" / "CMP",
        archeon_dir / "templates" / "STO",
        archeon_dir / "templates" / "API",
        archeon_dir / "templates" / "MDL",
        archeon_dir / "templates" / "FNC",
        archeon_dir / "templates" / "EVT",
        archeon_dir / "tests",
        archeon_dir / "utils",
        archeon_dir / "config",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        init_file = d / "__init__.py"
        if not init_file.exists() and d.name not in ("templates", "CMP", "STO", "API", "MDL", "FNC", "EVT"):
            init_file.write_text(f"# Archeon {d.name.title()}\n")
    
    # Create ARCHEON.arcon
    arcon_path = archeon_dir / DEFAULT_ARCON
    if not arcon_path.exists():
        arcon_path.write_text(
            "# Archeon Knowledge Graph\n"
            "# Version: 2.0\n"
            f"# Project: {target.name}\n"
            "\n"
            "# === ORCHESTRATOR LAYER ===\n"
            "ORC:main :: PRS:glyph :: VAL:chain :: SPW:agent :: TST:e2e\n"
            "GRF:domain :: ORC:main\n"
            "\n"
            "# === AGENT CHAINS ===\n"
            "# Add chains using: archeon parse \"<chain>\"\n"
        )
    
    # Create .archeonrc config file
    rc_path = target / ".archeonrc"
    if not rc_path.exists():
        rc_path.write_text(
            "# Archeon Configuration\n"
            "frontend: react\n"
            "backend: fastapi\n"
            "db: mongo\n"
            "output_dir: ./src\n"
        )
    
    rprint(f"[green]✓[/green] Initialized Archeon project at [bold]{archeon_dir}[/bold]")
    rprint(f"  Created {DEFAULT_ARCON}")
    rprint(f"  Created .archeonrc")
    rprint(f"\n  Next: [cyan]archeon parse \"NED:example => TSK:action => OUT:result\"[/cyan]")


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
    frontend: str = typer.Option("react", "--frontend", "-f", help="Frontend framework"),
    backend: str = typer.Option("fastapi", "--backend", "-b", help="Backend framework"),
    db: str = typer.Option("mongo", "--db", "-d", help="Database type"),
    output: str = typer.Option(".", "--output", "-o", help="Output directory"),
    force: bool = typer.Option(False, "--force", help="Force regeneration of all glyphs"),
):
    """Generate code for all unresolved glyphs."""
    from archeon.orchestrator.SPW_spawner import AgentSpawner
    
    arcon_path = get_arcon_path()
    
    if not arcon_path.exists():
        rprint(f"[red]✗[/red] No {DEFAULT_ARCON} found. Run [cyan]archeon init[/cyan] first.")
        raise typer.Exit(1)
    
    graph = load_graph(str(arcon_path))
    unresolved = graph.get_unresolved_glyphs()
    
    if not unresolved and not force:
        rprint("[green]✓[/green] All glyphs already resolved - nothing to generate")
        return
    
    rprint(f"[cyan]Generating code for {len(unresolved)} glyph(s)...[/cyan]")
    rprint(f"  Frontend: {frontend}, Backend: {backend}, DB: {db}")
    rprint(f"  Output: {output}")
    
    # Create spawner with appropriate framework per glyph type
    spawner = AgentSpawner(
        output_dir=output, 
        framework=frontend,
        backend=backend,
        db=db
    )
    
    # Process all unresolved glyphs
    batch = spawner.spawn_all(graph, force=force)
    
    # Display results
    table = Table(title="Generation Results")
    table.add_column("Glyph", style="cyan")
    table.add_column("File", style="green")
    table.add_column("Status")
    
    for result in batch.results:
        status_style = {
            "success": "[green]✓[/green]",
            "skipped": "[yellow]○[/yellow]",
            "error": "[red]✗[/red]",
        }.get(result.status, result.status)
        
        file_display = result.file_path or "-"
        if result.error:
            file_display = f"[red]{result.error}[/red]"
        
        table.add_row(result.glyph, file_display, status_style)
    
    console.print(table)
    
    rprint(f"\n[green]✓ Generated:[/green] {batch.success_count}")
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


@app.command()
def intent(
    text: str = typer.Argument(..., help="Natural language description"),
    auto_errors: bool = typer.Option(False, "--auto-errors", help="Auto-suggest error paths"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Parse from markdown file instead"),
):
    """Parse natural language into proposed chains."""
    from archeon.orchestrator.INT_intent import parse_intent, parse_markdown, suggest_errors
    
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
    
    for i, proposal in enumerate(result.proposals, 1):
        confidence_style = {
            'high': '[green]HIGH[/green]',
            'medium': '[yellow]MEDIUM[/yellow]',
            'low': '[red]LOW[/red]',
        }.get(proposal.confidence.value, proposal.confidence.value)
        
        rprint(Panel.fit(
            f"[bold cyan]{proposal.chain}[/bold cyan]\n\n"
            f"Confidence: {confidence_style}\n"
            f"Reasoning:\n" + "\n".join(f"  • {r}" for r in proposal.reasoning),
            title=f"Proposal {i}"
        ))
        
        # Show suggested errors
        if auto_errors or proposal.suggested_errors:
            errors = proposal.suggested_errors or suggest_errors(proposal.chain)
            if errors:
                rprint("\n[yellow]Suggested error paths:[/yellow]")
                for err in errors:
                    rprint(f"  [dim]→[/dim] {err}")
        
        # Prompt for action
        if arcon_path.exists():
            rprint("")
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
                    
            elif action == "e":  # Edit
                edited = Prompt.ask("Edit chain", default=proposal.chain)
                try:
                    graph = load_graph(str(arcon_path))
                    stored = graph.add_chain(edited)
                    graph.save()
                    rprint(f"[green]✓[/green] Added edited chain to graph")
                except Exception as e:
                    rprint(f"[red]✗[/red] Failed to add: {e}")
                    
            elif action == "s":  # Suggest errors
                errors = suggest_errors(proposal.chain)
                for err in errors:
                    error_chain = f"{proposal.chain} -> {err} => OUT:error"
                    rprint(f"  [cyan]{error_chain}[/cyan]")
                    
            else:  # Reject
                rprint("[dim]Rejected[/dim]")


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
