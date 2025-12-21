"""
EVT_agent.py - Event Emitter Code Generator

Generates event emitter code from EVT: glyphs.
"""

import re
from pathlib import Path
from typing import Optional

from archeon.agents.base_agent import BaseAgent
from archeon.orchestrator.PRS_parser import GlyphNode, ChainAST


class EVTAgent(BaseAgent):
    """Agent for generating event emitters."""

    prefix = "EVT"

    def resolve_path(self, glyph: GlyphNode, framework: str) -> str:
        """Return events/{name}.py"""
        name = self._extract_event_name(glyph)
        return f"events/{name}.py"

    def get_template(self, framework: str) -> str:
        """Load event template for framework."""
        template = self.load_template("pubsub")
        if not template:
            raise ValueError(f"No template found for EVT:{framework}")
        return template

    def generate(self, glyph: GlyphNode, chain: ChainAST, framework: str) -> str:
        """Generate event emitter code."""
        template = self.get_template(framework)
        
        event_name = self._extract_event_name(glyph)
        event_class = self._to_pascal_case(event_name)

        # Get standard header placeholders for @archeon:file
        placeholders = self.get_header_placeholders(glyph, chain)
        
        # Add event-specific placeholders
        placeholders.update({
            "IMPORTS": "",
            "EVENT_NAME": event_class,
            "EVENT_NAME_LOWER": event_name.lower(),
            "EVENT_FIELDS": "    data: Any = None",
        })

        return self.fill_template(template, placeholders)

    def generate_test(self, glyph: GlyphNode, framework: str) -> str:
        """Generate event emitter test."""
        event_name = self._extract_event_name(glyph)
        event_class = self._to_pascal_case(event_name)

        test_content = f'''# @archeon {glyph.qualified_name}
# Generated test - Do not edit manually

import pytest
from events.{event_name} import {event_class}Event, {event_class}Emitter, {event_name.lower()}_emitter


@pytest.fixture
def emitter():
    return {event_class}Emitter()


def test_event_creation():
    """Test {event_class}Event can be created."""
    event = {event_class}Event(data={{"test": True}})
    assert event.data is not None


def test_subscribe_and_emit(emitter):
    """Test subscribing and emitting events."""
    received = []
    
    def handler(event):
        received.append(event)
    
    unsubscribe = emitter.subscribe(handler)
    emitter.emit({event_class}Event(data="test"))
    
    assert len(received) == 1
    assert received[0].data == "test"
    
    unsubscribe()


def test_unsubscribe(emitter):
    """Test unsubscribing from events."""
    received = []
    
    unsubscribe = emitter.subscribe(lambda e: received.append(e))
    unsubscribe()
    
    emitter.emit({event_class}Event())
    
    assert len(received) == 0


def test_clear_listeners(emitter):
    """Test clearing all listeners."""
    emitter.subscribe(lambda e: None)
    emitter.subscribe(lambda e: None)
    
    emitter.clear()
    
    # Should not raise
    emitter.emit({event_class}Event())
'''
        return test_content

    def _extract_event_name(self, glyph: GlyphNode) -> str:
        """Extract event name from glyph."""
        if glyph.namespace and glyph.action:
            return f"{glyph.namespace}_{glyph.action}"
        if '.' in glyph.name:
            parts = glyph.name.split('.')
            return '_'.join(parts)
        return glyph.name

    @staticmethod
    def _to_pascal_case(name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))
