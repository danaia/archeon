"""
GRF_exporter.py - Archeon Graph Export

Export knowledge graph to DOT (Graphviz), JSON, and PNG formats.
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from archeon.orchestrator.GRF_graph import KnowledgeGraph, StoredChain
from archeon.orchestrator.PRS_parser import ChainAST, GlyphNode, Edge
from archeon.config.legend import GLYPH_LEGEND, EDGE_TYPES


# DOT color scheme by glyph type
DOT_COLORS = {
    'NED': '#9b59b6',    # Purple
    'TSK': '#3498db',    # Blue
    'V': '#5c6bc0',      # Indigo
    'CMP': '#00bcd4',    # Cyan
    'STO': '#4caf50',    # Green
    'FNC': '#ffc107',    # Yellow
    'EVT': '#ff9800',    # Orange
    'API': '#f44336',    # Red
    'MDL': '#795548',    # Brown
    'OUT': '#607d8b',    # Gray
    'ERR': '#e91e63',    # Magenta
    'ORC': '#9e9e9e',    # Gray
    'PRS': '#9e9e9e',
    'VAL': '#9e9e9e',
    'SPW': '#9e9e9e',
    'TST': '#9e9e9e',
    'GRF': '#9e9e9e',
}

# DOT node shapes by glyph type
DOT_SHAPES = {
    'NED': 'ellipse',
    'TSK': 'box',
    'V': 'folder',
    'CMP': 'component',
    'STO': 'cylinder',
    'FNC': 'diamond',
    'EVT': 'hexagon',
    'API': 'parallelogram',
    'MDL': 'box3d',
    'OUT': 'oval',
    'ERR': 'triangle',
    'ORC': 'octagon',
    'PRS': 'octagon',
    'VAL': 'octagon',
    'SPW': 'octagon',
    'TST': 'octagon',
    'GRF': 'octagon',
}

# DOT edge styles by operator
DOT_EDGE_STYLES = {
    '=>': {'style': 'solid', 'color': '#333333', 'label': ''},
    '->': {'style': 'solid', 'color': '#e91e63', 'arrowhead': 'vee', 'label': ''},
    '~>': {'style': 'dashed', 'color': '#4caf50', 'label': 'reactive'},
    '!>': {'style': 'dotted', 'color': '#ff9800', 'label': 'side-effect'},
    '::': {'style': 'solid', 'color': '#9e9e9e', 'label': 'internal'},
    '@': {'style': 'dashed', 'color': '#5c6bc0', 'arrowhead': 'none', 'label': 'contains'},
}


@dataclass
class ExportResult:
    """Result of export operation."""
    success: bool
    path: str
    format: str
    error: str = ""
    node_count: int = 0
    edge_count: int = 0


def export_dot(graph: KnowledgeGraph, output_path: Optional[str] = None) -> str:
    """
    Export graph to DOT (Graphviz) format.
    
    Args:
        graph: Knowledge graph to export
        output_path: Optional path to write file
        
    Returns:
        DOT format string
    """
    lines = [
        'digraph Archeon {',
        '  rankdir=LR;',
        '  node [fontname="Helvetica", fontsize=10];',
        '  edge [fontname="Helvetica", fontsize=8];',
        '',
    ]
    
    # Collect all nodes and edges
    nodes: dict[str, GlyphNode] = {}
    edges: list[tuple[str, str, str]] = []  # (source, target, operator)
    
    for stored in graph.chains:
        for node in stored.ast.nodes:
            nodes[node.qualified_name] = node
        
        for edge in stored.ast.edges:
            # Edges use indices, convert to qualified names
            source = stored.ast.nodes[edge.source_idx].qualified_name
            target = stored.ast.nodes[edge.target_idx].qualified_name
            edges.append((source, target, edge.operator))
    
    # Generate node definitions
    lines.append('  // Nodes')
    for qualified_name, node in sorted(nodes.items()):
        prefix = node.prefix
        color = DOT_COLORS.get(prefix, '#999999')
        shape = DOT_SHAPES.get(prefix, 'box')
        
        # Escape label
        label = qualified_name.replace('"', '\\"')
        
        # Add modifiers to label
        if node.modifiers:
            label += f"\\n[{', '.join(node.modifiers)}]"
        
        lines.append(
            f'  "{qualified_name}" ['
            f'label="{label}", '
            f'shape="{shape}", '
            f'style="filled", '
            f'fillcolor="{color}", '
            f'fontcolor="white"'
            f'];'
        )
    
    lines.append('')
    lines.append('  // Edges')
    
    # Generate edge definitions
    seen_edges = set()
    for source, target, operator in edges:
        edge_key = (source, target, operator)
        if edge_key in seen_edges:
            continue
        seen_edges.add(edge_key)
        
        style_info = DOT_EDGE_STYLES.get(operator, DOT_EDGE_STYLES['=>'])
        
        attrs = [f'style="{style_info.get("style", "solid")}"']
        attrs.append(f'color="{style_info.get("color", "#333333")}"')
        
        if style_info.get('label'):
            attrs.append(f'label="{style_info["label"]}"')
        
        if style_info.get('arrowhead'):
            attrs.append(f'arrowhead="{style_info["arrowhead"]}"')
        
        lines.append(f'  "{source}" -> "{target}" [{", ".join(attrs)}];')
    
    lines.append('}')
    
    dot_content = '\n'.join(lines)
    
    if output_path:
        Path(output_path).write_text(dot_content)
    
    return dot_content


def export_json(graph: KnowledgeGraph, output_path: Optional[str] = None) -> dict:
    """
    Export graph to JSON format.
    
    Args:
        graph: Knowledge graph to export
        output_path: Optional path to write file
        
    Returns:
        JSON-serializable dict
    """
    nodes = []
    edges = []
    chains = []
    
    # Collect unique nodes
    seen_nodes = set()
    for stored in graph.chains:
        chain_nodes = []
        for node in stored.ast.nodes:
            if node.qualified_name not in seen_nodes:
                seen_nodes.add(node.qualified_name)
                node_data = {
                    'id': node.qualified_name,
                    'prefix': node.prefix,
                    'name': node.name,
                    'modifiers': node.modifiers,
                    'args': node.args,
                    'layer': GLYPH_LEGEND.get(node.prefix, {}).get('layer', 'unknown'),
                }
                nodes.append(node_data)
            chain_nodes.append(node.qualified_name)
        
        # Collect edges
        for edge in stored.ast.edges:
            # Edges use indices, convert to qualified names
            source = stored.ast.nodes[edge.source_idx].qualified_name
            target = stored.ast.nodes[edge.target_idx].qualified_name
            edge_data = {
                'source': source,
                'target': target,
                'operator': edge.operator,
                'type': EDGE_TYPES.get(edge.operator, {}).get('name', 'unknown'),
            }
            edges.append(edge_data)
        
        # Chain metadata
        chain_data = {
            'raw': stored.ast.raw,
            'version': stored.ast.version,
            'framework': stored.ast.framework,
            'deprecated': stored.ast.deprecated,
            'section': stored.section,
            'line': stored.line_number,
            'nodes': chain_nodes,
        }
        chains.append(chain_data)
    
    result = {
        'metadata': {
            'format': 'archeon-graph',
            'version': '2.0',
            'stats': graph.stats(),
        },
        'nodes': nodes,
        'edges': edges,
        'chains': chains,
    }
    
    if output_path:
        Path(output_path).write_text(json.dumps(result, indent=2))
    
    return result


def export_png(
    graph: KnowledgeGraph,
    output_path: str,
    dot_path: Optional[str] = None
) -> ExportResult:
    """
    Export graph to PNG using Graphviz.
    
    Requires `dot` command to be installed.
    
    Args:
        graph: Knowledge graph to export
        output_path: Path for PNG output
        dot_path: Optional path to save intermediate DOT file
        
    Returns:
        ExportResult with success status
    """
    # Generate DOT
    dot_content = export_dot(graph)
    
    # Save DOT if requested
    if dot_path:
        Path(dot_path).write_text(dot_content)
    
    # Count nodes and edges
    node_count = len(set(
        node.qualified_name
        for stored in graph.chains
        for node in stored.ast.nodes
    ))
    edge_count = sum(len(stored.ast.edges) for stored in graph.chains)
    
    # Try to run graphviz
    try:
        result = subprocess.run(
            ['dot', '-Tpng', '-o', output_path],
            input=dot_content,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return ExportResult(
                success=False,
                path=output_path,
                format='png',
                error=result.stderr or "Graphviz dot command failed",
                node_count=node_count,
                edge_count=edge_count
            )
        
        return ExportResult(
            success=True,
            path=output_path,
            format='png',
            node_count=node_count,
            edge_count=edge_count
        )
        
    except FileNotFoundError:
        return ExportResult(
            success=False,
            path=output_path,
            format='png',
            error="Graphviz not installed. Install with: brew install graphviz",
            node_count=node_count,
            edge_count=edge_count
        )
    except subprocess.TimeoutExpired:
        return ExportResult(
            success=False,
            path=output_path,
            format='png',
            error="Graphviz timed out",
            node_count=node_count,
            edge_count=edge_count
        )


def export_svg(
    graph: KnowledgeGraph,
    output_path: str
) -> ExportResult:
    """
    Export graph to SVG using Graphviz.
    
    Args:
        graph: Knowledge graph to export
        output_path: Path for SVG output
        
    Returns:
        ExportResult with success status
    """
    dot_content = export_dot(graph)
    
    node_count = len(set(
        node.qualified_name
        for stored in graph.chains
        for node in stored.ast.nodes
    ))
    edge_count = sum(len(stored.ast.edges) for stored in graph.chains)
    
    try:
        result = subprocess.run(
            ['dot', '-Tsvg', '-o', output_path],
            input=dot_content,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return ExportResult(
                success=False,
                path=output_path,
                format='svg',
                error=result.stderr or "Graphviz dot command failed",
                node_count=node_count,
                edge_count=edge_count
            )
        
        return ExportResult(
            success=True,
            path=output_path,
            format='svg',
            node_count=node_count,
            edge_count=edge_count
        )
        
    except FileNotFoundError:
        return ExportResult(
            success=False,
            path=output_path,
            format='svg',
            error="Graphviz not installed. Install with: brew install graphviz",
            node_count=node_count,
            edge_count=edge_count
        )


def export_mermaid(graph: KnowledgeGraph, output_path: Optional[str] = None) -> str:
    """
    Export graph to Mermaid diagram format.
    
    Args:
        graph: Knowledge graph to export
        output_path: Optional path to write file
        
    Returns:
        Mermaid format string
    """
    lines = ['graph LR']
    
    # Collect nodes and edges
    nodes: dict[str, GlyphNode] = {}
    edges: list[tuple[str, str, str]] = []
    
    for stored in graph.chains:
        for node in stored.ast.nodes:
            nodes[node.qualified_name] = node
        for edge in stored.ast.edges:
            edges.append((edge.source, edge.target, edge.operator))
    
    # Generate node definitions with styling
    for qualified_name, node in sorted(nodes.items()):
        # Mermaid node ID (sanitize)
        node_id = qualified_name.replace(':', '_').replace('.', '_').replace('/', '_')
        label = qualified_name
        
        lines.append(f'    {node_id}["{label}"]')
    
    # Edge mappings for Mermaid
    mermaid_edges = {
        '=>': '-->',
        '->': '-.->',
        '~>': '-.->',
        '!>': '-.-o',
        '::': '-->',
        '@': '--o',
    }
    
    # Generate edges
    seen = set()
    for source, target, operator in edges:
        edge_key = (source, target)
        if edge_key in seen:
            continue
        seen.add(edge_key)
        
        source_id = source.replace(':', '_').replace('.', '_').replace('/', '_')
        target_id = target.replace(':', '_').replace('.', '_').replace('/', '_')
        arrow = mermaid_edges.get(operator, '-->')
        
        lines.append(f'    {source_id} {arrow} {target_id}')
    
    # Add styling
    lines.append('')
    lines.append('    %% Styling')
    
    # Group nodes by prefix for styling
    for prefix, color in DOT_COLORS.items():
        node_ids = [
            n.replace(':', '_').replace('.', '_').replace('/', '_')
            for n in nodes
            if n.startswith(f'{prefix}:')
        ]
        if node_ids:
            lines.append(f'    style {",".join(node_ids)} fill:{color},color:white')
    
    content = '\n'.join(lines)
    
    if output_path:
        Path(output_path).write_text(content)
    
    return content
