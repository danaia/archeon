"""
CTX_context.py - Context Budget Manager

Manages context window budgets for smaller models (30B parameters, ~60K tokens).
Ensures no single operation exceeds the context budget.

CRITICAL INVARIANT: All context passed to agents MUST fit within budget.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from archeon.orchestrator.PRS_parser import ChainAST, GlyphNode
from archeon.orchestrator.GRF_graph import KnowledgeGraph, StoredChain


class ContextTier(Enum):
    """Context budget tiers for different model sizes."""
    TINY = 8_000      # 7B models
    SMALL = 16_000    # 14B models  
    MEDIUM = 32_000   # 30B models (Qwen3)
    LARGE = 60_000    # 70B models
    UNLIMITED = -1    # Cloud models


@dataclass
class ContextBudget:
    """Tracks token budget for a single operation."""
    tier: ContextTier
    max_tokens: int
    used_tokens: int = 0
    
    # Allocation percentages (must sum to 1.0)
    GLYPH_ALLOC = 0.10      # 10% for glyph notation
    TEMPLATE_ALLOC = 0.20    # 20% for template
    DEPS_ALLOC = 0.30        # 30% for dependencies  
    CHAIN_ALLOC = 0.20       # 20% for chain context
    OUTPUT_ALLOC = 0.20      # 20% reserved for output
    
    @property
    def remaining(self) -> int:
        if self.max_tokens == -1:
            return 999_999
        return max(0, self.max_tokens - self.used_tokens)
    
    @property
    def glyph_budget(self) -> int:
        return int(self.max_tokens * self.GLYPH_ALLOC)
    
    @property
    def template_budget(self) -> int:
        return int(self.max_tokens * self.TEMPLATE_ALLOC)
    
    @property
    def deps_budget(self) -> int:
        return int(self.max_tokens * self.DEPS_ALLOC)
    
    @property
    def chain_budget(self) -> int:
        return int(self.max_tokens * self.CHAIN_ALLOC)
    
    def allocate(self, tokens: int, category: str = "general") -> bool:
        """Try to allocate tokens. Returns False if over budget."""
        if self.max_tokens == -1:
            return True
        if self.used_tokens + tokens > self.max_tokens:
            return False
        self.used_tokens += tokens
        return True
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate: ~4 chars per token."""
        return len(text) // 4
    
    @classmethod
    def for_model(cls, model_size: str = "30b") -> 'ContextBudget':
        """Create budget for model size."""
        tiers = {
            "7b": ContextTier.TINY,
            "14b": ContextTier.SMALL,
            "30b": ContextTier.MEDIUM,
            "70b": ContextTier.LARGE,
            "cloud": ContextTier.UNLIMITED,
        }
        tier = tiers.get(model_size.lower(), ContextTier.MEDIUM)
        return cls(tier=tier, max_tokens=tier.value)


@dataclass
class GlyphProjection:
    """
    A minimal projection of the knowledge graph.
    
    Contains ONLY what's needed for a single glyph operation:
    - The target glyph
    - Its immediate chain
    - Direct dependencies (1-hop)
    - Relevant error paths
    
    This is the MAXIMUM context any agent should receive.
    """
    target: GlyphNode
    chain: ChainAST
    dependencies: list[GlyphNode] = field(default_factory=list)
    error_paths: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    
    def to_compact(self) -> str:
        """
        Return hyper-compressed context string.
        
        Example output:
        ---
        TARGET: CMP:LoginForm[stateful]
        CHAIN: CMP:LoginForm => STO:authStore => API:POST/auth
        DEPS: STO:authStore, FNC:auth.validateCreds
        ERRS: ERR:auth.invalidCreds, ERR:auth.tokenExpired
        ---
        
        This is ~200 chars vs 2000+ chars of full context.
        """
        lines = [
            "---",
            f"TARGET: {self.target.qualified_name}",
            f"CHAIN: {self.chain.raw}",
        ]
        
        if self.dependencies:
            deps = ", ".join(d.qualified_name for d in self.dependencies)
            lines.append(f"DEPS: {deps}")
        
        if self.error_paths:
            lines.append(f"ERRS: {', '.join(self.error_paths)}")
        
        if self.imports:
            lines.append(f"IMPORTS: {', '.join(self.imports)}")
        
        lines.append("---")
        return "\n".join(lines)
    
    def token_estimate(self) -> int:
        """Estimate tokens for this projection."""
        return len(self.to_compact()) // 4


class ContextProjector:
    """
    Projects minimal context from the full knowledge graph.
    
    The key insight: A 30B model doesn't need to see your entire codebase.
    It only needs to see:
    1. What glyph it's building
    2. What that glyph connects to (1 hop)
    3. The template to fill
    
    This reduces context from potentially 100K+ tokens to ~5K tokens.
    """
    
    def __init__(self, graph: KnowledgeGraph, budget: Optional[ContextBudget] = None):
        self.graph = graph
        self.budget = budget or ContextBudget.for_model("30b")
    
    def project(self, glyph_name: str) -> Optional[GlyphProjection]:
        """
        Create a minimal projection for a single glyph.
        
        Args:
            glyph_name: Qualified glyph name (e.g., "CMP:LoginForm")
        
        Returns:
            GlyphProjection with bounded context, or None if not found
        """
        # Find chains containing this glyph
        chains = self.graph.find_chains_containing(glyph_name)
        if not chains:
            return None
        
        # Use the first (most relevant) chain
        stored = chains[0]
        chain = stored.ast
        
        # Find the target node in the chain
        target = None
        for node in chain.nodes:
            if node.qualified_name == glyph_name:
                target = node
                break
        
        if not target:
            return None
        
        # Collect 1-hop dependencies (direct neighbors only)
        deps = self._get_direct_deps(chain, target)
        
        # Collect error paths for this glyph
        error_paths = self._get_error_paths(glyph_name)
        
        # Determine imports based on dependencies
        imports = self._infer_imports(deps)
        
        projection = GlyphProjection(
            target=target,
            chain=chain,
            dependencies=deps,
            error_paths=error_paths,
            imports=imports
        )
        
        # Verify within budget
        if projection.token_estimate() > self.budget.chain_budget:
            # Trim dependencies if over budget
            projection = self._trim_to_budget(projection)
        
        return projection
    
    def _get_direct_deps(self, chain: ChainAST, target: GlyphNode) -> list[GlyphNode]:
        """Get only direct dependencies (1-hop neighbors)."""
        deps = []
        target_idx = None
        
        # Find target index
        for i, node in enumerate(chain.nodes):
            if node.qualified_name == target.qualified_name:
                target_idx = i
                break
        
        if target_idx is None:
            return deps
        
        # Find nodes connected by edges
        for edge in chain.edges:
            if edge.source_idx == target_idx:
                deps.append(chain.nodes[edge.target_idx])
            elif edge.target_idx == target_idx:
                deps.append(chain.nodes[edge.source_idx])
        
        return deps
    
    def _get_error_paths(self, glyph_name: str) -> list[str]:
        """Find error glyphs related to this glyph."""
        errors = []
        
        # Extract namespace from glyph (e.g., "auth" from "FNC:auth.validate")
        if ":" in glyph_name and "." in glyph_name:
            namespace = glyph_name.split(":")[1].split(".")[0]
            
            # Find ERR glyphs in same namespace
            for chain in self.graph.chains:
                for node in chain.ast.nodes:
                    if node.prefix == "ERR" and namespace in node.name:
                        errors.append(node.qualified_name)
        
        return list(set(errors))[:3]  # Max 3 error paths
    
    def _infer_imports(self, deps: list[GlyphNode]) -> list[str]:
        """Infer required imports from dependencies."""
        imports = []
        
        for dep in deps:
            if dep.prefix == "STO":
                imports.append(f"use{dep.name}")
            elif dep.prefix == "FNC":
                if dep.namespace:
                    imports.append(f"{dep.namespace}.{dep.action}")
                else:
                    imports.append(dep.name)
        
        return imports
    
    def _trim_to_budget(self, projection: GlyphProjection) -> GlyphProjection:
        """Trim projection to fit within budget."""
        # Remove dependencies until within budget
        while projection.token_estimate() > self.budget.chain_budget:
            if projection.dependencies:
                projection.dependencies.pop()
            elif projection.error_paths:
                projection.error_paths.pop()
            else:
                break
        
        return projection
    
    def project_batch(self, glyph_names: list[str]) -> list[GlyphProjection]:
        """
        Project multiple glyphs, respecting total budget.
        
        For batch operations, we further constrain each projection
        to ensure the total fits in context.
        """
        projections = []
        per_glyph_budget = self.budget.remaining // max(len(glyph_names), 1)
        
        for name in glyph_names:
            proj = self.project(name)
            if proj and proj.token_estimate() <= per_glyph_budget:
                projections.append(proj)
        
        return projections


def create_minimal_prompt(projection: GlyphProjection, template: str, index_context: str = "") -> str:
    """
    Create the minimal prompt for agent execution.
    
    This is the ONLY context the agent needs. Nothing more.
    
    Total: ~2-5K tokens for a 60K context model = plenty of room
    
    Args:
        projection: The glyph projection with chain context
        template: The code template to fill
        index_context: Optional semantic index context for existing files
    """
    # Build index section if provided
    index_section = ""
    if index_context:
        index_section = f"""
# Existing Files (Semantic Index):
{index_context}

# Section Rules:
- Edit ONLY within @archeon:section blocks
- Do NOT delete or modify @archeon markers
- If new section needed, add it explicitly
"""

    return f"""# Task: Generate {projection.target.qualified_name}

{projection.to_compact()}
{index_section}
# Template:
```
{template}
```

# Instructions:
1. Fill the template placeholders
2. Import: {', '.join(projection.imports) or 'none'}
3. Handle errors: {', '.join(projection.error_paths) or 'none'}

Generate ONLY the filled template. No explanations."""
