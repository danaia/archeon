"""
FNC_agent.py - Function Code Generator

Generates function/utility code from FNC: glyphs.
"""

import re
from pathlib import Path
from typing import Optional

from archeon.agents.base_agent import BaseAgent
from archeon.orchestrator.PRS_parser import GlyphNode, ChainAST


class FNCAgent(BaseAgent):
    """Agent for generating functions."""

    prefix = "FNC"

    # Namespace to path mapping
    NAMESPACE_PATHS = {
        "auth": "lib/auth",
        "validation": "lib/validation",
        "ui": "lib/ui",
        "utils": "lib/utils",
        "email": "lib/email",
        "crypto": "lib/crypto",
    }

    def resolve_path(self, glyph: GlyphNode, framework: str) -> str:
        """Return lib/{namespace}.{ext}"""
        namespace = glyph.namespace or "utils"
        base_path = self.NAMESPACE_PATHS.get(namespace, f"lib/{namespace}")
        
        # Determine extension based on framework
        # React uses TypeScript, Vue uses plain JavaScript
        if framework in ("react", "typescript"):
            return f"{base_path}.ts"
        elif framework in ("vue", "vue3"):
            return f"{base_path}.js"
        return f"{base_path}.py"

    def get_template(self, framework: str) -> str:
        """Load function template for framework."""
        # Map frameworks to template names
        # React uses TypeScript, Vue uses plain JavaScript (same template, different extension)
        if framework in ("fastapi", "python", "mongo"):
            template_name = "python"
        else:
            template_name = "typescript"  # JS/TS share same template structure
        template = self.load_template(template_name)
        if not template:
            raise ValueError(f"No template found for FNC:{framework}")
        return template

    def generate(self, glyph: GlyphNode, chain: ChainAST, framework: str) -> str:
        """Generate function code."""
        template = self.get_template(framework)
        
        func_name = self._extract_function_name(glyph)
        namespace = glyph.namespace or "utils"
        
        # React uses TypeScript types, Vue uses plain JavaScript
        is_typescript = framework in ("react", "typescript")

        placeholders = {
            "GLYPH_QUALIFIED_NAME": glyph.qualified_name,
            "IMPORTS": "",
            "FUNCTION_NAME": func_name,
            "PARAMETERS": self._build_parameters(is_typescript),
            "RETURN_TYPE": "any" if is_typescript else "Any",
            "DOCSTRING": f"Function for {glyph.qualified_name}",
            "ARGS_DOC": "        (define arguments)",
            "RETURN_DOC": "(define return value)",
            "PARAMS_DOC": " * @param input - Input parameter",
            "FUNCTION_BODY": self._build_body(is_typescript),
        }

        return self.fill_template(template, placeholders)

    def generate_test(self, glyph: GlyphNode, framework: str) -> str:
        """Generate function test."""
        func_name = self._extract_function_name(glyph)
        namespace = glyph.namespace or "utils"
        # React uses TypeScript, Vue uses plain JavaScript
        is_typescript = framework in ("react", "typescript")

        if is_typescript or framework in ("vue", "vue3"):
            test_content = f'''// @archeon {glyph.qualified_name}
// Generated test - Do not edit manually

import {{ {func_name} }} from '../lib/{namespace}';

describe('{func_name}', () => {{
  it('returns expected output', () => {{
    const result = {func_name}();
    expect(result).toBeDefined();
  }});

  it('handles edge cases', () => {{
    // TODO: Add edge case tests
  }});
}});
'''
        else:
            test_content = f'''# @archeon {glyph.qualified_name}
# Generated test - Do not edit manually

import pytest
from lib.{namespace} import {func_name}


def test_{func_name}_basic():
    """Test {func_name} returns expected output."""
    result = {func_name}()
    assert result is not None


def test_{func_name}_edge_cases():
    """Test {func_name} handles edge cases."""
    # TODO: Add edge case tests
    pass
'''
        return test_content

    def _extract_function_name(self, glyph: GlyphNode) -> str:
        """Extract function name from glyph."""
        if glyph.action:
            return self._to_snake_case(glyph.action)
        if '.' in glyph.name:
            return self._to_snake_case(glyph.name.split('.')[1])
        return self._to_snake_case(glyph.name)

    def _build_parameters(self, is_typescript: bool) -> str:
        """Build function parameters."""
        if is_typescript:
            return "input?: any"
        return "input: Any = None"

    def _build_body(self, is_typescript: bool) -> str:
        """Build function body placeholder."""
        if is_typescript:
            return "  // TODO: Implement function logic\n  return input;"
        return "    # TODO: Implement function logic\n    return input"

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert camelCase/PascalCase to snake_case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
