"""
SPW_spawner.py - Agent Spawner

Orchestrates code generation by dispatching to appropriate agents.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Type

from archeon.orchestrator.PRS_parser import GlyphNode, ChainAST
from archeon.orchestrator.GRF_graph import KnowledgeGraph, StoredChain
from archeon.agents.base_agent import BaseAgent
from archeon.agents.CMP_agent import CMPAgent
from archeon.agents.STO_agent import STOAgent
from archeon.agents.API_agent import APIAgent
from archeon.agents.MDL_agent import MDLAgent
from archeon.agents.FNC_agent import FNCAgent
from archeon.agents.EVT_agent import EVTAgent


@dataclass
class SpawnResult:
    """Result of spawning code for a glyph."""
    glyph: str
    file_path: Optional[str] = None
    test_path: Optional[str] = None
    status: str = "pending"  # pending, success, skipped, error
    error: Optional[str] = None


@dataclass
class BatchResult:
    """Result of spawning code for multiple glyphs."""
    results: list[SpawnResult] = field(default_factory=list)
    
    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.status == "success")
    
    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if r.status == "error")
    
    @property
    def skipped_count(self) -> int:
        return sum(1 for r in self.results if r.status == "skipped")


class AgentSpawner:
    """Spawns agents to generate code from glyphs."""

    # Registry of prefix -> agent class
    AGENT_REGISTRY: dict[str, Type[BaseAgent]] = {
        "CMP": CMPAgent,
        "STO": STOAgent,
        "API": APIAgent,
        "MDL": MDLAgent,
        "FNC": FNCAgent,
        "EVT": EVTAgent,
    }

    # Glyphs that don't generate code
    SKIP_PREFIXES = {"NED", "TSK", "OUT", "ERR", "V", "ORC", "PRS", "VAL", "SPW", "TST", "GRF"}

    # Prefix to default framework mapping
    PREFIX_FRAMEWORKS = {
        "CMP": "react",      # Frontend component
        "STO": "zustand",    # Frontend state
        "API": "fastapi",    # Backend API
        "MDL": "mongo",      # Database model
        "FNC": "python",     # Default to Python for shared
        "EVT": "pubsub",     # Event emitter
    }

    def __init__(
        self, 
        output_dir: str = ".", 
        framework: str = "react",
        backend: str = "fastapi",
        db: str = "mongo"
    ):
        self.output_dir = Path(output_dir)
        self.framework = framework
        self.backend = backend
        self.db = db
        self._agents: dict[str, BaseAgent] = {}

    def get_framework_for_glyph(self, prefix: str) -> str:
        """Get the appropriate framework for a glyph prefix."""
        default = self.PREFIX_FRAMEWORKS.get(prefix, self.framework)
        
        # Use configured backend/db for relevant glyphs
        if prefix == "API":
            return self.backend
        if prefix == "MDL":
            return self.db
        if prefix in ("CMP", "STO"):
            return self.framework
        
        return default

    def get_agent(self, prefix: str) -> Optional[BaseAgent]:
        """Get or create agent instance for a prefix."""
        if prefix in self.SKIP_PREFIXES:
            return None
        
        if prefix not in self._agents:
            agent_class = self.AGENT_REGISTRY.get(prefix)
            if agent_class:
                self._agents[prefix] = agent_class()
        
        return self._agents.get(prefix)

    def spawn(
        self, 
        glyph: GlyphNode, 
        chain: ChainAST, 
        framework: Optional[str] = None,
        force: bool = False
    ) -> SpawnResult:
        """
        Spawn code generation for a single glyph.
        
        Args:
            glyph: The glyph to generate code for
            chain: The chain context
            framework: Override default framework
            force: Force regeneration even if file exists
            
        Returns:
            SpawnResult with paths and status
        """
        # Use glyph-appropriate framework unless overridden
        fw = framework or self.get_framework_for_glyph(glyph.prefix)
        result = SpawnResult(glyph=glyph.qualified_name)

        # Skip meta and internal glyphs
        if glyph.prefix in self.SKIP_PREFIXES:
            result.status = "skipped"
            return result

        # Get agent
        agent = self.get_agent(glyph.prefix)
        if not agent:
            result.status = "error"
            result.error = f"No agent registered for prefix: {glyph.prefix}"
            return result

        try:
            # Resolve output path
            rel_path = agent.resolve_path(glyph, fw)
            full_path = self.output_dir / rel_path

            # Check if file exists
            if full_path.exists() and not force:
                result.status = "skipped"
                result.file_path = str(rel_path)
                return result

            # Generate code
            code = agent.generate(glyph, chain, fw)
            
            # Write file
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(code)
            result.file_path = str(rel_path)

            # Generate test
            test_code = agent.generate_test(glyph, fw)
            test_rel_path = f"tests/generated/test_{Path(rel_path).stem}.py"
            test_full_path = self.output_dir / test_rel_path
            test_full_path.parent.mkdir(parents=True, exist_ok=True)
            test_full_path.write_text(test_code)
            result.test_path = test_rel_path

            result.status = "success"

        except Exception as e:
            result.status = "error"
            result.error = str(e)

        return result

    def spawn_chain(
        self, 
        chain: ChainAST, 
        framework: Optional[str] = None,
        force: bool = False
    ) -> BatchResult:
        """
        Spawn code for all glyphs in a chain.
        
        Args:
            chain: The chain to process
            framework: Override default framework
            force: Force regeneration
            
        Returns:
            BatchResult with all spawn results
        """
        batch = BatchResult()
        seen = set()

        for glyph in chain.nodes:
            # Skip duplicates within chain
            if glyph.qualified_name in seen:
                continue
            seen.add(glyph.qualified_name)

            result = self.spawn(glyph, chain, framework, force)
            batch.results.append(result)

        return batch

    def spawn_all(
        self, 
        graph: KnowledgeGraph,
        framework: Optional[str] = None,
        force: bool = False
    ) -> BatchResult:
        """
        Spawn code for all unresolved glyphs in the graph.
        
        Args:
            graph: The knowledge graph
            framework: Override default framework
            force: Force regeneration of all glyphs
            
        Returns:
            BatchResult with all spawn results
        """
        batch = BatchResult()
        fw = framework or self.framework

        # Get unresolved glyphs
        unresolved = graph.get_unresolved_glyphs() if not force else graph.get_all_glyphs()

        for glyph_name in unresolved:
            # Find a chain containing this glyph for context
            chains = graph.find_chains_by_glyph(glyph_name)
            if not chains:
                continue

            chain = chains[0].ast
            
            # Find the actual glyph node
            glyph = None
            for node in chain.nodes:
                if node.qualified_name == glyph_name:
                    glyph = node
                    break

            if not glyph:
                continue

            result = self.spawn(glyph, chain, None, force)  # Let glyph determine framework
            batch.results.append(result)

            # Mark as resolved in graph
            if result.status == "success" and result.file_path:
                graph.mark_resolved(
                    glyph_name, 
                    result.file_path, 
                    result.test_path
                )

        return batch


def spawn_from_graph(
    graph: KnowledgeGraph,
    output_dir: str = ".",
    framework: str = "react",
    backend: str = "fastapi",
    db: str = "mongo",
    force: bool = False
) -> BatchResult:
    """Convenience function to spawn all unresolved glyphs."""
    spawner = AgentSpawner(
        output_dir=output_dir, 
        framework=framework,
        backend=backend,
        db=db
    )
    return spawner.spawn_all(graph, force=force)
