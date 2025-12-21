"""
SPW_spawner.py - Agent Spawner

Orchestrates code generation by dispatching to appropriate agents.
Supports monorepo structure with client/server separation.
Automatically updates semantic index after file generation.
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
from archeon.orchestrator.IDX_index import IndexBuilder


@dataclass
class SpawnResult:
    """Result of spawning code for a glyph."""
    glyph: str
    file_path: Optional[str] = None
    test_path: Optional[str] = None
    status: str = "pending"  # pending, success, skipped, error
    error: Optional[str] = None
    target: str = ""  # "client" or "server"


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
    
    @property
    def client_count(self) -> int:
        return sum(1 for r in self.results if r.target == "client" and r.status == "success")
    
    @property
    def server_count(self) -> int:
        return sum(1 for r in self.results if r.target == "server" and r.status == "success")


@dataclass
class ProjectConfig:
    """Project configuration from .archeonrc"""
    monorepo: bool = True
    client_dir: str = "./client/src"
    server_dir: str = "./server/src"
    frontend: str = "react"
    backend: str = "fastapi"
    db: str = "mongo"
    output_dir: str = "./src"  # Fallback for non-monorepo
    
    @classmethod
    def load(cls, project_root: Optional[Path] = None) -> 'ProjectConfig':
        """Load config from .archeonrc file."""
        config = cls()
        
        # Find .archeonrc
        search_paths = []
        if project_root:
            search_paths.append(project_root / ".archeonrc")
        search_paths.append(Path.cwd() / ".archeonrc")
        
        for parent in Path.cwd().parents:
            search_paths.append(parent / ".archeonrc")
            if (parent / "archeon").exists():
                break
        
        rc_path = None
        for p in search_paths:
            if p.exists():
                rc_path = p
                break
        
        if not rc_path:
            return config
        
        # Parse simple YAML-like format
        for line in rc_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == "monorepo":
                    config.monorepo = value.lower() == "true"
                elif key == "client_dir":
                    config.client_dir = value
                elif key == "server_dir":
                    config.server_dir = value
                elif key == "frontend":
                    config.frontend = value
                elif key == "backend":
                    config.backend = value
                elif key == "db":
                    config.db = value
                elif key == "output_dir":
                    config.output_dir = value
        
        return config


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
    
    # Frontend vs Backend glyph classification
    CLIENT_PREFIXES = {"CMP", "STO", "V"}  # Frontend glyphs -> client dir
    SERVER_PREFIXES = {"API", "MDL", "EVT"}  # Backend glyphs -> server dir
    SHARED_PREFIXES = {"FNC"}  # Depends on namespace (FNC:ui -> client, FNC:auth -> server)

    def __init__(
        self, 
        output_dir: str = ".", 
        framework: str = "react",
        backend: str = "fastapi",
        db: str = "mongo",
        config: Optional[ProjectConfig] = None
    ):
        self.config = config or ProjectConfig.load()
        self.output_dir = Path(output_dir)
        self.framework = framework or self.config.frontend
        self.backend = backend or self.config.backend
        self.db = db or self.config.db
        self._agents: dict[str, BaseAgent] = {}
        self._index_builder: Optional[IndexBuilder] = None
    
    def _get_index_builder(self) -> IndexBuilder:
        """Get or create the index builder."""
        if self._index_builder is None:
            self._index_builder = IndexBuilder(str(self.output_dir))
            # Load existing index if present
            self._index_builder.load()
        return self._index_builder
    
    def _update_index(self, file_path: str) -> None:
        """
        Update the semantic index after generating a file.
        Scans the file for @archeon:section markers and updates the index.
        """
        builder = self._get_index_builder()
        entry = builder.build_from_file(file_path)
        if entry:
            # Save immediately to keep index current
            builder.save()
    
    def get_target_dir(self, glyph: GlyphNode) -> tuple[Path, str]:
        """
        Determine the target directory (client or server) for a glyph.
        
        Returns:
            Tuple of (directory_path, target_name)
        """
        if not self.config.monorepo:
            return self.output_dir / self.config.output_dir, "single"
        
        prefix = glyph.prefix
        
        # Explicit frontend glyphs
        if prefix in self.CLIENT_PREFIXES:
            return self.output_dir / self.config.client_dir, "client"
        
        # Explicit backend glyphs
        if prefix in self.SERVER_PREFIXES:
            return self.output_dir / self.config.server_dir, "server"
        
        # Shared glyphs - check namespace
        if prefix == "FNC":
            namespace = glyph.namespace or ""
            # UI-related functions go to client
            if namespace in ("ui", "utils", "hooks", "components"):
                return self.output_dir / self.config.client_dir, "client"
            # Everything else goes to server
            return self.output_dir / self.config.server_dir, "server"
        
        # Default to server
        return self.output_dir / self.config.server_dir, "server"

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
            # Determine target directory (client or server)
            target_dir, target_name = self.get_target_dir(glyph)
            result.target = target_name
            
            # Resolve output path
            rel_path = agent.resolve_path(glyph, fw)
            full_path = target_dir / rel_path

            # Check if file exists
            if full_path.exists() and not force:
                result.status = "skipped"
                result.file_path = str(target_dir.relative_to(self.output_dir) / rel_path)
                return result

            # Generate code
            code = agent.generate(glyph, chain, fw)
            
            # Write file
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(code)
            result.file_path = str(target_dir.relative_to(self.output_dir) / rel_path)

            # Update semantic index with section info
            self._update_index(str(full_path))

            # Generate test in appropriate test directory
            test_code = agent.generate_test(glyph, fw)
            if target_name == "client":
                test_rel_path = f"tests/test_{Path(rel_path).stem}.tsx"
            else:
                test_rel_path = f"tests/test_{Path(rel_path).stem}.py"
            
            # Adjust test path for monorepo
            if self.config.monorepo:
                test_base = self.output_dir / ("client" if target_name == "client" else "server")
            else:
                test_base = self.output_dir
                
            test_full_path = test_base / test_rel_path
            test_full_path.parent.mkdir(parents=True, exist_ok=True)
            test_full_path.write_text(test_code)
            result.test_path = str(test_full_path.relative_to(self.output_dir))

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
    framework: Optional[str] = None,
    backend: Optional[str] = None,
    db: Optional[str] = None,
    force: bool = False,
    config: Optional[ProjectConfig] = None
) -> BatchResult:
    """
    Convenience function to spawn all unresolved glyphs.
    
    Automatically loads .archeonrc config for monorepo support.
    """
    # Load config if not provided
    config = config or ProjectConfig.load(Path(output_dir))
    
    spawner = AgentSpawner(
        output_dir=output_dir, 
        framework=framework or config.frontend,
        backend=backend or config.backend,
        db=db or config.db,
        config=config
    )
    return spawner.spawn_all(graph, force=force)
