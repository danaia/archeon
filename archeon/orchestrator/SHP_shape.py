"""
Architecture Shape Loader - Central JSON-driven template system.

This module loads .shape.json files that define complete architecture templates
including glyph snippets, directory structures, and configurations.
"""

import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class GlyphShape:
    """A single glyph's template configuration."""
    layer: str
    output_directory: str
    output_extension: str
    output_naming: str
    sections: list[str]
    snippet: str
    placeholders: dict[str, dict]


@dataclass
class ArchitectureShape:
    """Complete architecture shape loaded from JSON."""
    id: str
    name: str
    version: str
    description: str
    tags: list[str]
    stack: dict
    directories: dict
    glyphs: dict[str, GlyphShape]
    config: dict
    dependencies: dict
    prebuilt: dict  # Pre-built components like ThemeToggle
    
    @classmethod
    def from_json(cls, data: dict) -> "ArchitectureShape":
        """Parse JSON data into ArchitectureShape."""
        meta = data.get("meta", {})
        glyphs = {}
        
        for glyph_name, glyph_data in data.get("glyphs", {}).items():
            output = glyph_data.get("output", {})
            glyphs[glyph_name] = GlyphShape(
                layer=glyph_data.get("layer", "shared"),
                output_directory=output.get("directory", ""),
                output_extension=output.get("extension", ""),
                output_naming=output.get("naming", "PascalCase"),
                sections=glyph_data.get("sections", []),
                snippet=glyph_data.get("snippet", ""),
                placeholders=glyph_data.get("placeholders", {}),
            )
        
        return cls(
            id=meta.get("id", "unknown"),
            name=meta.get("name", "Unknown"),
            version=meta.get("version", "0.0.0"),
            description=meta.get("description", ""),
            tags=meta.get("tags", []),
            stack=data.get("stack", {}),
            directories=data.get("directories", {}),
            glyphs=glyphs,
            config=data.get("config", {}),
            dependencies=data.get("dependencies", {}),
            prebuilt=data.get("prebuilt", {}),
        )


class ShapeLoader:
    """Loads and manages architecture shape files."""
    
    def __init__(self, shapes_dir: Optional[Path] = None):
        """Initialize with shapes directory path."""
        if shapes_dir is None:
            # Look in archeon/architectures (parent of orchestrator)
            shapes_dir = Path(__file__).parent.parent / "architectures"
        self.shapes_dir = shapes_dir
        self._cache: dict[str, ArchitectureShape] = {}
    
    def get_shapes_dir(self) -> Path:
        """Get the architectures directory path."""
        return self.shapes_dir
    
    def list_shapes(self) -> list[dict]:
        """List all available architecture shapes with metadata."""
        shapes = []
        if not self.shapes_dir.exists():
            return shapes
        
        for shape_file in self.shapes_dir.glob("*.shape.json"):
            try:
                with open(shape_file, "r") as f:
                    data = json.load(f)
                    meta = data.get("meta", {})
                    shapes.append({
                        "id": meta.get("id", shape_file.stem),
                        "name": meta.get("name", shape_file.stem),
                        "description": meta.get("description", ""),
                        "tags": meta.get("tags", []),
                        "file": shape_file.name,
                    })
            except (json.JSONDecodeError, IOError):
                continue
        
        return shapes
    
    def load_shape(self, shape_id: str) -> Optional[ArchitectureShape]:
        """Load a shape by ID. Returns cached version if available."""
        if shape_id in self._cache:
            return self._cache[shape_id]
        
        shape_file = self.shapes_dir / f"{shape_id}.shape.json"
        if not shape_file.exists():
            # Try to find by scanning all shapes
            for f in self.shapes_dir.glob("*.shape.json"):
                try:
                    with open(f, "r") as file:
                        data = json.load(file)
                        if data.get("meta", {}).get("id") == shape_id:
                            shape_file = f
                            break
                except (json.JSONDecodeError, IOError):
                    continue
            else:
                return None
        
        try:
            with open(shape_file, "r") as f:
                data = json.load(f)
                shape = ArchitectureShape.from_json(data)
                self._cache[shape_id] = shape
                return shape
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading shape {shape_id}: {e}")
            return None
    
    def get_glyph_snippet(self, shape_id: str, glyph: str) -> Optional[str]:
        """Get the code snippet template for a specific glyph in a shape."""
        shape = self.load_shape(shape_id)
        if shape and glyph in shape.glyphs:
            return shape.glyphs[glyph].snippet
        return None
    
    def get_glyph_shape(self, shape_id: str, glyph: str) -> Optional[GlyphShape]:
        """Get the full glyph configuration."""
        shape = self.load_shape(shape_id)
        if shape and glyph in shape.glyphs:
            return shape.glyphs[glyph]
        return None
    
    def render_snippet(
        self,
        shape_id: str,
        glyph: str,
        values: dict[str, str],
    ) -> Optional[str]:
        """Render a glyph snippet with placeholder values."""
        snippet = self.get_glyph_snippet(shape_id, glyph)
        if snippet is None:
            return None
        
        # Replace placeholders with values
        result = snippet
        glyph_shape = self.get_glyph_shape(shape_id, glyph)
        
        if glyph_shape:
            for placeholder, config in glyph_shape.placeholders.items():
                key = f"{{{placeholder}}}"
                value = values.get(placeholder, config.get("default", ""))
                result = result.replace(key, str(value))
        
        return result
    
    def get_output_path(
        self,
        shape_id: str,
        glyph: str,
        name: str,
    ) -> Optional[str]:
        """Get the output file path for a generated glyph."""
        shape = self.load_shape(shape_id)
        glyph_shape = self.get_glyph_shape(shape_id, glyph)
        
        if not shape or not glyph_shape:
            return None
        
        # Determine layer and directory
        layer = glyph_shape.layer
        dir_key = glyph_shape.output_directory
        
        # Get directory from shape directories config
        if layer in shape.directories and dir_key in shape.directories[layer]:
            directory = shape.directories[layer][dir_key]
        else:
            directory = dir_key
        
        # Apply naming convention
        naming = glyph_shape.output_naming
        if naming == "PascalCase":
            filename = name
        elif naming == "camelCase":
            filename = name[0].lower() + name[1:] if name else name
        elif naming == "kebab-case":
            filename = "".join(
                f"-{c.lower()}" if c.isupper() else c for c in name
            ).lstrip("-")
        elif naming == "snake_case":
            filename = "".join(
                f"_{c.lower()}" if c.isupper() else c for c in name
            ).lstrip("_")
        else:
            filename = name
        
        ext = glyph_shape.output_extension
        return f"{directory}/{filename}{ext}"


# Global loader instance
_loader: Optional[ShapeLoader] = None


def get_loader() -> ShapeLoader:
    """Get the global ShapeLoader instance."""
    global _loader
    if _loader is None:
        _loader = ShapeLoader()
    return _loader


def list_architectures() -> list[dict]:
    """List all available architecture shapes."""
    return get_loader().list_shapes()


def load_architecture(arch_id: str) -> Optional[ArchitectureShape]:
    """Load an architecture shape by ID."""
    return get_loader().load_shape(arch_id)


def render_glyph(
    arch_id: str,
    glyph: str,
    values: dict[str, str],
) -> Optional[str]:
    """Render a glyph snippet with values."""
    return get_loader().render_snippet(arch_id, glyph, values)
