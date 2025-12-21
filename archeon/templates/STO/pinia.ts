// @archeon {GLYPH_QUALIFIED_NAME}
// Generated Pinia store - Vue 3 state management
{IMPORTS}

import { defineStore } from 'pinia';
import { ref, computed, type Ref, type ComputedRef } from 'vue';

// Types
interface User {
  id: string;
  email: string;
  name?: string;
}

// State interface
export interface {STORE_NAME}State {
{STATE_INTERFACE}
}

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

// Type helper for use in components
export type {STORE_NAME}Store = ReturnType<typeof use{STORE_NAME}Store>;

export default use{STORE_NAME}Store;
