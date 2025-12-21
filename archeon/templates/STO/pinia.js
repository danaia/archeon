// @ts-nocheck
// @archeon {GLYPH_QUALIFIED_NAME}
// Generated Pinia store - Vue 3 state management (plain JavaScript)
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
{IMPORTS}

export const useStoreNameStore = defineStore('storeId', () => {
{STATE_REFS}

{GETTERS}

{ACTIONS}

  function $reset() {
{RESET_ACTION}
  }

return {
  // {STATE_RETURN}
  // {GETTERS_RETURN}
  // {ACTIONS_RETURN}
  $reset
}
})
