"""
API_agent.py - API Endpoint Code Generator

Generates HTTP endpoint code from API: glyphs.
"""

import re
from pathlib import Path
from typing import Optional

from archeon.agents.base_agent import BaseAgent
from archeon.orchestrator.PRS_parser import GlyphNode, ChainAST


class APIAgent(BaseAgent):
    """Agent for generating API endpoints."""

    prefix = "API"

    def resolve_path(self, glyph: GlyphNode, framework: str) -> str:
        """Return api/routes/{route}.py"""
        route = self._extract_route(glyph)
        # Convert /auth/login to auth_login
        route_name = route.strip('/').replace('/', '_')
        return f"api/routes/{route_name}.py"

    def get_template(self, framework: str) -> str:
        """Load API template for framework."""
        template = self.load_template(framework)
        if not template:
            raise ValueError(f"No template found for API:{framework}")
        return template

    def generate(self, glyph: GlyphNode, chain: ChainAST, framework: str) -> str:
        """Generate API endpoint code."""
        template = self.get_template(framework)
        
        method = self._extract_method(glyph)
        route = self._extract_route(glyph)
        handler_name = self._route_to_handler(route, method)
        
        # Find connected ERR glyphs for error handling
        error_glyphs = self._find_error_paths(glyph, chain)

        # Get standard header placeholders for @archeon:file
        placeholders = self.get_header_placeholders(glyph, chain)
        
        # Add API-specific placeholders
        placeholders.update({
            "IMPORTS": "",
            "ROUTE_PREFIX": self._get_route_prefix(route),
            "TAG": self._get_tag(route),
            "REQUEST_MODEL": f"{handler_name.title().replace('_', '')}Request",
            "REQUEST_FIELDS": "    pass  # Define request fields",
            "RESPONSE_MODEL": f"{handler_name.title().replace('_', '')}Response",
            "RESPONSE_FIELDS": "    pass  # Define response fields",
            "ERROR_MODEL": f"{handler_name.title().replace('_', '')}Error",
            "METHOD": method.lower(),
            "ROUTE": self._get_route_path(route),
            "HANDLER_NAME": handler_name,
            "PARAMETERS": self._build_parameters(method, f"{handler_name.title().replace('_', '')}Request"),
            "DOCSTRING": f"{method} {route}",
            "HANDLER_BODY": self._build_handler_body(error_glyphs, f"{handler_name.title().replace('_', '')}Response"),
        })

        return self.fill_template(template, placeholders)

    def generate_test(self, glyph: GlyphNode, framework: str) -> str:
        """Generate API endpoint test."""
        method = self._extract_method(glyph)
        route = self._extract_route(glyph)
        handler_name = self._route_to_handler(route, method)

        test_content = f'''# @archeon {glyph.qualified_name}
# Generated test - Do not edit manually

import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_{handler_name}_success(client: AsyncClient):
    """Test successful {method} {route}."""
    response = await client.{method.lower()}("{route}")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_{handler_name}_validation_error(client: AsyncClient):
    """Test {method} {route} with invalid input."""
    response = await client.{method.lower()}("{route}", json={{}})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
'''
        return test_content

    def _extract_method(self, glyph: GlyphNode) -> str:
        """Extract HTTP method from glyph."""
        if glyph.namespace:
            return glyph.namespace.upper()
        # Try parsing from name
        name = glyph.name.upper()
        if name in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH'):
            return name
        return 'GET'

    def _extract_route(self, glyph: GlyphNode) -> str:
        """Extract route path from glyph."""
        if glyph.action:
            return glyph.action
        # Name might be like POST/auth
        if '/' in glyph.name:
            parts = glyph.name.split('/', 1)
            return '/' + parts[1]
        return f"/{glyph.name.lower()}"

    def _route_to_handler(self, route: str, method: str) -> str:
        """Convert route to handler function name."""
        # /auth/login -> auth_login
        name = route.strip('/').replace('/', '_').replace('-', '_')
        return f"{method.lower()}_{name}"

    def _get_route_prefix(self, route: str) -> str:
        """Get route prefix for router."""
        parts = route.strip('/').split('/')
        return f"/{parts[0]}" if parts else ""

    def _get_route_path(self, route: str) -> str:
        """Get route path relative to prefix."""
        parts = route.strip('/').split('/')
        if len(parts) > 1:
            return '/' + '/'.join(parts[1:])
        return '/'

    def _get_tag(self, route: str) -> str:
        """Get OpenAPI tag from route."""
        parts = route.strip('/').split('/')
        return parts[0] if parts else "default"

    def _build_parameters(self, method: str, request_model: str) -> str:
        """Build function parameters."""
        if method.upper() in ('POST', 'PUT', 'PATCH'):
            return f"    request: {request_model}"
        return ""

    def _build_handler_body(self, error_glyphs: list[GlyphNode], response_model: str) -> str:
        """Build handler body with error handling."""
        lines = ["    # TODO: Implement business logic"]
        
        if error_glyphs:
            lines.append("    # Error paths from chain:")
            for err in error_glyphs:
                lines.append(f"    # - {err.qualified_name}")
        
        lines.append(f"    return {response_model}()")
        return "\n".join(lines)

    def _find_error_paths(self, glyph: GlyphNode, chain: ChainAST) -> list[GlyphNode]:
        """Find ERR glyphs connected via control flow."""
        errors = []
        glyph_idx = None
        
        for i, node in enumerate(chain.nodes):
            if node.qualified_name == glyph.qualified_name:
                glyph_idx = i
                break
        
        if glyph_idx is not None:
            for edge in chain.edges:
                if edge.source_idx == glyph_idx and edge.operator == '->':
                    target = chain.nodes[edge.target_idx]
                    if target.prefix == 'ERR':
                        errors.append(target)
        
        return errors
