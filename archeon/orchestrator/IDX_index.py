"""
IDX_index.py - Archeon Semantic Index

Builds and maintains the semantic affordance index (ARCHEON.index.json).
This is the AI's fast-lookup table for navigating the codebase.

The index stores:
- glyph -> file mapping
- intent per glyph
- sections within each file
- chain references

The index is:
- Built by scanning @archeon:section comments
- Deterministically reproducible
- The source of truth is the code itself
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

from archeon.orchestrator.SCN_scanner import (
    scan_file,
    scan_directory,
    get_section_names,
    ScannedFile,
)


@dataclass
class GlyphEntry:
    """Index entry for a single glyph."""
    glyph: str
    file: str
    intent: str = ""
    chain: str = ""
    sections: list[str] = field(default_factory=list)


@dataclass
class SemanticIndex:
    """The complete semantic index for a project."""
    version: str = "1.0"
    project: str = ""
    entries: dict[str, GlyphEntry] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "version": self.version,
            "project": self.project,
            "glyphs": {
                glyph: {
                    "file": entry.file,
                    "intent": entry.intent,
                    "chain": entry.chain,
                    "sections": entry.sections,
                }
                for glyph, entry in self.entries.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SemanticIndex":
        """Load from dictionary."""
        index = cls(
            version=data.get("version", "1.0"),
            project=data.get("project", ""),
        )
        
        glyphs = data.get("glyphs", {})
        for glyph, entry_data in glyphs.items():
            index.entries[glyph] = GlyphEntry(
                glyph=glyph,
                file=entry_data.get("file", ""),
                intent=entry_data.get("intent", ""),
                chain=entry_data.get("chain", ""),
                sections=entry_data.get("sections", []),
            )
        
        return index


class IndexBuilder:
    """Builds and maintains the semantic index."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.index = SemanticIndex(
            project=self.project_root.name
        )
    
    def build_from_directory(
        self,
        directory: Optional[str] = None,
        extensions: Optional[list[str]] = None
    ) -> SemanticIndex:
        """
        Scan a directory and build the complete index.
        
        Args:
            directory: Directory to scan (default: project root)
            extensions: File extensions to include
            
        Returns:
            The built SemanticIndex
        """
        scan_dir = directory or str(self.project_root)
        scanned_files = scan_directory(scan_dir, extensions)
        
        for scanned in scanned_files:
            self._add_scanned_file(scanned)
        
        return self.index
    
    def build_from_file(self, filepath: str) -> Optional[GlyphEntry]:
        """
        Scan a single file and add/update its entry.
        
        Args:
            filepath: Path to the file
            
        Returns:
            The GlyphEntry if file is an Archeon file, None otherwise
        """
        scanned = scan_file(filepath)
        if not scanned.is_archeon_file:
            return None
        
        return self._add_scanned_file(scanned)
    
    def _add_scanned_file(self, scanned: ScannedFile) -> Optional[GlyphEntry]:
        """Add a scanned file to the index."""
        if not scanned.is_archeon_file or not scanned.header.glyph:
            return None
        
        # Skip template placeholder files (have {PLACEHOLDER} values)
        glyph = scanned.header.glyph
        if '{' in glyph or glyph.startswith('{'):
            return None
        
        # Skip if intent is a placeholder
        intent = scanned.header.intent
        if intent and ('{' in intent or intent.startswith('{')):
            intent = ""  # Clear placeholder, keep file indexed
        
        # Skip if chain is a placeholder  
        chain = scanned.header.chain
        if chain and ('{' in chain or chain.startswith('{')):
            chain = ""  # Clear placeholder, keep file indexed
        
        # Make path relative to project root
        try:
            rel_path = Path(scanned.path).relative_to(self.project_root)
        except ValueError:
            rel_path = Path(scanned.path)
        
        entry = GlyphEntry(
            glyph=glyph,
            file=str(rel_path),
            intent=intent,
            chain=chain,
            sections=get_section_names(scanned),
        )
        
        self.index.entries[entry.glyph] = entry
        return entry
    
    def remove_glyph(self, glyph: str) -> bool:
        """Remove a glyph from the index."""
        if glyph in self.index.entries:
            del self.index.entries[glyph]
            return True
        return False
    
    def get_entry(self, glyph: str) -> Optional[GlyphEntry]:
        """Get the index entry for a glyph."""
        return self.index.entries.get(glyph)
    
    def get_file_for_glyph(self, glyph: str) -> Optional[str]:
        """Get the file path for a glyph."""
        entry = self.index.entries.get(glyph)
        return entry.file if entry else None
    
    def get_sections_for_glyph(self, glyph: str) -> list[str]:
        """Get the section names for a glyph."""
        entry = self.index.entries.get(glyph)
        return entry.sections if entry else []
    
    def save(self, filepath: Optional[str] = None) -> str:
        """
        Save the index to a JSON file.
        
        Args:
            filepath: Output path (default: archeon/ARCHEON.index.json)
            
        Returns:
            Path to the saved file
        """
        if filepath is None:
            # Save in archeon/ directory, not project root
            archeon_dir = self.project_root / "archeon"
            if archeon_dir.exists():
                filepath = str(archeon_dir / "ARCHEON.index.json")
            else:
                filepath = str(self.project_root / "ARCHEON.index.json")
        
        with open(filepath, 'w') as f:
            json.dump(self.index.to_dict(), f, indent=2)
        
        return filepath
    
    def load(self, filepath: Optional[str] = None) -> SemanticIndex:
        """
        Load an existing index from JSON.
        
        Args:
            filepath: Input path (default: archeon/ARCHEON.index.json)
            
        Returns:
            The loaded SemanticIndex
        """
        if filepath is None:
            # Load from archeon/ directory first, fallback to root
            archeon_dir = self.project_root / "archeon"
            archeon_path = archeon_dir / "ARCHEON.index.json"
            if archeon_path.exists():
                filepath = str(archeon_path)
            else:
                filepath = str(self.project_root / "ARCHEON.index.json")
        
        if not Path(filepath).exists():
            return self.index
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.index = SemanticIndex.from_dict(data)
        return self.index


def build_index(project_root: str, output_path: Optional[str] = None) -> str:
    """
    Convenience function to build and save the index.
    
    Args:
        project_root: Root directory of the project
        output_path: Where to save the index (default: ARCHEON.index.json)
        
    Returns:
        Path to the saved index file
    """
    builder = IndexBuilder(project_root)
    builder.build_from_directory()
    return builder.save(output_path)


def load_index(project_root: str) -> SemanticIndex:
    """
    Convenience function to load an existing index.
    
    Args:
        project_root: Root directory of the project
        
    Returns:
        The loaded SemanticIndex
    """
    builder = IndexBuilder(project_root)
    return builder.load()


def format_index_for_prompt(
    index: SemanticIndex,
    glyphs: Optional[list[str]] = None
) -> str:
    """
    Format the index for inclusion in an LLM prompt.
    
    Args:
        index: The semantic index
        glyphs: Specific glyphs to include (default: all)
        
    Returns:
        Formatted string for prompt injection
    """
    lines = ["INDEX:"]
    
    entries = index.entries
    if glyphs:
        entries = {g: e for g, e in entries.items() if g in glyphs}
    
    for glyph, entry in sorted(entries.items()):
        lines.append(f"{glyph}")
        lines.append(f"  file: {entry.file}")
        if entry.intent:
            lines.append(f"  intent: {entry.intent}")
        if entry.sections:
            lines.append(f"  sections:")
            for section in entry.sections:
                lines.append(f"    - {section}")
    
    return "\n".join(lines)


def format_scope_instruction(
    entry: GlyphEntry,
    sections: Optional[list[str]] = None
) -> str:
    """
    Generate scope instructions for editing a specific glyph.
    
    Args:
        entry: The glyph's index entry
        sections: Specific sections to allow editing (default: all)
        
    Returns:
        Formatted scope instruction for prompt
    """
    lines = [
        "SCOPE:",
        f"- File: {entry.file}",
    ]
    
    allowed_sections = sections or entry.sections
    if allowed_sections:
        lines.append("- Modify only sections:")
        for section in allowed_sections:
            lines.append(f"    - {section}")
    
    lines.extend([
        "",
        "RULES:",
        "- Do not edit outside @archeon:section blocks",
        "- If a new section is required, request permission",
        "- Preserve all @archeon markers",
    ])
    
    return "\n".join(lines)
