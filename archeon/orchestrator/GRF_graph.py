"""
GRF_graph.py - Archeon Knowledge Graph

Stores and manages the knowledge graph of chains.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

from archeon.orchestrator.PRS_parser import ChainAST, GlyphNode, Edge, parse_chain, ParseError


@dataclass
class StoredChain:
    """A chain stored in the graph with metadata."""
    ast: ChainAST
    line_number: int = 0
    section: str = ""


@dataclass
class Resolution:
    """Tracks resolved (generated) artifacts for a glyph."""
    glyph: str
    file_path: str
    test_path: Optional[str] = None
    generated_at: Optional[str] = None


class KnowledgeGraph:
    """In-memory knowledge graph built from ARCHEON.arcon."""

    def __init__(self):
        self.chains: list[StoredChain] = []
        self.sections: dict[str, list[int]] = {}  # section name -> chain indices
        self._glyph_index: dict[str, list[int]] = {}  # glyph name -> chain indices
        self._resolutions: dict[str, Resolution] = {}  # glyph -> resolution
        self._filepath: Optional[str] = None

    def load(self, filepath: str) -> None:
        """Load graph from .arcon file."""
        self._filepath = filepath
        self.chains = []
        self.sections = {}
        self._glyph_index = {}

        current_section = ""
        line_number = 0

        with open(filepath, 'r') as f:
            for line in f:
                line_number += 1
                stripped = line.strip()

                # Track sections (## headers)
                if stripped.startswith('## '):
                    current_section = stripped[3:].strip()
                    if current_section not in self.sections:
                        self.sections[current_section] = []
                    continue

                # Skip comments and empty lines
                if not stripped or stripped.startswith('#'):
                    continue

                # Parse chain
                try:
                    ast = parse_chain(stripped)
                    if ast.nodes:
                        chain_idx = len(self.chains)
                        self.chains.append(StoredChain(
                            ast=ast,
                            line_number=line_number,
                            section=current_section
                        ))

                        # Index by section
                        if current_section in self.sections:
                            self.sections[current_section].append(chain_idx)

                        # Index by glyph
                        for node in ast.nodes:
                            key = node.qualified_name
                            if key not in self._glyph_index:
                                self._glyph_index[key] = []
                            self._glyph_index[key].append(chain_idx)

                except ParseError:
                    continue

    def save(self, filepath: Optional[str] = None) -> None:
        """Save graph to .arcon file."""
        filepath = filepath or self._filepath
        if not filepath:
            raise ValueError("No filepath specified")

        lines = [
            "# Archeon Knowledge Graph",
            "# Version: 2.0",
            f"# Project: {Path(filepath).parent.name}",
            "",
        ]

        # Group chains by section
        sections_written = set()
        for section_name, chain_indices in self.sections.items():
            if section_name:
                lines.append(f"## {section_name}")
            for idx in chain_indices:
                if idx < len(self.chains):
                    lines.append(self.chains[idx].ast.raw)
            lines.append("")
            sections_written.update(chain_indices)

        # Write unsectioned chains
        unsectioned = [i for i in range(len(self.chains)) if i not in sections_written]
        if unsectioned:
            lines.append("## Unsorted")
            for idx in unsectioned:
                lines.append(self.chains[idx].ast.raw)

        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))

        self._filepath = filepath

    def add_chain(self, chain_str: str, section: str = "") -> StoredChain:
        """Parse and add a chain to the graph."""
        ast = parse_chain(chain_str)
        if not ast.nodes:
            raise ValueError("Empty chain")

        # Check for version conflicts
        root_glyph = ast.nodes[0].qualified_name
        existing = self.find_chains_by_glyph(root_glyph)

        if existing and ast.version:
            for stored in existing:
                if stored.ast.version == ast.version:
                    raise ValueError(f"Version {ast.version} already exists for {root_glyph}")

        # Auto-assign version if not specified
        if not ast.version and existing:
            max_version = 0
            for stored in existing:
                if stored.ast.version and stored.ast.version.startswith('v'):
                    try:
                        v = int(stored.ast.version[1:])
                        max_version = max(max_version, v)
                    except ValueError:
                        pass
            ast.version = f"v{max_version + 1}"
            # Update raw string
            ast.raw = f"@{ast.version} {ast.raw}"

        chain_idx = len(self.chains)
        stored = StoredChain(ast=ast, section=section)
        self.chains.append(stored)

        # Update indices
        if section:
            if section not in self.sections:
                self.sections[section] = []
            self.sections[section].append(chain_idx)

        for node in ast.nodes:
            key = node.qualified_name
            if key not in self._glyph_index:
                self._glyph_index[key] = []
            self._glyph_index[key].append(chain_idx)

        return stored

    def remove_chain(self, version: str, root_glyph: str) -> bool:
        """Remove a chain by version and root glyph."""
        for i, stored in enumerate(self.chains):
            if stored.ast.version == version:
                if stored.ast.nodes and stored.ast.nodes[0].qualified_name == root_glyph:
                    self.chains.pop(i)
                    self._rebuild_indices()
                    return True
        return False

    def deprecate_chain(self, version: str, root_glyph: str) -> bool:
        """Mark a chain as deprecated."""
        for stored in self.chains:
            if stored.ast.version == version:
                if stored.ast.nodes and stored.ast.nodes[0].qualified_name == root_glyph:
                    stored.ast.deprecated = True
                    if '[deprecated]' not in stored.ast.raw:
                        stored.ast.raw = stored.ast.raw.replace(
                            f"@{version}",
                            f"@{version} [deprecated]"
                        )
                    return True
        return False

    def find_chains_by_glyph(self, glyph_name: str) -> list[StoredChain]:
        """Find all chains containing a glyph."""
        indices = self._glyph_index.get(glyph_name, [])
        return [self.chains[i] for i in indices if i < len(self.chains)]

    def find_dependencies(self, glyph_name: str) -> list[GlyphNode]:
        """Find upstream dependencies of a glyph."""
        deps = []
        for stored in self.chains:
            for i, node in enumerate(stored.ast.nodes):
                if node.qualified_name == glyph_name:
                    # Find nodes that point to this one
                    for edge in stored.ast.edges:
                        if edge.target_idx == i:
                            deps.append(stored.ast.nodes[edge.source_idx])
        return deps

    def find_dependents(self, glyph_name: str) -> list[GlyphNode]:
        """Find downstream dependents of a glyph."""
        deps = []
        for stored in self.chains:
            for i, node in enumerate(stored.ast.nodes):
                if node.qualified_name == glyph_name:
                    # Find nodes this one points to
                    for edge in stored.ast.edges:
                        if edge.source_idx == i:
                            deps.append(stored.ast.nodes[edge.target_idx])
        return deps

    def get_all_glyphs(self) -> set[str]:
        """Get all unique glyphs in the graph."""
        return set(self._glyph_index.keys())

    def get_unresolved_glyphs(self) -> set[str]:
        """Get glyphs that need code generation (no resolved artifacts)."""
        from archeon.config.legend import GLYPH_LEGEND
        
        unresolved = set()
        for glyph in self._glyph_index.keys():
            # Skip if already resolved
            if glyph in self._resolutions:
                continue
            
            # Extract prefix from glyph
            prefix = glyph.split(':')[0] if ':' in glyph else glyph
            
            # Skip meta glyphs (no code gen)
            glyph_def = GLYPH_LEGEND.get(prefix, {})
            if glyph_def.get('layer') == 'meta':
                continue
            
            # Skip V (structural container, no code)
            if prefix == 'V':
                continue
            
            # Skip internal orchestrator glyphs
            if glyph_def.get('layer') == 'internal':
                continue
            
            # This glyph needs generation
            if glyph_def.get('agent'):
                unresolved.add(glyph)
        
        return unresolved

    def mark_resolved(self, glyph: str, file_path: str, test_path: Optional[str] = None) -> None:
        """Mark a glyph as resolved (code generated)."""
        from datetime import datetime
        self._resolutions[glyph] = Resolution(
            glyph=glyph,
            file_path=file_path,
            test_path=test_path,
            generated_at=datetime.now().isoformat()
        )

    def is_resolved(self, glyph: str) -> bool:
        """Check if a glyph has been resolved."""
        return glyph in self._resolutions

    def get_resolution(self, glyph: str) -> Optional[Resolution]:
        """Get resolution info for a glyph."""
        return self._resolutions.get(glyph)

    def clear_resolution(self, glyph: str) -> None:
        """Clear resolution status for a glyph (force regeneration)."""
        self._resolutions.pop(glyph, None)

    def get_chains_by_version(self, root_glyph: str) -> dict[str, StoredChain]:
        """Get all versions of chains starting with a glyph."""
        versions = {}
        for stored in self.find_chains_by_glyph(root_glyph):
            if stored.ast.nodes[0].qualified_name == root_glyph:
                version = stored.ast.version or 'unversioned'
                versions[version] = stored
        return versions

    def get_latest_chain(self, root_glyph: str) -> Optional[StoredChain]:
        """Get the latest (highest version) chain for a root glyph."""
        versions = self.get_chains_by_version(root_glyph)
        if not versions:
            return None

        if 'latest' in versions:
            return versions['latest']

        # Find highest numeric version
        max_v = -1
        latest = None
        for v, chain in versions.items():
            if v.startswith('v'):
                try:
                    num = int(v[1:])
                    if num > max_v:
                        max_v = num
                        latest = chain
                except ValueError:
                    pass
        return latest or list(versions.values())[0]

    def _rebuild_indices(self) -> None:
        """Rebuild internal indices after mutation."""
        self._glyph_index = {}
        self.sections = {}

        for i, stored in enumerate(self.chains):
            if stored.section:
                if stored.section not in self.sections:
                    self.sections[stored.section] = []
                self.sections[stored.section].append(i)

            for node in stored.ast.nodes:
                key = node.qualified_name
                if key not in self._glyph_index:
                    self._glyph_index[key] = []
                self._glyph_index[key].append(i)

    def stats(self) -> dict:
        """Get graph statistics."""
        return {
            'total_chains': len(self.chains),
            'total_glyphs': len(self._glyph_index),
            'sections': list(self.sections.keys()),
            'deprecated': sum(1 for c in self.chains if c.ast.deprecated),
        }

    def find_similar_chains(self, proposed_chain: str, threshold: float = 0.3) -> list[tuple[StoredChain, float, list[str]]]:
        """
        Find existing chains that are similar to a proposed chain.
        
        Args:
            proposed_chain: The proposed chain string to compare
            threshold: Minimum similarity score (0-1) to include
            
        Returns:
            List of (StoredChain, similarity_score, shared_glyphs) sorted by similarity
        """
        # Extract glyphs from proposed chain
        proposed_glyphs = set()
        for part in proposed_chain.replace(' => ', '|').replace(' -> ', '|').replace(' ~> ', '|').split('|'):
            part = part.strip()
            if part and ':' in part:
                # Extract the base glyph (e.g., NED:login from NED:login)
                proposed_glyphs.add(part)
                # Also add the prefix for broader matching
                prefix = part.split(':')[0]
                name = part.split(':')[1].split('.')[0].split('(')[0].lower() if ':' in part else ''
                proposed_glyphs.add(f"{prefix}:{name}")
        
        similar = []
        
        for stored in self.chains:
            if stored.ast.deprecated:
                continue
                
            # Extract glyphs from stored chain
            stored_glyphs = set()
            for node in stored.ast.nodes:
                stored_glyphs.add(node.qualified_name)
                # Also add normalized version for comparison
                prefix = node.prefix
                name = node.name.split('.')[0].split('(')[0].lower() if node.name else ''
                stored_glyphs.add(f"{prefix}:{name}")
            
            # Calculate Jaccard similarity
            shared = proposed_glyphs & stored_glyphs
            union = proposed_glyphs | stored_glyphs
            
            if union:
                similarity = len(shared) / len(union)
                
                if similarity >= threshold:
                    # Get the actual shared glyph names
                    shared_names = [g for g in shared if g in [n.qualified_name for n in stored.ast.nodes]]
                    similar.append((stored, similarity, shared_names))
        
        # Sort by similarity (highest first)
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar


def load_graph(filepath: str) -> KnowledgeGraph:
    """Convenience function to load a graph."""
    graph = KnowledgeGraph()
    if os.path.exists(filepath):
        graph.load(filepath)
    return graph
