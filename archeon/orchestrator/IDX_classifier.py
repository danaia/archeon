"""
File-to-Glyph classification for INDEX command.

Classifies files in an arbitrary codebase by detecting file types,
directory patterns, and code signatures to assign Archeon glyphs.
Supports auto-detection of tech stack from dependency files.

Enhanced with data flow analysis for stores and API endpoints.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Set, Optional, Tuple, List


@dataclass
class StoreAnalysis:
    """Analyzed state management store."""
    file_path: Path
    store_name: str
    state_properties: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    getters: List[str] = field(default_factory=list)
    api_calls: List[str] = field(default_factory=list)  # Detected fetch/axios calls
    subscriptions: List[str] = field(default_factory=list)  # What subscribes to this store
    framework: str = "unknown"  # pinia, zustand, redux, vuex
    
    def has_async_data(self) -> bool:
        """Check if store fetches data from API."""
        return len(self.api_calls) > 0


@dataclass
class APIEndpointAnalysis:
    """Analyzed API endpoint."""
    file_path: Path
    method: str  # GET, POST, PUT, DELETE, etc.
    path: str    # /api/users, /auth/login, etc.
    handler_name: str
    request_model: Optional[str] = None  # Pydantic model, DTO, etc.
    response_model: Optional[str] = None
    calls_to: List[str] = field(default_factory=list)  # What this endpoint calls
    
    @property
    def qualified_name(self) -> str:
        return f"API:{self.method}{self.path}"


@dataclass
class DataFlowEdge:
    """Represents a data flow connection."""
    source_glyph: str  # e.g., "STO:AuthStore"
    target_glyph: str  # e.g., "API:POST/auth/login"
    flow_type: str     # "fetch", "mutation", "subscription", "callback"
    method: Optional[str] = None  # HTTP method if applicable
    
    def to_chain_segment(self) -> str:
        """Convert to chain notation segment."""
        operator = "~>" if self.flow_type in ("subscription", "callback") else "=>"
        return f"{self.source_glyph} {operator} {self.target_glyph}"


@dataclass
class TechStack:
    """Detected technology stack."""
    frontend_framework: Optional[str] = None  # vue, react, svelte, etc.
    state_management: Optional[str] = None    # pinia, zustand, redux, etc.
    backend_framework: Optional[str] = None   # fastapi, django, express, etc.
    backend_language: Optional[str] = None    # python, javascript, typescript, go, etc.
    orm: Optional[str] = None                 # pydantic, sqlalchemy, prisma, mongoose, etc.
    
    def has_frontend(self) -> bool:
        return self.frontend_framework is not None
    
    def has_backend(self) -> bool:
        return self.backend_framework is not None


class StoreAnalyzer:
    """Deep analysis of state management stores."""
    
    # Patterns to detect store frameworks
    STORE_PATTERNS = {
        'pinia': {
            'detect': r'defineStore\s*\(',
            'state': r'state\s*:\s*\(\)\s*=>\s*\({([^}]+)\}',
            'actions': r'actions\s*:\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
            'getters': r'getters\s*:\s*\{([^}]+)\}',
        },
        'zustand': {
            'detect': r'create\s*\(\s*\(set',
            'state': r'\(set\s*,\s*get\s*\)\s*=>\s*\({([^}]+)',
            'actions': r'(\w+):\s*(?:async\s*)?\([^)]*\)\s*=>',
        },
        'redux': {
            'detect': r'createSlice\s*\(',
            'state': r'initialState\s*[:=]\s*\{([^}]+)\}',
            'actions': r'reducers\s*:\s*\{([^}]+)\}',
        },
        'vuex': {
            'detect': r'new\s+Vuex\.Store\s*\(',
            'state': r'state\s*:\s*\{([^}]+)\}',
            'actions': r'actions\s*:\s*\{([^}]+)\}',
            'mutations': r'mutations\s*:\s*\{([^}]+)\}',
        },
    }
    
    # Patterns to detect API calls within stores
    API_CALL_PATTERNS = [
        r'fetch\s*\(\s*["\']([^"\'/]*/?[^"\']*)["\']\'',  # fetch('/api/...')
        r'axios\.(get|post|put|patch|delete)\s*\(\s*["\']([^"\']+)["\']\'',
        r'\$axios\.(get|post|put|patch|delete)\s*\(\s*["\']([^"\']+)["\']\'',
        r'\.fetch\s*\(\s*["\']([^"\']+)["\']\'',
        r'useFetch\s*\(\s*["\']([^"\']+)["\']\'',
        r'api\.(get|post|put|patch|delete)\s*\(\s*["\']([^"\']+)["\']\'',
    ]
    
    def analyze_store(self, file_path: Path, content: str) -> Optional[StoreAnalysis]:
        """Analyze a store file for state, actions, and data flow."""
        # Detect framework
        framework = None
        for fw, patterns in self.STORE_PATTERNS.items():
            if re.search(patterns['detect'], content):
                framework = fw
                break
        
        if not framework:
            return None
        
        analysis = StoreAnalysis(
            file_path=file_path,
            store_name=self._extract_store_name(file_path, content, framework),
            framework=framework
        )
        
        # Extract state properties
        patterns = self.STORE_PATTERNS[framework]
        if 'state' in patterns:
            state_match = re.search(patterns['state'], content, re.DOTALL)
            if state_match:
                analysis.state_properties = self._extract_property_names(state_match.group(1))
        
        # Extract actions
        if 'actions' in patterns:
            actions_match = re.search(patterns['actions'], content, re.DOTALL)
            if actions_match:
                analysis.actions = self._extract_function_names(actions_match.group(1))
        
        # Extract getters
        if 'getters' in patterns:
            getters_match = re.search(patterns['getters'], content, re.DOTALL)
            if getters_match:
                analysis.getters = self._extract_function_names(getters_match.group(1))
        
        # Find API calls
        analysis.api_calls = self._extract_api_calls(content)
        
        return analysis
    
    def _extract_store_name(self, file_path: Path, content: str, framework: str) -> str:
        """Extract the store name from file or content."""
        if framework == 'pinia':
            match = re.search(r"defineStore\s*\([\'\"]([^\'\"]+)[\'\"]", content)
            if match:
                return match.group(1)
        elif framework == 'zustand':
            match = re.search(r"export\s+const\s+(use\w+Store|\w+Store)\s*=", content)
            if match:
                return match.group(1)
        
        # Fallback to filename
        name = file_path.stem
        return ''.join(word.capitalize() for word in name.replace('.store', '').replace('Store', '').split('_')) + 'Store'
    
    def _extract_property_names(self, state_block: str) -> List[str]:
        """Extract property names from state block."""
        props = []
        for match in re.finditer(r'(\w+)\s*:', state_block):
            prop = match.group(1)
            if prop not in ('type', 'default', 'required'):
                props.append(prop)
        return props
    
    def _extract_function_names(self, block: str) -> List[str]:
        """Extract function/method names from a block."""
        functions = []
        # Match: functionName(, async functionName(, functionName:
        for match in re.finditer(r'(?:async\s+)?(\w+)\s*(?:\(|:)', block):
            fn = match.group(1)
            if fn not in ('function', 'async', 'return', 'if', 'else', 'const', 'let', 'var'):
                functions.append(fn)
        return list(set(functions))
    
    def _extract_api_calls(self, content: str) -> List[str]:
        """Extract API call paths from store content."""
        api_calls = []
        
        # Generic fetch pattern: fetch('url') or fetch(`url`)
        for match in re.finditer(r'fetch\s*\(\s*["\'\'`]([^"\'\'`]+)["\'\'`]', content):
            url = match.group(1)
            if not url.startswith('http') or '/api' in url:
                api_calls.append(('GET', url))  # Assume GET for plain fetch
        
        # Axios patterns
        for match in re.finditer(r'axios\.(get|post|put|patch|delete)\s*\(\s*["\'\'`]([^"\'\'`]+)["\'\'`]', content, re.IGNORECASE):
            method, url = match.groups()
            api_calls.append((method.upper(), url))
        
        # useFetch (Nuxt)
        for match in re.finditer(r'useFetch\s*\(\s*["\'\'`]([^"\'\'`]+)["\'\'`]', content):
            api_calls.append(('GET', match.group(1)))
        
        # $fetch (Nuxt)
        for match in re.finditer(r'\$fetch\s*\(\s*["\'\'`]([^"\'\'`]+)["\'\'`]', content):
            api_calls.append(('GET', match.group(1)))
        
        # Format as API glyphs
        return [f"API:{method}{path}" for method, path in api_calls]


class APIAnalyzer:
    """Deep analysis of API endpoint files."""
    
    # Patterns for different backend frameworks
    ENDPOINT_PATTERNS = {
        'fastapi': [
            (r'@(?:router|app)\.(get|post|put|patch|delete|options)\s*\(["\']([^"\']+)["\']', 'decorator'),
            (r'async\s+def\s+(\w+)\s*\([^)]*(?:request|response|db|session)', 'handler'),
        ],
        'express': [
            (r'router\.(get|post|put|patch|delete)\s*\(["\']([^"\']+)["\']', 'method'),
            (r'app\.(get|post|put|patch|delete)\s*\(["\']([^"\']+)["\']', 'method'),
        ],
        'django': [
            (r'path\s*\(["\']([^"\']+)["\']\s*,\s*(\w+)', 'url_pattern'),
            (r'def\s+(get|post|put|patch|delete)\s*\(self', 'class_method'),
        ],
        'flask': [
            (r'@(?:app|bp|blueprint)\.route\s*\(["\']([^"\']+)["\'].*methods\s*=\s*\[([^\]]+)\]', 'route'),
            (r'@(?:app|bp|blueprint)\.(get|post|put|patch|delete)\s*\(["\']([^"\']+)["\']', 'shorthand'),
        ],
    }
    
    # Model reference patterns
    MODEL_PATTERNS = [
        r':\s*(\w+(?:Schema|Model|DTO|Request|Response|Input|Output))\s*(?:=|\)|,)',
        r'response_model\s*=\s*(\w+)',
        r'->\s*(\w+(?:Schema|Model|DTO|Response))',
    ]
    
    def analyze_api_file(self, file_path: Path, content: str, framework: str = 'auto') -> List[APIEndpointAnalysis]:
        """Analyze an API file for all endpoints."""
        endpoints = []
        
        if framework == 'auto':
            framework = self._detect_framework(content)
        
        if not framework:
            return endpoints
        
        patterns = self.ENDPOINT_PATTERNS.get(framework, [])
        
        for pattern, pattern_type in patterns:
            for match in re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE):
                endpoint = self._parse_endpoint_match(match, pattern_type, file_path, content)
                if endpoint:
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _detect_framework(self, content: str) -> Optional[str]:
        """Auto-detect the API framework."""
        if 'fastapi' in content.lower() or '@router.' in content or 'APIRouter' in content:
            return 'fastapi'
        if 'express' in content.lower() or 'router.get' in content:
            return 'express'
        if 'django' in content.lower() or 'from django' in content:
            return 'django'
        if 'flask' in content.lower() or 'from flask' in content:
            return 'flask'
        return None
    
    def _parse_endpoint_match(self, match, pattern_type: str, file_path: Path, content: str) -> Optional[APIEndpointAnalysis]:
        """Parse a regex match into an APIEndpointAnalysis."""
        groups = match.groups()
        
        if pattern_type == 'decorator':
            method, path = groups[0].upper(), groups[1]
        elif pattern_type == 'method':
            method, path = groups[0].upper(), groups[1]
        elif pattern_type == 'handler':
            # Just function name, need to find decorator above
            return None
        elif pattern_type == 'url_pattern':
            path, handler = groups
            method = 'GET'  # Default for Django URL patterns
        elif pattern_type == 'route':
            path = groups[0]
            methods_str = groups[1] if len(groups) > 1 else 'GET'
            method = re.findall(r"['\'](\w+)['\"]", methods_str)
            method = method[0].upper() if method else 'GET'
        elif pattern_type == 'shorthand':
            method, path = groups[0].upper(), groups[1]
        else:
            return None
        
        # Find handler name (function defined after the decorator)
        handler_match = re.search(rf'{re.escape(match.group(0))}[^\n]*\n(?:async\s+)?def\s+(\w+)', content)
        handler_name = handler_match.group(1) if handler_match else 'handler'
        
        # Find models referenced
        request_model = None
        response_model = None
        for model_pattern in self.MODEL_PATTERNS:
            model_match = re.search(model_pattern, content[match.start():match.start()+500])
            if model_match:
                model_name = model_match.group(1)
                if 'Request' in model_name or 'Input' in model_name:
                    request_model = model_name
                else:
                    response_model = model_name
        
        return APIEndpointAnalysis(
            file_path=file_path,
            method=method,
            path=path,
            handler_name=handler_name,
            request_model=request_model,
            response_model=response_model,
        )


class DataFlowAnalyzer:
    """Analyze data flow between stores and API endpoints."""
    
    def __init__(self):
        self.store_analyzer = StoreAnalyzer()
        self.api_analyzer = APIAnalyzer()
        self.stores: Dict[str, StoreAnalysis] = {}
        self.endpoints: Dict[str, APIEndpointAnalysis] = {}
        self.data_flows: List[DataFlowEdge] = []
    
    def analyze_store_file(self, file_path: Path, content: str) -> Optional[StoreAnalysis]:
        """Analyze a store file and track it."""
        analysis = self.store_analyzer.analyze_store(file_path, content)
        if analysis:
            self.stores[f"STO:{analysis.store_name}"] = analysis
        return analysis
    
    def analyze_api_file(self, file_path: Path, content: str) -> List[APIEndpointAnalysis]:
        """Analyze an API file and track endpoints."""
        endpoints = self.api_analyzer.analyze_api_file(file_path, content)
        for ep in endpoints:
            self.endpoints[ep.qualified_name] = ep
        return endpoints
    
    def build_data_flow_graph(self) -> List[DataFlowEdge]:
        """Build edges representing data flow between stores and APIs."""
        self.data_flows = []
        
        # Connect stores to the APIs they call
        for store_name, store in self.stores.items():
            for api_call in store.api_calls:
                # Extract method from the api_call (e.g., "API:POST/api/auth" -> "POST")
                method = 'GET'
                if ':' in api_call:
                    parts = api_call.split(':', 1)[1]
                    method_match = re.match(r'(GET|POST|PUT|PATCH|DELETE)', parts)
                    if method_match:
                        method = method_match.group(1)
                
                # Find matching endpoint
                matched_endpoint = self._match_api_call_to_endpoint(api_call)
                if matched_endpoint:
                    self.data_flows.append(DataFlowEdge(
                        source_glyph=store_name,
                        target_glyph=matched_endpoint,
                        flow_type='fetch',
                        method=method
                    ))
                else:
                    # Still track the API call even if no backend endpoint found
                    self.data_flows.append(DataFlowEdge(
                        source_glyph=store_name,
                        target_glyph=api_call,
                        flow_type='fetch',
                        method=method
                    ))
        
        return self.data_flows
    
    def _match_api_call_to_endpoint(self, api_call: str) -> Optional[str]:
        """Match a frontend API call to a backend endpoint."""
        # Extract path from api_call (e.g., "API:GET/users" -> "/users")
        if ':' in api_call:
            parts = api_call.split(':', 1)[1]
            # Extract path after method
            method_match = re.match(r'(GET|POST|PUT|PATCH|DELETE)(.+)', parts)
            if method_match:
                call_method, call_path = method_match.groups()
            else:
                call_method, call_path = 'GET', parts
        else:
            call_method, call_path = 'GET', api_call
        
        # Clean the path
        call_path = call_path.split('?')[0]  # Remove query params
        call_path = re.sub(r'/\{[^}]+\}', '/{id}', call_path)  # Normalize params
        
        # Find matching endpoint
        for ep_name, endpoint in self.endpoints.items():
            ep_path = endpoint.path
            # Normalize backend path params
            ep_path = re.sub(r'/:\w+', '/{id}', ep_path)  # Express :id
            ep_path = re.sub(r'/\{\w+\}', '/{id}', ep_path)  # FastAPI {id}
            
            if call_path.endswith(ep_path) or ep_path.endswith(call_path) or call_path == ep_path:
                if call_method == endpoint.method:
                    return ep_name
        
        return None
    
    def get_data_flow_chains(self) -> List[str]:
        """Generate chain notation strings for data flows."""
        chains = []
        
        # Group flows by store
        store_flows: Dict[str, List[DataFlowEdge]] = {}
        for flow in self.data_flows:
            if flow.source_glyph not in store_flows:
                store_flows[flow.source_glyph] = []
            store_flows[flow.source_glyph].append(flow)
        
        # Generate chains
        for store_name, flows in store_flows.items():
            # Create a chain for each data flow pattern
            for flow in flows:
                chain = f"@v1 {flow.to_chain_segment()}"
                chains.append(chain)
        
        return chains
    
    def get_summary(self) -> Dict:
        """Get summary of data flow analysis."""
        return {
            'stores_analyzed': len(self.stores),
            'endpoints_found': len(self.endpoints),
            'data_flow_edges': len(self.data_flows),
            'stores': {name: {
                'actions': store.actions,
                'api_calls': store.api_calls,
                'framework': store.framework,
            } for name, store in self.stores.items()},
            'endpoints': {name: {
                'method': ep.method,
                'path': ep.path,
            } for name, ep in self.endpoints.items()},
        }


class FileClassifier:
    """Classify files to Archeon glyphs based on patterns and signatures."""
    
    # Priority-ordered glyph classification patterns
    # Format: (glyph, path_patterns, content_markers)
    # Order matters: more specific patterns (CMP) should come before general ones (V)
    GLYPH_PATTERNS = {
        'CMP': (
            [
                r'\.component\.vue$',
                r'.*/components/.*\.vue$',   # nested components/
                r'components/.*\.vue$',      # root components/
                r'src/components/.*\.vue$',
                r'\.component\.tsx?$',
                r'.*/components/.*\.tsx?$',  # nested components/
                r'components/.*\.tsx?$',     # root components/
                r'src/components/.*\.tsx?$',
            ],
            [
                r'<template>',
                r'defineComponent\s*\(',
                r'function\s+\w+\s*\([^)]*\)\s*\{[\s\S]*return\s+\(?\s*<',
                r'class\s+\w+\s+extends\s+(React\.)?Component',
            ]
        ),
        'V': (
            [
                r'.*/pages?/.*\.vue$',
                r'.*/views?/.*\.vue$',
                r'pages?/.*\.vue$',
                r'views?/.*\.vue$',
                r'.*Page\.vue$',
                r'.*Layout\.vue$',
                r'.*/app/.*page\.tsx?$',
                r'app/.*page\.tsx?$',
                r'.*/pages?/.*\.tsx?$',
                r'pages?/.*\.tsx?$',
            ],
            [
                r'export\s+default\s+function\s+\w+Page',
                r'export\s+default\s+function\s+\w+Layout',
            ]
        ),
        'STO': (
            [
                r'.*/stores?/.*\.(js|ts)$',  # stores/ or store/ anywhere in path
                r'stores?/.*\.(js|ts)$',     # stores/ at root
                r'.*[Ss]tore\.(js|ts)$',     # *Store.js or *store.js
                r'.*\.store\.(js|ts)$',      # *.store.js
            ],
            [
                r'defineStore\s*\(',
                r'create\s*\(\s*\(set',
                r'createSlice\s*\(',
                r'new\s+Vuex\.Store\s*\(',
                r'@observable',
            ]
        ),
        'API': (
            [
                r'.*/routers?/.*\.py$',      # nested routers/
                r'routers?/.*\.py$',         # root routers/
                r'.*/api/.*\.(ts|js)$',      # nested api/
                r'api/.*\.(ts|js)$',         # root api/
                r'.*/routes?/.*\.(ts|js|py)$',
                r'routes?/.*\.(ts|js|py)$',
                r'.*_router\.py$',
                r'.*/handlers?/.*\.py$',
                r'handlers?/.*\.py$',
            ],
            [
                r'@(router|app)\.(get|post|put|patch|delete|options)\s*\(',
                r'router\.(get|post|put|patch|delete|options)\s*\(',
                r'export\s+(async\s+)?function\s+(GET|POST|PUT|PATCH|DELETE|OPTIONS)',
                r'def\s+\w+\s*\([^)]*\)\s*:\s*.*(?:GET|POST|PUT|PATCH|DELETE)',
            ]
        ),
        'MDL': (
            [
                r'.*/models?/.*\.py$',
                r'models?/.*\.py$',
                r'.*/models?/.*\.ts$',
                r'models?/.*\.ts$',
                r'.*\.model\.(py|ts)$',
                r'schema\.prisma$',
            ],
            [
                r'class\s+\w+\s*\(.*Model\)',
                r'mongoose\.Schema\s*\(',
                r'@Entity\s*\(',
                r'model\s+\w+\s*\{',
                r'class\s+\w+\s*\(BaseModel\)',
            ]
        ),
        'EVT': (
            [
                r'.*/events?/.*\.(js|ts|py)$',
                r'events?/.*\.(js|ts|py)$',
                r'.*pubsub.*\.(js|ts|py)$',
                r'.*channel.*\.(js|ts|py)$',
            ],
            [
                r'EventEmitter',
                r'publish\s*\(',
                r'subscribe\s*\(',
                r'on\s*\(\s*["\']',
                r'emit\s*\(\s*["\']',
                r'addEventListener',
            ]
        ),
        'FNC': (
            [
                r'.*/utils?/.*\.(js|ts|py)$',
                r'utils?/.*\.(js|ts|py)$',
                r'.*/helpers?/.*\.(js|ts|py)$',
                r'helpers?/.*\.(js|ts|py)$',
                r'.*/lib/.*\.(js|ts|py)$',
                r'lib/.*\.(js|ts|py)$',
            ],
            [
                r'export\s+(const|function|async)\s+\w+',
                r'^def\s+\w+\s*\(',
            ]
        ),
    }
    
    # Supported languages
    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.ts', '.tsx', '.jsx',
        '.vue', '.svelte', '.html', '.css',
        '.go', '.rb', '.php', '.java', '.kt'
    }
    
    # Directories to skip
    SKIP_DIRS = {
        'node_modules', '__pycache__', '.git', 'dist', 'build',
        '.next', '.nuxt', 'coverage', '.venv', 'venv', 'env',
        'vendor', 'bin', 'obj', 'target', '.pytest_cache',
        '.tox', 'site-packages', 'eggs', '.eggs', '.tox',
        'htmlcov', '.mypy_cache', '.dmypy.json', '.pyre',
        '.vscode', '.idea', 'out', 'logs', 'tmp'
    }
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.tech_stack = TechStack()
        self._detect_tech_stack()
    
    def _detect_tech_stack(self):
        """Auto-detect tech stack from dependency files."""
        # Check for JavaScript/Node.js projects (root and common subdirs)
        pkg_locations = [
            self.project_root / 'package.json',
            self.project_root / 'client' / 'package.json',
            self.project_root / 'frontend' / 'package.json',
            self.project_root / 'web' / 'package.json',
            self.project_root / 'app' / 'package.json',
        ]
        for pkg_path in pkg_locations:
            if pkg_path.exists():
                self._parse_package_json(pkg_path)
                break
        
        # Check for Python projects (root and common subdirs)
        py_locations = [
            (self.project_root / 'pyproject.toml', 'toml'),
            (self.project_root / 'server' / 'pyproject.toml', 'toml'),
            (self.project_root / 'backend' / 'pyproject.toml', 'toml'),
            (self.project_root / 'api' / 'pyproject.toml', 'toml'),
            (self.project_root / 'requirements.txt', 'txt'),
            (self.project_root / 'server' / 'requirements.txt', 'txt'),
            (self.project_root / 'backend' / 'requirements.txt', 'txt'),
        ]
        for py_path, file_type in py_locations:
            if py_path.exists():
                if file_type == 'toml':
                    self._parse_pyproject_toml(py_path)
                else:
                    self._parse_requirements_txt(py_path)
                break
        
        # Check for Go projects
        if (self.project_root / 'go.mod').exists():
            self.tech_stack.backend_language = 'go'
        
        # Fallback: scan for framework imports in Python files
        if not self.tech_stack.backend_framework:
            self._detect_backend_from_code()
    
    def _parse_package_json(self, pkg_path: Optional[Path] = None):
        """Parse package.json to detect frontend/state frameworks."""
        try:
            if pkg_path is None:
                pkg_path = self.project_root / 'package.json'
            with open(pkg_path) as f:
                pkg = json.load(f)
            
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
            
            # Detect frontend framework
            if 'vue' in deps or '@vue/core' in deps:
                self.tech_stack.frontend_framework = 'vue'
                if 'pinia' in deps:
                    self.tech_stack.state_management = 'pinia'
                elif 'vuex' in deps:
                    self.tech_stack.state_management = 'vuex'
            
            if 'react' in deps or 'react-dom' in deps:
                self.tech_stack.frontend_framework = 'react'
                if 'zustand' in deps:
                    self.tech_stack.state_management = 'zustand'
                elif '@reduxjs/toolkit' in deps or 'redux' in deps:
                    self.tech_stack.state_management = 'redux'
            
            if 'svelte' in deps:
                self.tech_stack.frontend_framework = 'svelte'
            
            # Detect backend framework
            if 'express' in deps:
                self.tech_stack.backend_framework = 'express'
                self.tech_stack.backend_language = 'javascript'
            
            if 'next' in deps or 'nextjs' in deps:
                self.tech_stack.backend_framework = 'next'
                self.tech_stack.backend_language = 'javascript'
        except Exception as e:
            print(f"Warning: Could not parse package.json: {e}")
    
    def _parse_pyproject_toml(self, toml_path: Optional[Path] = None):
        """Parse pyproject.toml to detect backend framework."""
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                return
        
        try:
            if toml_path is None:
                toml_path = self.project_root / 'pyproject.toml'
            with open(toml_path, 'rb') as f:
                data = tomllib.load(f)
            
            deps = {}
            if 'project' in data and 'dependencies' in data['project']:
                deps.update({d.split()[0]: d for d in data['project']['dependencies']})
            
            if 'tool' in data and 'poetry' in data['tool'] and 'dependencies' in data['tool']['poetry']:
                deps.update(data['tool']['poetry']['dependencies'])
            
            # Detect backend framework
            if 'fastapi' in deps:
                self.tech_stack.backend_framework = 'fastapi'
                self.tech_stack.backend_language = 'python'
            elif 'django' in deps:
                self.tech_stack.backend_framework = 'django'
                self.tech_stack.backend_language = 'python'
            elif 'flask' in deps:
                self.tech_stack.backend_framework = 'flask'
                self.tech_stack.backend_language = 'python'
            else:
                self.tech_stack.backend_language = 'python'
            
            # Detect ORM
            if 'sqlalchemy' in deps or 'SQLAlchemy' in deps:
                self.tech_stack.orm = 'sqlalchemy'
            elif 'pydantic' in deps:
                self.tech_stack.orm = 'pydantic'
        except Exception as e:
            print(f"Warning: Could not parse pyproject.toml: {e}")
    
    def _parse_requirements_txt(self, req_path: Path):
        """Parse requirements.txt to detect backend framework."""
        try:
            content = req_path.read_text(encoding='utf-8', errors='ignore').lower()
            
            # Detect backend framework
            if 'fastapi' in content:
                self.tech_stack.backend_framework = 'fastapi'
                self.tech_stack.backend_language = 'python'
            elif 'django' in content:
                self.tech_stack.backend_framework = 'django'
                self.tech_stack.backend_language = 'python'
            elif 'flask' in content:
                self.tech_stack.backend_framework = 'flask'
                self.tech_stack.backend_language = 'python'
            else:
                self.tech_stack.backend_language = 'python'
        except Exception as e:
            print(f"Warning: Could not parse requirements.txt: {e}")
    
    def _detect_backend_from_code(self):
        """Detect backend framework by scanning Python files for imports."""
        # Look for server/ or backend/ directories
        server_dirs = ['server', 'backend', 'api', 'app']
        for server_dir in server_dirs:
            server_path = self.project_root / server_dir
            if server_path.exists():
                for py_file in server_path.rglob('*.py'):
                    try:
                        content = py_file.read_text(encoding='utf-8', errors='ignore')
                        if 'from fastapi' in content or 'import fastapi' in content:
                            self.tech_stack.backend_framework = 'fastapi'
                            self.tech_stack.backend_language = 'python'
                            return
                        elif 'from django' in content or 'import django' in content:
                            self.tech_stack.backend_framework = 'django'
                            self.tech_stack.backend_language = 'python'
                            return
                        elif 'from flask' in content or 'import flask' in content:
                            self.tech_stack.backend_framework = 'flask'
                            self.tech_stack.backend_language = 'python'
                            return
                    except Exception:
                        continue
    
    # Files to skip entirely (not just directories)
    SKIP_FILES = {
        'index.html', 'vite.config.js', 'vite.config.ts', 
        'webpack.config.js', 'webpack.config.ts',
        'babel.config.js', 'babel.config.json',
        'tailwind.config.js', 'tailwind.config.ts',
        'postcss.config.js', 'postcss.config.cjs',
        'jest.config.js', 'jest.config.ts',
        'vitest.config.js', 'vitest.config.ts',
        'tsconfig.json', 'tsconfig.node.json',
        'eslint.config.js', '.eslintrc.js', '.eslintrc.json',
        'prettier.config.js', '.prettierrc', '.prettierrc.js',
        'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
        '.env', '.env.local', '.env.development', '.env.production',
        'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
        'Makefile', 'README.md', 'LICENSE',
    }
    
    def classify_file(self, file_path: Path) -> Optional[str]:
        """
        Classify a single file to a glyph type.
        
        Returns the glyph string (e.g., 'CMP', 'API') or None if unclassifiable.
        """
        # Skip config/meta files entirely
        if file_path.name in self.SKIP_FILES:
            return None
        
        # Skip HTML files (they're not code glyphs)
        if file_path.suffix == '.html':
            return None
        
        # Skip CSS files (they're not code glyphs)
        if file_path.suffix == '.css':
            return None
        
        # Check if file should be processed
        if file_path.suffix not in self.SUPPORTED_EXTENSIONS:
            return None
        
        # Read file content for signature matching
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return None
        
        # Try path-based classification first (most reliable)
        rel_path = str(file_path.relative_to(self.project_root))
        
        for glyph, (path_patterns, content_markers) in self.GLYPH_PATTERNS.items():
            # Check path patterns
            for pattern in path_patterns:
                if re.search(pattern, rel_path, re.IGNORECASE):
                    return glyph
            
            # Check content signatures
            for marker in content_markers:
                if re.search(marker, content, re.MULTILINE | re.IGNORECASE):
                    return glyph
        
        # Fallback: Only classify as FNC if it's in a meaningful code location
        # Skip entry point files like main.js, main.py, index.js
        entry_points = {'main.js', 'main.ts', 'index.js', 'index.ts', 'main.py', '__init__.py'}
        if file_path.name in entry_points:
            return None
        
        # Only FNC for actual utility/helper files or files with function definitions
        if file_path.suffix in {'.py', '.js', '.ts'}:
            # Check if file has actual function/class definitions
            if re.search(r'^def\s+\w+|^class\s+\w+|^async\s+def\s+\w+', content, re.MULTILINE):
                return 'FNC'
            if re.search(r'export\s+(const|function|class|async\s+function)', content):
                return 'FNC'
        
        return None
    
    def extract_qualified_name(self, file_path: Path, glyph: str) -> str:
        """
        Extract a qualified name from file path and content.
        
        Examples:
          - API:POST/auth/login
          - CMP:LoginForm
          - STO:AuthStore
          - MDL:User
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            content = ''
        
        if glyph == 'API':
            # Try to extract HTTP method and path
            match = re.search(
                r'@(?:router|app)\.(get|post|put|patch|delete|options)\s*\(["\']([^"\']+)["\']',
                content,
                re.IGNORECASE
            )
            if match:
                method, path = match.groups()
                return f"API:{method.upper()}{path}"
        
        # Default: use PascalCase filename
        name = file_path.stem
        # Convert snake_case to PascalCase
        name = ''.join(word.capitalize() for word in name.split('_'))
        
        return f"{glyph}:{name}"
    
    def classify_directory(self, directory: Optional[Path] = None) -> Dict[Path, str]:
        """
        Classify all files in a directory.
        
        Returns dict mapping file paths to glyphs.
        """
        if directory is None:
            directory = self.project_root
        
        classified = {}
        
        def should_skip(path: Path) -> bool:
            """Check if a path should be skipped."""
            for part in path.relative_to(self.project_root).parts:
                if part in self.SKIP_DIRS:
                    return True
            return False
        
        for file_path in directory.rglob('*'):
            # Skip files in excluded directories
            if should_skip(file_path):
                continue
            
            # Skip directories
            if file_path.is_dir():
                continue
            
            glyph = self.classify_file(file_path)
            if glyph:
                classified[file_path] = glyph
        
        return classified
    
    def extract_imports(self, file_path: Path) -> Set[Path]:
        """
        Extract import paths from a file.
        
        Returns set of relative file paths that this file imports.
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            return set()
        
        imports = set()
        
        # JavaScript/TypeScript imports
        for match in re.finditer(
            r'(?:import\s+.*\s+from\s+["\']([^"\']+)["\']|require\s*\(\s*["\']([^"\']+)["\']\s*\))',
            content
        ):
            import_path = match.group(1) or match.group(2)
            imports.add(self._resolve_import(import_path, file_path))
        
        # Python imports
        for match in re.finditer(
            r'(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))',
            content
        ):
            import_path = match.group(1) or match.group(2)
            imports.add(self._resolve_import(import_path, file_path))
        
        return imports
    
    def _resolve_import(self, import_path: str, from_file: Path) -> Path:
        """
        Resolve an import path to a file path.
        
        Simple heuristic: relative imports use from_file location,
        absolute imports are resolved from project root.
        """
        import_path = import_path.lstrip('./').rstrip('/')
        
        # Relative import
        if import_path.startswith('.'):
            base = from_file.parent
            return base / import_path
        
        # Absolute import from project root or node_modules
        return self.project_root / import_path
