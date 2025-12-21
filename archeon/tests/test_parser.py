"""
Tests for orchestrator/PRS_parser.py
"""

import pytest
from archeon.orchestrator.PRS_parser import (
    ChainParser,
    parse_chain,
    GlyphNode,
    ChainAST,
    ParseError,
)


class TestGlyphParsing:
    """Tests for individual glyph parsing."""

    def test_simple_glyph(self):
        """Parse simple glyph like NED:login."""
        ast = parse_chain("NED:login")
        assert len(ast.nodes) == 1
        assert ast.nodes[0].prefix == 'NED'
        assert ast.nodes[0].name == 'login'

    def test_qualified_glyph(self):
        """Parse qualified glyph like FNC:auth.validateCreds."""
        ast = parse_chain("FNC:auth.validateCreds")
        node = ast.nodes[0]
        assert node.prefix == 'FNC'
        assert node.namespace == 'auth'
        assert node.action == 'validateCreds'
        assert node.qualified_name == 'FNC:auth.validateCreds'

    def test_api_glyph(self):
        """Parse API glyph like API:POST/auth."""
        ast = parse_chain("API:POST/auth")
        node = ast.nodes[0]
        assert node.prefix == 'API'
        assert node.namespace == 'POST'
        assert node.action == '/auth'

    def test_glyph_with_modifier(self):
        """Parse glyph with modifier like CMP:Form[stateful]."""
        ast = parse_chain("CMP:Form[stateful]")
        node = ast.nodes[0]
        assert node.prefix == 'CMP'
        assert node.name == 'Form'
        assert 'stateful' in node.modifiers

    def test_glyph_with_args(self):
        """Parse glyph with args like OUT:toast('Success')."""
        ast = parse_chain("OUT:toast('Success')")
        node = ast.nodes[0]
        assert node.prefix == 'OUT'
        assert 'Success' in node.args


class TestChainParsing:
    """Tests for full chain parsing."""

    def test_simple_chain(self):
        """Parse simple chain with structural edges."""
        ast = parse_chain("NED:login => TSK:submit => CMP:LoginForm")
        assert len(ast.nodes) == 3
        assert len(ast.edges) == 2
        assert ast.edges[0].operator == '=>'
        assert ast.edges[1].operator == '=>'

    def test_chain_with_version(self):
        """Parse chain with version tag."""
        ast = parse_chain("@v1 NED:login => TSK:submit")
        assert ast.version == 'v1'
        assert len(ast.nodes) == 2

    def test_chain_with_framework(self):
        """Parse chain with framework tag."""
        ast = parse_chain("[react] CMP:Dashboard => STO:userStore")
        assert ast.framework == 'react'
        assert len(ast.nodes) == 2

    def test_chain_with_version_and_framework(self):
        """Parse chain with both version and framework."""
        ast = parse_chain("@v2 [fastapi] API:POST/auth => MDL:user.findOne")
        assert ast.version == 'v2'
        assert ast.framework == 'fastapi'
        assert len(ast.nodes) == 2

    def test_deprecated_chain(self):
        """Parse deprecated chain."""
        ast = parse_chain("@v1 [deprecated] NED:old => OUT:result")
        assert ast.version == 'v1'
        assert ast.deprecated is True

    def test_reactive_edge(self):
        """Parse chain with reactive edge."""
        ast = parse_chain("CMP:Input => STO:store ~> CMP:Input")
        assert len(ast.edges) == 2
        assert ast.edges[0].operator == '=>'
        assert ast.edges[1].operator == '~>'

    def test_control_edge(self):
        """Parse chain with control edge."""
        ast = parse_chain("API:POST/auth -> ERR:auth.invalid")
        assert len(ast.edges) == 1
        assert ast.edges[0].operator == '->'

    def test_side_effect_edge(self):
        """Parse chain with side-effect edge."""
        ast = parse_chain("MDL:user.create !> FNC:email.sendWelcome")
        assert len(ast.edges) == 1
        assert ast.edges[0].operator == '!>'


class TestContainmentParsing:
    """Tests for containment syntax."""

    def test_containment_syntax(self):
        """Parse V: @ CMP:A, CMP:B containment."""
        ast = parse_chain("V:ProfilePage @ CMP:Header, CMP:ProfileCard, CMP:ActivityFeed")
        assert len(ast.nodes) == 4
        assert ast.nodes[0].prefix == 'V'
        assert ast.nodes[0].name == 'ProfilePage'
        assert all(e.operator == '@' for e in ast.edges)
        assert len(ast.edges) == 3

    def test_containment_all_edges_from_container(self):
        """All containment edges originate from container."""
        ast = parse_chain("V:Page @ CMP:A, CMP:B")
        for edge in ast.edges:
            assert edge.source_idx == 0  # Container is always index 0


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_string(self):
        """Empty string returns empty AST."""
        ast = parse_chain("")
        assert len(ast.nodes) == 0

    def test_comment_line(self):
        """Comment line returns empty AST."""
        ast = parse_chain("# This is a comment")
        assert len(ast.nodes) == 0

    def test_whitespace_handling(self):
        """Whitespace is handled correctly."""
        ast = parse_chain("  NED:login   =>   TSK:submit  ")
        assert len(ast.nodes) == 2

    def test_complex_chain(self):
        """Parse complex real-world chain."""
        chain = "@v1 [react] NED:login => TSK:submitCreds => CMP:LoginForm[stateful] => API:POST/auth => OUT:redirect('/dashboard')"
        ast = parse_chain(chain)
        assert ast.version == 'v1'
        assert ast.framework == 'react'
        assert len(ast.nodes) == 5
        assert ast.nodes[2].modifiers == ['stateful']


class TestQualifiedNames:
    """Tests for qualified name generation."""

    def test_simple_qualified_name(self):
        """Simple glyph qualified name."""
        ast = parse_chain("CMP:LoginForm")
        assert ast.nodes[0].qualified_name == 'CMP:LoginForm'

    def test_namespace_qualified_name(self):
        """Namespaced glyph qualified name."""
        ast = parse_chain("FNC:auth.validate")
        assert ast.nodes[0].qualified_name == 'FNC:auth.validate'
