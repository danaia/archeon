"""
base_agent.py - Abstract Base Agent

Defines the contract all agents must follow.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from archeon.orchestrator.PRS_parser import GlyphNode, ChainAST


class BaseAgent(ABC):
    """Abstract base class for all code generation agents."""

    prefix: str  # Glyph prefix this agent handles (e.g., 'CMP', 'API')
    templates_dir: Path = Path(__file__).parent.parent / "templates"

    @abstractmethod
    def generate(self, glyph: GlyphNode, chain: ChainAST, framework: str) -> str:
        """
        Generate code for a glyph.

        Args:
            glyph: The parsed glyph node
            chain: The full chain AST for context
            framework: Target framework (react, vue, fastapi, etc.)

        Returns:
            Path to the generated file
        """
        pass

    @abstractmethod
    def get_template(self, framework: str) -> str:
        """
        Get the template content for a framework.

        Args:
            framework: Target framework

        Returns:
            Template string with placeholders
        """
        pass

    @abstractmethod
    def generate_test(self, glyph: GlyphNode, framework: str) -> str:
        """
        Generate a test file for the glyph.

        Args:
            glyph: The parsed glyph node
            framework: Target framework

        Returns:
            Path to the generated test file
        """
        pass

    @abstractmethod
    def resolve_path(self, glyph: GlyphNode, framework: str) -> str:
        """
        Determine the output file path for a glyph.

        Args:
            glyph: The parsed glyph node
            framework: Target framework

        Returns:
            Relative file path for the generated code
        """
        pass

    def load_template(self, framework: str) -> Optional[str]:
        """Load template file from templates directory."""
        template_dir = self.templates_dir / self.prefix
        
        # Try framework-specific template
        for ext in ['.py', '.tsx', '.ts', '.js', '.vue', '.svelte']:
            template_path = template_dir / f"{framework}{ext}"
            if template_path.exists():
                return template_path.read_text()

        return None

    def fill_template(self, template: str, placeholders: dict[str, str]) -> str:
        """Replace placeholders in template with values."""
        result = template
        for key, value in placeholders.items():
            result = result.replace(f"{{{key}}}", value)
        return result

    def write_file(self, path: str, content: str, output_dir: str = ".") -> str:
        """Write generated content to file."""
        full_path = Path(output_dir) / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        return str(full_path)
