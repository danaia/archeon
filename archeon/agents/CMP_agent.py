"""
CMP_agent.py - Component Code Generator

Generates UI component code from CMP: glyphs.
"""

import re
from pathlib import Path
from typing import Optional

from archeon.agents.base_agent import BaseAgent
from archeon.orchestrator.PRS_parser import GlyphNode, ChainAST


class CMPAgent(BaseAgent):
    """Agent for generating UI components."""

    prefix = "CMP"

    # Framework to file extension mapping
    EXTENSIONS = {
        "react": ".tsx",
        "vue": ".vue",
        "svelte": ".svelte",
    }

    def resolve_path(self, glyph: GlyphNode, framework: str) -> str:
        """Return components/{name}.{ext}"""
        ext = self.EXTENSIONS.get(framework, ".tsx")
        name = glyph.name
        return f"components/{name}{ext}"

    def get_template(self, framework: str) -> str:
        """Load component template for framework."""
        template = self.load_template(framework)
        if not template:
            raise ValueError(f"No template found for CMP:{framework}")
        return template

    def generate(self, glyph: GlyphNode, chain: ChainAST, framework: str) -> str:
        """Generate component code."""
        template = self.get_template(framework)
        
        # Build placeholders
        name = glyph.name
        is_stateful = "stateful" in glyph.modifiers
        is_headless = "headless" in glyph.modifiers
        is_presentational = "presentational" in glyph.modifiers

        placeholders = {
            "GLYPH_QUALIFIED_NAME": glyph.qualified_name,
            "COMPONENT_NAME": name,
            "COMPONENT_NAME_KEBAB": self._to_kebab(name),
            "IMPORTS": "",
            "PROPS_INTERFACE": "  // Props will be defined based on chain context",
            "PROPS_DESTRUCTURE": "props",
            "RENDER_CONTENT": "      {/* Component content */}",
        }

        # React-specific
        if framework == "react":
            if is_stateful:
                placeholders["USE_STATE_IMPORT"] = ", { useState }"
                placeholders["STATE_INTERFACE"] = f"interface {name}State {{\n  // State properties\n}}\n"
                placeholders["STATE_HOOKS"] = "  const [state, setState] = useState<" + name + "State>({});\n"
            else:
                placeholders["USE_STATE_IMPORT"] = ""
                placeholders["STATE_INTERFACE"] = ""
                placeholders["STATE_HOOKS"] = ""

            placeholders["HANDLERS"] = ""
            
            if is_headless:
                placeholders["RENDER_CONTENT"] = "      {/* @headless - logic-only component */}"

        # Vue-specific
        elif framework == "vue":
            if is_stateful:
                placeholders["STATE_REFS"] = f"const state = ref<{name}State>({{}});"
            else:
                placeholders["STATE_REFS"] = ""
            placeholders["HANDLERS"] = ""
            placeholders["STYLES"] = ""

        return self.fill_template(template, placeholders)

    def generate_test(self, glyph: GlyphNode, framework: str) -> str:
        """Generate component test."""
        name = glyph.name
        
        if framework == "react":
            test_content = f'''// @archeon {glyph.qualified_name}
// Generated test - Do not edit manually

import {{ render, screen }} from '@testing-library/react';
import {{ {name} }} from '../components/{name}';

describe('{name}', () => {{
  it('renders without crashing', () => {{
    render(<{name} />);
    expect(screen.getByTestId('{self._to_kebab(name)}')).toBeInTheDocument();
  }});

  it('matches snapshot', () => {{
    const {{ container }} = render(<{name} />);
    expect(container.firstChild).toMatchSnapshot();
  }});
}});
'''
        elif framework == "vue":
            test_content = f'''// @archeon {glyph.qualified_name}
// Generated test - Do not edit manually

import {{ mount }} from '@vue/test-utils';
import {name} from '../components/{name}.vue';

describe('{name}', () => {{
  it('renders without crashing', () => {{
    const wrapper = mount({name});
    expect(wrapper.find('[data-testid="{self._to_kebab(name)}"]').exists()).toBe(true);
  }});

  it('matches snapshot', () => {{
    const wrapper = mount({name});
    expect(wrapper.html()).toMatchSnapshot();
  }});
}});
'''
        else:
            test_content = f"// Test for {glyph.qualified_name} - template not available for {framework}"

        return test_content

    @staticmethod
    def _to_kebab(name: str) -> str:
        """Convert PascalCase to kebab-case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
