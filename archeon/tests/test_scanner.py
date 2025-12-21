"""
test_scanner.py - Tests for Semantic Section Scanner

Tests the SCN_scanner module that extracts @archeon markers from files.
"""

import pytest
from io import StringIO
from pathlib import Path
import tempfile
import os

from archeon.orchestrator.SCN_scanner import (
    scan_file,
    scan_directory,
    validate_sections,
    get_section_names,
    format_header_comment,
    format_section_comment,
    format_endsection_comment,
    STANDARD_SECTIONS,
    ScannedFile,
    SectionInfo,
)


class TestSectionParsing:
    """Tests for parsing @archeon:section markers."""
    
    def test_basic_section_detection(self, tmp_path):
        """Test basic section start and end detection."""
        content = """// @archeon:file
// @glyph CMP:Test
// @intent Test component
// @chain @v1 NED:test => CMP:Test

// @archeon:section imports
import React from 'react';
// @archeon:endsection

// @archeon:section render
return <div>Test</div>;
// @archeon:endsection
"""
        test_file = tmp_path / "test.tsx"
        test_file.write_text(content)
        
        scanned = scan_file(str(test_file))
        
        assert scanned.is_archeon_file
        assert scanned.header.glyph == "CMP:Test"
        assert scanned.header.intent == "Test component"
        assert len(scanned.sections) == 2
        assert scanned.sections[0].name == "imports"
        assert scanned.sections[1].name == "render"
    
    def test_python_section_detection(self, tmp_path):
        """Test section detection in Python files."""
        content = """# @archeon:file
# @glyph FNC:helper
# @intent Helper function
# @chain @v1 NED:task => FNC:helper

# @archeon:section imports
from typing import Any
# @archeon:endsection

# @archeon:section implementation
def helper():
    pass
# @archeon:endsection
"""
        test_file = tmp_path / "helper.py"
        test_file.write_text(content)
        
        scanned = scan_file(str(test_file))
        
        assert scanned.is_archeon_file
        assert scanned.header.glyph == "FNC:helper"
        assert len(scanned.sections) == 2
        assert "imports" in get_section_names(scanned)
        assert "implementation" in get_section_names(scanned)
    
    def test_html_comment_sections(self, tmp_path):
        """Test section detection in Vue/HTML files."""
        content = """<!-- @archeon:file -->
<!-- @glyph CMP:Widget -->
<!-- @intent Widget component -->
<!-- @chain @v1 NED:widget => CMP:Widget -->

<script setup>
// @archeon:section imports
import { ref } from 'vue';
// @archeon:endsection
</script>

<!-- @archeon:section render -->
<template>
  <div>Widget</div>
</template>
<!-- @archeon:endsection -->
"""
        test_file = tmp_path / "widget.vue"
        test_file.write_text(content)
        
        scanned = scan_file(str(test_file))
        
        assert scanned.is_archeon_file
        assert scanned.header.glyph == "CMP:Widget"
        assert len(scanned.sections) == 2


class TestSectionValidation:
    """Tests for section validation rules."""
    
    def test_nested_sections_error(self, tmp_path):
        """Test that nested sections are detected as errors."""
        content = """// @archeon:file
// @glyph CMP:Test
// @intent Test
// @chain @v1 CMP:Test

// @archeon:section outer
// @archeon:section inner
// @archeon:endsection
// @archeon:endsection
"""
        test_file = tmp_path / "nested.tsx"
        test_file.write_text(content)
        
        scanned = scan_file(str(test_file))
        errors = validate_sections(scanned)
        
        assert len(errors) > 0
        assert any("nest" in e.lower() for e in errors)
    
    def test_unclosed_section_error(self, tmp_path):
        """Test that unclosed sections are detected as errors."""
        content = """// @archeon:file
// @glyph CMP:Test
// @intent Test
// @chain @v1 CMP:Test

// @archeon:section unclosed
const x = 1;
"""
        test_file = tmp_path / "unclosed.tsx"
        test_file.write_text(content)
        
        scanned = scan_file(str(test_file))
        errors = validate_sections(scanned)
        
        assert len(errors) > 0
        assert any("never closed" in e.lower() or "unclosed" in e.lower() for e in errors)
    
    def test_duplicate_section_names_error(self, tmp_path):
        """Test that duplicate section names are detected."""
        content = """// @archeon:file
// @glyph CMP:Test
// @intent Test
// @chain @v1 CMP:Test

// @archeon:section imports
import x from 'x';
// @archeon:endsection

// @archeon:section imports
import y from 'y';
// @archeon:endsection
"""
        test_file = tmp_path / "duplicate.tsx"
        test_file.write_text(content)
        
        scanned = scan_file(str(test_file))
        errors = validate_sections(scanned)
        
        assert len(errors) > 0
        assert any("duplicate" in e.lower() for e in errors)
    
    def test_orphaned_endsection_error(self, tmp_path):
        """Test that endsection without start is detected."""
        content = """// @archeon:file
// @glyph CMP:Test
// @intent Test
// @chain @v1 CMP:Test

const x = 1;
// @archeon:endsection
"""
        test_file = tmp_path / "orphaned.tsx"
        test_file.write_text(content)
        
        scanned = scan_file(str(test_file))
        errors = validate_sections(scanned)
        
        assert len(errors) > 0
        assert any("without" in e.lower() for e in errors)


class TestHeaderParsing:
    """Tests for @archeon:file header parsing."""
    
    def test_complete_header(self, tmp_path):
        """Test parsing a complete header."""
        content = """// @archeon:file
// @glyph CMP:LoginForm
// @intent User login input and submission
// @chain @v1 NED:login => CMP:LoginForm => STO:Auth

export function LoginForm() {}
"""
        test_file = tmp_path / "login.tsx"
        test_file.write_text(content)
        
        scanned = scan_file(str(test_file))
        
        assert scanned.is_archeon_file
        assert scanned.header.glyph == "CMP:LoginForm"
        assert scanned.header.intent == "User login input and submission"
        assert "@v1" in scanned.header.chain
    
    def test_minimal_header(self, tmp_path):
        """Test parsing a minimal header (just @archeon:file and @glyph)."""
        content = """# @archeon:file
# @glyph FNC:util

def util():
    pass
"""
        test_file = tmp_path / "util.py"
        test_file.write_text(content)
        
        scanned = scan_file(str(test_file))
        
        assert scanned.is_archeon_file
        assert scanned.header.glyph == "FNC:util"
    
    def test_non_archeon_file(self, tmp_path):
        """Test that files without @archeon:file are detected correctly."""
        content = """// Regular JavaScript file
export function regular() {}
"""
        test_file = tmp_path / "regular.js"
        test_file.write_text(content)
        
        scanned = scan_file(str(test_file))
        
        assert not scanned.is_archeon_file


class TestFormatters:
    """Tests for comment formatting functions."""
    
    def test_format_header_js(self):
        """Test JavaScript header formatting."""
        header = format_header_comment(
            glyph="CMP:Test",
            intent="Test component",
            chain="@v1 NED:test => CMP:Test",
            comment_style="//"
        )
        
        assert "@archeon:file" in header
        assert "@glyph CMP:Test" in header
        assert "@intent Test component" in header
        assert "@chain @v1 NED:test => CMP:Test" in header
    
    def test_format_header_python(self):
        """Test Python header formatting."""
        header = format_header_comment(
            glyph="FNC:helper",
            intent="Helper function",
            chain="@v1 FNC:helper",
            comment_style="#"
        )
        
        assert "# @archeon:file" in header
        assert "# @glyph FNC:helper" in header
    
    def test_format_section(self):
        """Test section comment formatting."""
        section = format_section_comment(
            name="imports",
            intent="External dependencies",
            comment_style="//"
        )
        
        assert "@archeon:section imports" in section
        assert "External dependencies" in section
    
    def test_format_endsection(self):
        """Test endsection comment formatting."""
        end = format_endsection_comment("//")
        assert "@archeon:endsection" in end


class TestStandardSections:
    """Tests for standard section definitions."""
    
    def test_cmp_sections(self):
        """Test CMP has correct standard sections."""
        sections = STANDARD_SECTIONS.get("CMP", [])
        assert "imports" in sections
        assert "props_and_state" in sections
        assert "handlers" in sections
        assert "render" in sections
    
    def test_sto_sections(self):
        """Test STO has correct standard sections."""
        sections = STANDARD_SECTIONS.get("STO", [])
        assert "imports" in sections
        assert "state" in sections
        assert "actions" in sections
        assert "selectors" in sections
    
    def test_api_sections(self):
        """Test API has correct standard sections."""
        sections = STANDARD_SECTIONS.get("API", [])
        assert "imports" in sections
        assert "models" in sections
        assert "endpoint" in sections
    
    def test_all_types_have_imports(self):
        """Test all glyph types have imports section."""
        for glyph_type, sections in STANDARD_SECTIONS.items():
            assert "imports" in sections, f"{glyph_type} missing imports section"
