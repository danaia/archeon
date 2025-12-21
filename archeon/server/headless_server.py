"""
headless_server.py - Archeon Headless HTTP Server

Provides HTTP endpoints for headless component execution.
"""

import json
import http.server
import socketserver
import urllib.parse
from typing import Optional
from pathlib import Path

from archeon.orchestrator.GRF_graph import KnowledgeGraph
from archeon.orchestrator.HED_executor import (
    HeadlessExecutor,
    ExecutionMode,
    ExecutionResult,
)


class HeadlessRequestHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for headless execution."""
    
    # Class-level graph and executor (set by serve())
    graph: Optional[KnowledgeGraph] = None
    executor: Optional[HeadlessExecutor] = None
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        
        # Route requests
        if path == "/health":
            self._health()
        elif path == "/api/status":
            self._status()
        elif path == "/api/chains":
            self._list_chains()
        elif path == "/api/metrics":
            chain_id = query.get("chain", [None])[0]
            self._metrics(chain_id)
        elif path.startswith("/api/cmp/"):
            # /api/cmp/{component}
            component = path.split("/api/cmp/")[1].split("/")[0]
            action = query.get("action", [None])[0]
            mode = query.get("mode", ["sandbox"])[0]
            
            if path.endswith("/metrics"):
                self._component_metrics(component)
            else:
                self._execute_component(component, action, mode, query)
        elif path.startswith("/api/chain/"):
            # /api/chain/{chain_id}
            chain_id = path.split("/api/chain/")[1].split("/")[0]
            mode = query.get("mode", ["sandbox"])[0]
            self._execute_chain_by_id(chain_id, mode, query)
        else:
            self._not_found()
    
    def do_POST(self):
        """Handle POST requests."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # Read body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length else '{}'
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._error(400, "Invalid JSON body")
            return
        
        # Route requests
        if path.startswith("/api/cmp/"):
            component = path.split("/api/cmp/")[1].split("/")[0]
            mode = data.get("mode", "sandbox")
            action = data.get("action")
            self._execute_component(component, action, mode, {}, data.get("input", {}))
        elif path.startswith("/api/chain/"):
            chain_id = path.split("/api/chain/")[1]
            mode = data.get("mode", "sandbox")
            self._execute_chain_by_id(chain_id, mode, {}, data.get("input", {}))
        elif path == "/api/execute":
            # Execute raw chain string
            chain_str = data.get("chain")
            if not chain_str:
                self._error(400, "Missing 'chain' in request body")
                return
            mode = data.get("mode", "sandbox")
            self._execute_raw_chain(chain_str, mode, data.get("input", {}))
        else:
            self._not_found()
    
    def _health(self):
        """Health check endpoint."""
        self._json_response(200, {"status": "ok", "service": "archeon-headless"})
    
    def _status(self):
        """Get server status."""
        if not self.graph:
            self._error(500, "No graph loaded")
            return
        
        self._json_response(200, {
            "status": "ready",
            "chains": len(self.graph.chains),
            "glyphs": len(self.graph.get_all_glyphs()),
            "sections": list(self.graph.sections.keys()),
        })
    
    def _list_chains(self):
        """List all chains."""
        if not self.graph:
            self._error(500, "No graph loaded")
            return
        
        chains = []
        for stored in self.graph.chains:
            chains.append({
                "id": stored.ast.raw,
                "version": stored.ast.version,
                "framework": stored.ast.framework,
                "nodes": len(stored.ast.nodes),
                "section": stored.section,
            })
        
        self._json_response(200, {"chains": chains, "total": len(chains)})
    
    def _metrics(self, chain_id: Optional[str]):
        """Get execution metrics."""
        if not self.executor:
            self._error(500, "Executor not initialized")
            return
        
        metrics = self.executor.get_metrics(chain_id)
        self._json_response(200, {"metrics": metrics})
    
    def _component_metrics(self, component: str):
        """Get metrics for a specific component."""
        if not self.executor:
            self._error(500, "Executor not initialized")
            return
        
        # Find chains containing this component
        all_metrics = self.executor.get_metrics()
        component_metrics = {}
        
        for chain_id, m in all_metrics.items():
            if component.lower() in chain_id.lower():
                component_metrics[chain_id] = m
        
        self._json_response(200, {
            "component": component,
            "metrics": component_metrics
        })
    
    def _execute_component(
        self,
        component: str,
        action: Optional[str],
        mode: str,
        query: dict,
        input_data: Optional[dict] = None
    ):
        """Execute a component in headless mode."""
        if not self.graph or not self.executor:
            self._error(500, "Server not properly initialized")
            return
        
        # Find chains containing this component
        glyph_name = f"CMP:{component}"
        chains = self.graph.find_chain(glyph_name)
        
        if not chains:
            self._error(404, f"No chains found containing {glyph_name}")
            return
        
        # Execute first matching chain
        exec_mode = ExecutionMode.LIVE if mode == "live" else ExecutionMode.SANDBOX
        result = self.executor.execute(
            chains[0].ast,
            exec_mode,
            input_data or {},
            strict=False
        )
        
        self._execution_response(result)
    
    def _execute_chain_by_id(
        self,
        chain_id: str,
        mode: str,
        query: dict,
        input_data: Optional[dict] = None
    ):
        """Execute a chain by its ID (raw string)."""
        if not self.graph or not self.executor:
            self._error(500, "Server not properly initialized")
            return
        
        # Find chain by raw string match
        chain_id = urllib.parse.unquote(chain_id)
        matching = None
        
        for stored in self.graph.chains:
            if stored.ast.raw == chain_id or chain_id in stored.ast.raw:
                matching = stored
                break
        
        if not matching:
            self._error(404, f"Chain not found: {chain_id}")
            return
        
        exec_mode = ExecutionMode.LIVE if mode == "live" else ExecutionMode.SANDBOX
        result = self.executor.execute(
            matching.ast,
            exec_mode,
            input_data or {},
            strict=False
        )
        
        self._execution_response(result)
    
    def _execute_raw_chain(self, chain_str: str, mode: str, input_data: dict):
        """Execute a raw chain string."""
        if not self.executor:
            self._error(500, "Executor not initialized")
            return
        
        from archeon.orchestrator.PRS_parser import parse_chain, ParseError
        
        try:
            ast = parse_chain(chain_str)
        except ParseError as e:
            self._error(400, f"Invalid chain: {e}")
            return
        
        exec_mode = ExecutionMode.LIVE if mode == "live" else ExecutionMode.SANDBOX
        result = self.executor.execute(ast, exec_mode, input_data, strict=False)
        
        self._execution_response(result)
    
    def _execution_response(self, result: ExecutionResult):
        """Send execution result as response."""
        status = 200 if result.success else 500
        self._json_response(status, {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "trace": result.trace.to_dict(),
        })
    
    def _json_response(self, status: int, data: dict):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _error(self, status: int, message: str):
        """Send error response."""
        self._json_response(status, {"error": message})
    
    def _not_found(self):
        """Send 404 response."""
        self._error(404, f"Not found: {self.path}")
    
    def log_message(self, format: str, *args):
        """Override to customize logging."""
        print(f"[headless] {args[0]} {args[1]} {args[2]}")


def serve(
    arcon_path: str,
    host: str = "localhost",
    port: int = 8765,
    quiet: bool = False
) -> None:
    """
    Start the headless HTTP server.
    
    Args:
        arcon_path: Path to ARCHEON.arcon file
        host: Host to bind to
        port: Port to listen on
        quiet: Suppress output
    """
    # Load graph
    graph = KnowledgeGraph()
    graph.load(arcon_path)
    
    # Create executor
    executor = HeadlessExecutor(graph)
    
    # Set class-level attributes
    HeadlessRequestHandler.graph = graph
    HeadlessRequestHandler.executor = executor
    
    # Create server
    with socketserver.TCPServer((host, port), HeadlessRequestHandler) as server:
        if not quiet:
            print(f"🚀 Archeon Headless Server running at http://{host}:{port}")
            print(f"   Loaded {len(graph.chains)} chains, {len(graph.get_all_glyphs())} glyphs")
            print(f"\nEndpoints:")
            print(f"   GET  /health              - Health check")
            print(f"   GET  /api/status          - Server status")
            print(f"   GET  /api/chains          - List all chains")
            print(f"   GET  /api/metrics         - Execution metrics")
            print(f"   GET  /api/cmp/{{name}}      - Execute component (sandbox)")
            print(f"   POST /api/cmp/{{name}}      - Execute component with input")
            print(f"   POST /api/execute         - Execute raw chain")
            print(f"\nQuery params: ?mode=sandbox|live&action=...")
            print(f"\nPress Ctrl+C to stop")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            if not quiet:
                print("\n👋 Server stopped")


def create_app(arcon_path: str):
    """
    Create a WSGI-compatible application.
    
    This can be used with production WSGI servers like gunicorn:
        gunicorn "archeon.server.headless_server:create_app('/path/to/ARCHEON.arcon')"
    
    Args:
        arcon_path: Path to ARCHEON.arcon file
        
    Returns:
        WSGI application callable
    """
    # Load graph and executor
    graph = KnowledgeGraph()
    graph.load(arcon_path)
    executor = HeadlessExecutor(graph)
    
    def app(environ, start_response):
        """WSGI application."""
        path = environ.get('PATH_INFO', '/')
        method = environ.get('REQUEST_METHOD', 'GET')
        query_string = environ.get('QUERY_STRING', '')
        query = urllib.parse.parse_qs(query_string)
        
        # Read body for POST
        input_data = {}
        if method == 'POST':
            try:
                content_length = int(environ.get('CONTENT_LENGTH', 0))
                body = environ['wsgi.input'].read(content_length).decode('utf-8')
                if body:
                    data = json.loads(body)
                    input_data = data.get('input', {})
            except (ValueError, json.JSONDecodeError):
                pass
        
        # Route and execute
        response_data = {"error": "Not found"}
        status = "404 Not Found"
        
        if path == "/health":
            response_data = {"status": "ok"}
            status = "200 OK"
        elif path == "/api/status":
            response_data = {
                "status": "ready",
                "chains": len(graph.chains),
                "glyphs": len(graph.get_all_glyphs()),
            }
            status = "200 OK"
        elif path.startswith("/api/cmp/"):
            component = path.split("/api/cmp/")[1].split("/")[0]
            glyph_name = f"CMP:{component}"
            chains = graph.find_chain(glyph_name)
            
            if chains:
                mode_str = query.get("mode", ["sandbox"])[0]
                exec_mode = ExecutionMode.LIVE if mode_str == "live" else ExecutionMode.SANDBOX
                result = executor.execute(chains[0].ast, exec_mode, input_data, strict=False)
                response_data = {
                    "success": result.success,
                    "output": result.output,
                    "trace": result.trace.to_dict(),
                }
                status = "200 OK" if result.success else "500 Internal Server Error"
            else:
                response_data = {"error": f"Component not found: {component}"}
                status = "404 Not Found"
        
        # Send response
        response_body = json.dumps(response_data, indent=2).encode()
        headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_body))),
            ('Access-Control-Allow-Origin', '*'),
        ]
        start_response(status, headers)
        return [response_body]
    
    return app
