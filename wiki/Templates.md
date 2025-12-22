# Templates

Archeon generates code using templates. This guide explains how the template system works and how to customize it for your project.

## Template Location

Templates are in the Archeon installation directory:

```
archeon/templates/
├── _config/              # Design token templates
│   ├── design-tokens.json
│   ├── tailwind.config.js
│   ├── theme.css
│   └── TOKENS.md
├── _server/              # Server utilities
│   └── db.py
├── API/                  # API endpoint templates
│   └── fastapi.py
├── CMP/                  # Component templates
│   ├── react.tsx
│   ├── vue.vue
│   └── vue3.vue
├── EVT/                  # Event templates
│   └── pubsub.py
├── FNC/                  # Function templates
│   └── python.py
├── MDL/                  # Model templates
│   └── mongo.py
└── STO/                  # Store templates
    ├── pinia.js
    ├── theme-pinia.js
    ├── theme-zustand.js
    └── zustand.js
```

## Template Structure

Templates use placeholder syntax for variable substitution:

```vue
<!-- @archeon:file -->
<!-- @glyph {GLYPH_QUALIFIED_NAME} -->
<!-- @intent {COMPONENT_INTENT} -->
<!-- @chain {CHAIN_REFERENCE} -->

<script setup>
// @archeon:section imports
import { ref } from 'vue';
{IMPORTS}
// @archeon:endsection

// @archeon:section props_and_state
const props = defineProps({
{PROPS_DEFINITION}
});

{STATE_REFS}
// @archeon:endsection

// @archeon:section handlers
{HANDLERS}
// @archeon:endsection
</script>

<template>
  <!-- @archeon:section render -->
  <div class="{TAILWIND_CLASSES}">
{RENDER_CONTENT}
  </div>
  <!-- @archeon:endsection -->
</template>
```

## Placeholder Variables

### Common Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{GLYPH_QUALIFIED_NAME}` | Full glyph name | `CMP:LoginForm` |
| `{COMPONENT_NAME}` | Component name | `LoginForm` |
| `{COMPONENT_NAME_KEBAB}` | Kebab-case name | `login-form` |
| `{COMPONENT_INTENT}` | Purpose description | `User login input and submission` |
| `{CHAIN_REFERENCE}` | Chain version | `@v1` |

### Component-Specific

| Placeholder | Description |
|-------------|-------------|
| `{IMPORTS}` | Import statements |
| `{PROPS_DEFINITION}` | Props definition |
| `{STATE_REFS}` | State declarations |
| `{HANDLERS}` | Event handlers |
| `{RENDER_CONTENT}` | Template body |
| `{TAILWIND_CLASSES}` | CSS classes |
| `{STORE_IMPORT}` | Store import statement |

### API-Specific

| Placeholder | Description |
|-------------|-------------|
| `{HTTP_METHOD}` | GET, POST, PUT, DELETE |
| `{ROUTE_PATH}` | /api/auth/login |
| `{REQUEST_MODEL}` | Request schema |
| `{RESPONSE_MODEL}` | Response schema |
| `{HANDLER_LOGIC}` | Endpoint implementation |

## Section Markers

Every template uses semantic section markers:

```
// @archeon:section <section_name>
// <1-sentence purpose>
<code>
// @archeon:endsection
```

**Standard Sections by Glyph:**

### CMP (Component)
- `imports` - Dependencies
- `props_and_state` - Props and reactive state
- `handlers` - Event handlers
- `render` - Template markup
- `styles` - CSS (if applicable)

### STO (Store)
- `imports` - Dependencies
- `state` - State declarations
- `actions` - State mutations
- `selectors` - Computed properties

### API (Endpoint)
- `imports` - Dependencies
- `models` - Request/response schemas
- `endpoint` - Route handler
- `helpers` - Utility functions

### FNC (Function)
- `imports` - Dependencies
- `implementation` - Main logic
- `helpers` - Helper functions

### MDL (Model)
- `imports` - Dependencies
- `schema` - Data schema
- `methods` - Model methods
- `indexes` - Database indexes

## Editing Templates

### Option 1: Direct Edit (Installed with `-e`)

If you installed Archeon in editable mode, edit templates directly:

```bash
# Edit Vue3 component template
vim archeon/templates/CMP/vue3.vue

# Changes take effect immediately
arc gen
```

### Option 2: Override in Project

Create project-specific templates:

```bash
mkdir -p .archeon/templates/CMP
cp archeon/templates/CMP/vue3.vue .archeon/templates/CMP/vue3.vue
vim .archeon/templates/CMP/vue3.vue
```

Archeon checks `.archeon/templates/` first, then falls back to global templates.

### Option 3: CLI Edit Command

```bash
arc template edit CMP --frontend vue3
```

Opens template in your default editor.

## Example: Customizing Vue3 Component

Let's customize the Vue3 component template to use Composition API with `<script setup lang="ts">`:

```vue
<!-- @archeon:file -->
<!-- @glyph {GLYPH_QUALIFIED_NAME} -->
<!-- @intent {COMPONENT_INTENT} -->
<!-- @chain {CHAIN_REFERENCE} -->

<script setup lang="ts">
// @archeon:section imports
// External dependencies and types
import { ref, computed, onMounted, type Ref } from 'vue';
import { useThemeStore } from '@/stores/themeStore';
{STORE_IMPORT}
{IMPORTS}
// @archeon:endsection

// @archeon:section props_and_state
// Component props with TypeScript types
interface Props {
{PROPS_INTERFACE}
}

const props = withDefaults(defineProps<Props>(), {
{PROPS_DEFAULTS}
});

// Emits
const emit = defineEmits<{
{EMITS_INTERFACE}
}>();

// Theme support
const themeStore = useThemeStore();

// Local state
{STATE_REFS}

// Computed properties
{COMPUTED}
// @archeon:endsection

// @archeon:section handlers
// Event handlers and lifecycle
{HANDLERS}

{LIFECYCLE}
// @archeon:endsection
</script>

<template>
  <!-- @archeon:section render -->
  <!-- Component template -->
  <div 
    :class="[
      '{BASE_CLASSES}',
      {DYNAMIC_CLASSES}
    ]"
    data-testid="{COMPONENT_NAME_KEBAB}"
  >
{RENDER_CONTENT}
  </div>
  <!-- @archeon:endsection -->
</template>

<style scoped>
/* @archeon:section styles */
/* Component-specific styles */
{STYLES}
/* @archeon:endsection */
</style>
```

## Example: Customizing API Template

Here's a customized FastAPI template with better error handling:

```python
# @archeon:file
# @glyph {GLYPH_QUALIFIED_NAME}
# @intent {ENDPOINT_INTENT}
# @chain {CHAIN_REFERENCE}

# @archeon:section imports
# Dependencies and models
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, validator
from typing import Optional
import logging

{IMPORTS}
# @archeon:endsection

# @archeon:section models
# Request and response schemas
class {REQUEST_MODEL_NAME}(BaseModel):
{REQUEST_SCHEMA}
    
    @validator('*', pre=True)
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

class {RESPONSE_MODEL_NAME}(BaseModel):
{RESPONSE_SCHEMA}
# @archeon:endsection

# @archeon:section endpoint
# Router and endpoint definition
router = APIRouter(prefix="/api", tags=["{TAG_NAME}"])
logger = logging.getLogger(__name__)

@router.{HTTP_METHOD_LOWER}("{ROUTE_PATH}", 
    response_model={RESPONSE_MODEL_NAME},
    status_code=status.HTTP_{STATUS_CODE}_{STATUS_TEXT})
async def {HANDLER_NAME}(
    request: {REQUEST_MODEL_NAME},
    {DEPENDENCIES}
):
    """
    {ENDPOINT_DESCRIPTION}
    
    Raises:
        HTTPException: {ERROR_CONDITIONS}
    """
    try:
        logger.info(f"{HANDLER_NAME} called with: {request.dict()}")
        
{HANDLER_LOGIC}
        
        return {RESPONSE_OBJECT}
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
# @archeon:endsection

# @archeon:section helpers
# Helper functions
{HELPERS}
# @archeon:endsection
```

## Theme Templates

Archeon includes special templates for design token management:

### design-tokens.json

DTCG-compliant token definitions:

```json
{
  "color": {
    "primary": {
      "$type": "color",
      "$value": "{color.blue.500}"
    },
    "blue": {
      "50": { "$type": "color", "$value": "#eff6ff" },
      "500": { "$type": "color", "$value": "#3b82f6" }
    }
  },
  "spacing": {
    "sm": { "$type": "dimension", "$value": "0.5rem" },
    "md": { "$type": "dimension", "$value": "1rem" }
  }
}
```

### token-transformer.js

Transforms tokens to multiple outputs:

```javascript
// Generates:
// - tokens.css (CSS variables)
// - tokens.tailwind.js (Tailwind config)
// - tokens.semantic.css (Semantic layer)
```

Run with:
```bash
node client/src/tokens/token-transformer.js
```

## Template Context

Templates receive context from the chain parser:

```python
{
  "glyph": {
    "type": "CMP",
    "name": "LoginForm",
    "qualified": "CMP:LoginForm",
    "modifiers": ["stateful"],
    "intent": "User login input and submission"
  },
  "chain": {
    "version": "v1",
    "upstream": ["NED:login", "TSK:submit"],
    "downstream": ["STO:Auth", "API:POST/auth/login"]
  },
  "dependencies": {
    "stores": ["STO:Auth"],
    "apis": ["API:POST/auth/login"],
    "components": []
  },
  "config": {
    "frontend": "vue3",
    "backend": "fastapi"
  }
}
```

## Conditional Logic

Templates can include conditional blocks:

```vue
{#if HAS_STORE}
import { use{STORE_NAME}Store } from '@/stores/{STORE_NAME}Store';
const {STORE_NAME_LOWER}Store = use{STORE_NAME}Store();
{/if}

{#if IS_ASYNC}
const loading = ref(false);
const error = ref(null);
{/if}
```

## Testing Templates

Generate to temporary directory:

```bash
# Dry run
arc gen --dry-run

# Generate to temp directory
arc gen --output /tmp/archeon-test
```

## Best Practices

### 1. Keep Templates Minimal

Templates should provide structure, not implementation:

✅ **Good:**
```vue
// @archeon:section handlers
async function handleSubmit() {
  // TODO: Implement submission logic
}
// @archeon:endsection
```

❌ **Bad:**
```vue
// @archeon:section handlers
async function handleSubmit() {
  const response = await fetch('/api/endpoint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: formData.value })
  });
  // ... 50 more lines
}
// @archeon:endsection
```

### 2. Use Semantic Sections

Every code block should be in a semantic section:

```vue
// @archeon:section handlers
// User interaction handlers
function handleClick() { }
function handleSubmit() { }
// @archeon:endsection
```

### 3. Include Type Information

For TypeScript projects, include types:

```typescript
// @archeon:section imports
import type { User } from '@/types';
// @archeon:endsection

// @archeon:section props_and_state
interface Props {
  user: User;
  onUpdate: (user: User) => void;
}
// @archeon:endsection
```

### 4. Document Intent

Always include `@archeon:file` header:

```vue
<!-- @archeon:file -->
<!-- @glyph CMP:LoginForm -->
<!-- @intent User login input and submission -->
<!-- @chain @v1 -->
```

## Resetting Templates

Reset to defaults:

```bash
# Reset specific template
arc template reset CMP --frontend vue3

# Reset all templates
arc template reset --all
```

## Next Steps

- 🏗️ [Architecture](Architecture) - System design principles
- 🎨 [Design Tokens](Design-Tokens) - Token system guide
- 💻 [CLI Commands](CLI-Commands) - Template management commands
