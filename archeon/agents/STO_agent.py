"""
STO_agent.py - Store Code Generator

Generates client state store code from STO: glyphs.
"""

import re
from pathlib import Path
from typing import Optional

from archeon.agents.base_agent import BaseAgent
from archeon.orchestrator.PRS_parser import GlyphNode, ChainAST


class STOAgent(BaseAgent):
    """Agent for generating client state stores."""

    prefix = "STO"

    def resolve_path(self, glyph: GlyphNode, framework: str) -> str:
        """Return stores/{name}Store.ts"""
        name = glyph.name
        # Remove 'Store' suffix if present to avoid duplication
        if name.lower().endswith('store'):
            name = name[:-5]
        return f"stores/{name}Store.ts"

    def get_template(self, framework: str) -> str:
        """Load store template for framework."""
        template = self.load_template(framework)
        if not template:
            raise ValueError(f"No template found for STO:{framework}")
        return template

    def generate(self, glyph: GlyphNode, chain: ChainAST, framework: str) -> str:
        """Generate store code."""
        template = self.get_template(framework)
        
        name = glyph.name
        if name.lower().endswith('store'):
            name = name[:-5]
        store_name = f"{name[0].upper()}{name[1:]}"

        # Extract actions from chain context (look for action: syntax)
        actions = self._extract_actions(chain)

        placeholders = {
            "GLYPH_QUALIFIED_NAME": glyph.qualified_name,
            "STORE_NAME": store_name,
            "IMPORTS": "",
            "STATE_INTERFACE": "  // State properties",
            "ACTIONS_INTERFACE": self._build_actions_interface(actions),
            "INITIAL_STATE": "  // Initial values",
            "ACTIONS": self._build_actions(actions),
        }

        return self.fill_template(template, placeholders)

    def generate_test(self, glyph: GlyphNode, framework: str) -> str:
        """Generate store test."""
        name = glyph.name
        if name.lower().endswith('store'):
            name = name[:-5]
        store_name = f"{name[0].upper()}{name[1:]}"

        test_content = f'''// @archeon {glyph.qualified_name}
// Generated test - Do not edit manually

import {{ act, renderHook }} from '@testing-library/react';
import {{ use{store_name} }} from '../stores/{name}Store';

describe('{store_name}Store', () => {{
  beforeEach(() => {{
    // Reset store state before each test
    const {{ result }} = renderHook(() => use{store_name}());
    act(() => {{
      // Reset to initial state
    }});
  }});

  it('has initial state', () => {{
    const {{ result }} = renderHook(() => use{store_name}());
    expect(result.current).toBeDefined();
  }});
}});
'''
        return test_content

    def _extract_actions(self, chain: ChainAST) -> list[str]:
        """Extract action names from chain."""
        actions = []
        for node in chain.nodes:
            # Look for action args in the glyph
            if node.args:
                actions.extend(node.args)
        return actions if actions else ["update", "reset"]

    def _build_actions_interface(self, actions: list[str]) -> str:
        """Build TypeScript interface for actions."""
        lines = []
        for action in actions:
            lines.append(f"  {action}: () => void;")
        return "\n".join(lines) if lines else "  // No actions defined"

    def _build_actions(self, actions: list[str]) -> str:
        """Build Zustand action implementations."""
        lines = []
        for action in actions:
            lines.append(f"  {action}: () => {{")
            lines.append(f"    set((state) => ({{ ...state }}));")
            lines.append(f"  }},\n")
        return "\n".join(lines) if lines else "  // No actions defined"
