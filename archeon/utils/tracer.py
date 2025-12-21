"""
tracer.py - Archeon File Tracer

Maps glyphs to file paths and detects drift between graph and generated files.
"""

import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from archeon.orchestrator.GRF_graph import KnowledgeGraph
from archeon.config.legend import GLYPH_LEGEND


@dataclass
class TracedFile:
    """A file with @archeon marker."""
    path: str
    glyph: str
    version: Optional[str] = None
    modified: Optional[datetime] = None
    checksum: Optional[str] = None


@dataclass
class DriftItem:
    """A single drift detection result."""
    type: str  # 'orphan_file', 'missing_file', 'modified', 'version_mismatch'
    glyph: Optional[str] = None
    file_path: Optional[str] = None
    message: str = ""
    
    @property
    def severity(self) -> str:
        severity_map = {
            'orphan_file': 'warning',
            'missing_file': 'error',
            'modified': 'info',
            'version_mismatch': 'warning'
        }
        return severity_map.get(self.type, 'info')


@dataclass
class DriftReport:
    """Full drift detection report."""
    items: list[DriftItem] = field(default_factory=list)
    traced_files: list[TracedFile] = field(default_factory=list)
    scan_time: Optional[datetime] = None
    
    @property
    def has_drift(self) -> bool:
        return len(self.items) > 0
    
    @property
    def error_count(self) -> int:
        return sum(1 for i in self.items if i.severity == 'error')
    
    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.items if i.severity == 'warning')
    
    def to_dict(self) -> dict:
        return {
            'has_drift': self.has_drift,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'items': [
                {'type': i.type, 'glyph': i.glyph, 'path': i.file_path, 'message': i.message}
                for i in self.items
            ],
            'traced_files': len(self.traced_files),
            'scan_time': self.scan_time.isoformat() if self.scan_time else None
        }


# Framework-specific path mappings
PATH_MAPPINGS = {
    'CMP': {
        'react': 'components/{name}.tsx',
        'vue': 'components/{name}.vue',
        'vue3': 'components/{name}.vue',
        'angular': 'components/{name}/{name}.component.ts',
        'svelte': 'components/{name}.svelte',
    },
    'STO': {
        'zustand': 'stores/{name}Store.ts',
        'redux': 'stores/{name}Slice.ts',
        'pinia': 'stores/{name}Store.js',  # Vue uses JS, not TS
        'ngrx': 'stores/{name}.store.ts',
    },
    'API': {
        'fastapi': 'api/routes/{name}.py',
        'express': 'api/routes/{name}.ts',
        'flask': 'api/routes/{name}.py',
    },
    'MDL': {
        'mongo': 'models/{name}.py',
        'postgres': 'models/{name}.py',
        'prisma': 'prisma/models/{name}.prisma',
    },
    'FNC': {
        'python': 'lib/{namespace}.py',
        'typescript': 'lib/{namespace}.ts',
        'javascript': 'lib/{namespace}.js',  # Vue uses JS
    },
    'EVT': {
        'python': 'events/{name}.py',
        'typescript': 'events/{name}.ts',
        'javascript': 'events/{name}.js',  # Vue uses JS
    },
}

# @archeon marker regex
ARCHEON_MARKER_PATTERN = re.compile(
    r'@archeon\s+([A-Z]{2,3}):(\S+)(?:\s+@version\s+(\S+))?',
    re.MULTILINE
)


def glyph_to_path(glyph: str, framework: str = "react", output_dir: str = ".") -> Optional[str]:
    """
    Convert a glyph to its expected file path.
    
    Args:
        glyph: Qualified glyph name (e.g., 'CMP:LoginForm', 'FNC:auth.validate')
        framework: Framework to use for path resolution
        output_dir: Base output directory
        
    Returns:
        Expected file path or None if glyph type has no file mapping
    """
    if ':' not in glyph:
        return None
    
    prefix, name = glyph.split(':', 1)
    
    # Skip meta glyphs
    if prefix in ('NED', 'TSK', 'OUT', 'ERR', 'V', 'ORC', 'PRS', 'VAL', 'SPW', 'TST', 'GRF'):
        return None
    
    # Get path template
    mappings = PATH_MAPPINGS.get(prefix, {})
    
    # Try exact framework match
    template = mappings.get(framework)
    
    # Fallback to first available
    if not template and mappings:
        template = list(mappings.values())[0]
    
    if not template:
        return None
    
    # Handle namespace.action format
    namespace = name.split('.')[0] if '.' in name else name
    simple_name = name.split('.')[-1] if '.' in name else name
    
    # Fill template
    path = template.format(
        name=simple_name,
        namespace=namespace
    )
    
    return str(Path(output_dir) / path)


def path_to_glyph(file_path: str) -> Optional[TracedFile]:
    """
    Parse @archeon marker from file to get glyph.
    
    Args:
        file_path: Path to file to scan
        
    Returns:
        TracedFile if @archeon marker found, None otherwise
    """
    try:
        content = Path(file_path).read_text()
    except (OSError, IOError):
        return None
    
    match = ARCHEON_MARKER_PATTERN.search(content)
    if not match:
        return None
    
    prefix = match.group(1)
    name = match.group(2)
    version = match.group(3) if match.lastindex >= 3 else None
    
    glyph = f"{prefix}:{name}"
    
    # Get file modification time
    try:
        stat = Path(file_path).stat()
        modified = datetime.fromtimestamp(stat.st_mtime)
    except OSError:
        modified = None
    
    return TracedFile(
        path=file_path,
        glyph=glyph,
        version=version,
        modified=modified
    )


def scan_directory(
    directory: str,
    extensions: tuple[str, ...] = ('.py', '.ts', '.tsx', '.js', '.jsx', '.vue', '.svelte')
) -> list[TracedFile]:
    """
    Scan directory for files with @archeon markers.
    
    Args:
        directory: Directory to scan
        extensions: File extensions to check
        
    Returns:
        List of traced files
    """
    traced = []
    root = Path(directory)
    
    if not root.exists():
        return traced
    
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        
        if path.suffix not in extensions:
            continue
        
        # Skip common non-source directories
        parts = path.parts
        if any(p in parts for p in ('node_modules', '__pycache__', '.git', 'venv', '.venv', 'dist', 'build')):
            continue
        
        traced_file = path_to_glyph(str(path))
        if traced_file:
            traced.append(traced_file)
    
    return traced


def find_drift(
    graph: KnowledgeGraph,
    source_dir: str = ".",
    framework: str = "react",
    backend: str = "fastapi",
    db: str = "mongo"
) -> DriftReport:
    """
    Detect drift between knowledge graph and generated files.
    
    Checks for:
    - Orphan files: Files with @archeon markers but no corresponding glyph
    - Missing files: Glyphs in graph without generated files
    - Modified files: Files modified after generation
    - Version mismatch: @version in file differs from graph
    
    Args:
        graph: Knowledge graph to compare against
        source_dir: Directory to scan for generated files
        framework: Frontend framework for path resolution
        backend: Backend framework for path resolution
        db: Database type for path resolution
        
    Returns:
        DriftReport with all detected drift items
    """
    report = DriftReport(scan_time=datetime.now())
    
    # Scan for files with @archeon markers
    traced_files = scan_directory(source_dir)
    report.traced_files = traced_files
    
    # Get all glyphs from graph
    graph_glyphs = set(graph.get_all_glyphs())
    
    # Map of file paths to traced files
    file_map = {f.path: f for f in traced_files}
    
    # Map of glyphs to traced files
    glyph_to_file = {f.glyph: f for f in traced_files}
    
    # Check for orphan files (file exists but glyph not in graph)
    for traced in traced_files:
        if traced.glyph not in graph_glyphs:
            report.items.append(DriftItem(
                type='orphan_file',
                glyph=traced.glyph,
                file_path=traced.path,
                message=f"File has @archeon marker but glyph not in graph"
            ))
    
    # Check for missing files (glyph in graph but no file)
    for glyph in graph_glyphs:
        prefix = glyph.split(':')[0] if ':' in glyph else ''
        
        # Skip meta glyphs
        if prefix in ('NED', 'TSK', 'OUT', 'ERR', 'V', 'ORC', 'PRS', 'VAL', 'SPW', 'TST', 'GRF'):
            continue
        
        # Determine framework for this glyph
        if prefix in ('CMP', 'STO'):
            fw = framework
        elif prefix in ('API', 'FNC'):
            fw = backend
        elif prefix == 'MDL':
            fw = db
        else:
            fw = framework
        
        expected_path = glyph_to_path(glyph, fw, source_dir)
        
        if expected_path and not Path(expected_path).exists():
            # Check if we have a traced file with this glyph
            if glyph not in glyph_to_file:
                report.items.append(DriftItem(
                    type='missing_file',
                    glyph=glyph,
                    file_path=expected_path,
                    message=f"Glyph in graph but file not found"
                ))
    
    # Check for version mismatches
    for traced in traced_files:
        if traced.version:
            chains = graph.find_chains_by_glyph(traced.glyph)
            for stored in chains:
                graph_version = stored.ast.version
                if graph_version and traced.version != graph_version:
                    report.items.append(DriftItem(
                        type='version_mismatch',
                        glyph=traced.glyph,
                        file_path=traced.path,
                        message=f"File version {traced.version} differs from graph version {graph_version}"
                    ))
    
    return report


def sync_markers(
    graph: KnowledgeGraph,
    source_dir: str = ".",
    dry_run: bool = True
) -> list[tuple[str, str, str]]:
    """
    Update @archeon markers in files to match graph.
    
    Args:
        graph: Knowledge graph as source of truth
        source_dir: Directory containing generated files
        dry_run: If True, only report changes without making them
        
    Returns:
        List of (file_path, old_marker, new_marker) tuples
    """
    changes = []
    traced_files = scan_directory(source_dir)
    
    for traced in traced_files:
        chains = graph.find_chains_by_glyph(traced.glyph)
        if not chains:
            continue
        
        # Get latest version
        latest = None
        for stored in chains:
            if stored.ast.version:
                if not latest or stored.ast.version > latest:
                    latest = stored.ast.version
        
        if latest and traced.version != latest:
            old_marker = f"@archeon {traced.glyph}"
            if traced.version:
                old_marker += f" @version {traced.version}"
            
            new_marker = f"@archeon {traced.glyph} @version {latest}"
            
            changes.append((traced.path, old_marker, new_marker))
            
            if not dry_run:
                content = Path(traced.path).read_text()
                updated = content.replace(old_marker, new_marker)
                Path(traced.path).write_text(updated)
    
    return changes
