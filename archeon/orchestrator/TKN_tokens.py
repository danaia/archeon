"""
Token transformer for Archeon design system.

Transforms design-tokens.json (DTCG format) into:
- CSS custom properties
- Tailwind CSS config extension
- JavaScript/TypeScript constants

This is the Python implementation that powers the `arc tokens` command.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List


def to_kebab(s: str) -> str:
    """Convert camelCase to kebab-case."""
    return re.sub(r'([a-z])([A-Z])', r'\1-\2', s).lower()


def resolve_reference(value: Any, tokens: Dict) -> Any:
    """Resolve token references like {color.primitive.blue.500}."""
    if not isinstance(value, str):
        return value
    
    match = re.match(r'^\{(.+)\}$', value)
    if not match:
        return value
    
    ref_path = match.group(1).split('.')
    resolved = tokens
    
    for key in ref_path:
        if isinstance(resolved, dict) and key in resolved:
            resolved = resolved[key]
        else:
            return value  # Return unresolved if path doesn't exist
    
    # If resolved value is an object with $value, get that
    if isinstance(resolved, dict) and '$value' in resolved:
        return resolve_reference(resolved['$value'], tokens)
    
    return resolved


def flatten_to_css_vars(obj: Dict, prefix: str, tokens: Dict) -> Dict[str, str]:
    """Flatten nested tokens into CSS variable names."""
    result = {}
    
    for key, value in obj.items():
        # Skip metadata keys
        if key.startswith('$'):
            continue
        
        var_name = f"{prefix}-{to_kebab(key)}" if prefix else to_kebab(key)
        
        if isinstance(value, dict):
            if '$value' in value:
                # This is a token with a value
                resolved = resolve_reference(value['$value'], tokens)
                if not isinstance(resolved, dict):
                    result[f"--{var_name}"] = str(resolved)
            else:
                # Nested object, recurse
                result.update(flatten_to_css_vars(value, var_name, tokens))
    
    return result


def generate_css(tokens: Dict, include_dark: bool = True) -> str:
    """Generate CSS custom properties from design tokens."""
    css_vars = flatten_to_css_vars(tokens, '', tokens)
    
    lines = [
        "/* Generated from design-tokens.json by Archeon */",
        "/* DO NOT EDIT - Run `arc tokens` to regenerate */",
        "",
        ":root {"
    ]
    
    # Group by category
    current_category = ''
    for name, value in sorted(css_vars.items()):
        parts = name.split('-')
        if len(parts) > 1:
            category = parts[1]
            if category != current_category:
                current_category = category
                lines.append(f"\n  /* {category.upper()} */")
        lines.append(f"  {name}: {value};")
    
    lines.append("}")
    
    # Add dark mode overrides if surface/content tokens exist
    if include_dark and 'color' in tokens:
        dark_vars = []
        color = tokens.get('color', {})
        
        # Surface colors for dark mode
        if 'surface' in color and 'dark' in color['surface']:
            for key, val in color['surface']['dark'].items():
                if '$value' in val:
                    resolved = resolve_reference(val['$value'], tokens)
                    dark_vars.append(f"  --color-surface-{to_kebab(key)}: {resolved};")
        
        # Content colors for dark mode
        if 'content' in color and 'dark' in color['content']:
            for key, val in color['content']['dark'].items():
                if '$value' in val:
                    resolved = resolve_reference(val['$value'], tokens)
                    dark_vars.append(f"  --color-content-{to_kebab(key)}: {resolved};")
        
        # Border colors for dark mode
        if 'border' in color and 'dark' in color['border']:
            for key, val in color['border']['dark'].items():
                if '$value' in val:
                    resolved = resolve_reference(val['$value'], tokens)
                    dark_vars.append(f"  --color-border-{to_kebab(key)}: {resolved};")
        
        if dark_vars:
            lines.extend([
                "",
                ".dark {",
                *dark_vars,
                "}"
            ])
    
    return "\n".join(lines)


def generate_tailwind_extension(tokens: Dict) -> str:
    """Generate Tailwind config extension from design tokens."""
    config = {
        "colors": {},
        "spacing": {},
        "fontSize": {},
        "fontWeight": {},
        "fontFamily": {},
        "lineHeight": {},
        "letterSpacing": {},
        "borderRadius": {},
        "boxShadow": {},
        "zIndex": {},
        "transitionDuration": {},
        "transitionTimingFunction": {},
    }
    
    # Process colors
    if 'color' in tokens and 'primitive' in tokens['color']:
        for color_name, shades in tokens['color']['primitive'].items():
            if isinstance(shades, dict) and '$value' not in shades:
                config['colors'][color_name] = {}
                for shade, token in shades.items():
                    if isinstance(token, dict) and '$value' in token:
                        config['colors'][color_name][shade] = token['$value']
            elif isinstance(shades, dict) and '$value' in shades:
                config['colors'][color_name] = shades['$value']
    
    # Process spacing
    if 'spacing' in tokens:
        for key, token in tokens['spacing'].items():
            if not key.startswith('$') and isinstance(token, dict) and '$value' in token:
                config['spacing'][key] = token['$value']
    
    # Process typography
    if 'typography' in tokens:
        typo = tokens['typography']
        if 'fontSize' in typo:
            for key, token in typo['fontSize'].items():
                if not key.startswith('$') and isinstance(token, dict) and '$value' in token:
                    config['fontSize'][key] = token['$value']
        if 'fontWeight' in typo:
            for key, token in typo['fontWeight'].items():
                if not key.startswith('$') and isinstance(token, dict) and '$value' in token:
                    config['fontWeight'][key] = str(token['$value'])
        if 'fontFamily' in typo:
            for key, token in typo['fontFamily'].items():
                if not key.startswith('$') and isinstance(token, dict) and '$value' in token:
                    config['fontFamily'][key] = token['$value']
        if 'lineHeight' in typo:
            for key, token in typo['lineHeight'].items():
                if not key.startswith('$') and isinstance(token, dict) and '$value' in token:
                    config['lineHeight'][key] = str(token['$value'])
        if 'letterSpacing' in typo:
            for key, token in typo['letterSpacing'].items():
                if not key.startswith('$') and isinstance(token, dict) and '$value' in token:
                    config['letterSpacing'][key] = token['$value']
    
    # Process border radius
    if 'borderRadius' in tokens:
        for key, token in tokens['borderRadius'].items():
            if not key.startswith('$') and isinstance(token, dict) and '$value' in token:
                name = 'DEFAULT' if key == 'default' else key
                config['borderRadius'][name] = token['$value']
    
    # Process shadows
    if 'shadow' in tokens:
        for key, token in tokens['shadow'].items():
            if not key.startswith('$') and key != 'dark' and isinstance(token, dict) and '$value' in token:
                name = 'DEFAULT' if key == 'default' else key
                config['boxShadow'][name] = token['$value']
    
    # Process z-index
    if 'zIndex' in tokens:
        for key, token in tokens['zIndex'].items():
            if not key.startswith('$') and isinstance(token, dict) and '$value' in token:
                config['zIndex'][key] = str(token['$value'])
    
    # Process animation
    if 'animation' in tokens:
        anim = tokens['animation']
        if 'duration' in anim:
            for key, token in anim['duration'].items():
                if not key.startswith('$') and isinstance(token, dict) and '$value' in token:
                    config['transitionDuration'][key] = token['$value']
        if 'easing' in anim:
            for key, token in anim['easing'].items():
                if not key.startswith('$') and isinstance(token, dict) and '$value' in token:
                    config['transitionTimingFunction'][key] = token['$value']
    
    # Remove empty sections
    config = {k: v for k, v in config.items() if v}
    
    lines = [
        "// Generated from design-tokens.json by Archeon",
        "// DO NOT EDIT - Run `arc tokens` to regenerate",
        "",
        "/** @type {import('tailwindcss').Config['theme']['extend']} */",
        f"export const themeExtend = {json.dumps(config, indent=2)};",
        "",
        "export default themeExtend;",
    ]
    
    return "\n".join(lines)


def generate_js_tokens(tokens: Dict) -> str:
    """Generate JavaScript module from design tokens."""
    lines = [
        "// Generated from design-tokens.json by Archeon",
        "// DO NOT EDIT - Run `arc tokens` to regenerate",
        "",
        f"export const tokens = {json.dumps(tokens, indent=2)};",
        "",
        "// Helper to get a token value by path",
        "export function getToken(path) {",
        "  const keys = path.split('.');",
        "  let value = tokens;",
        "  for (const key of keys) {",
        "    if (value && value[key] !== undefined) {",
        "      value = value[key];",
        "    } else {",
        "      return undefined;",
        "    }",
        "  }",
        "  return value?.$value ?? value;",
        "}",
        "",
        "// Convenience exports",
        "export const colors = tokens.color;",
        "export const typography = tokens.typography;",
        "export const spacing = tokens.spacing;",
        "export const shadows = tokens.shadow;",
        "export const borderRadius = tokens.borderRadius;",
        "export const animation = tokens.animation;",
        "export const breakpoints = tokens.breakpoint;",
        "export const components = tokens.component;",
        "",
        "export default tokens;",
    ]
    
    return "\n".join(lines)


def generate_semantic_css(tokens: Dict) -> str:
    """Generate semantic/aliased CSS variables for component use."""
    lines = [
        "/* Semantic design tokens - use these in components */",
        "/* Generated from design-tokens.json by Archeon */",
        "",
        ":root {",
        "  /* === SEMANTIC COLORS === */",
    ]
    
    # Add semantic color aliases
    if 'color' in tokens and 'semantic' in tokens['color']:
        for name, variants in tokens['color']['semantic'].items():
            if isinstance(variants, dict) and '$value' not in variants:
                for variant, token in variants.items():
                    if isinstance(token, dict) and '$value' in token:
                        resolved = resolve_reference(token['$value'], tokens)
                        lines.append(f"  --{name}-{to_kebab(variant)}: {resolved};")
    
    # Add surface aliases
    lines.append("")
    lines.append("  /* === SURFACES === */")
    if 'color' in tokens and 'surface' in tokens['color'] and 'light' in tokens['color']['surface']:
        for name, token in tokens['color']['surface']['light'].items():
            if isinstance(token, dict) and '$value' in token:
                resolved = resolve_reference(token['$value'], tokens)
                lines.append(f"  --surface-{to_kebab(name)}: {resolved};")
    
    # Add content aliases
    lines.append("")
    lines.append("  /* === CONTENT === */")
    if 'color' in tokens and 'content' in tokens['color'] and 'light' in tokens['color']['content']:
        for name, token in tokens['color']['content']['light'].items():
            if isinstance(token, dict) and '$value' in token:
                resolved = resolve_reference(token['$value'], tokens)
                lines.append(f"  --content-{to_kebab(name)}: {resolved};")
    
    # Add border aliases
    lines.append("")
    lines.append("  /* === BORDERS === */")
    if 'color' in tokens and 'border' in tokens['color'] and 'light' in tokens['color']['border']:
        for name, token in tokens['color']['border']['light'].items():
            if isinstance(token, dict) and '$value' in token:
                resolved = resolve_reference(token['$value'], tokens)
                lines.append(f"  --border-{to_kebab(name)}: {resolved};")
    
    # Add component tokens
    if 'component' in tokens:
        lines.append("")
        lines.append("  /* === COMPONENTS === */")
        for comp_name, comp_tokens in tokens['component'].items():
            if isinstance(comp_tokens, dict) and '$value' not in comp_tokens:
                for prop, val in comp_tokens.items():
                    if isinstance(val, dict) and '$value' in val:
                        resolved = resolve_reference(val['$value'], tokens)
                        lines.append(f"  --{to_kebab(comp_name)}-{to_kebab(prop)}: {resolved};")
                    elif isinstance(val, dict) and '$value' not in val:
                        # Nested (e.g., button.height.sm)
                        for size, size_val in val.items():
                            if isinstance(size_val, dict) and '$value' in size_val:
                                resolved = resolve_reference(size_val['$value'], tokens)
                                lines.append(f"  --{to_kebab(comp_name)}-{to_kebab(prop)}-{to_kebab(size)}: {resolved};")
    
    lines.append("}")
    
    # Dark mode overrides
    dark_lines = []
    if 'color' in tokens:
        color = tokens['color']
        if 'surface' in color and 'dark' in color['surface']:
            for name, token in color['surface']['dark'].items():
                if isinstance(token, dict) and '$value' in token:
                    resolved = resolve_reference(token['$value'], tokens)
                    dark_lines.append(f"  --surface-{to_kebab(name)}: {resolved};")
        if 'content' in color and 'dark' in color['content']:
            for name, token in color['content']['dark'].items():
                if isinstance(token, dict) and '$value' in token:
                    resolved = resolve_reference(token['$value'], tokens)
                    dark_lines.append(f"  --content-{to_kebab(name)}: {resolved};")
        if 'border' in color and 'dark' in color['border']:
            for name, token in color['border']['dark'].items():
                if isinstance(token, dict) and '$value' in token:
                    resolved = resolve_reference(token['$value'], tokens)
                    dark_lines.append(f"  --border-{to_kebab(name)}: {resolved};")
    
    if dark_lines:
        lines.extend([
            "",
            ".dark {",
            *dark_lines,
            "}"
        ])
    
    return "\n".join(lines)


class TokenTransformer:
    """Main class for transforming design tokens."""
    
    def __init__(self, tokens_path: Path):
        self.tokens_path = tokens_path
        self.tokens = self._load_tokens()
    
    def _load_tokens(self) -> Dict:
        """Load design tokens from JSON file."""
        if not self.tokens_path.exists():
            raise FileNotFoundError(f"Design tokens file not found: {self.tokens_path}")
        
        with open(self.tokens_path) as f:
            return json.load(f)
    
    def generate_all(self, output_dir: Path) -> List[Path]:
        """Generate all output files."""
        output_dir.mkdir(parents=True, exist_ok=True)
        generated = []
        
        # CSS variables (full)
        css_path = output_dir / "tokens.css"
        css_path.write_text(generate_css(self.tokens))
        generated.append(css_path)
        
        # Semantic CSS (for component use)
        semantic_path = output_dir / "tokens.semantic.css"
        semantic_path.write_text(generate_semantic_css(self.tokens))
        generated.append(semantic_path)
        
        # Tailwind extension
        tw_path = output_dir / "tokens.tailwind.js"
        tw_path.write_text(generate_tailwind_extension(self.tokens))
        generated.append(tw_path)
        
        # JavaScript module
        js_path = output_dir / "tokens.js"
        js_path.write_text(generate_js_tokens(self.tokens))
        generated.append(js_path)
        
        return generated
    
    def generate_css_only(self, output_path: Path) -> Path:
        """Generate only CSS variables."""
        output_path.write_text(generate_css(self.tokens))
        return output_path
    
    def get_metadata(self) -> Dict:
        """Get token file metadata."""
        return self.tokens.get('$metadata', {})
