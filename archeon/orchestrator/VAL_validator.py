"""
VAL_validator.py - Archeon Validation Engine

Validates chains for structure, cycles, boundaries, and other rules.
"""

from dataclasses import dataclass, field
from typing import Optional

from archeon.orchestrator.PRS_parser import ChainAST, GlyphNode, Edge
from archeon.orchestrator.GRF_graph import KnowledgeGraph
from archeon.config.legend import GLYPH_LEGEND, EDGE_TYPES, BOUNDARY_RULES


@dataclass
class ValidationError:
    """A validation error."""
    code: str
    message: str
    location: Optional[str] = None
    node: Optional[str] = None


@dataclass
class ValidationWarning:
    """A validation warning."""
    code: str
    message: str
    location: Optional[str] = None
    node: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validation."""
    valid: bool = True
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationWarning] = field(default_factory=list)

    def add_error(self, code: str, message: str, **kwargs):
        self.errors.append(ValidationError(code=code, message=message, **kwargs))
        self.valid = False

    def add_warning(self, code: str, message: str, **kwargs):
        self.warnings.append(ValidationWarning(code=code, message=message, **kwargs))

    def merge(self, other: 'ValidationResult'):
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.valid:
            self.valid = False


class ChainValidator:
    """Validates individual chains."""

    def validate(self, ast: ChainAST) -> ValidationResult:
        """Run all validations on a chain."""
        result = ValidationResult()

        if not ast.nodes:
            return result

        result.merge(self.validate_structure(ast))
        result.merge(self.validate_output(ast))
        result.merge(self.validate_cycles(ast))
        result.merge(self.validate_boundaries(ast))
        result.merge(self.validate_error_paths(ast))

        return result

    def validate_structure(self, ast: ChainAST) -> ValidationResult:
        """Validate basic chain structure."""
        result = ValidationResult()

        # Check all nodes are valid glyphs
        for node in ast.nodes:
            if node.prefix not in GLYPH_LEGEND:
                result.add_error(
                    'ERR:glyph.unknown',
                    f"Unknown glyph prefix: {node.prefix}",
                    node=node.qualified_name
                )

        # Check all edges connect valid nodes
        for edge in ast.edges:
            if edge.source_idx >= len(ast.nodes):
                result.add_error(
                    'ERR:edge.invalidSource',
                    f"Edge source index {edge.source_idx} out of range"
                )
            if edge.target_idx >= len(ast.nodes):
                result.add_error(
                    'ERR:edge.invalidTarget',
                    f"Edge target index {edge.target_idx} out of range"
                )
            if edge.operator not in EDGE_TYPES:
                result.add_error(
                    'ERR:edge.unknownOperator',
                    f"Unknown operator: {edge.operator}"
                )

        return result

    def validate_output(self, ast: ChainAST) -> ValidationResult:
        """Validate chain ends with OUT: glyph."""
        result = ValidationResult()

        if not ast.nodes:
            return result

        # Find terminal nodes (nodes with no outgoing edges)
        has_outgoing = set()
        for edge in ast.edges:
            has_outgoing.add(edge.source_idx)

        terminal_indices = [i for i in range(len(ast.nodes)) if i not in has_outgoing]

        # Check if any terminal is OUT or ERR
        has_output = False
        for idx in terminal_indices:
            node = ast.nodes[idx]
            if node.prefix in ('OUT', 'ERR'):
                has_output = True
                break

        if not has_output and not self._is_containment_chain(ast):
            result.add_warning(
                'WARN:chain.noOutput',
                "Chain does not end with OUT: or ERR: glyph"
            )

        return result

    def validate_cycles(self, ast: ChainAST) -> ValidationResult:
        """Validate no illegal cycles exist."""
        result = ValidationResult()

        # Build adjacency list
        adj: dict[int, list[tuple[int, str]]] = {i: [] for i in range(len(ast.nodes))}
        for edge in ast.edges:
            adj[edge.source_idx].append((edge.target_idx, edge.operator))

        # DFS for cycles, tracking operator types
        visited = set()
        rec_stack = set()

        def dfs(node: int, path_operators: list[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor, operator in adj[node]:
                if neighbor not in visited:
                    if dfs(neighbor, path_operators + [operator]):
                        return True
                elif neighbor in rec_stack:
                    # Cycle detected - check if allowed
                    cycle_ops = path_operators + [operator]
                    # Cycles only allowed if ALL edges are reactive (~>)
                    non_reactive = [op for op in cycle_ops if op not in ('~>', '!>')]
                    if non_reactive:
                        result.add_error(
                            'ERR:chain.structuralCycle',
                            f"Structural cycle detected through {non_reactive[0]} operator",
                            node=ast.nodes[node].qualified_name
                        )
                        return True

            rec_stack.remove(node)
            return False

        for i in range(len(ast.nodes)):
            if i not in visited:
                dfs(i, [])

        return result

    def validate_boundaries(self, ast: ChainAST) -> ValidationResult:
        """Validate ownership boundary rules."""
        result = ValidationResult()

        for edge in ast.edges:
            if edge.source_idx >= len(ast.nodes) or edge.target_idx >= len(ast.nodes):
                continue

            source = ast.nodes[edge.source_idx]
            target = ast.nodes[edge.target_idx]

            for rule in BOUNDARY_RULES:
                # Check operator-based rules
                if 'operator' in rule and rule.get('from') == source.prefix:
                    if edge.operator == rule['operator'] and not rule['allowed']:
                        result.add_error(
                            f"ERR:boundary.{source.prefix.lower()}DataFlow",
                            rule['reason'],
                            node=source.qualified_name
                        )

                # Check from-to rules
                if 'to' in rule:
                    from_prefix = rule['from']
                    # Handle qualified prefixes like FNC:ui
                    if ':' in from_prefix:
                        prefix, qualifier = from_prefix.split(':')
                        if source.prefix == prefix and source.namespace == qualifier:
                            if target.prefix == rule['to'] and not rule['allowed']:
                                result.add_error(
                                    f"ERR:boundary.{source.prefix.lower()}To{target.prefix}",
                                    rule['reason'],
                                    node=source.qualified_name
                                )
                    else:
                        if source.prefix == from_prefix and target.prefix == rule['to']:
                            if not rule['allowed']:
                                result.add_error(
                                    f"ERR:boundary.{source.prefix.lower()}To{target.prefix.lower()}",
                                    rule['reason'],
                                    node=source.qualified_name
                                )

        return result

    def validate_error_paths(self, ast: ChainAST) -> ValidationResult:
        """Check if API endpoints have error paths."""
        result = ValidationResult()

        api_nodes = [n for n in ast.nodes if n.prefix == 'API']
        err_nodes = [n for n in ast.nodes if n.prefix == 'ERR']

        for api_node in api_nodes:
            # Check if this API has any error branches in the graph
            has_error_path = False
            for edge in ast.edges:
                if edge.source_idx < len(ast.nodes):
                    source = ast.nodes[edge.source_idx]
                    if source.qualified_name == api_node.qualified_name:
                        if edge.operator == '->' and edge.target_idx < len(ast.nodes):
                            target = ast.nodes[edge.target_idx]
                            if target.prefix == 'ERR':
                                has_error_path = True
                                break

            if not has_error_path and err_nodes:
                # Only warn if there ARE error nodes but not connected to this API
                pass  # We'll check this at graph level

        return result

    def _is_containment_chain(self, ast: ChainAST) -> bool:
        """Check if chain is containment (V: @ CMP:)."""
        if ast.edges:
            return all(e.operator == '@' for e in ast.edges)
        return False


class GraphValidator:
    """Validates the entire knowledge graph."""

    def __init__(self, graph: KnowledgeGraph):
        self.graph = graph
        self.chain_validator = ChainValidator()

    def validate(self) -> ValidationResult:
        """Run all validations on the graph."""
        result = ValidationResult()

        # Validate each chain
        for stored in self.graph.chains:
            chain_result = self.chain_validator.validate(stored.ast)
            result.merge(chain_result)

        # Graph-level validations
        result.merge(self.validate_duplicates())
        result.merge(self.validate_versions())
        result.merge(self.validate_api_error_paths())

        return result

    def validate_duplicates(self) -> ValidationResult:
        """Check for duplicate qualified glyphs."""
        result = ValidationResult()
        seen: dict[str, list[str]] = {}  # glyph -> list of chain versions

        for stored in self.graph.chains:
            for node in stored.ast.nodes:
                key = node.qualified_name
                version = stored.ast.version or 'unversioned'

                if key not in seen:
                    seen[key] = []

                # Same glyph in same version is a duplicate
                if version in seen[key]:
                    result.add_error(
                        'ERR:glyph.duplicate',
                        f"Duplicate glyph {key} in version {version}",
                        node=key
                    )
                else:
                    seen[key].append(version)

        return result

    def validate_versions(self) -> ValidationResult:
        """Check for version conflicts."""
        result = ValidationResult()
        root_versions: dict[str, set[str]] = {}

        for stored in self.graph.chains:
            if not stored.ast.nodes:
                continue

            root = stored.ast.nodes[0].qualified_name
            version = stored.ast.version or 'unversioned'

            if root not in root_versions:
                root_versions[root] = set()

            if version in root_versions[root]:
                result.add_error(
                    'ERR:version.conflict',
                    f"Version {version} already exists for root {root}",
                    node=root
                )
            else:
                root_versions[root].add(version)

        return result

    def validate_api_error_paths(self) -> ValidationResult:
        """Check all API endpoints have at least one error path."""
        result = ValidationResult()

        # Collect all API glyphs
        api_glyphs = set()
        api_with_errors = set()

        for stored in self.graph.chains:
            for node in stored.ast.nodes:
                if node.prefix == 'API':
                    api_glyphs.add(node.qualified_name)

            # Check for error branches
            for edge in stored.ast.edges:
                if edge.operator == '->' and edge.source_idx < len(stored.ast.nodes):
                    source = stored.ast.nodes[edge.source_idx]
                    if source.prefix == 'API' and edge.target_idx < len(stored.ast.nodes):
                        target = stored.ast.nodes[edge.target_idx]
                        if target.prefix == 'ERR':
                            api_with_errors.add(source.qualified_name)

        # Warn for APIs without error paths
        for api in api_glyphs:
            if api not in api_with_errors:
                result.add_warning(
                    'WARN:api.noErrorPath',
                    f"API endpoint {api} has no error path defined",
                    node=api
                )

        return result

    def validate_boundaries_only(self) -> ValidationResult:
        """Run only boundary validation."""
        result = ValidationResult()
        for stored in self.graph.chains:
            result.merge(self.chain_validator.validate_boundaries(stored.ast))
        return result

    def validate_cycles_only(self) -> ValidationResult:
        """Run only cycle validation."""
        result = ValidationResult()
        for stored in self.graph.chains:
            result.merge(self.chain_validator.validate_cycles(stored.ast))
        return result


def validate_chain(ast: ChainAST) -> ValidationResult:
    """Convenience function to validate a single chain."""
    validator = ChainValidator()
    return validator.validate(ast)


def validate_graph(graph: KnowledgeGraph) -> ValidationResult:
    """Convenience function to validate a graph."""
    validator = GraphValidator(graph)
    return validator.validate()


def validate_headless(ast: ChainAST) -> ValidationResult:
    """
    Validate that a chain can run in headless mode.
    
    Checks that all executable glyphs (CMP, API, FNC, STO, MDL, EVT)
    have the [headless] modifier.
    """
    result = ValidationResult()
    
    executable_prefixes = {"CMP", "API", "FNC", "STO", "MDL", "EVT"}
    
    for node in ast.nodes:
        if node.prefix in executable_prefixes:
            if "headless" not in node.modifiers:
                result.add_error(
                    'ERR:headless.required',
                    f"{node.qualified_name} missing [headless] modifier - "
                    "only headless components can be executed in headless mode",
                    node=node.qualified_name
                )
    
    # Check for at least one headless node
    headless_nodes = [n for n in ast.nodes 
                      if n.prefix in executable_prefixes 
                      and "headless" in n.modifiers]
    
    if not headless_nodes and any(n.prefix in executable_prefixes for n in ast.nodes):
        result.add_warning(
            'WARN:headless.noEntry',
            "No [headless] annotated nodes found - chain cannot be executed",
        )
    
    return result
