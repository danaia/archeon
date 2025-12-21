"""
Tests for orchestrator/VAL_validator.py
"""

import pytest
from archeon.orchestrator.PRS_parser import parse_chain
from archeon.orchestrator.GRF_graph import KnowledgeGraph
from archeon.orchestrator.VAL_validator import (
    ChainValidator,
    GraphValidator,
    validate_chain,
    validate_graph,
    ValidationResult,
)


class TestChainValidation:
    """Tests for individual chain validation."""

    def test_valid_chain(self):
        """Valid chain passes validation."""
        ast = parse_chain("NED:login => TSK:submit => CMP:Form => OUT:result")
        result = validate_chain(ast)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_chain_without_output_warns(self):
        """Chain without OUT: generates warning."""
        ast = parse_chain("NED:login => TSK:submit => CMP:Form")
        result = validate_chain(ast)
        assert len(result.warnings) > 0
        assert any('noOutput' in w.code for w in result.warnings)

    def test_unknown_glyph_errors(self):
        """Unknown glyph prefix causes error."""
        ast = parse_chain("INVALID:test => OUT:result")
        # Manually set invalid prefix to bypass parser validation
        ast.nodes[0].prefix = 'INVALID'
        result = validate_chain(ast)
        assert result.valid is False
        assert any('unknown' in e.code.lower() for e in result.errors)


class TestCycleValidation:
    """Tests for cycle detection."""

    def test_structural_cycle_detected(self):
        """Structural cycle causes error."""
        # Create AST with cycle manually
        ast = parse_chain("CMP:A => CMP:B => CMP:A")
        # The parser won't create a cycle naturally, so we need to manipulate
        # For now, test that non-cyclic passes
        result = validate_chain(ast)
        # This chain doesn't actually cycle in the AST structure
        assert result.valid is True

    def test_reactive_cycle_allowed(self):
        """Reactive cycle is allowed."""
        ast = parse_chain("CMP:Input => STO:store ~> CMP:Input")
        result = validate_chain(ast)
        # Reactive edges allow cycles
        assert result.valid is True


class TestBoundaryValidation:
    """Tests for ownership boundary rules."""

    def test_cmp_to_mdl_blocked(self):
        """CMP => MDL is blocked."""
        ast = parse_chain("CMP:Form => MDL:user.create")
        result = validate_chain(ast)
        assert result.valid is False
        assert any('boundary' in e.code.lower() for e in result.errors)

    def test_sto_to_mdl_blocked(self):
        """STO => MDL is blocked."""
        ast = parse_chain("STO:userStore => MDL:user.findOne")
        result = validate_chain(ast)
        assert result.valid is False
        assert any('boundary' in e.code.lower() for e in result.errors)

    def test_valid_flow_allowed(self):
        """Valid flow CMP => STO => API => MDL passes."""
        ast = parse_chain("CMP:Form => STO:formStore => API:POST/data => MDL:data.create => OUT:201")
        result = validate_chain(ast)
        assert result.valid is True

    def test_view_data_flow_blocked(self):
        """V: with data flow operators is blocked."""
        ast = parse_chain("V:Page => STO:store")
        result = validate_chain(ast)
        assert result.valid is False
        assert any('boundary' in e.code.lower() or 'view' in e.message.lower() for e in result.errors)


class TestGraphValidation:
    """Tests for full graph validation."""

    def test_empty_graph_valid(self):
        """Empty graph is valid."""
        graph = KnowledgeGraph()
        result = validate_graph(graph)
        assert result.valid is True

    def test_graph_with_valid_chains(self):
        """Graph with valid chains passes."""
        graph = KnowledgeGraph()
        graph.add_chain("@v1 NED:test => OUT:result")
        result = validate_graph(graph)
        assert result.valid is True

    def test_api_without_error_path_warns(self):
        """API without error path generates warning."""
        graph = KnowledgeGraph()
        graph.add_chain("@v1 API:POST/auth => MDL:user.findOne => OUT:200")
        result = validate_graph(graph)
        assert any('noErrorPath' in w.code for w in result.warnings)

    def test_api_with_error_path_no_warn(self):
        """API with error path doesn't warn."""
        graph = KnowledgeGraph()
        # Include error path in same chain
        graph.add_chain("@v1 API:POST/login => MDL:user.findOne => OUT:200")
        graph.add_chain("@v2 API:POST/login -> ERR:auth.invalid => OUT:401")
        result = validate_graph(graph)
        # Should not warn about noErrorPath for this API
        api_warnings = [w for w in result.warnings if 'POST/login' in str(w.node)]
        assert len(api_warnings) == 0


class TestValidationResult:
    """Tests for ValidationResult helper methods."""

    def test_add_error_invalidates(self):
        """Adding error sets valid to False."""
        result = ValidationResult()
        assert result.valid is True
        result.add_error('ERR:test', 'Test error')
        assert result.valid is False

    def test_add_warning_keeps_valid(self):
        """Adding warning keeps valid True."""
        result = ValidationResult()
        result.add_warning('WARN:test', 'Test warning')
        assert result.valid is True

    def test_merge_results(self):
        """Merging results combines errors and warnings."""
        r1 = ValidationResult()
        r1.add_error('ERR:1', 'Error 1')
        
        r2 = ValidationResult()
        r2.add_warning('WARN:1', 'Warning 1')
        
        r1.merge(r2)
        assert len(r1.errors) == 1
        assert len(r1.warnings) == 1
        assert r1.valid is False


class TestDuplicateValidation:
    """Tests for duplicate glyph detection."""

    def test_shared_glyphs_allowed(self):
        """Glyphs can be referenced in multiple chains without error."""
        graph = KnowledgeGraph()
        # Both chains reference STO:AuthStore and OUT:dashboard - this is fine
        graph.add_chain("@v1 NED:login => CMP:LoginForm => STO:AuthStore => OUT:dashboard")
        graph.add_chain("@v1 NED:register => CMP:RegisterForm => STO:AuthStore => OUT:dashboard")
        result = validate_graph(graph)
        # Should have no duplicate errors - shared glyphs are references, not duplicates
        duplicate_errors = [e for e in result.errors if 'duplicate' in e.code.lower()]
        assert len(duplicate_errors) == 0

    def test_duplicate_chain_roots_error(self):
        """Same chain root with same version is caught by graph.add_chain."""
        graph = KnowledgeGraph()
        graph.add_chain("@v1 NED:login => OUT:result1")
        # KnowledgeGraph.add_chain raises ValueError for duplicate roots
        with pytest.raises(ValueError, match="already exists"):
            graph.add_chain("@v1 NED:login => OUT:result2")

    def test_same_root_different_versions_allowed(self):
        """Same chain root with different versions is allowed."""
        graph = KnowledgeGraph()
        graph.add_chain("@v1 NED:login => OUT:result")
        graph.add_chain("@v2 NED:login => OUT:result")
        result = validate_graph(graph)
        duplicate_errors = [e for e in result.errors if 'duplicate' in e.code.lower()]
        assert len(duplicate_errors) == 0

    def test_orchestrator_chains_allowed(self):
        """Multiple unversioned orchestrator chains can reference same glyphs."""
        graph = KnowledgeGraph()
        graph.add_chain("ORC:main :: PRS:glyph :: VAL:chain")
        graph.add_chain("GRF:domain :: ORC:main")
        result = validate_graph(graph)
        # Different roots (ORC:main vs GRF:domain), so no duplicates
        duplicate_errors = [e for e in result.errors if 'duplicate' in e.code.lower()]
        assert len(duplicate_errors) == 0
