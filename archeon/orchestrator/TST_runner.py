"""
TST_runner.py - Archeon Test Generator & Runner

Generates chain-level integration tests from glyph chains.
Walks from NED: → OUT: generating test steps for each glyph.
"""

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from archeon.orchestrator.PRS_parser import ChainAST, GlyphNode, Edge
from archeon.orchestrator.GRF_graph import KnowledgeGraph, StoredChain
from archeon.config.legend import GLYPH_LEGEND


@dataclass
class TestStep:
    """A single step in a generated test."""
    glyph: str
    action: str
    assertion: str
    comment: str = ""


@dataclass
class GeneratedTest:
    """A generated test file."""
    name: str
    path: str
    content: str
    chain_version: Optional[str] = None
    is_error_path: bool = False


@dataclass
class TestResult:
    """Result of running a test."""
    name: str
    passed: bool
    output: str = ""
    error: str = ""
    duration_ms: float = 0


@dataclass
class RunResult:
    """Batch test run results."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    results: list[TestResult] = field(default_factory=list)
    
    @property
    def success(self) -> bool:
        return self.failed == 0 and self.errors == 0


class TestGenerator:
    """Generate pytest tests from chains."""
    
    def __init__(self, output_dir: str = "tests/generated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_happy_path_test(self, chain: ChainAST) -> GeneratedTest:
        """Generate a happy path test that walks NED: → OUT:."""
        # Find the root glyph (first node)
        if not chain.nodes:
            raise ValueError("Empty chain")
        
        root = chain.nodes[0]
        root_name = self._extract_name(root.qualified_name)
        test_name = f"test_{root_name}_happy_path"
        
        # Build test steps from chain
        steps = self._build_test_steps(chain, is_error_path=False)
        
        # Generate test content
        content = self._render_test(
            test_name=test_name,
            chain_raw=chain.raw,
            steps=steps,
            version=chain.version,
            is_error_path=False
        )
        
        path = self.output_dir / f"test_{root_name}.py"
        
        return GeneratedTest(
            name=test_name,
            path=str(path),
            content=content,
            chain_version=chain.version,
            is_error_path=False
        )
    
    def generate_error_path_test(self, chain: ChainAST, error_glyph: str) -> GeneratedTest:
        """Generate an error path test for ERR: branches."""
        root = chain.nodes[0] if chain.nodes else None
        if not root:
            raise ValueError("Empty chain")
        
        root_name = self._extract_name(root.qualified_name)
        error_name = self._extract_name(error_glyph)
        test_name = f"test_{root_name}_error_{error_name}"
        
        # Build steps leading to error
        steps = self._build_error_steps(chain, error_glyph)
        
        content = self._render_test(
            test_name=test_name,
            chain_raw=chain.raw,
            steps=steps,
            version=chain.version,
            is_error_path=True,
            error_glyph=error_glyph
        )
        
        path = self.output_dir / f"test_{root_name}_errors.py"
        
        return GeneratedTest(
            name=test_name,
            path=str(path),
            content=content,
            chain_version=chain.version,
            is_error_path=True
        )
    
    def generate_from_chain(self, chain: ChainAST) -> list[GeneratedTest]:
        """Generate all tests for a chain (happy + error paths)."""
        tests = []
        
        # Happy path
        try:
            tests.append(self.generate_happy_path_test(chain))
        except ValueError:
            pass
        
        # Error paths - find all ERR: nodes
        for node in chain.nodes:
            if node.prefix == "ERR":
                try:
                    tests.append(self.generate_error_path_test(chain, node.qualified_name))
                except ValueError:
                    pass
        
        return tests
    
    def generate_from_graph(self, graph: KnowledgeGraph) -> list[GeneratedTest]:
        """Generate tests for all chains in the graph."""
        tests = []
        seen_chains = set()
        
        for stored in graph.chains:
            chain_key = stored.ast.raw
            if chain_key in seen_chains:
                continue
            seen_chains.add(chain_key)
            
            # Skip orchestrator internal chains
            if stored.ast.nodes and stored.ast.nodes[0].prefix in ("ORC", "GRF", "PRS", "VAL", "SPW", "TST"):
                continue
            
            tests.extend(self.generate_from_chain(stored.ast))
        
        return tests
    
    def write_tests(self, tests: list[GeneratedTest]) -> list[str]:
        """Write generated tests to files."""
        written = []
        
        # Group tests by file path
        by_file: dict[str, list[GeneratedTest]] = {}
        for test in tests:
            if test.path not in by_file:
                by_file[test.path] = []
            by_file[test.path].append(test)
        
        for path, file_tests in by_file.items():
            # Combine tests into single file
            content = self._combine_tests(file_tests)
            
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_text(content)
            written.append(path)
        
        return written
    
    def _build_test_steps(self, chain: ChainAST, is_error_path: bool) -> list[TestStep]:
        """Build test steps from chain nodes."""
        steps = []
        
        for node in chain.nodes:
            step = self._glyph_to_step(node, is_error_path)
            if step:
                steps.append(step)
        
        return steps
    
    def _build_error_steps(self, chain: ChainAST, error_glyph: str) -> list[TestStep]:
        """Build steps leading to an error path."""
        steps = []
        found_error = False
        
        # Walk chain until we hit the error glyph
        for node in chain.nodes:
            step = self._glyph_to_step(node, is_error_path=True)
            if step:
                steps.append(step)
            
            if node.qualified_name == error_glyph:
                found_error = True
                break
        
        if not found_error:
            # Look for error in edges (branching)
            for edge in chain.edges:
                if edge.target == error_glyph:
                    steps.append(TestStep(
                        glyph=error_glyph,
                        action=f"# Trigger error condition for {error_glyph}",
                        assertion=f"assert response.status_code >= 400",
                        comment=f"Error path: {edge.source} -> {error_glyph}"
                    ))
                    break
        
        return steps
    
    def _glyph_to_step(self, node: GlyphNode, is_error_path: bool) -> Optional[TestStep]:
        """Convert a glyph node to a test step."""
        prefix = node.prefix
        name = self._extract_name(node.qualified_name)
        
        step_map = {
            "NED": TestStep(
                glyph=node.qualified_name,
                action=f"# User need: {name}",
                assertion="# Precondition setup",
                comment="Entry point"
            ),
            "TSK": TestStep(
                glyph=node.qualified_name,
                action=f"# User action: {name}",
                assertion="# Action triggered",
                comment="User task"
            ),
            "CMP": TestStep(
                glyph=node.qualified_name,
                action=f"component = render({name})",
                assertion=f"assert component is not None",
                comment=f"Render component"
            ),
            "STO": TestStep(
                glyph=node.qualified_name,
                action=f"store = get_store('{name}')",
                assertion="assert store.state is not None",
                comment="Access store"
            ),
            "FNC": TestStep(
                glyph=node.qualified_name,
                action=f"result = {name}(test_input)",
                assertion="assert result is not None",
                comment="Call function"
            ),
            "API": TestStep(
                glyph=node.qualified_name,
                action=f"response = client.{self._extract_method(node)}('{self._extract_route(node)}')",
                assertion="assert response.status_code == 200" if not is_error_path else "assert response.status_code >= 400",
                comment="API call"
            ),
            "MDL": TestStep(
                glyph=node.qualified_name,
                action=f"data = await db.{name}(query)",
                assertion="assert data is not None",
                comment="Database query"
            ),
            "EVT": TestStep(
                glyph=node.qualified_name,
                action=f"event = emit('{name}')",
                assertion="assert event.published",
                comment="Emit event"
            ),
            "OUT": TestStep(
                glyph=node.qualified_name,
                action=f"# Expected output: {node.args or name}",
                assertion=f"assert output == '{node.args or name}'",
                comment="Final assertion"
            ),
            "ERR": TestStep(
                glyph=node.qualified_name,
                action=f"# Error condition: {name}",
                assertion="assert error is not None",
                comment="Error assertion"
            ),
        }
        
        return step_map.get(prefix)
    
    def _extract_name(self, qualified_name: str) -> str:
        """Extract simple name from qualified name."""
        if ':' in qualified_name:
            after_prefix = qualified_name.split(':', 1)[1]
            # Handle namespace.action format
            if '.' in after_prefix:
                return after_prefix.split('.')[-1]
            return after_prefix
        return qualified_name
    
    def _extract_method(self, node: GlyphNode) -> str:
        """Extract HTTP method from API glyph."""
        name = node.name
        if '/' in name:
            method = name.split('/')[0].lower()
            if method in ('get', 'post', 'put', 'patch', 'delete'):
                return method
        return 'get'
    
    def _extract_route(self, node: GlyphNode) -> str:
        """Extract route from API glyph."""
        name = node.name
        if '/' in name:
            return '/' + '/'.join(name.split('/')[1:])
        return '/' + name
    
    def _render_test(
        self,
        test_name: str,
        chain_raw: str,
        steps: list[TestStep],
        version: Optional[str],
        is_error_path: bool,
        error_glyph: str = ""
    ) -> str:
        """Render a pytest test function."""
        lines = [
            '"""',
            f'@archeon {chain_raw}',
            f'@version {version or "v1"}',
            f'@type {"error_path" if is_error_path else "happy_path"}',
            '"""',
            '',
            'import pytest',
            '',
            '',
            f'def {test_name}():',
            f'    """',
            f'    Chain: {chain_raw[:60]}...' if len(chain_raw) > 60 else f'    Chain: {chain_raw}',
        ]
        
        if is_error_path:
            lines.append(f'    Error: {error_glyph}')
        
        lines.extend([
            '    """',
            '    # Test setup',
            '    test_input = {}',
            '',
        ])
        
        for step in steps:
            if step.comment:
                lines.append(f'    # {step.comment}')
            lines.append(f'    {step.action}')
            lines.append(f'    {step.assertion}')
            lines.append('')
        
        # Final assertion
        if not is_error_path:
            lines.append('    # Happy path completed')
            lines.append('    assert True, "Chain executed successfully"')
        else:
            lines.append('    # Error path validated')
            lines.append('    assert True, "Error handling verified"')
        
        lines.append('')
        
        return '\n'.join(lines)
    
    def _combine_tests(self, tests: list[GeneratedTest]) -> str:
        """Combine multiple tests into a single file."""
        header = [
            '"""',
            'Auto-generated Archeon integration tests.',
            '',
            'DO NOT EDIT - regenerate with: archeon test --generate',
            '"""',
            '',
            'import pytest',
            '',
            '# Test fixtures',
            '@pytest.fixture',
            'def test_input():',
            '    return {}',
            '',
            '@pytest.fixture',
            'def client():',
            '    """HTTP test client."""',
            '    # TODO: Initialize test client',
            '    return None',
            '',
            '@pytest.fixture',
            'def db():',
            '    """Database test fixture."""',
            '    # TODO: Initialize test database',
            '    return None',
            '',
            '',
        ]
        
        body = []
        for test in tests:
            # Extract just the test function (skip imports)
            lines = test.content.split('\n')
            in_function = False
            for line in lines:
                if line.startswith('def test_'):
                    in_function = True
                if in_function:
                    body.append(line)
        
        return '\n'.join(header + body)


class TestRunner:
    """Run generated tests via pytest."""
    
    def __init__(self, test_dir: str = "tests/generated"):
        self.test_dir = Path(test_dir)
    
    def run_all(self, verbose: bool = False) -> RunResult:
        """Run all generated tests."""
        if not self.test_dir.exists():
            return RunResult(total=0, passed=0, failed=0, errors=1, results=[
                TestResult(name="setup", passed=False, error="No generated tests found")
            ])
        
        return self._run_pytest(str(self.test_dir), verbose)
    
    def run_chain(self, chain_name: str, verbose: bool = False) -> RunResult:
        """Run tests for a specific chain."""
        test_file = self.test_dir / f"test_{chain_name}.py"
        
        if not test_file.exists():
            return RunResult(total=0, passed=0, failed=0, errors=1, results=[
                TestResult(name=chain_name, passed=False, error=f"Test file not found: {test_file}")
            ])
        
        return self._run_pytest(str(test_file), verbose)
    
    def run_errors_only(self, verbose: bool = False) -> RunResult:
        """Run only error path tests."""
        return self._run_pytest(
            str(self.test_dir),
            verbose,
            extra_args=["-k", "error"]
        )
    
    def _run_pytest(
        self, 
        path: str, 
        verbose: bool,
        extra_args: list[str] | None = None
    ) -> RunResult:
        """Execute pytest and parse results."""
        cmd = ["python", "-m", "pytest", path, "--tb=short"]
        
        if verbose:
            cmd.append("-v")
        
        if extra_args:
            cmd.extend(extra_args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return self._parse_pytest_output(result.stdout, result.returncode)
            
        except subprocess.TimeoutExpired:
            return RunResult(
                total=0, passed=0, failed=0, errors=1,
                results=[TestResult(name="timeout", passed=False, error="Test execution timed out")]
            )
        except Exception as e:
            return RunResult(
                total=0, passed=0, failed=0, errors=1,
                results=[TestResult(name="error", passed=False, error=str(e))]
            )
    
    def _parse_pytest_output(self, output: str, return_code: int) -> RunResult:
        """Parse pytest output for results."""
        result = RunResult()
        result.results.append(TestResult(
            name="pytest",
            passed=return_code == 0,
            output=output
        ))
        
        # Parse summary line (e.g., "5 passed, 2 failed in 0.03s")
        for line in output.split('\n'):
            if 'passed' in line or 'failed' in line or 'error' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        try:
                            result.passed = int(parts[i-1])
                        except ValueError:
                            pass
                    elif part == 'failed' and i > 0:
                        try:
                            result.failed = int(parts[i-1])
                        except ValueError:
                            pass
                    elif part == 'error' and i > 0:
                        try:
                            result.errors = int(parts[i-1])
                        except ValueError:
                            pass
        
        result.total = result.passed + result.failed + result.errors
        return result
