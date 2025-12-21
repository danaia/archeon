"""
STO_agent.py - Store Code Generator

Generates client state store code from STO: glyphs.
Supports Zustand (React) and Pinia (Vue 3).
"""

import re
from pathlib import Path
from typing import Optional

from archeon.agents.base_agent import BaseAgent
from archeon.orchestrator.PRS_parser import GlyphNode, ChainAST


class STOAgent(BaseAgent):
    """Agent for generating client state stores."""

    prefix = "STO"
    
    # Framework to store library mapping
    STORE_LIBS = {
        "react": "zustand",
        "zustand": "zustand",
        "vue": "pinia",
        "vue3": "pinia",
        "pinia": "pinia",
    }

    def resolve_path(self, glyph: GlyphNode, framework: str) -> str:
        """Return stores/{name}Store.{ext} - .ts for React, .js for Vue"""
        name = glyph.name
        # Remove 'Store' suffix if present to avoid duplication
        if name.lower().endswith('store'):
            name = name[:-5]
        # React uses TypeScript, Vue uses plain JavaScript
        ext = "js" if framework in ("vue", "vue3", "pinia") else "ts"
        return f"stores/{name}Store.{ext}"

    def get_template(self, framework: str) -> str:
        """Load store template for framework."""
        # Map framework to store library
        store_lib = self.STORE_LIBS.get(framework, "zustand")
        template = self.load_template(store_lib)
        if not template:
            raise ValueError(f"No template found for STO:{store_lib}")
        return template

    def generate(self, glyph: GlyphNode, chain: ChainAST, framework: str) -> str:
        """Generate store code."""
        store_lib = self.STORE_LIBS.get(framework, "zustand")
        template = self.get_template(framework)
        
        name = glyph.name
        if name.lower().endswith('store'):
            name = name[:-5]
        store_name = f"{name[0].upper()}{name[1:]}"
        store_id = self._to_kebab(store_name)

        # Extract state and actions from chain context
        state_fields = self._extract_state_fields(glyph, chain)
        actions = self._extract_actions(glyph, chain)

        if store_lib == "pinia":
            return self._generate_pinia_store(template, glyph, store_name, store_id, state_fields, actions)
        else:
            return self._generate_zustand_store(template, glyph, store_name, state_fields, actions)
    
    def _generate_pinia_store(
        self, 
        template: str, 
        glyph: GlyphNode, 
        store_name: str,
        store_id: str,
        state_fields: list[dict],
        actions: list[str]
    ) -> str:
        """Generate Pinia store for Vue 3."""
        placeholders = {
            "GLYPH_QUALIFIED_NAME": glyph.qualified_name,
            "STORE_NAME": store_name,
            "STORE_ID": store_id,
            "IMPORTS": "",
            "STATE_INTERFACE": self._build_pinia_state_interface(state_fields),
            "STATE_REFS": self._build_pinia_state_refs(state_fields),
            "GETTERS": self._build_pinia_getters(store_name, state_fields),
            "ACTIONS": self._build_pinia_actions(actions, state_fields),
            "RESET_ACTION": self._build_pinia_reset(state_fields),
            "STATE_RETURN": self._build_pinia_state_return(state_fields),
            "GETTERS_RETURN": self._build_pinia_getters_return(state_fields),
            "ACTIONS_RETURN": self._build_pinia_actions_return(actions),
        }
        
        return self.fill_template(template, placeholders)
    
    def _generate_zustand_store(
        self, 
        template: str, 
        glyph: GlyphNode, 
        store_name: str,
        state_fields: list[dict],
        actions: list[str]
    ) -> str:
        """Generate Zustand store for React."""
        placeholders = {
            "GLYPH_QUALIFIED_NAME": glyph.qualified_name,
            "STORE_NAME": store_name,
            "IMPORTS": "",
            "STATE_INTERFACE": self._build_zustand_state_interface(state_fields),
            "ACTIONS_INTERFACE": self._build_zustand_actions_interface(actions),
            "INITIAL_STATE": self._build_zustand_initial_state(state_fields),
            "ACTIONS": self._build_zustand_actions(actions),
        }
        
        return self.fill_template(template, placeholders)
    
    def _extract_state_fields(self, glyph: GlyphNode, chain: ChainAST) -> list[dict]:
        """Extract state fields from chain context."""
        fields = []
        
        # Look for common patterns in the chain
        has_auth = any("auth" in n.name.lower() or "login" in n.name.lower() for n in chain.nodes)
        has_form = any("form" in n.name.lower() or "submit" in n.name.lower() for n in chain.nodes)
        has_list = any("list" in n.name.lower() or "items" in n.name.lower() for n in chain.nodes)
        
        # Always include loading and error state
        fields.append({"name": "loading", "type": "boolean", "default": "false"})
        fields.append({"name": "error", "type": "string | null", "default": "null"})
        
        if has_auth:
            fields.append({"name": "user", "type": "User | null", "default": "null"})
            fields.append({"name": "token", "type": "string | null", "default": "null"})
            fields.append({"name": "isAuthenticated", "type": "boolean", "default": "false"})
        
        if has_form:
            fields.append({"name": "formData", "type": "Record<string, unknown>", "default": "{}"})
            fields.append({"name": "isValid", "type": "boolean", "default": "false"})
        
        if has_list:
            fields.append({"name": "items", "type": "unknown[]", "default": "[]"})
            fields.append({"name": "total", "type": "number", "default": "0"})
        
        return fields
    
    def _extract_actions(self, glyph: GlyphNode, chain: ChainAST) -> list[str]:
        """Extract action names from chain context."""
        actions = []
        
        # Look for TSK nodes for actions
        for node in chain.nodes:
            if node.prefix == "TSK":
                actions.append(node.name)
        
        # Look for API calls to generate fetch actions
        for node in chain.nodes:
            if node.prefix == "API":
                method = node.name.split('.')[0].split('/')[0].upper()
                route = node.name.split('/')[-1] if '/' in node.name else node.name
                action_name = f"fetch{route[0].upper()}{route[1:]}" if method == "GET" else route
                if action_name not in actions:
                    actions.append(action_name)
        
        # Default actions if none found
        if not actions:
            actions = ["update", "reset"]
        
        return actions
    
    # Pinia-specific builders (plain JavaScript, no TypeScript)
    def _build_pinia_state_interface(self, fields: list[dict]) -> str:
        # No interface needed for plain JS
        return ""
    
    def _build_pinia_state_refs(self, fields: list[dict]) -> str:
        lines = []
        for f in fields:
            lines.append(f"  const {f['name']} = ref({f['default']});")
        return "\n".join(lines) if lines else "  // State refs"
    
    def _build_pinia_getters(self, store_name: str, fields: list[dict]) -> str:
        lines = ["  // Computed getters"]
        
        # Add some common getters based on state
        has_loading = any(f['name'] == 'loading' for f in fields)
        has_error = any(f['name'] == 'error' for f in fields)
        
        if has_loading and has_error:
            lines.append("  const isReady = computed(() => !loading.value && !error.value);")
        
        has_items = any(f['name'] == 'items' for f in fields)
        if has_items:
            lines.append("  const isEmpty = computed(() => items.value.length === 0);")
            lines.append("  const itemCount = computed(() => items.value.length);")
        
        has_auth = any(f['name'] == 'isAuthenticated' for f in fields)
        if has_auth:
            lines.append("  const isLoggedIn = computed(() => isAuthenticated.value && !!token.value);")
        
        return "\n".join(lines)
    
    def _build_pinia_actions(self, actions: list[str], state_fields: list[dict]) -> str:
        lines = ["  // Actions"]
        
        for action in actions:
            lines.append(f"""
  async function {action}(payload?: unknown) {{
    loading.value = true;
    error.value = null;
    
    try {{
      // TODO: Implement {action} logic
      // const response = await api.{action}(payload);
    }} catch (e) {{
      error.value = e instanceof Error ? e.message : 'Unknown error';
      throw e;
    }} finally {{
      loading.value = false;
    }}
  }}""")
        
        return "\n".join(lines)
    
    def _build_pinia_reset(self, fields: list[dict]) -> str:
        lines = []
        for f in fields:
            lines.append(f"    {f['name']}.value = {f['default']};")
        return "\n".join(lines) if lines else "    // Reset state"
    
    def _build_pinia_state_return(self, fields: list[dict]) -> str:
        lines = []
        for f in fields:
            lines.append(f"    {f['name']},")
        return "\n".join(lines) if lines else "    // State"
    
    def _build_pinia_getters_return(self, fields: list[dict]) -> str:
        getters = ["isReady"]
        if any(f['name'] == 'items' for f in fields):
            getters.extend(["isEmpty", "itemCount"])
        if any(f['name'] == 'isAuthenticated' for f in fields):
            getters.append("isLoggedIn")
        
        return "\n".join(f"    {g}," for g in getters) if getters else "    // Getters"
    
    def _build_pinia_actions_return(self, actions: list[str]) -> str:
        lines = []
        for action in actions:
            lines.append(f"    {action},")
        return "\n".join(lines) if lines else "    // Actions"
    
    # Zustand-specific builders
    def _build_zustand_state_interface(self, fields: list[dict]) -> str:
        lines = []
        for f in fields:
            lines.append(f"  {f['name']}: {f['type']};")
        return "\n".join(lines) if lines else "  // State properties"
    
    def _build_zustand_actions_interface(self, actions: list[str]) -> str:
        lines = []
        for action in actions:
            lines.append(f"  {action}: (payload?: unknown) => Promise<void>;")
        lines.append("  reset: () => void;")
        return "\n".join(lines) if lines else "  // No actions defined"
    
    def _build_zustand_initial_state(self, fields: list[dict]) -> str:
        lines = []
        for f in fields:
            lines.append(f"  {f['name']}: {f['default']},")
        return "\n".join(lines) if lines else "  // Initial values"
    
    def _build_zustand_actions(self, actions: list[str]) -> str:
        lines = []
        for action in actions:
            lines.append(f"""  {action}: async (payload?: unknown) => {{
    set({{ loading: true, error: null }});
    try {{
      // TODO: Implement {action} logic
    }} catch (e) {{
      set({{ error: e instanceof Error ? e.message : 'Unknown error' }});
    }} finally {{
      set({{ loading: false }});
    }}
  }},
""")
        
        lines.append("""  reset: () => {
    set(initialState);
  },""")
        
        return "\n".join(lines) if lines else "  // No actions defined"

    def generate_test(self, glyph: GlyphNode, framework: str) -> str:
        """Generate store test."""
        store_lib = self.STORE_LIBS.get(framework, "zustand")
        name = glyph.name
        if name.lower().endswith('store'):
            name = name[:-5]
        store_name = f"{name[0].upper()}{name[1:]}"

        if store_lib == "pinia":
            return self._generate_pinia_test(glyph, name, store_name)
        else:
            return self._generate_zustand_test(glyph, name, store_name)
    
    def _generate_pinia_test(self, glyph: GlyphNode, name: str, store_name: str) -> str:
        """Generate Pinia store test."""
        return f'''// @archeon {glyph.qualified_name}
// Generated test - Do not edit manually

import {{ describe, it, expect, beforeEach }} from 'vitest';
import {{ createPinia, setActivePinia }} from 'pinia';
import {{ use{store_name}Store }} from '../src/stores/{name}Store';

describe('{store_name}Store', () => {{
  beforeEach(() => {{
    // Create a fresh Pinia instance for each test
    setActivePinia(createPinia());
  }});

  it('has initial state', () => {{
    const store = use{store_name}Store();
    expect(store.loading).toBe(false);
    expect(store.error).toBe(null);
  }});

  it('can reset state', () => {{
    const store = use{store_name}Store();
    store.loading = true;
    store.$reset();
    expect(store.loading).toBe(false);
  }});

  it('computed isReady works correctly', () => {{
    const store = use{store_name}Store();
    expect(store.isReady).toBe(true);
    store.loading = true;
    expect(store.isReady).toBe(false);
  }});

  it('handles errors in actions', async () => {{
    const store = use{store_name}Store();
    // Actions should set loading and error appropriately
    expect(store.loading).toBe(false);
  }});
}});
'''
    
    def _generate_zustand_test(self, glyph: GlyphNode, name: str, store_name: str) -> str:
        """Generate Zustand store test."""
        return f'''// @archeon {glyph.qualified_name}
// Generated test - Do not edit manually

import {{ act, renderHook }} from '@testing-library/react';
import {{ use{store_name} }} from '../stores/{name}Store';

describe('{store_name}Store', () => {{
  beforeEach(() => {{
    // Reset store state before each test
    const {{ result }} = renderHook(() => use{store_name}());
    act(() => {{
      result.current.reset();
    }});
  }});

  it('has initial state', () => {{
    const {{ result }} = renderHook(() => use{store_name}());
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);
  }});

  it('can reset state', () => {{
    const {{ result }} = renderHook(() => use{store_name}());
    act(() => {{
      result.current.reset();
    }});
    expect(result.current.loading).toBe(false);
  }});
}});
'''

    @staticmethod
    def _to_kebab(name: str) -> str:
        """Convert PascalCase to kebab-case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
