"""
INDEX command orchestrator.

Orchestrates the indexing of arbitrary codebases by:
1. Detecting tech stack
2. Classifying files to glyphs
3. Analyzing data flow (stores ↔ APIs)
4. Building import graphs
5. Inferring chains
6. Writing to ARCHEON.index.json
"""

import json
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

from archeon.orchestrator.IDX_classifier import FileClassifier, DataFlowAnalyzer, StoreAnalysis, APIEndpointAnalysis
from archeon.orchestrator.IDX_inferrer import ChainInferrer


@dataclass
class IndexedGlyph:
    """Single entry in the index."""
    file: str
    glyph: str
    qualified_name: str
    chain: Optional[str] = None
    confidence: float = 1.0
    data_flow: Optional[Dict] = None  # Store->API connections


@dataclass
class ArcheonIndex:
    """Complete index document."""
    version: str = "1.0"
    project: str = "indexed-project"
    glyphs: Dict[str, dict] = None
    data_flows: List[dict] = None  # Store->API data flow edges
    
    def __post_init__(self):
        if self.glyphs is None:
            self.glyphs = {}
        if self.data_flows is None:
            self.data_flows = []


class IndexOrchestrator:
    """Orchestrate the INDEX command for arbitrary codebases."""
    
    def __init__(self, project_path: str, output_file: Optional[str] = None):
        self.project_root = Path(project_path).resolve()
        self.output_file = Path(output_file) if output_file else self.project_root / "ARCHEON.index.json"
        
        self.classifier = FileClassifier(str(self.project_root))
        self.inferrer = ChainInferrer()
        self.data_flow_analyzer = DataFlowAnalyzer()
        
        self.classified_files: Dict[Path, str] = {}
        self.qualified_names: Dict[Path, str] = {}
        self.import_map: Dict[Path, set] = {}
        self.store_analyses: Dict[str, StoreAnalysis] = {}
        self.api_analyses: Dict[str, APIEndpointAnalysis] = {}
        self.index = ArcheonIndex(project=self.project_root.name)
    
    def run(self, verbose: bool = False) -> ArcheonIndex:
        """
        Execute the full INDEX pipeline.
        
        Returns the generated index.
        """
        if verbose:
            print(f"📦 Indexing project: {self.project_root}")
        
        # Step 1: Classify all files
        if verbose:
            print("🔍 Classifying files...")
        self._classify_files(verbose)
        
        # Step 2: Analyze data flow (stores and APIs)
        if verbose:
            print("🔄 Analyzing data flow (stores ↔ APIs)...")
        self._analyze_data_flow(verbose)
        
        # Step 3: Extract imports
        if verbose:
            print("📍 Extracting imports...")
        self._extract_imports(verbose)
        
        # Step 4: Build dependency graph (with data flow edges)
        if verbose:
            print("🔗 Building dependency graph...")
        self._build_graph_with_data_flow()
        
        # Step 5: Infer chains
        if verbose:
            print("⛓️  Inferring chains...")
        chains = self.inferrer.infer_chains()
        
        # Step 6: Add data flow chains
        data_flow_chains = self.data_flow_analyzer.get_data_flow_chains()
        chains.extend(data_flow_chains)
        
        # Step 7: Generate index
        if verbose:
            print("📝 Generating index...")
        self._generate_index(chains, verbose)
        
        # Step 8: Write index
        if verbose:
            print(f"💾 Writing index to {self.output_file}")
        self._write_index()
        
        if verbose:
            stats = self.inferrer.get_graph_stats()
            df_summary = self.data_flow_analyzer.get_summary()
            print(f"\n✅ Index complete!")
            print(f"   Files classified: {stats['total_files']}")
            print(f"   Glyphs: {stats['glyph_coverage']}")
            print(f"   Chains: {len(chains)}")
            print(f"   📊 Data Flow Analysis:")
            print(f"      Stores analyzed: {df_summary['stores_analyzed']}")
            print(f"      API endpoints: {df_summary['endpoints_found']}")
            print(f"      Data flow edges: {df_summary['data_flow_edges']}")
            
            # Show store->API connections
            if df_summary['stores']:
                print(f"   🗄️  Store → API Connections:")
                for store_name, store_info in df_summary['stores'].items():
                    if store_info['api_calls']:
                        print(f"      {store_name}:")
                        for api_call in store_info['api_calls']:
                            print(f"         → {api_call}")
        
        return self.index
    
    def _analyze_data_flow(self, verbose: bool = False):
        """Analyze data flow in stores and API endpoints."""
        for file_path, glyph in self.classified_files.items():
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            
            if glyph == 'STO':
                analysis = self.data_flow_analyzer.analyze_store_file(file_path, content)
                if analysis:
                    self.store_analyses[f"STO:{analysis.store_name}"] = analysis
                    if verbose and analysis.api_calls:
                        print(f"   📦 {analysis.store_name}: {len(analysis.api_calls)} API calls")
            
            elif glyph == 'API':
                endpoints = self.data_flow_analyzer.analyze_api_file(file_path, content)
                for ep in endpoints:
                    self.api_analyses[ep.qualified_name] = ep
                    if verbose:
                        print(f"   🔌 {ep.qualified_name}")
        
        # Build the data flow graph
        self.data_flow_analyzer.build_data_flow_graph()
    
    def _build_graph_with_data_flow(self):
        """Build dependency graph including data flow edges."""
        # First build the import-based graph
        self.inferrer.build_graph(
            self.classified_files,
            self.qualified_names,
            self.import_map
        )
        
        # Then register store->API connections
        for store_name, analysis in self.store_analyses.items():
            if analysis.api_calls:
                self.inferrer.register_store_api_calls(store_name, analysis.api_calls)
    
    def _classify_files(self, verbose: bool = False):
        """Classify all files in the project."""
        classified = self.classifier.classify_directory()
        
        for file_path, glyph in classified.items():
            self.classified_files[file_path] = glyph
            qualified_name = self.classifier.extract_qualified_name(file_path, glyph)
            self.qualified_names[file_path] = qualified_name
            
            if verbose and len(self.classified_files) % 10 == 0:
                print(f"   Classified {len(self.classified_files)} files...")
    
    def _extract_imports(self, verbose: bool = False):
        """Extract imports from classified files."""
        for file_path in self.classified_files.keys():
            imports = self.classifier.extract_imports(file_path)
            self.import_map[file_path] = imports
    
    def _generate_index(self, chains: list, verbose: bool = False):
        """Generate the ARCHEON.index.json structure with data flow."""
        glyphs_dict = {}
        
        # Group files by glyph
        glyph_to_files: Dict[str, list] = {}
        for file_path, glyph in self.classified_files.items():
            qualified_name = self.qualified_names[file_path]
            if qualified_name not in glyph_to_files:
                glyph_to_files[qualified_name] = []
            glyph_to_files[qualified_name].append({
                'file': str(file_path.relative_to(self.project_root)),
                'glyph': glyph,
            })
        
        # Create index entries
        for qualified_name, file_info_list in sorted(glyph_to_files.items()):
            file_info = file_info_list[0]  # Use first match
            glyph_type = file_info['glyph']
            
            # Find chains this glyph participates in
            participating_chains = [
                chain for chain in chains 
                if qualified_name in chain
            ]
            
            # Generate intent based on glyph type and name
            name_part = qualified_name.split(':')[-1] if ':' in qualified_name else qualified_name
            intent = self._generate_intent(glyph_type, name_part, qualified_name)
            
            # Generate sections based on glyph type
            sections = self._get_sections_for_glyph(glyph_type)
            
            entry = {
                'file': file_info['file'],
                'intent': intent,
                'chain': '@v1' if participating_chains else None,
                'sections': sections,
            }
            
            glyphs_dict[qualified_name] = entry
        
        # Add data flow edges to index
        data_flows = []
        for edge in self.data_flow_analyzer.data_flows:
            data_flows.append({
                'source': edge.source_glyph,
                'target': edge.target_glyph,
                'type': edge.flow_type,
                'method': edge.method,
            })
        
        self.index.glyphs = glyphs_dict
        self.index.data_flows = data_flows
    
    def _generate_intent(self, glyph_type: str, name: str, qualified_name: str) -> str:
        """Generate a human-readable intent description for a glyph."""
        # Clean up the name for readability
        readable_name = name.replace('_', ' ').replace('-', ' ')
        
        # Handle API endpoints specially
        if glyph_type == 'API':
            # Extract method and path from qualified name like "API:GET/users"
            parts = qualified_name.replace('API:', '').split('/')
            method = 'GET'
            path_parts = parts
            for m in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
                if parts[0].startswith(m):
                    method = m
                    path_parts = [parts[0][len(m):]] + parts[1:]
                    break
            
            path = '/'.join(path_parts).strip('/')
            operation = path_parts[-1] if path_parts else 'root'
            
            if method == 'POST':
                return f"Create {operation} endpoint"
            elif method == 'PUT' or method == 'PATCH':
                return f"Update {operation} endpoint"
            elif method == 'DELETE':
                return f"Delete {operation} endpoint"
            else:
                return f"Get {operation} endpoint"
        
        intents = {
            'CMP': f"{readable_name} component",
            'V': f"{readable_name} view/page",
            'STO': f"{readable_name} state management",
            'MDL': f"{readable_name} data model",
            'FNC': f"{readable_name} utility function",
            'EVT': f"{readable_name} event handler",
        }
        
        return intents.get(glyph_type, f"{readable_name} implementation")
    
    def _get_sections_for_glyph(self, glyph_type: str) -> List[str]:
        """Get the standard sections for a glyph type."""
        sections = {
            'CMP': ['imports', 'props_and_state', 'handlers', 'render'],
            'V': ['imports', 'props_and_state', 'handlers', 'render'],
            'STO': ['imports', 'state', 'actions'],
            'API': ['imports', 'config', 'helpers', 'endpoints'],
            'MDL': ['imports', 'models'],
            'FNC': ['imports', 'implementation'],
            'EVT': ['imports', 'handlers'],
        }
        return sections.get(glyph_type, ['imports', 'implementation'])
    
    def _write_index(self):
        """Write the index to ARCHEON.index.json."""
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to serializable format
        index_data = {
            'version': self.index.version,
            'project': self.index.project,
            'glyphs': self.index.glyphs,
            'data_flows': self.index.data_flows,
        }
        
        with open(self.output_file, 'w') as f:
            json.dump(index_data, f, indent=2)
    
    def get_stats(self) -> Dict:
        """Get statistics about the indexed project."""
        stats = self.inferrer.get_graph_stats()
        stats['output_file'] = str(self.output_file)
        stats['tech_stack'] = {
            'frontend': self.classifier.tech_stack.frontend_framework,
            'backend': self.classifier.tech_stack.backend_framework,
            'language': self.classifier.tech_stack.backend_language,
            'state_management': self.classifier.tech_stack.state_management,
        }
        stats['data_flow'] = self.data_flow_analyzer.get_summary()
        return stats
