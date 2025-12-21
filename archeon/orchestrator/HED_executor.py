"""
HED_executor.py - Archeon Headless Execution Engine

Executes chains in sandbox or live mode with full tracing.
Only [headless] annotated components can be executed.
"""

import time
import json
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any, Callable
from pathlib import Path

from archeon.orchestrator.PRS_parser import ChainAST, GlyphNode
from archeon.orchestrator.GRF_graph import KnowledgeGraph, StoredChain


class ExecutionMode(Enum):
    """Execution mode for headless runs."""
    SANDBOX = "sandbox"  # Default: trace only, mock API calls
    LIVE = "live"        # Execute real API calls (requires explicit opt-in)


class StepStatus(Enum):
    """Status of an execution step."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    MOCKED = "mocked"


@dataclass
class StepTrace:
    """Trace for a single execution step."""
    glyph: str
    status: StepStatus
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    input_data: Optional[dict] = None
    output_data: Optional[dict] = None
    error: Optional[str] = None
    mocked: bool = False
    
    def to_dict(self) -> dict:
        return {
            "glyph": self.glyph,
            "status": self.status.value,
            "duration_ms": self.duration_ms,
            "input": self.input_data,
            "output": self.output_data,
            "error": self.error,
            "mocked": self.mocked
        }


@dataclass
class ExecutionTrace:
    """Complete trace for a chain execution."""
    chain_id: str
    mode: ExecutionMode
    started_at: str
    completed_at: Optional[str] = None
    status: str = "running"
    steps: list[StepTrace] = field(default_factory=list)
    final_output: Optional[dict] = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "chain_id": self.chain_id,
            "mode": self.mode.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "steps": [s.to_dict() for s in self.steps],
            "final_output": self.final_output,
            "error": self.error,
            "metadata": self.metadata
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class ExecutionResult:
    """Result of chain execution."""
    success: bool
    trace: ExecutionTrace
    output: Optional[Any] = None
    error: Optional[str] = None


class MockRegistry:
    """Registry for mock handlers in sandbox mode."""
    
    def __init__(self):
        self._mocks: dict[str, Callable] = {}
        self._default_mocks: dict[str, dict] = {
            # API mocks by method
            "GET": {"status": 200, "data": {}},
            "POST": {"status": 201, "data": {"id": "mock-id"}},
            "PUT": {"status": 200, "data": {"updated": True}},
            "PATCH": {"status": 200, "data": {"patched": True}},
            "DELETE": {"status": 204, "data": None},
        }
        
        # Common API response mocks
        self._api_mocks: dict[str, dict] = {
            "auth": {"token": "mock-jwt-token", "user_id": "user-123"},
            "login": {"success": True, "token": "mock-jwt-token"},
            "logout": {"success": True},
            "register": {"id": "user-123", "email": "mock@example.com"},
            "user": {"id": "user-123", "name": "Mock User", "email": "mock@example.com"},
            "users": {"items": [], "total": 0},
        }
    
    def register(self, glyph: str, handler: Callable) -> None:
        """Register a custom mock handler for a glyph."""
        self._mocks[glyph] = handler
    
    def get_mock(self, glyph: GlyphNode) -> dict:
        """Get mock response for a glyph."""
        qualified = glyph.qualified_name
        
        # Check for custom mock
        if qualified in self._mocks:
            return self._mocks[qualified]({})
        
        # API glyphs get method-based mocks
        if glyph.prefix == "API":
            # Parse method from name (e.g., "POST./auth" -> "POST")
            method = glyph.name.split('.')[0].split('/')[0].upper()
            route = glyph.name.split('/')[-1] if '/' in glyph.name else glyph.name
            
            # Check for route-specific mock
            if route in self._api_mocks:
                return {"status": 200, **self._api_mocks[route]}
            
            return self._default_mocks.get(method, {"status": 200, "data": {}})
        
        # STO glyphs return state
        if glyph.prefix == "STO":
            return {"state": {}, "actions": []}
        
        # FNC glyphs return generic result
        if glyph.prefix == "FNC":
            return {"result": None, "success": True}
        
        # EVT glyphs return event info
        if glyph.prefix == "EVT":
            return {"emitted": True, "event": glyph.name, "data": {}}
        
        # MDL glyphs return model data
        if glyph.prefix == "MDL":
            return {"id": "mock-id", "created_at": datetime.now().isoformat()}
        
        # CMP glyphs return render info
        if glyph.prefix == "CMP":
            return {"rendered": True, "component": glyph.name}
        
        # Default
        return {"success": True}


class HeadlessValidator:
    """Validates that components can be executed in headless mode."""
    
    @staticmethod
    def is_headless(glyph: GlyphNode) -> bool:
        """Check if a glyph has the [headless] modifier."""
        return "headless" in glyph.modifiers
    
    @staticmethod
    def can_execute(chain: ChainAST, strict: bool = True) -> tuple[bool, list[str]]:
        """
        Check if a chain can be executed in headless mode.
        
        Args:
            chain: The chain AST to validate
            strict: If True, all executable glyphs must have [headless]
            
        Returns:
            Tuple of (can_execute, list of validation errors)
        """
        errors = []
        executable_prefixes = {"CMP", "API", "FNC", "STO", "MDL", "EVT"}
        
        for node in chain.nodes:
            if node.prefix in executable_prefixes:
                if strict and "headless" not in node.modifiers:
                    errors.append(
                        f"{node.qualified_name} missing [headless] modifier - "
                        "only headless components can be executed"
                    )
        
        return len(errors) == 0, errors
    
    @staticmethod
    def find_headless_entry(chain: ChainAST) -> Optional[GlyphNode]:
        """Find the first headless component that can serve as entry point."""
        for node in chain.nodes:
            if "headless" in node.modifiers:
                return node
        return None


class HeadlessExecutor:
    """
    Executes chains in headless mode with full tracing.
    
    Sandbox mode (default): All API calls are mocked, no side effects.
    Live mode: Executes real code (requires explicit opt-in).
    """
    
    def __init__(self, graph: Optional[KnowledgeGraph] = None):
        self.graph = graph
        self.mock_registry = MockRegistry()
        self.validator = HeadlessValidator()
        self._execution_history: list[ExecutionTrace] = []
        self._metrics: dict[str, dict] = {}
    
    def execute(
        self,
        chain: ChainAST,
        mode: ExecutionMode = ExecutionMode.SANDBOX,
        input_data: Optional[dict] = None,
        strict: bool = True
    ) -> ExecutionResult:
        """
        Execute a chain in the specified mode.
        
        Args:
            chain: The chain AST to execute
            mode: SANDBOX (mock APIs) or LIVE (real execution)
            input_data: Initial input data for the chain
            strict: If True, require all executable glyphs to have [headless]
            
        Returns:
            ExecutionResult with trace and output
        """
        # Validate headless capability
        can_exec, errors = self.validator.can_execute(chain, strict=strict)
        if not can_exec and strict:
            trace = ExecutionTrace(
                chain_id=chain.raw or "unknown",
                mode=mode,
                started_at=datetime.now().isoformat(),
                status="failed",
                error="; ".join(errors)
            )
            return ExecutionResult(
                success=False,
                trace=trace,
                error="Headless validation failed: " + "; ".join(errors)
            )
        
        # Create execution trace
        trace = ExecutionTrace(
            chain_id=chain.raw or "unknown",
            mode=mode,
            started_at=datetime.now().isoformat(),
            metadata={
                "version": chain.version,
                "framework": chain.framework,
                "node_count": len(chain.nodes),
                "strict": strict
            }
        )
        
        current_data = input_data or {}
        
        try:
            # Execute each node in sequence
            for i, node in enumerate(chain.nodes):
                step = self._execute_step(node, current_data, mode)
                trace.steps.append(step)
                
                # Update current data with step output
                if step.output_data:
                    current_data = {**current_data, **step.output_data}
                
                # Stop on failure
                if step.status == StepStatus.FAILED:
                    trace.status = "failed"
                    trace.error = step.error
                    break
            
            # Mark complete if all steps succeeded
            if trace.status == "running":
                trace.status = "completed"
                trace.final_output = current_data
            
        except Exception as e:
            trace.status = "failed"
            trace.error = str(e)
        
        trace.completed_at = datetime.now().isoformat()
        
        # Record metrics
        self._record_metrics(chain, trace)
        self._execution_history.append(trace)
        
        return ExecutionResult(
            success=trace.status == "completed",
            trace=trace,
            output=trace.final_output,
            error=trace.error
        )
    
    def _execute_step(
        self,
        node: GlyphNode,
        input_data: dict,
        mode: ExecutionMode
    ) -> StepTrace:
        """Execute a single step in the chain."""
        start_time = time.time()
        
        step = StepTrace(
            glyph=node.qualified_name,
            status=StepStatus.RUNNING,
            start_time=start_time,
            input_data=input_data
        )
        
        # Meta glyphs are traced but not executed
        meta_prefixes = {"NED", "TSK", "OUT", "ERR", "V", "ORC", "GRF"}
        if node.prefix in meta_prefixes:
            step.status = StepStatus.SUCCESS
            step.output_data = self._handle_meta_glyph(node, input_data)
            step.end_time = time.time()
            step.duration_ms = (step.end_time - start_time) * 1000
            return step
        
        # Internal orchestrator glyphs with special execution
        if node.prefix == "TKN":
            step.output_data = self._execute_tkn(node, input_data)
            step.status = StepStatus.SUCCESS
            step.end_time = time.time()
            step.duration_ms = (step.end_time - start_time) * 1000
            return step
        
        try:
            if mode == ExecutionMode.SANDBOX:
                # Mock the execution
                step.mocked = True
                step.output_data = self.mock_registry.get_mock(node)
                step.status = StepStatus.MOCKED
            else:
                # Live mode - attempt real execution
                step.output_data = self._execute_live(node, input_data)
                step.status = StepStatus.SUCCESS
                
        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
        
        step.end_time = time.time()
        step.duration_ms = (step.end_time - start_time) * 1000
        
        return step
    
    def _handle_meta_glyph(self, node: GlyphNode, data: dict) -> dict:
        """Handle meta glyphs (NED, TSK, OUT, ERR, etc.)."""
        if node.prefix == "NED":
            return {"need": node.name, "acknowledged": True}
        elif node.prefix == "TSK":
            return {"task": node.name, "started": True}
        elif node.prefix == "OUT":
            # OUT glyphs define the output format
            output_type = node.name
            if node.args:
                return {"type": output_type, "message": node.args[0], "data": data}
            return {"type": output_type, "data": data}
        elif node.prefix == "ERR":
            return {"error": node.name, "triggered": False}
        else:
            return {"glyph": node.qualified_name, "passthrough": True}
    
    def _execute_tkn(self, node: GlyphNode, data: dict) -> dict:
        """
        Execute TKN (design token) glyph.
        
        Transforms design-tokens.json to CSS/Tailwind/JS outputs.
        This is a deterministic build step that propagates token changes.
        """
        from archeon.orchestrator.TKN_tokens import TokenTransformer
        from pathlib import Path
        
        # Determine source and output paths from input data or defaults
        source = data.get("source")
        output_dir = data.get("output", "client/src/tokens")
        format_type = data.get("format", "all")
        
        # Look for design tokens in standard locations
        if source:
            tokens_path = Path(source)
        else:
            candidates = [
                Path("archeon/_config/design-tokens.json"),
                Path("client/src/tokens/design-tokens.json"),
                Path(__file__).parent.parent / "templates" / "_config" / "design-tokens.json",
            ]
            tokens_path = next((p for p in candidates if p.exists()), candidates[-1])
        
        try:
            transformer = TokenTransformer(tokens_path)
            output_path = Path(output_dir)
            
            if format_type == "all":
                generated = transformer.generate_all(output_path)
                files = [str(f.name) for f in generated]
            else:
                # Single format
                from archeon.orchestrator.TKN_tokens import (
                    generate_css, generate_tailwind_extension, generate_js_tokens
                )
                output_path.mkdir(parents=True, exist_ok=True)
                
                if format_type == "css":
                    out = output_path / "tokens.css"
                    out.write_text(generate_css(transformer.tokens))
                    files = [out.name]
                elif format_type == "tailwind":
                    out = output_path / "tokens.tailwind.js"
                    out.write_text(generate_tailwind_extension(transformer.tokens))
                    files = [out.name]
                elif format_type == "js":
                    out = output_path / "tokens.js"
                    out.write_text(generate_js_tokens(transformer.tokens))
                    files = [out.name]
                else:
                    files = []
            
            return {
                "glyph": node.qualified_name,
                "action": "token_transform",
                "source": str(tokens_path),
                "output_dir": str(output_path),
                "generated": files,
                "success": True
            }
            
        except FileNotFoundError as e:
            return {
                "glyph": node.qualified_name,
                "action": "token_transform",
                "error": f"Design tokens not found: {e}",
                "success": False
            }
        except Exception as e:
            return {
                "glyph": node.qualified_name,
                "action": "token_transform",
                "error": str(e),
                "success": False
            }
    
    def _execute_live(self, node: GlyphNode, data: dict) -> dict:
        """
        Execute a glyph in live mode.
        
        This attempts to actually run the generated code.
        """
        # Check for headless modifier
        if "headless" not in node.modifiers:
            raise RuntimeError(
                f"Cannot execute {node.qualified_name} in live mode - "
                "missing [headless] modifier"
            )
        
        # TODO: Implement actual code execution
        # This would involve:
        # 1. Finding the generated file via tracer
        # 2. Importing/loading the module
        # 3. Calling the appropriate function/method
        
        # For now, return a placeholder indicating live execution attempted
        return {
            "live_execution": True,
            "glyph": node.qualified_name,
            "status": "executed",
            "note": "Live execution not yet implemented"
        }
    
    def _record_metrics(self, chain: ChainAST, trace: ExecutionTrace) -> None:
        """Record execution metrics."""
        chain_id = chain.raw or "unknown"
        
        if chain_id not in self._metrics:
            self._metrics[chain_id] = {
                "executions": 0,
                "successes": 0,
                "failures": 0,
                "total_duration_ms": 0,
                "avg_duration_ms": 0,
                "last_execution": None
            }
        
        m = self._metrics[chain_id]
        m["executions"] += 1
        
        if trace.status == "completed":
            m["successes"] += 1
        else:
            m["failures"] += 1
        
        # Calculate duration
        total_ms = sum(s.duration_ms or 0 for s in trace.steps)
        m["total_duration_ms"] += total_ms
        m["avg_duration_ms"] = m["total_duration_ms"] / m["executions"]
        m["last_execution"] = trace.started_at
    
    def get_metrics(self, chain_id: Optional[str] = None) -> dict:
        """Get execution metrics."""
        if chain_id:
            return self._metrics.get(chain_id, {})
        return self._metrics
    
    def get_history(self, limit: int = 100) -> list[ExecutionTrace]:
        """Get execution history."""
        return self._execution_history[-limit:]
    
    def execute_by_glyph(
        self,
        glyph_name: str,
        mode: ExecutionMode = ExecutionMode.SANDBOX,
        input_data: Optional[dict] = None
    ) -> list[ExecutionResult]:
        """
        Execute all chains containing a specific glyph.
        
        Args:
            glyph_name: The qualified glyph name to find
            mode: Execution mode
            input_data: Input data for the chains
            
        Returns:
            List of execution results for each chain
        """
        if not self.graph:
            raise RuntimeError("No graph loaded - cannot find chains by glyph")
        
        results = []
        for chain in self.graph.find_chains_by_glyph(glyph_name):
            result = self.execute(chain.ast, mode, input_data, strict=False)
            results.append(result)
        
        return results


# Convenience functions

def run_sandbox(chain: ChainAST, input_data: Optional[dict] = None) -> ExecutionResult:
    """Run a chain in sandbox mode (mocked APIs)."""
    executor = HeadlessExecutor()
    return executor.execute(chain, ExecutionMode.SANDBOX, input_data, strict=False)


def run_live(chain: ChainAST, input_data: Optional[dict] = None) -> ExecutionResult:
    """Run a chain in live mode (real execution)."""
    executor = HeadlessExecutor()
    return executor.execute(chain, ExecutionMode.LIVE, input_data, strict=True)


def validate_headless(chain: ChainAST) -> tuple[bool, list[str]]:
    """Validate that a chain can run in headless mode."""
    return HeadlessValidator.can_execute(chain, strict=True)
