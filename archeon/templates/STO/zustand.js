// @archeon:file
// @glyph {GLYPH_QUALIFIED_NAME}
// @intent {STORE_INTENT}
// @chain {CHAIN_REFERENCE}

// @archeon:section imports
// External dependencies
import { create } from 'zustand';
import axios from 'axios';
{IMPORTS}
// @archeon:endsection

// @archeon:section state
// Initial state shape
const initialState = {
{INITIAL_STATE}
};
// @archeon:endsection

// @archeon:section actions
// State mutations and async operations
export const use{STORE_NAME} = create((set, get) => ({
  ...initialState,

{ACTIONS}
}));
// @archeon:endsection

// @archeon:section selectors
// Derived state selectors
{SELECTORS}
// @archeon:endsection

export default use{STORE_NAME};
