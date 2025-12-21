"""
Tests for config/legend.py
"""

import pytest
from archeon.config.legend import (
    GLYPH_LEGEND,
    EDGE_TYPES,
    BOUNDARY_RULES,
    get_glyph,
    get_edge_type,
    is_valid_glyph,
    is_valid_operator,
    get_agent_glyphs,
    get_meta_glyphs,
)


class TestGlyphLegend:
    """Tests for GLYPH_LEGEND definitions."""

    def test_all_glyphs_defined(self):
        """Verify all 18 glyphs are defined."""
        expected = {
            'NED', 'TSK', 'OUT', 'ERR',  # Meta
            'V', 'CMP', 'STO',            # Frontend
            'FNC', 'EVT',                 # Shared
            'API', 'MDL',                 # Backend
            'ORC', 'PRS', 'VAL', 'SPW', 'TST', 'GRF',  # Internal
            'CTX', 'MIC',                 # Context management
        }
        assert set(GLYPH_LEGEND.keys()) == expected

    def test_glyph_required_fields(self):
        """Each glyph has required fields."""
        required = {'name', 'description', 'agent', 'color', 'layer'}
        for prefix, info in GLYPH_LEGEND.items():
            for field in required:
                assert field in info, f"{prefix} missing {field}"

    def test_get_glyph(self):
        """get_glyph returns correct data."""
        cmp = get_glyph('CMP')
        assert cmp is not None
        assert cmp['name'] == 'Component'
        assert cmp['agent'] == 'CMP_agent'

    def test_get_glyph_unknown(self):
        """get_glyph returns None for unknown."""
        assert get_glyph('UNKNOWN') is None

    def test_is_valid_glyph(self):
        """is_valid_glyph works correctly."""
        assert is_valid_glyph('CMP') is True
        assert is_valid_glyph('API') is True
        assert is_valid_glyph('INVALID') is False


class TestEdgeTypes:
    """Tests for EDGE_TYPES definitions."""

    def test_all_edge_types_defined(self):
        """Verify all 6 edge types are defined."""
        expected = {'=>', '~>', '!>', '->', '::', '@'}
        assert set(EDGE_TYPES.keys()) == expected

    def test_edge_type_fields(self):
        """Each edge type has required fields."""
        required = {'name', 'description', 'cycles_allowed', 'visual'}
        for op, info in EDGE_TYPES.items():
            for field in required:
                assert field in info, f"{op} missing {field}"

    def test_structural_no_cycles(self):
        """Structural operators don't allow cycles."""
        assert EDGE_TYPES['=>']['cycles_allowed'] is False
        assert EDGE_TYPES['->']['cycles_allowed'] is False
        assert EDGE_TYPES['::']['cycles_allowed'] is False

    def test_reactive_allows_cycles(self):
        """Reactive operators allow cycles."""
        assert EDGE_TYPES['~>']['cycles_allowed'] is True
        assert EDGE_TYPES['!>']['cycles_allowed'] is True

    def test_get_edge_type(self):
        """get_edge_type works correctly."""
        structural = get_edge_type('=>')
        assert structural is not None
        assert structural['name'] == 'structural'

    def test_is_valid_operator(self):
        """is_valid_operator works correctly."""
        assert is_valid_operator('=>') is True
        assert is_valid_operator('~>') is True
        assert is_valid_operator('>>>') is False


class TestBoundaryRules:
    """Tests for BOUNDARY_RULES definitions."""

    def test_boundary_rules_exist(self):
        """Verify boundary rules are defined."""
        assert len(BOUNDARY_RULES) > 0

    def test_view_cannot_data_flow(self):
        """V: cannot use data flow operators."""
        view_rules = [r for r in BOUNDARY_RULES if r.get('from') == 'V']
        blocked_ops = [r['operator'] for r in view_rules if not r['allowed']]
        assert '=>' in blocked_ops
        assert '~>' in blocked_ops
        assert '->' in blocked_ops
        assert '!>' in blocked_ops

    def test_cmp_cannot_access_mdl(self):
        """CMP cannot directly access MDL."""
        rule = next((r for r in BOUNDARY_RULES 
                     if r.get('from') == 'CMP' and r.get('to') == 'MDL'), None)
        assert rule is not None
        assert rule['allowed'] is False


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_agent_glyphs(self):
        """get_agent_glyphs returns glyphs with agents."""
        agents = get_agent_glyphs()
        assert 'CMP' in agents
        assert 'API' in agents
        assert 'MDL' in agents
        # Meta glyphs should not be included
        assert 'NED' not in agents
        assert 'OUT' not in agents

    def test_get_meta_glyphs(self):
        """get_meta_glyphs returns meta layer glyphs."""
        meta = get_meta_glyphs()
        assert 'NED' in meta
        assert 'TSK' in meta
        assert 'OUT' in meta
        assert 'ERR' in meta
        # Non-meta should not be included
        assert 'CMP' not in meta
        assert 'API' not in meta
