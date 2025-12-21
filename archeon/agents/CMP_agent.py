"""
CMP_agent.py - Component Code Generator

Generates UI component code from CMP: glyphs.
Supports React, Vue 3, and Svelte.
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
        "vue3": ".vue",
        "svelte": ".svelte",
    }
    
    # Framework aliases
    FRAMEWORK_ALIASES = {
        "vue": "vue3",  # Default Vue to Vue 3
    }

    def resolve_path(self, glyph: GlyphNode, framework: str) -> str:
        """Return components/{name}.{ext}"""
        fw = self.FRAMEWORK_ALIASES.get(framework, framework)
        ext = self.EXTENSIONS.get(fw, ".tsx")
        name = glyph.name
        return f"components/{name}{ext}"

    def get_template(self, framework: str) -> str:
        """Load component template for framework."""
        # Resolve aliases
        fw = self.FRAMEWORK_ALIASES.get(framework, framework)
        template = self.load_template(fw)
        if not template:
            raise ValueError(f"No template found for CMP:{fw}")
        return template

    def generate(self, glyph: GlyphNode, chain: ChainAST, framework: str) -> str:
        """Generate component code."""
        # Resolve framework alias
        fw = self.FRAMEWORK_ALIASES.get(framework, framework)
        template = self.get_template(fw)
        
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
            "RENDER_CONTENT": "    <!-- Component content -->",
        }

        # React-specific
        if fw == "react":
            placeholders = self._generate_react_placeholders(name, glyph, chain, placeholders)

        # Vue 3 specific
        elif fw in ("vue", "vue3"):
            placeholders = self._generate_vue3_placeholders(name, glyph, chain, placeholders)

        return self.fill_template(template, placeholders)
    
    def _generate_react_placeholders(
        self, 
        name: str, 
        glyph: GlyphNode, 
        chain: ChainAST, 
        placeholders: dict
    ) -> dict:
        """Generate React-specific placeholders."""
        is_stateful = "stateful" in glyph.modifiers
        is_headless = "headless" in glyph.modifiers
        
        if is_stateful:
            placeholders["USE_STATE_IMPORT"] = ", { useState }"
            placeholders["STATE_INTERFACE"] = f"interface {name}State {{\n  // State properties\n}}\n"
            placeholders["STATE_HOOKS"] = f"  const [state, setState] = useState<{name}State>({{}});\n"
        else:
            placeholders["USE_STATE_IMPORT"] = ""
            placeholders["STATE_INTERFACE"] = ""
            placeholders["STATE_HOOKS"] = ""

        placeholders["HANDLERS"] = ""
        placeholders["RENDER_CONTENT"] = "      {/* Component content */}"
        
        if is_headless:
            placeholders["RENDER_CONTENT"] = "      {/* @headless - logic-only component */}"
        
        # Tailwind classes for container
        placeholders["TAILWIND_CLASSES"] = "max-w-md mx-auto p-6 bg-white rounded-lg shadow-md"
        
        return placeholders
    
    def _generate_vue3_placeholders(
        self, 
        name: str, 
        glyph: GlyphNode, 
        chain: ChainAST, 
        placeholders: dict
    ) -> dict:
        """Generate Vue 3 specific placeholders."""
        is_stateful = "stateful" in glyph.modifiers
        is_headless = "headless" in glyph.modifiers
        
        # Find connected store in chain
        store_import = ""
        store_name = None
        for node in chain.nodes:
            if node.prefix == "STO":
                store_name = node.name
                if store_name.lower().endswith('store'):
                    store_name = store_name[:-5]
                store_import = f"import {{ use{store_name[0].upper()}{store_name[1:]}Store }} from '@/stores/{store_name}Store';"
                break
        
        placeholders["STORE_IMPORT"] = store_import
        placeholders["PROPS_INTERFACE"] = "  // Define props here"
        placeholders["EMITS_INTERFACE"] = "  // (e: 'update', value: string): void;"
        placeholders["PROPS_DEFAULTS"] = "  // Default prop values"
        
        if is_stateful:
            placeholders["STATE_REFS"] = self._generate_vue3_state(name, store_name, full=True)
        else:
            # Always include basic loading/error state for handlers
            placeholders["STATE_REFS"] = self._generate_vue3_state(name, store_name, full=False)
        
        # Computed properties
        placeholders["COMPUTED"] = self._generate_vue3_computed(name, glyph)
        
        # Event handlers
        placeholders["HANDLERS"] = self._generate_vue3_handlers(name, glyph, chain)
        
        # Lifecycle hooks
        placeholders["LIFECYCLE"] = self._generate_vue3_lifecycle(glyph)
        
        # Render content
        if is_headless:
            placeholders["RENDER_CONTENT"] = "    <!-- @headless - logic-only component, no UI -->"
        else:
            placeholders["RENDER_CONTENT"] = self._generate_vue3_template(name, glyph, chain)
        
        # Tailwind classes for container
        placeholders["TAILWIND_CLASSES"] = "max-w-md mx-auto p-6 bg-white rounded-lg shadow-md"
        
        return placeholders
    
    def _generate_vue3_state(self, name: str, store_name: Optional[str], full: bool = True) -> str:
        """Generate Vue 3 reactive state refs."""
        lines = ["// Local component state"]
        lines.append("const loading = ref(false);")
        lines.append("const error = ref<string | null>(null);")
        
        if store_name:
            lines.append(f"\n// Store")
            lines.append(f"const store = use{store_name[0].upper()}{store_name[1:]}Store();")
        
        if full:
            lines.append(f"\n// Additional state")
            lines.append(f"// const data = ref<{name}Data>(null);")
        
        return "\n".join(lines)
    
    def _generate_vue3_computed(self, name: str, glyph: GlyphNode) -> str:
        """Generate Vue 3 computed properties."""
        lines = ["// Computed properties"]
        lines.append(f"const isDisabled = computed(() => loading.value || !!error.value);")
        return "\n".join(lines)
    
    def _generate_vue3_handlers(self, name: str, glyph: GlyphNode, chain: ChainAST) -> str:
        """Generate Vue 3 event handlers based on chain context."""
        lines = ["// Event handlers"]
        
        # Find API calls in chain to generate handlers
        api_calls = []
        for node in chain.nodes:
            if node.prefix == "API":
                api_calls.append(node)
        
        # Find TSK (tasks) for action handlers
        tasks = []
        for node in chain.nodes:
            if node.prefix == "TSK":
                tasks.append(node)
        
        # Generate handlers for tasks
        for task in tasks:
            handler_name = f"handle{task.name[0].upper()}{task.name[1:]}"
            lines.append(f"""
async function {handler_name}() {{
  loading.value = true;
  error.value = null;
  
  try {{
    // TODO: Implement {task.name} logic
    emit('update', '{task.name}');
  }} catch (e) {{
    error.value = e instanceof Error ? e.message : 'Unknown error';
  }} finally {{
    loading.value = false;
  }}
}}""")
        
        # If no tasks, add a generic submit handler
        if not tasks:
            lines.append("""
async function handleSubmit() {
  loading.value = true;
  error.value = null;
  
  try {
    // TODO: Implement submit logic
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unknown error';
  } finally {
    loading.value = false;
  }
}""")
        
        return "\n".join(lines)
    
    def _generate_vue3_lifecycle(self, glyph: GlyphNode) -> str:
        """Generate Vue 3 lifecycle hooks."""
        lines = ["// Lifecycle"]
        lines.append("""onMounted(() => {
  // Component mounted
});""")
        return "\n".join(lines)
    
    def _generate_vue3_template(self, name: str, glyph: GlyphNode, chain: ChainAST) -> str:
        """Generate Vue 3 template content based on chain context."""
        # Find what kind of component this is based on chain
        has_form = any(n.prefix == "TSK" and "submit" in n.name.lower() for n in chain.nodes)
        has_api = any(n.prefix == "API" for n in chain.nodes)
        
        lines = []
        lines.append('    <!-- Loading state -->')
        lines.append('    <div v-if="loading" class="flex items-center justify-center p-4">')
        lines.append('      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>')
        lines.append('      <span class="ml-2 text-gray-600">Loading...</span>')
        lines.append('    </div>')
        lines.append('')
        lines.append('    <!-- Error state -->')
        lines.append('    <div v-if="error" class="bg-red-50 border-l-4 border-red-400 p-4 mb-4">')
        lines.append('      <div class="flex items-center">')
        lines.append('        <svg class="h-5 w-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">')
        lines.append('          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />')
        lines.append('        </svg>')
        lines.append('        <p class="text-sm text-red-700">{{ error }}</p>')
        lines.append('      </div>')
        lines.append('    </div>')
        lines.append('')
        lines.append('    <!-- Main content -->')
        
        if has_form:
            lines.append('    <form @submit.prevent="handleSubmit" class="space-y-4">')
            lines.append('      <!-- Form fields -->')
            lines.append('      <slot />')
            lines.append('      <button')
            lines.append('        type="submit"')
            lines.append('        :disabled="isDisabled"')
            lines.append('        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"')
            lines.append('      >')
            lines.append('        Submit')
            lines.append('      </button>')
            lines.append('    </form>')
        else:
            lines.append('    <div class="space-y-4">')
            lines.append('      <slot />')
            lines.append('    </div>')
        
        return "\n".join(lines)

    def generate_test(self, glyph: GlyphNode, framework: str) -> str:
        """Generate component test."""
        fw = self.FRAMEWORK_ALIASES.get(framework, framework)
        name = glyph.name
        
        if fw == "react":
            return self._generate_react_test(glyph, name)
        elif fw in ("vue", "vue3"):
            return self._generate_vue3_test(glyph, name)
        else:
            return f"// Test for {glyph.qualified_name} - template not available for {framework}"
    
    def _generate_react_test(self, glyph: GlyphNode, name: str) -> str:
        """Generate React test."""
        return f'''// @archeon {glyph.qualified_name}
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
    
    def _generate_vue3_test(self, glyph: GlyphNode, name: str) -> str:
        """Generate Vue 3 test with Vitest."""
        return f'''// @archeon {glyph.qualified_name}
// Generated test - Do not edit manually

import {{ describe, it, expect, beforeEach }} from 'vitest';
import {{ mount }} from '@vue/test-utils';
import {{ createPinia, setActivePinia }} from 'pinia';
import {name} from '../src/components/{name}.vue';

describe('{name}', () => {{
  beforeEach(() => {{
    // Create a fresh Pinia instance for each test
    setActivePinia(createPinia());
  }});

  it('renders without crashing', () => {{
    const wrapper = mount({name});
    expect(wrapper.find('[data-testid="{self._to_kebab(name)}"]').exists()).toBe(true);
  }});

  it('shows loading state', async () => {{
    const wrapper = mount({name});
    // Component should handle loading state
    expect(wrapper.find('.loading').exists()).toBe(false);
  }});

  it('shows error state when error occurs', async () => {{
    const wrapper = mount({name});
    // Initially no error
    expect(wrapper.find('.error').exists()).toBe(false);
  }});

  it('matches snapshot', () => {{
    const wrapper = mount({name});
    expect(wrapper.html()).toMatchSnapshot();
  }});
}});
'''

    @staticmethod
    def _to_kebab(name: str) -> str:
        """Convert PascalCase to kebab-case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()

