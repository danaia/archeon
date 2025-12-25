"""
Architecture shapes module.

This package contains JSON-based architecture shape definitions (.shape.json)
that drive the Archeon code generation system.

Available shapes are loaded from *.shape.json files in this directory.

Usage:
    from archeon.orchestrator.SHP_shape import list_architectures, load_architecture
    
    # List all available shapes
    shapes = list_architectures()
    
    # Load a specific shape
    shape = load_architecture("vue3-fastapi")
    
    # Get a glyph snippet
    snippet = shape.glyphs["CMP"].snippet
"""

from archeon.orchestrator.SHP_shape import (
    list_architectures,
    load_architecture,
    render_glyph,
    get_loader,
    ShapeLoader,
    ArchitectureShape,
    GlyphShape,
)

__all__ = [
    "list_architectures",
    "load_architecture", 
    "render_glyph",
    "get_loader",
    "ShapeLoader",
    "ArchitectureShape",
    "GlyphShape",
]
