"""
Chain inference from glyph dependency graph.

Builds a dependency graph from classified files and infers
Archeon chain notation from the relationships.

Enhanced with data flow analysis for stores and API endpoints.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional
from collections import defaultdict


@dataclass
class GlyphNode:
    """Represents a glyph in the dependency graph."""
    file_path: Path
    glyph: str
    qualified_name: str
    imports: Set[Path]  # Files this glyph imports
    data_sources: List[str] = field(default_factory=list)  # API calls, store subscriptions
    data_targets: List[str] = field(default_factory=list)  # What receives data from this


@dataclass
class DataFlowChain:
    """Represents a data flow path through the architecture."""
    root: str           # Starting point (usually CMP or V)
    nodes: List[str]    # Ordered list of glyphs
    operators: List[str]  # Operators between nodes
    flow_type: str      # "structural", "reactive", "fetch"
    
    def to_string(self) -> str:
        """Convert to chain notation."""
        if not self.nodes:
            return ""
        parts = [self.nodes[0]]
        for i, (node, op) in enumerate(zip(self.nodes[1:], self.operators)):
            parts.append(op)
            parts.append(node)
        return "@v1 " + " ".join(parts)


class ChainInferrer:
    """Infer glyph chains from dependency graphs with data flow awareness."""
    
    # Layer ordering for chain assembly (frontend → backend flow)
    LAYER_ORDER = {
        'V': 0,       # Views - entry points
        'CMP': 1,     # Components - UI building blocks
        'STO': 2,     # Stores - state management
        'FNC': 3,     # Functions - utilities
        'EVT': 4,     # Events - pub/sub
        'API': 5,     # API endpoints - backend entry
        'MDL': 6,     # Models - data layer
    }
    
    # Operators based on connection types
    OPERATORS = {
        'structural': '=>',      # Default: import/compile-time
        'reactive': '~>',        # Store subscriptions, event listeners
        'control': '->',         # Error handling, conditionals
        'sideeffect': '!>',      # Logging, analytics
        'async_fetch': '=>',     # Async data fetching (still uses => but tracked)
    }
    
    # Data flow patterns to detect
    DATA_FLOW_PATTERNS = {
        'store_to_api': {
            'pattern': ('STO', 'API'),
            'operator': '=>',
            'description': 'Store fetching from API'
        },
        'cmp_to_store': {
            'pattern': ('CMP', 'STO'),
            'operator': '~>',
            'description': 'Component subscribing to store'
        },
        'view_to_store': {
            'pattern': ('V', 'STO'),
            'operator': '~>',
            'description': 'View subscribing to store'
        },
        'api_to_model': {
            'pattern': ('API', 'MDL'),
            'operator': '=>',
            'description': 'API using model'
        },
        'store_mutation': {
            'pattern': ('CMP', 'STO'),
            'operator': '=>',
            'description': 'Component calling store action'
        },
    }
    
    def __init__(self):
        self.nodes: Dict[str, GlyphNode] = {}
        self.edges: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # from_glyph -> [(to_glyph, operator)]
        self.data_flow_edges: List[Tuple[str, str, str]] = []  # (from, to, flow_type)
        self.store_api_connections: Dict[str, List[str]] = defaultdict(list)  # store -> [api calls]
    
    def add_node(self, qualified_name: str, glyph: str, file_path: Path, imports: Set[Path],
                 data_sources: List[str] = None, data_targets: List[str] = None):
        """Add a classified glyph to the graph."""
        self.nodes[qualified_name] = GlyphNode(
            file_path=file_path,
            glyph=glyph,
            qualified_name=qualified_name,
            imports=imports,
            data_sources=data_sources or [],
            data_targets=data_targets or []
        )
    
    def add_data_flow(self, from_glyph: str, to_glyph: str, flow_type: str):
        """Add a data flow edge (e.g., store fetching from API)."""
        self.data_flow_edges.append((from_glyph, to_glyph, flow_type))
        
        # Determine operator based on flow type
        operator = self.OPERATORS.get(flow_type, '=>')
        
        # Add to regular edges if not already present
        existing_targets = [t for t, _ in self.edges[from_glyph]]
        if to_glyph not in existing_targets:
            self.edges[from_glyph].append((to_glyph, operator))
    
    def register_store_api_calls(self, store_name: str, api_calls: List[str]):
        """Register API calls made by a store for data flow tracking."""
        self.store_api_connections[store_name] = api_calls
        for api_call in api_calls:
            self.add_data_flow(store_name, api_call, 'async_fetch')
    
    def build_graph(self, classified_files: Dict[Path, str], 
                    qualified_names: Dict[Path, str],
                    import_map: Dict[Path, Set[Path]]):
        """
        Build the dependency graph from classified files.
        
        Args:
            classified_files: Map of file_path -> glyph
            qualified_names: Map of file_path -> qualified_name
            import_map: Map of file_path -> set of imported file paths
        """
        # Add all nodes
        for file_path, glyph in classified_files.items():
            qualified_name = qualified_names.get(file_path, f"{glyph}:Unknown")
            imports = import_map.get(file_path, set())
            self.add_node(qualified_name, glyph, file_path, imports)
        
        # Build edges by tracing imports
        for qualified_name, node in self.nodes.items():
            for imported_file in node.imports:
                # Find if imported file is in our graph
                for other_name, other_node in self.nodes.items():
                    if other_node.file_path == imported_file or other_name == str(imported_file):
                        operator = self._infer_operator(node.glyph, other_node.glyph, node.file_path)
                        self.edges[qualified_name].append((other_name, operator))
                        break
        
        # Add data flow edges from store->API connections
        for store_name, api_calls in self.store_api_connections.items():
            for api_call in api_calls:
                # API calls might not be in nodes (external APIs), but we still track them
                if api_call not in self.nodes:
                    # Create a synthetic node for the API endpoint
                    self.nodes[api_call] = GlyphNode(
                        file_path=Path("external"),
                        glyph="API",
                        qualified_name=api_call,
                        imports=set(),
                        data_sources=[],
                        data_targets=[store_name]
                    )
    
    def _infer_operator(self, from_glyph: str, to_glyph: str, from_file: Path) -> str:
        """
        Infer the operator type based on glyphs and context.
        Enhanced with data flow pattern recognition.
        """
        # Check known data flow patterns
        for pattern_name, pattern_info in self.DATA_FLOW_PATTERNS.items():
            if (from_glyph, to_glyph) == pattern_info['pattern']:
                return pattern_info['operator']
        
        # Event/reactive connections
        if from_glyph in ('EVT', 'STO') or to_glyph == 'EVT':
            return self.OPERATORS['reactive']
        
        # Store subscriptions from components
        if from_glyph in ('CMP', 'V') and to_glyph == 'STO':
            return self.OPERATORS['reactive']
        
        # Error paths
        if to_glyph == 'ERR':
            return self.OPERATORS['control']
        
        # Default: structural
        return self.OPERATORS['structural']
    
    def find_chain_roots(self) -> List[str]:
        """
        Find entry points in the graph.
        
        Roots are typically V (Views) or CMP (Components) with no incoming edges.
        """
        roots = []
        
        # Build reverse edges for incoming connections
        incoming = defaultdict(list)
        for from_glyph, to_list in self.edges.items():
            for to_glyph, _ in to_list:
                incoming[to_glyph].append(from_glyph)
        
        # Find nodes with no incoming edges
        for qualified_name, node in self.nodes.items():
            if node.glyph in ('V', 'CMP') and qualified_name not in incoming:
                roots.append(qualified_name)
        
        # If no roots found, use all V and CMP nodes
        if not roots:
            roots = [name for name, node in self.nodes.items() if node.glyph in ('V', 'CMP')]
        
        return roots
    
    def trace_chain(self, root: str, max_depth: int = 10) -> List[str]:
        """
        Trace a data flow chain from a root node using DFS.
        
        Returns list of qualified names in layer order.
        """
        chain = []
        visited = set()
        
        def dfs(qualified_name: str, depth: int):
            if depth > max_depth or qualified_name in visited:
                return
            
            visited.add(qualified_name)
            
            if qualified_name in self.nodes:
                chain.append(qualified_name)
                
                # Follow edges in layer order
                sorted_edges = sorted(
                    self.edges.get(qualified_name, []),
                    key=lambda x: self.LAYER_ORDER.get(self.nodes[x[0]].glyph, 99)
                )
                
                for next_glyph, _ in sorted_edges:
                    dfs(next_glyph, depth + 1)
        
        dfs(root, 0)
        return chain
    
    def infer_chains(self) -> List[str]:
        """
        Infer all chains from the graph.
        
        Returns list of chain notation strings.
        """
        chains = []
        roots = self.find_chain_roots()
        
        for root in roots:
            chain = self.trace_chain(root)
            if chain:
                chain_str = self._assemble_chain_string(chain)
                if chain_str:
                    chains.append(chain_str)
        
        return chains
    
    def _assemble_chain_string(self, chain: List[str]) -> Optional[str]:
        """
        Assemble a chain notation string from a traced path.
        
        Example: "@v1 CMP:LoginForm => STO:Auth => API:POST/auth/login"
        """
        if not chain:
            return None
        
        parts = []
        for i, qualified_name in enumerate(chain):
            if i > 0 and i - 1 < len(chain):
                # Get operator from previous connection
                prev_name = chain[i - 1]
                edges = self.edges.get(prev_name, [])
                operator = '=>'
                for target, op in edges:
                    if target == qualified_name:
                        operator = op
                        break
                parts.append(operator)
            
            parts.append(qualified_name)
        
        # Build chain string
        chain_str = " ".join(parts)
        
        # Add version prefix
        chain_str = "@v1 " + chain_str
        
        return chain_str
    
    def validate_boundary_rules(self, chain_str: str) -> Tuple[bool, List[str]]:
        """
        Validate that a chain respects boundary rules.
        
        Forbidden connections:
        - CMP -> MDL
        - STO -> MDL
        - EVT -> API
        - V -> API
        - V -> MDL
        
        Returns (is_valid, list of error messages)
        """
        errors = []
        
        # Extract glyphs from chain
        glyphs = re.findall(r'([A-Z]{3}):[\w:/]+', chain_str)
        
        forbidden = [
            ('CMP', 'MDL'),
            ('STO', 'MDL'),
            ('EVT', 'API'),
            ('V', 'API'),
            ('V', 'MDL'),
        ]
        
        for i in range(len(glyphs) - 1):
            from_glyph = glyphs[i]
            to_glyph = glyphs[i + 1]
            
            if (from_glyph, to_glyph) in forbidden:
                errors.append(
                    f"Boundary violation: {from_glyph} -> {to_glyph} is not allowed"
                )
        
        return len(errors) == 0, errors
    
    def get_glyph_coverage(self) -> Dict[str, int]:
        """
        Get coverage stats of glyphs in the graph.
        
        Returns dict mapping glyph -> count.
        """
        coverage = defaultdict(int)
        for node in self.nodes.values():
            coverage[node.glyph] += 1
        return dict(coverage)
    
    def get_graph_stats(self) -> Dict:
        """Get statistics about the inferred graph."""
        return {
            'total_files': len(self.nodes),
            'total_edges': sum(len(edges) for edges in self.edges.values()),
            'glyph_coverage': self.get_glyph_coverage(),
            'chain_roots': self.find_chain_roots(),
        }
