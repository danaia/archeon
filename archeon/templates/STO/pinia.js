// @archeon {GLYPH_QUALIFIED_NAME}
// Generated Pinia store - Vue 3 state management (plain JavaScript)
{IMPORTS}

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

// Store definition using Composition API (recommended for Vue 3)
export const use{STORE_NAME}Store = defineStore('{STORE_ID}', () => {
  // State
{STATE_REFS}

{GETTERS}

{ACTIONS}

  // Reset action
  function $reset() {
{RESET_ACTION}
  }

  return {
    // State
{STATE_RETURN}
    // Getters
{GETTERS_RETURN}
    // Actions
{ACTIONS_RETURN}
    $reset,
  };
});

export default use{STORE_NAME}Store;
