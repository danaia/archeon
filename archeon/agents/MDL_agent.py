"""
MDL_agent.py - Model Code Generator

Generates database model code from MDL: glyphs.
"""

import re
from pathlib import Path
from typing import Optional

from archeon.agents.base_agent import BaseAgent
from archeon.orchestrator.PRS_parser import GlyphNode, ChainAST


class MDLAgent(BaseAgent):
    """Agent for generating database models."""

    prefix = "MDL"

    # Common operations that map to repository methods
    OPERATIONS = {
        "findOne": "find_one",
        "findMany": "find_many",
        "create": "create",
        "update": "update",
        "delete": "delete",
        "count": "count",
    }

    def resolve_path(self, glyph: GlyphNode, framework: str) -> str:
        """Return models/{entity}.py"""
        entity = self._extract_entity(glyph)
        return f"models/{entity}.py"

    def get_template(self, framework: str) -> str:
        """Load model template for framework."""
        template = self.load_template(framework)
        if not template:
            raise ValueError(f"No template found for MDL:{framework}")
        return template

    def generate(self, glyph: GlyphNode, chain: ChainAST, framework: str) -> str:
        """Generate model code."""
        template = self.get_template(framework)
        
        entity = self._extract_entity(glyph)
        operation = self._extract_operation(glyph)
        model_name = entity[0].upper() + entity[1:]

        # Get standard header placeholders for @archeon:file
        placeholders = self.get_header_placeholders(glyph, chain)
        
        # Add model-specific placeholders
        placeholders.update({
            "IMPORTS": "",
            "MODEL_NAME": model_name,
            "ENTITY": entity,
            "SCHEMA_FIELDS": "    id: Optional[str] = Field(default=None, alias='_id')",
            "METHODS": self._build_methods(operation, model_name),
        })

        return self.fill_template(template, placeholders)

    def generate_test(self, glyph: GlyphNode, framework: str) -> str:
        """Generate model test."""
        entity = self._extract_entity(glyph)
        operation = self._extract_operation(glyph)
        model_name = entity[0].upper() + entity[1:]

        test_content = f'''# @archeon {glyph.qualified_name}
# Generated test - Do not edit manually

import pytest
from unittest.mock import AsyncMock, MagicMock
from models.{entity} import {model_name}, {model_name}Repository


@pytest.fixture
def mock_collection():
    return AsyncMock()


@pytest.fixture
def repository(mock_collection):
    return {model_name}Repository(mock_collection)


@pytest.mark.asyncio
async def test_{entity}_model_creation():
    """Test {model_name} model creation."""
    model = {model_name}()
    assert model is not None


@pytest.mark.asyncio
async def test_{operation or 'find_one'}(repository, mock_collection):
    """Test {operation or 'findOne'} operation."""
    mock_collection.find_one.return_value = {{"_id": "test123"}}
    result = await repository.find_one("test123")
    assert result is not None
'''
        return test_content

    def _extract_entity(self, glyph: GlyphNode) -> str:
        """Extract entity name from glyph."""
        if glyph.namespace:
            return glyph.namespace
        # Name might be like user.findOne
        if '.' in glyph.name:
            return glyph.name.split('.')[0]
        return glyph.name

    def _extract_operation(self, glyph: GlyphNode) -> Optional[str]:
        """Extract operation from glyph."""
        if glyph.action:
            return self.OPERATIONS.get(glyph.action, glyph.action)
        if '.' in glyph.name:
            op = glyph.name.split('.')[1]
            return self.OPERATIONS.get(op, op)
        return None

    def _build_methods(self, operation: Optional[str], model_name: str) -> str:
        """Build repository methods."""
        methods = []
        
        # Always include basic CRUD
        methods.append(f'''    async def find_one(self, id: str) -> Optional[{model_name}]:
        """Find a {model_name} by ID."""
        doc = await self.collection.find_one({{"_id": id}})
        return {model_name}(**doc) if doc else None
''')
        
        methods.append(f'''    async def find_many(self, filter: dict = None) -> list[{model_name}]:
        """Find multiple {model_name} documents."""
        cursor = self.collection.find(filter or {{}})
        return [{model_name}(**doc) async for doc in cursor]
''')
        
        methods.append(f'''    async def create(self, model: {model_name}) -> str:
        """Create a new {model_name}."""
        result = await self.collection.insert_one(model.model_dump(by_alias=True, exclude_none=True))
        return str(result.inserted_id)
''')
        
        methods.append(f'''    async def update(self, id: str, data: dict) -> bool:
        """Update a {model_name}."""
        result = await self.collection.update_one({{"_id": id}}, {{"$set": data}})
        return result.modified_count > 0
''')
        
        methods.append(f'''    async def delete(self, id: str) -> bool:
        """Delete a {model_name}."""
        result = await self.collection.delete_one({{"_id": id}})
        return result.deleted_count > 0
''')
        
        return "\n".join(methods)
