"""
SCN_scanner.py - Semantic Section Scanner

Scans files for @archeon:section markers and extracts semantic affordances.
This is the foundation of the AI-native code navigation system.

The scanner:
- Finds @archeon:file headers
- Extracts @glyph, @intent, @chain metadata
- Discovers @archeon:section / @archeon:endsection blocks
- Validates section rules (no nesting, contiguous)
- Returns structured section data for index building
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SectionInfo:
    """Represents a semantic section within a file."""
    name: str
    intent: str = ""
    start_line: int = 0  # For validation only, not stored in index
    end_line: int = 0


@dataclass
class FileHeader:
    """Represents the @archeon:file header metadata."""
    glyph: str = ""
    intent: str = ""
    chain: str = ""


@dataclass
class ScannedFile:
    """Result of scanning a single file."""
    path: str
    header: FileHeader
    sections: list[SectionInfo] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    is_archeon_file: bool = False


# Comment patterns for different languages
COMMENT_PATTERNS = {
    # Single-line comment prefixes
    'python': '#',
    'javascript': '//',
    'typescript': '//',
    'vue': '//',  # Script section uses //
    'html': '<!--',
    'css': '/*',
}

# File extension to language mapping
EXT_TO_LANG = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.jsx': 'javascript',
    '.vue': 'vue',
    '.svelte': 'javascript',
    '.html': 'html',
    '.css': 'css',
}


def get_comment_prefix(filepath: str) -> str:
    """Get the comment prefix for a file based on extension."""
    ext = Path(filepath).suffix.lower()
    lang = EXT_TO_LANG.get(ext, 'python')
    return COMMENT_PATTERNS.get(lang, '#')


def scan_file(filepath: str) -> ScannedFile:
    """
    Scan a file for Archeon semantic markers.
    
    Args:
        filepath: Path to the file to scan
        
    Returns:
        ScannedFile with extracted header, sections, and any errors
    """
    result = ScannedFile(path=filepath, header=FileHeader())
    
    try:
        content = Path(filepath).read_text()
    except Exception as e:
        result.errors.append(f"Could not read file: {e}")
        return result
    
    lines = content.split('\n')
    
    # Patterns for matching Archeon markers (language-agnostic)
    # These match regardless of comment style
    file_pattern = re.compile(r'@archeon:file\b')
    glyph_pattern = re.compile(r'@glyph\s+(\S+)')
    intent_pattern = re.compile(r'@intent\s+(.+?)(?:\s*-->|\s*\*/)?$')
    chain_pattern = re.compile(r'@chain\s+(.+?)(?:\s*-->|\s*\*/)?$')
    section_start_pattern = re.compile(r'@archeon:section\s+(\w+)')
    section_end_pattern = re.compile(r'@archeon:endsection\b')
    
    # State tracking
    in_header = False
    current_section: Optional[SectionInfo] = None
    section_depth = 0
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Check for file header marker
        if file_pattern.search(stripped):
            result.is_archeon_file = True
            in_header = True
            continue
        
        # Extract header metadata
        if in_header:
            glyph_match = glyph_pattern.search(stripped)
            if glyph_match:
                result.header.glyph = glyph_match.group(1)
                continue
            
            intent_match = intent_pattern.search(stripped)
            if intent_match:
                result.header.intent = intent_match.group(1).strip()
                continue
            
            chain_match = chain_pattern.search(stripped)
            if chain_match:
                result.header.chain = chain_match.group(1).strip()
                in_header = False  # Chain is typically the last header field
                continue
            
            # If we hit a non-comment line, header is done
            if stripped and not _is_comment_line(stripped):
                in_header = False
        
        # Check for section start
        section_start_match = section_start_pattern.search(stripped)
        if section_start_match:
            if current_section is not None:
                result.errors.append(
                    f"Line {i}: Nested section '{section_start_match.group(1)}' "
                    f"inside '{current_section.name}' - sections must not nest"
                )
            else:
                section_name = section_start_match.group(1)
                current_section = SectionInfo(
                    name=section_name,
                    start_line=i
                )
                section_depth += 1
                
                # Try to extract section intent from next line
                if i < len(lines):
                    next_line = lines[i].strip()  # i is 1-indexed, so lines[i] is next
                    if _is_comment_line(next_line):
                        # Extract intent from comment
                        intent = _extract_comment_text(next_line)
                        if intent and not intent.startswith('@'):
                            current_section.intent = intent
            continue
        
        # Check for section end
        if section_end_pattern.search(stripped):
            if current_section is None:
                result.errors.append(
                    f"Line {i}: Found @archeon:endsection without matching section start"
                )
            else:
                current_section.end_line = i
                result.sections.append(current_section)
                current_section = None
                section_depth -= 1
            continue
    
    # Check for unclosed sections
    if current_section is not None:
        result.errors.append(
            f"Section '{current_section.name}' starting at line {current_section.start_line} "
            "was never closed with @archeon:endsection"
        )
    
    return result


def _is_comment_line(line: str) -> bool:
    """Check if a line appears to be a comment."""
    stripped = line.strip()
    return (
        stripped.startswith('#') or
        stripped.startswith('//') or
        stripped.startswith('/*') or
        stripped.startswith('*') or
        stripped.startswith('<!--') or
        stripped.startswith('"""') or
        stripped.startswith("'''")
    )


def _extract_comment_text(line: str) -> str:
    """Extract the text content from a comment line."""
    stripped = line.strip()
    
    # Remove common comment prefixes
    for prefix in ['# ', '// ', '/* ', '* ', '<!-- ', '"""', "'''"]:
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix):]
            break
    
    # Remove trailing comment closers
    for suffix in [' */', ' -->', '"""', "'''"]:
        if stripped.endswith(suffix):
            stripped = stripped[:-len(suffix)]
            break
    
    return stripped.strip()


def scan_directory(
    directory: str,
    extensions: Optional[list[str]] = None
) -> list[ScannedFile]:
    """
    Scan all matching files in a directory for Archeon markers.
    
    Args:
        directory: Path to directory to scan
        extensions: List of file extensions to include (default: all known)
        
    Returns:
        List of ScannedFile results
    """
    if extensions is None:
        extensions = list(EXT_TO_LANG.keys())
    
    results = []
    dir_path = Path(directory)
    
    for ext in extensions:
        for filepath in dir_path.rglob(f"*{ext}"):
            # Skip node_modules, __pycache__, etc.
            if any(skip in str(filepath) for skip in [
                'node_modules', '__pycache__', '.git', 'dist', 'build'
            ]):
                continue
            
            scanned = scan_file(str(filepath))
            if scanned.is_archeon_file:
                results.append(scanned)
    
    return results


def validate_sections(scanned: ScannedFile) -> list[str]:
    """
    Validate section rules for a scanned file.
    
    Rules:
    - Sections must not nest
    - Sections must be contiguous (no gaps in coverage is optional)
    - Section names must be unique within a file
    
    Returns:
        List of validation error messages
    """
    errors = list(scanned.errors)  # Start with scan errors
    
    # Check for duplicate section names
    section_names = [s.name for s in scanned.sections]
    seen = set()
    for name in section_names:
        if name in seen:
            errors.append(f"Duplicate section name: '{name}'")
        seen.add(name)
    
    return errors


def get_section_names(scanned: ScannedFile) -> list[str]:
    """Get just the section names from a scanned file."""
    return [s.name for s in scanned.sections]


def format_header_comment(
    glyph: str,
    intent: str,
    chain: str,
    comment_style: str = '//'
) -> str:
    """
    Generate a properly formatted @archeon:file header.
    
    Args:
        glyph: The glyph identifier (e.g., 'CMP:LoginForm')
        intent: One-sentence description of the file's purpose
        chain: The chain reference (e.g., '@v1 NED:login => CMP:LoginForm')
        comment_style: Comment prefix to use
        
    Returns:
        Formatted header string
    """
    c = comment_style
    return f"""{c} @archeon:file
{c} @glyph {glyph}
{c} @intent {intent}
{c} @chain {chain}
"""


def format_section_comment(
    name: str,
    intent: str,
    comment_style: str = '//'
) -> str:
    """
    Generate a properly formatted @archeon:section comment.
    
    Args:
        name: Section name (snake_case)
        intent: One-sentence description of the section
        comment_style: Comment prefix to use
        
    Returns:
        Formatted section start comment
    """
    c = comment_style
    return f"""{c} @archeon:section {name}
{c} {intent}"""


def format_endsection_comment(comment_style: str = '//') -> str:
    """Generate a properly formatted @archeon:endsection comment."""
    return f"{comment_style} @archeon:endsection"


# Standard section definitions by glyph type
STANDARD_SECTIONS = {
    'CMP': ['imports', 'props_and_state', 'handlers', 'render', 'styles'],
    'STO': ['imports', 'state', 'actions', 'selectors'],
    'API': ['imports', 'models', 'endpoint', 'helpers'],
    'FNC': ['imports', 'implementation', 'helpers'],
    'EVT': ['imports', 'channels', 'handlers'],
    'MDL': ['imports', 'schema', 'methods', 'indexes'],
}


def get_standard_sections(glyph_prefix: str) -> list[str]:
    """Get the standard section names for a glyph type."""
    return STANDARD_SECTIONS.get(glyph_prefix, ['imports', 'implementation'])
