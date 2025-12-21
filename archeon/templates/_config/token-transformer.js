#!/usr/bin/env node
/**
 * @archeon CFG:token-transformer
 * Design Tokens Transformer
 * 
 * Transforms design-tokens.json (DTCG format) into:
 * - CSS custom properties
 * - Tailwind CSS config
 * - JavaScript/TypeScript constants
 * 
 * Usage:
 *   node token-transformer.js [options]
 * 
 * Options:
 *   --input   Path to design-tokens.json (default: ./design-tokens.json)
 *   --output  Output directory (default: ./generated)
 *   --format  Output format: css, tailwind, js, all (default: all)
 */

const fs = require('fs');
const path = require('path');

// Parse command line arguments
const args = process.argv.slice(2);
const getArg = (name, defaultVal) => {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : defaultVal;
};

const INPUT = getArg('input', './design-tokens.json');
const OUTPUT = getArg('output', './generated');
const FORMAT = getArg('format', 'all');

// Resolve token references like {color.primitive.blue.500}
function resolveReference(value, tokens) {
  if (typeof value !== 'string') return value;
  
  const refMatch = value.match(/^\{(.+)\}$/);
  if (!refMatch) return value;
  
  const refPath = refMatch[1].split('.');
  let resolved = tokens;
  
  for (const key of refPath) {
    if (resolved && resolved[key] !== undefined) {
      resolved = resolved[key];
    } else {
      return value; // Return unresolved if path doesn't exist
    }
  }
  
  // If resolved value is an object with $value, get that
  if (resolved && resolved.$value !== undefined) {
    return resolveReference(resolved.$value, tokens);
  }
  
  return resolved;
}

// Convert camelCase to kebab-case
function toKebab(str) {
  return str.replace(/([a-z])([A-Z])/g, '$1-$2').toLowerCase();
}

// Flatten nested tokens into CSS variable names
function flattenToCSSVars(obj, prefix = '', tokens) {
  const result = {};
  
  for (const [key, value] of Object.entries(obj)) {
    // Skip metadata keys
    if (key.startsWith('$')) continue;
    
    const varName = prefix ? `${prefix}-${toKebab(key)}` : toKebab(key);
    
    if (value && typeof value === 'object') {
      if (value.$value !== undefined) {
        // This is a token with a value
        const resolved = resolveReference(value.$value, tokens);
        if (typeof resolved !== 'object') {
          result[`--${varName}`] = resolved;
        }
      } else {
        // Nested object, recurse
        Object.assign(result, flattenToCSSVars(value, varName, tokens));
      }
    }
  }
  
  return result;
}

// Generate CSS custom properties
function generateCSS(tokens) {
  const cssVars = flattenToCSSVars(tokens, '', tokens);
  
  let css = `/* Generated from design-tokens.json - DO NOT EDIT */
/* Source: ${INPUT} */
/* Generated: ${new Date().toISOString()} */

:root {
`;
  
  // Group by category
  let currentCategory = '';
  for (const [name, value] of Object.entries(cssVars)) {
    const category = name.split('-')[1];
    if (category !== currentCategory) {
      currentCategory = category;
      css += `\n  /* === ${category.toUpperCase()} === */\n`;
    }
    css += `  ${name}: ${value};\n`;
  }
  
  css += `}
`;
  
  return css;
}

// Generate Tailwind-compatible config
function generateTailwindConfig(tokens) {
  const config = {
    theme: {
      extend: {
        colors: {},
        spacing: {},
        fontSize: {},
        fontWeight: {},
        fontFamily: {},
        lineHeight: {},
        letterSpacing: {},
        borderRadius: {},
        borderWidth: {},
        boxShadow: {},
        opacity: {},
        zIndex: {},
        transitionDuration: {},
        transitionTimingFunction: {},
      }
    }
  };
  
  // Process colors
  if (tokens.color?.primitive) {
    for (const [colorName, shades] of Object.entries(tokens.color.primitive)) {
      if (typeof shades === 'object' && !shades.$value) {
        config.theme.extend.colors[colorName] = {};
        for (const [shade, token] of Object.entries(shades)) {
          if (token.$value) {
            config.theme.extend.colors[colorName][shade] = token.$value;
          }
        }
      } else if (shades.$value) {
        config.theme.extend.colors[colorName] = shades.$value;
      }
    }
  }
  
  // Process spacing
  if (tokens.spacing) {
    for (const [key, token] of Object.entries(tokens.spacing)) {
      if (token.$value && !key.startsWith('$')) {
        config.theme.extend.spacing[key] = token.$value;
      }
    }
  }
  
  // Process typography
  if (tokens.typography) {
    if (tokens.typography.fontSize) {
      for (const [key, token] of Object.entries(tokens.typography.fontSize)) {
        if (token.$value && !key.startsWith('$')) {
          config.theme.extend.fontSize[key] = token.$value;
        }
      }
    }
    if (tokens.typography.fontWeight) {
      for (const [key, token] of Object.entries(tokens.typography.fontWeight)) {
        if (token.$value !== undefined && !key.startsWith('$')) {
          config.theme.extend.fontWeight[key] = String(token.$value);
        }
      }
    }
    if (tokens.typography.fontFamily) {
      for (const [key, token] of Object.entries(tokens.typography.fontFamily)) {
        if (token.$value && !key.startsWith('$')) {
          config.theme.extend.fontFamily[key] = token.$value;
        }
      }
    }
    if (tokens.typography.lineHeight) {
      for (const [key, token] of Object.entries(tokens.typography.lineHeight)) {
        if (token.$value !== undefined && !key.startsWith('$')) {
          config.theme.extend.lineHeight[key] = String(token.$value);
        }
      }
    }
    if (tokens.typography.letterSpacing) {
      for (const [key, token] of Object.entries(tokens.typography.letterSpacing)) {
        if (token.$value && !key.startsWith('$')) {
          config.theme.extend.letterSpacing[key] = token.$value;
        }
      }
    }
  }
  
  // Process border radius
  if (tokens.borderRadius) {
    for (const [key, token] of Object.entries(tokens.borderRadius)) {
      if (token.$value && !key.startsWith('$')) {
        const name = key === 'default' ? 'DEFAULT' : key;
        config.theme.extend.borderRadius[name] = token.$value;
      }
    }
  }
  
  // Process shadows
  if (tokens.shadow) {
    for (const [key, token] of Object.entries(tokens.shadow)) {
      if (token.$value && !key.startsWith('$') && key !== 'dark') {
        const name = key === 'default' ? 'DEFAULT' : key;
        config.theme.extend.boxShadow[name] = token.$value;
      }
    }
  }
  
  // Process z-index
  if (tokens.zIndex) {
    for (const [key, token] of Object.entries(tokens.zIndex)) {
      if (token.$value !== undefined && !key.startsWith('$')) {
        config.theme.extend.zIndex[key] = String(token.$value);
      }
    }
  }
  
  // Process animation
  if (tokens.animation) {
    if (tokens.animation.duration) {
      for (const [key, token] of Object.entries(tokens.animation.duration)) {
        if (token.$value && !key.startsWith('$')) {
          config.theme.extend.transitionDuration[key] = token.$value;
        }
      }
    }
    if (tokens.animation.easing) {
      for (const [key, token] of Object.entries(tokens.animation.easing)) {
        if (token.$value && !key.startsWith('$')) {
          config.theme.extend.transitionTimingFunction[key] = token.$value;
        }
      }
    }
  }
  
  return `// Generated from design-tokens.json - DO NOT EDIT
// Source: ${INPUT}
// Generated: ${new Date().toISOString()}

/** @type {import('tailwindcss').Config} */
module.exports = ${JSON.stringify(config, null, 2)};
`;
}

// Generate JavaScript/TypeScript constants
function generateJS(tokens) {
  return `// Generated from design-tokens.json - DO NOT EDIT
// Source: ${INPUT}
// Generated: ${new Date().toISOString()}

export const tokens = ${JSON.stringify(tokens, null, 2)};

// Helper to get a token value by path
export function getToken(path) {
  const keys = path.split('.');
  let value = tokens;
  for (const key of keys) {
    if (value && value[key] !== undefined) {
      value = value[key];
    } else {
      return undefined;
    }
  }
  return value?.$value ?? value;
}

// Color tokens
export const colors = tokens.color;

// Typography tokens
export const typography = tokens.typography;

// Spacing tokens  
export const spacing = tokens.spacing;

// Shadow tokens
export const shadows = tokens.shadow;

// Border radius tokens
export const borderRadius = tokens.borderRadius;

// Animation tokens
export const animation = tokens.animation;

// Breakpoint tokens
export const breakpoints = tokens.breakpoint;

// Component tokens
export const components = tokens.component;

export default tokens;
`;
}

// Main execution
function main() {
  // Read tokens file
  let tokens;
  try {
    const content = fs.readFileSync(INPUT, 'utf8');
    tokens = JSON.parse(content);
  } catch (err) {
    console.error(`Error reading ${INPUT}:`, err.message);
    process.exit(1);
  }
  
  // Create output directory
  if (!fs.existsSync(OUTPUT)) {
    fs.mkdirSync(OUTPUT, { recursive: true });
  }
  
  // Generate outputs based on format
  const formats = FORMAT === 'all' ? ['css', 'tailwind', 'js'] : [FORMAT];
  
  for (const format of formats) {
    let content, filename;
    
    switch (format) {
      case 'css':
        content = generateCSS(tokens);
        filename = 'tokens.css';
        break;
      case 'tailwind':
        content = generateTailwindConfig(tokens);
        filename = 'tailwind.tokens.js';
        break;
      case 'js':
        content = generateJS(tokens);
        filename = 'tokens.js';
        break;
      default:
        console.warn(`Unknown format: ${format}`);
        continue;
    }
    
    const outputPath = path.join(OUTPUT, filename);
    fs.writeFileSync(outputPath, content);
    console.log(`✓ Generated ${outputPath}`);
  }
  
  console.log('\nDone! Import the generated files in your project.');
}

main();
