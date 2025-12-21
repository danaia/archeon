// @archeon:file
// @glyph {GLYPH_QUALIFIED_NAME}
// @intent {STORE_INTENT}
// @chain {CHAIN_REFERENCE}

// @archeon:section imports
// External dependencies
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
{IMPORTS}
// @archeon:endsection

export const use{STORE_NAME}Store = defineStore('{STORE_ID}', () => {
// @archeon:section state
// Reactive state refs
{STATE_REFS}
// @archeon:endsection

// @archeon:section selectors
// Computed getters
{GETTERS}
// @archeon:endsection

// @archeon:section actions
// State mutations and async operations
{ACTIONS}

  function $reset() {
{RESET_ACTION}
  }
// @archeon:endsection

  return {
{STATE_RETURN}
{GETTERS_RETURN}
{ACTIONS_RETURN}
    $reset
  }
})
