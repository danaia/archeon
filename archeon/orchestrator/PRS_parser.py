"""
PRS_parser.py - Archeon Chain Parser

Parses glyph chain strings into structured ASTs.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from archeon.config.legend import is_valid_glyph, is_valid_operator, EDGE_TYPES


@dataclass
class GlyphNode:
    """Represents a parsed glyph."""
    prefix: str
    name: str
    namespace: Optional[str] = None
    action: Optional[str] = None
    modifiers: list[str] = field(default_factory=list)
    args: list[str] = field(default_factory=list)
    raw: str = ""

    @property
    def qualified_name(self) -> str:
        """Return fully qualified glyph name."""
        if self.namespace and self.action:
            return f"{self.prefix}:{self.namespace}.{self.action}"
        return f"{self.prefix}:{self.name}"


@dataclass
class Edge:
    """Represents an edge between glyphs."""
    source_idx: int
    target_idx: int
    operator: str


@dataclass
class ChainAST:
    """Abstract Syntax Tree for a parsed chain."""
    version: Optional[str] = None
    framework: Optional[str] = None
    nodes: list[GlyphNode] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    deprecated: bool = False
    raw: str = ""


class ParseError(Exception):
    """Raised when parsing fails."""
    def __init__(self, message: str, position: int = 0):
        self.message = message
        self.position = position
        super().__init__(f"{message} (position {position})")


class ChainParser:
    """Parser for Archeon chain notation."""

    # Regex patterns
    VERSION_PATTERN = re.compile(r'^@(v\d+|latest)(?:\s+\[deprecated\])?')
    FRAMEWORK_PATTERN = re.compile(r'^\[(\w+)\]')
    # Glyph pattern: PREFIX:name.action or PREFIX:METHOD/route
    # Allows dots, slashes, and alphanumerics in the name portion
    GLYPH_PATTERN = re.compile(r'^([A-Z]+):([a-zA-Z0-9_./]+)(\[[^\]]+\])?')
    OPERATOR_PATTERN = re.compile(r'^(=>|~>|!>|->|::|@)')
    MODIFIER_PATTERN = re.compile(r'\[([^\]]+)\]')
    ARGS_PATTERN = re.compile(r"\(([^)]*)\)")
    CONTAINMENT_PATTERN = re.compile(r'^([A-Z]+:[^\s@]+)\s*@\s*(.+)$')

    def parse(self, chain_str: str) -> ChainAST:
        """Parse a chain string into an AST."""
        chain_str = chain_str.strip()
        if not chain_str or chain_str.startswith('#'):
            return ChainAST(raw=chain_str)

        ast = ChainAST(raw=chain_str)
        pos = 0

        # Parse version tag
        version_match = self.VERSION_PATTERN.match(chain_str[pos:])
        if version_match:
            ast.version = version_match.group(1)
            ast.deprecated = '[deprecated]' in version_match.group(0)
            pos += version_match.end()
            chain_str = chain_str[pos:].strip()
            pos = 0

        # Parse framework tag
        framework_match = self.FRAMEWORK_PATTERN.match(chain_str[pos:])
        if framework_match:
            ast.framework = framework_match.group(1)
            pos += framework_match.end()
            chain_str = chain_str[pos:].strip()
            pos = 0

        # Check for containment syntax (V:Page @ CMP:A, CMP:B)
        containment_match = self.CONTAINMENT_PATTERN.match(chain_str)
        if containment_match:
            return self._parse_containment(containment_match, ast)

        # Parse regular chain
        return self._parse_chain(chain_str, ast)

    def _parse_containment(self, match: re.Match, ast: ChainAST) -> ChainAST:
        """Parse containment syntax: V:Page @ CMP:A, CMP:B, CMP:C"""
        container_str = match.group(1)
        children_str = match.group(2)

        # Parse container
        container = self._parse_glyph(container_str)
        if not container:
            raise ParseError(f"Invalid container glyph: {container_str}")
        ast.nodes.append(container)

        # Parse children
        children = [c.strip() for c in children_str.split(',')]
        for i, child_str in enumerate(children):
            child = self._parse_glyph(child_str)
            if not child:
                raise ParseError(f"Invalid child glyph: {child_str}")
            ast.nodes.append(child)
            ast.edges.append(Edge(source_idx=0, target_idx=i + 1, operator='@'))

        return ast

    def _parse_chain(self, chain_str: str, ast: ChainAST) -> ChainAST:
        """Parse a linear chain of glyphs connected by operators."""
        tokens = self._tokenize(chain_str)
        if not tokens:
            return ast

        current_idx = 0
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # Try to parse as glyph
            glyph = self._parse_glyph(token)
            if glyph:
                ast.nodes.append(glyph)
                if len(ast.nodes) > 1 and i > 0:
                    # Find the operator before this glyph
                    prev_token = tokens[i - 1] if i > 0 else None
                    if prev_token and is_valid_operator(prev_token):
                        ast.edges.append(Edge(
                            source_idx=current_idx,
                            target_idx=len(ast.nodes) - 1,
                            operator=prev_token
                        ))
                current_idx = len(ast.nodes) - 1
                i += 1
                continue

            # Try to parse as operator
            if is_valid_operator(token):
                i += 1
                continue

            # Unknown token
            raise ParseError(f"Unknown token: {token}", i)

        return ast

    def _tokenize(self, chain_str: str) -> list[str]:
        """Tokenize a chain string into glyphs and operators."""
        tokens = []
        remaining = chain_str.strip()

        while remaining:
            remaining = remaining.strip()
            if not remaining:
                break

            # Try operator first (longer matches first)
            op_match = self.OPERATOR_PATTERN.match(remaining)
            if op_match:
                tokens.append(op_match.group(1))
                remaining = remaining[op_match.end():]
                continue

            # Try glyph
            glyph_match = self.GLYPH_PATTERN.match(remaining)
            if glyph_match:
                full_match = glyph_match.group(0)
                # Check for args after modifier
                rest = remaining[glyph_match.end():]
                args_match = self.ARGS_PATTERN.match(rest)
                if args_match:
                    full_match += args_match.group(0)
                    remaining = rest[args_match.end():]
                else:
                    remaining = rest
                tokens.append(full_match)
                continue

            # Handle special syntax like "actions: foo, bar"
            if ':' in remaining and not self.GLYPH_PATTERN.match(remaining):
                tokens.append(remaining)
                break

            raise ParseError(f"Cannot tokenize: {remaining[:20]}...")

        return tokens

    def _parse_glyph(self, glyph_str: str) -> Optional[GlyphNode]:
        """Parse a single glyph string into a GlyphNode."""
        glyph_str = glyph_str.strip()
        match = self.GLYPH_PATTERN.match(glyph_str)
        if not match:
            return None

        prefix = match.group(1)
        name_part = match.group(2)
        modifier_str = match.group(3)

        # Allow unknown prefixes to be parsed - validation happens later
        node = GlyphNode(prefix=prefix, name=name_part, raw=glyph_str)

        # Parse namespace.action (e.g., auth.validateCreds)
        if '.' in name_part:
            parts = name_part.split('.', 1)
            node.namespace = parts[0]
            node.action = parts[1]
        # Parse method/route for API (e.g., POST/auth)
        elif '/' in name_part and prefix == 'API':
            parts = name_part.split('/', 1)
            node.namespace = parts[0]  # HTTP method
            node.action = '/' + parts[1]  # Route

        # Parse modifiers
        if modifier_str:
            modifiers = self.MODIFIER_PATTERN.findall(modifier_str)
            node.modifiers = modifiers

        # Parse args (e.g., toast('message'))
        rest = glyph_str[match.end():]
        args_match = self.ARGS_PATTERN.search(glyph_str)
        if args_match:
            args_str = args_match.group(1)
            node.args = [a.strip().strip("'\"") for a in args_str.split(',') if a.strip()]

        return node


def parse_chain(chain_str: str) -> ChainAST:
    """Convenience function to parse a chain string."""
    parser = ChainParser()
    return parser.parse(chain_str)


def parse_file(filepath: str) -> list[ChainAST]:
    """Parse all chains from an .arcon file."""
    chains = []
    parser = ChainParser()

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                try:
                    ast = parser.parse(line)
                    if ast.nodes:
                        chains.append(ast)
                except ParseError:
                    continue  # Skip invalid lines

    return chains
