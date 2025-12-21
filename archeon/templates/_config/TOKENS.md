# Design Tokens Documentation

This folder contains the design token system for Archeon-generated applications.

## What are Design Tokens?

Design tokens are the atomic values of a design system—colors, typography, spacing, shadows, and more—stored in a platform-agnostic format. They serve as the single source of truth for design decisions.

## File Structure

```
_config/
├── design-tokens.json      # Source of truth (DTCG format)
├── token-transformer.js    # Build script for tokens
├── theme.css               # Generated CSS variables
├── tailwind.config.js      # Tailwind configuration
└── theme-presets.css       # Pre-built color themes
```

## Design Tokens Format (DTCG)

We follow the [W3C Design Tokens Community Group](https://design-tokens.github.io/community-group/format/) specification:

```json
{
  "color": {
    "primary": {
      "500": {
        "$value": "#3b82f6",
        "$type": "color",
        "$description": "Primary brand color"
      }
    }
  }
}
```

### Token Properties

| Property | Description |
|----------|-------------|
| `$value` | The actual value of the token |
| `$type` | The type: `color`, `dimension`, `fontFamily`, `fontWeight`, `duration`, `cubicBezier`, `shadow`, `typography` |
| `$description` | Human-readable description |

### Token References

Tokens can reference other tokens using curly braces:

```json
{
  "color": {
    "semantic": {
      "primary": {
        "$value": "{color.primitive.blue.500}",
        "$type": "color"
      }
    }
  }
}
```

## Token Categories

### Colors (`color`)

- **Primitive Colors**: Raw color values (blue.500, gray.100, etc.)
- **Semantic Colors**: Contextual colors (primary, secondary, success, danger)
- **Surface Colors**: Background colors for light/dark modes
- **Content Colors**: Text/foreground colors
- **Border Colors**: Stroke colors

### Typography (`typography`)

- **Font Families**: sans, serif, mono
- **Font Sizes**: xs through 9xl
- **Font Weights**: thin through black
- **Line Heights**: none, tight, normal, relaxed, loose
- **Letter Spacing**: tighter through widest
- **Text Styles**: Composite styles (h1, body, label)

### Spacing (`spacing`)

4px base unit scale: 0, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, etc.

### Sizing (`sizing`)

- Fixed dimensions
- Container max-widths
- Icon sizes

### Border Radius (`borderRadius`)

none, sm, default, md, lg, xl, 2xl, 3xl, full

### Shadows (`shadow`)

sm, default, md, lg, xl, 2xl, inner, none (with dark mode variants)

### Animation (`animation`)

- **Duration**: instant, fastest, fast, normal, slow, slower, slowest
- **Easing**: linear, easeIn, easeOut, easeInOut, spring, bounce
- **Keyframes**: fadeIn, fadeOut, slideInUp, scaleIn, spin, pulse

### Breakpoints (`breakpoint`)

xs (320px), sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)

### Component Tokens (`component`)

Pre-defined sizing for common components:
- Button (height, padding, fontSize)
- Input (height, padding, borderRadius)
- Card (padding, borderRadius, shadow)
- Modal (maxWidth, padding)
- Avatar (size variants)
- Badge (padding, fontSize)

## Generating Output Files

Run the transformer script:

```bash
# Generate all formats
node token-transformer.js

# Generate only CSS
node token-transformer.js --format css

# Custom input/output
node token-transformer.js --input ./my-tokens.json --output ./dist
```

### Output Files

1. **tokens.css** - CSS custom properties for use in stylesheets
2. **tailwind.tokens.js** - Tailwind config extension
3. **tokens.js** - JavaScript module for programmatic access

## Using with Figma Tokens

The `design-tokens.json` format is compatible with:

- [Tokens Studio for Figma](https://tokens.studio/)
- [Figma Variables](https://www.figma.com/developers/api#variables)
- [Style Dictionary](https://amzn.github.io/style-dictionary/)

### Importing from Figma

1. Export tokens from Tokens Studio as JSON
2. Transform to DTCG format if needed
3. Replace `design-tokens.json`
4. Run the transformer

### Syncing with Figma

For two-way sync, consider using:
- Tokens Studio Pro (direct GitHub sync)
- Figma REST API + custom scripts

## Customizing Tokens

### Changing the Primary Color

Edit `design-tokens.json`:

```json
{
  "color": {
    "semantic": {
      "primary": {
        "default": { "$value": "{color.primitive.purple.500}", "$type": "color" }
      }
    }
  }
}
```

### Adding a New Color Palette

```json
{
  "color": {
    "primitive": {
      "brand": {
        "50": { "$value": "#f0f9ff", "$type": "color" },
        "500": { "$value": "#0ea5e9", "$type": "color" },
        "900": { "$value": "#0c4a6e", "$type": "color" }
      }
    }
  }
}
```

### Creating Component Tokens

```json
{
  "component": {
    "myComponent": {
      "padding": { "$value": "{spacing.4}", "$type": "dimension" },
      "borderRadius": { "$value": "{borderRadius.lg}", "$type": "dimension" },
      "backgroundColor": { "$value": "{color.surface.light.raised}", "$type": "color" }
    }
  }
}
```

## Best Practices

1. **Use semantic tokens in components** - Don't use primitive colors directly
2. **Reference existing tokens** - Use `{token.path}` syntax for consistency
3. **Document your tokens** - Use `$description` for context
4. **Keep primitives complete** - Full color scales enable flexibility
5. **Version your tokens** - Track changes in `$metadata.version`

## Integration Examples

### Vue 3 Component

```vue
<template>
  <button class="btn">Click me</button>
</template>

<style scoped>
.btn {
  background-color: var(--color-semantic-primary-default);
  color: var(--color-semantic-primary-foreground);
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--border-radius-md);
  font-size: var(--typography-font-size-sm);
  font-weight: var(--typography-font-weight-medium);
  transition: background-color var(--animation-duration-fast) var(--animation-easing-ease-out);
}

.btn:hover {
  background-color: var(--color-semantic-primary-hover);
}
</style>
```

### React Component with Tailwind

```tsx
// Using generated Tailwind config
<button className="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-fast">
  Click me
</button>
```

### JavaScript Access

```js
import { getToken, colors } from './tokens';

const primaryColor = getToken('color.semantic.primary.default');
const spacing = getToken('spacing.4'); // "1rem"
```
