// @archeon:file
// @glyph {GLYPH_QUALIFIED_NAME}
// @intent {COMPONENT_INTENT}
// @chain {CHAIN_REFERENCE}

// @archeon:section imports
// External dependencies and component imports
import React{USE_STATE_IMPORT} from 'react';
{THEME_IMPORT}
{IMPORTS}
// @archeon:endsection

// @archeon:section props_and_state
// Component props interface and local state definitions
{PROPS_INTERFACE}
// @archeon:endsection

export function {COMPONENT_NAME}({PROPS_DESTRUCTURE}) {
{THEME_HOOK}
// @archeon:section handlers
// Event handlers and side effects
{STATE_HOOKS}
{HANDLERS}
// @archeon:endsection

// @archeon:section render
// Component JSX structure and presentation
  return (
    <div 
      className="{TAILWIND_CLASSES}"
      data-testid="{COMPONENT_NAME_KEBAB}"
    >
{RENDER_CONTENT}
    </div>
  );
// @archeon:endsection
}

export default {COMPONENT_NAME};
