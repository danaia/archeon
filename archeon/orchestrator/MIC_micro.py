"""
MIC_micro.py - Micro-Agent Executor

Executes single-glyph operations with minimal context.
Designed for small models (30B parameters, ~60K context).

KEY PRINCIPLE: One glyph, one template, one output.
Never batch. Never overload.
"""

from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from pathlib import Path

from archeon.orchestrator.PRS_parser import GlyphNode, ChainAST
from archeon.orchestrator.GRF_graph import KnowledgeGraph
from archeon.orchestrator.CTX_context import (
    ContextBudget, 
    ContextProjector, 
    GlyphProjection,
    create_minimal_prompt
)
from archeon.agents.base_agent import BaseAgent


@dataclass
class MicroTask:
    """
    A single micro-task for agent execution.
    
    This is THE UNIT OF WORK for small models.
    Each task generates exactly ONE file.
    """
    glyph: str                          # e.g., "CMP:LoginForm"
    projection: GlyphProjection         # Minimal context
    template: str                        # The template to fill
    output_path: str                     # Where to write
    prompt: str = ""                     # Generated prompt
    
    @property
    def token_estimate(self) -> int:
        """Total tokens for this task."""
        return (
            self.projection.token_estimate() +
            len(self.template) // 4 +
            len(self.prompt) // 4
        )


@dataclass
class MicroResult:
    """Result of a micro-task execution."""
    task: MicroTask
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    tokens_used: int = 0


class MicroAgentExecutor:
    """
    Executes agents with minimal context overhead.
    
    The micro-agent pattern ensures:
    1. Each invocation handles ONE glyph
    2. Context is projected (1-hop only)
    3. Templates are used (never raw code)
    4. Total context fits in 60K tokens
    
    This is critical for running on a 5090 with a 30B model.
    """
    
    def __init__(
        self, 
        graph: KnowledgeGraph,
        agents: dict[str, BaseAgent],
        model_size: str = "30b"
    ):
        self.graph = graph
        self.agents = agents
        self.budget = ContextBudget.for_model(model_size)
        self.projector = ContextProjector(graph, self.budget)
    
    def prepare_task(self, glyph_name: str, framework: str) -> Optional[MicroTask]:
        """
        Prepare a micro-task for a single glyph.
        
        Returns None if:
        - Glyph not found in graph
        - No agent for this glyph type
        - Task would exceed context budget
        """
        # Project minimal context
        projection = self.projector.project(glyph_name)
        if not projection:
            return None
        
        # Get agent for this glyph type
        prefix = glyph_name.split(":")[0]
        agent = self.agents.get(prefix)
        if not agent:
            return None
        
        # Load template
        try:
            template = agent.get_template(framework)
        except ValueError:
            return None
        
        # Determine output path
        output_path = agent.resolve_path(projection.target, framework)
        
        # Create task
        task = MicroTask(
            glyph=glyph_name,
            projection=projection,
            template=template,
            output_path=output_path
        )
        
        # Generate prompt
        task.prompt = create_minimal_prompt(projection, template)
        
        # Verify within budget
        if task.token_estimate > self.budget.remaining:
            return None
        
        return task
    
    def execute(
        self, 
        task: MicroTask, 
        generator: Callable[[str], str]
    ) -> MicroResult:
        """
        Execute a micro-task using the provided generator.
        
        Args:
            task: The prepared micro-task
            generator: A function that takes a prompt and returns generated code
                      (This is your LLM call)
        
        Returns:
            MicroResult with success/failure and output
        """
        try:
            # Call the LLM with minimal prompt
            output = generator(task.prompt)
            
            # Track budget
            tokens_used = task.token_estimate + len(output) // 4
            
            return MicroResult(
                task=task,
                success=True,
                output=output,
                tokens_used=tokens_used
            )
        except Exception as e:
            return MicroResult(
                task=task,
                success=False,
                error=str(e)
            )
    
    def execute_sequence(
        self,
        glyph_names: list[str],
        framework: str,
        generator: Callable[[str], str]
    ) -> list[MicroResult]:
        """
        Execute a sequence of glyphs ONE AT A TIME.
        
        IMPORTANT: This is sequential, not parallel.
        Each task gets the full context budget.
        We reset the budget between tasks.
        
        This is the correct pattern for small models.
        """
        results = []
        
        for glyph_name in glyph_names:
            # Reset budget for each task
            self.budget.used_tokens = 0
            
            # Prepare and execute
            task = self.prepare_task(glyph_name, framework)
            if task:
                result = self.execute(task, generator)
                results.append(result)
            else:
                results.append(MicroResult(
                    task=MicroTask(
                        glyph=glyph_name,
                        projection=GlyphProjection(
                            target=GlyphNode(prefix="UNK", name="unknown"),
                            chain=ChainAST()
                        ),
                        template="",
                        output_path=""
                    ),
                    success=False,
                    error=f"Could not prepare task for {glyph_name}"
                ))
        
        return results


def print_context_report(task: MicroTask, budget: ContextBudget) -> str:
    """
    Generate a context budget report for debugging.
    
    Use this to verify your tasks fit within budget.
    """
    lines = [
        "=" * 50,
        "CONTEXT BUDGET REPORT",
        "=" * 50,
        f"Model Tier: {budget.tier.name}",
        f"Max Tokens: {budget.max_tokens:,}",
        "",
        "Allocation:",
        f"  Glyph notation:  {task.projection.token_estimate():,} / {budget.glyph_budget:,}",
        f"  Template:        {len(task.template) // 4:,} / {budget.template_budget:,}",
        f"  Chain context:   (included in projection)",
        f"  Output reserved: {budget.max_tokens * 0.2:,.0f}",
        "",
        f"Total Used: {task.token_estimate:,}",
        f"Remaining:  {budget.max_tokens - task.token_estimate:,}",
        "",
        "Status: " + ("✅ WITHIN BUDGET" if task.token_estimate < budget.max_tokens else "❌ OVER BUDGET"),
        "=" * 50,
    ]
    return "\n".join(lines)
