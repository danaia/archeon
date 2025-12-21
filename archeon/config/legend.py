"""
Archeon Glyph Legend - Global definitions for glyphs, edge types, and boundary rules.
"""

GLYPH_LEGEND = {
    # === User Intent Glyphs (Meta) ===
    'NED': {
        'name': 'Need',
        'description': 'User intent or motivation',
        'agent': None,
        'color': '#9B59B6',
        'layer': 'meta'
    },
    'TSK': {
        'name': 'Task',
        'description': 'User action',
        'agent': None,
        'color': '#3498DB',
        'layer': 'meta'
    },
    'OUT': {
        'name': 'Output',
        'description': 'Feedback layer (must exist to close chain)',
        'agent': None,
        'color': '#ECF0F1',
        'layer': 'meta'
    },
    'ERR': {
        'name': 'Error',
        'description': 'Failure/exception path',
        'agent': None,
        'color': '#E91E63',
        'layer': 'meta',
        'qualifiers': ['auth', 'validation', 'system', 'domain']
    },

    # === View Glyph (Structural Only) ===
    'V': {
        'name': 'View',
        'description': 'Structural container (no logic, no agent)',
        'agent': None,
        'color': '#5D3FD3',
        'layer': 'frontend',
        'contains': ['CMP'],
        'cannot_execute': True,
        'allowed_operators': ['@'],
        'file_patterns': {
            'vue': 'views/{name}.vue',
            'react': 'pages/{name}.tsx',
            'nextjs': 'app/{name}/page.tsx',
            'angular': '{name}/{name}.component.ts',
            'svelte': 'routes/{name}/+page.svelte'
        }
    },

    # === Component Glyphs ===
    'CMP': {
        'name': 'Component',
        'description': 'UI component (framework agnostic)',
        'agent': 'CMP_agent',
        'color': '#1ABC9C',
        'layer': 'frontend',
        'modifiers': ['stateful', 'presentational', 'headless']
    },

    # === State/Logic Glyphs ===
    'STO': {
        'name': 'Store',
        'description': 'Client state store',
        'agent': 'STO_agent',
        'color': '#2ECC71',
        'layer': 'frontend',
        'cannot_access': ['MDL']
    },
    'FNC': {
        'name': 'Function',
        'description': 'Callable logic',
        'agent': 'FNC_agent',
        'color': '#F1C40F',
        'layer': 'shared',
        'qualifiers': ['auth', 'ui', 'domain', 'validation', 'email']
    },
    'EVT': {
        'name': 'Event',
        'description': 'Event emitter',
        'agent': 'EVT_agent',
        'color': '#E67E22',
        'layer': 'shared',
        'cannot_cross': ['API']
    },

    # === Backend Glyphs ===
    'API': {
        'name': 'API',
        'description': 'HTTP endpoint',
        'agent': 'API_agent',
        'color': '#E74C3C',
        'layer': 'backend',
        'requires_error_paths': True
    },
    'MDL': {
        'name': 'Model',
        'description': 'Data model with API schemas and database operations',
        'agent': 'MDL_agent',
        'color': '#795548',
        'layer': 'backend',
        'qualifiers': ['user', 'chat', 'search', 'analytics']
    },

    # === Orchestrator Glyphs (Internal) ===
    'ORC': {
        'name': 'Orchestrator',
        'description': 'Core orchestrator node',
        'agent': None,
        'color': '#2C3E50',
        'layer': 'internal'
    },
    'PRS': {
        'name': 'Parser',
        'description': 'Chain/intent parser',
        'agent': None,
        'color': '#34495E',
        'layer': 'internal'
    },
    'VAL': {
        'name': 'Validator',
        'description': 'Validation engine',
        'agent': None,
        'color': '#7F8C8D',
        'layer': 'internal'
    },
    'SPW': {
        'name': 'Spawner',
        'description': 'Agent spawner',
        'agent': None,
        'color': '#95A5A6',
        'layer': 'internal'
    },
    'TST': {
        'name': 'Tester',
        'description': 'Test runner',
        'agent': None,
        'color': '#BDC3C7',
        'layer': 'internal'
    },
    'GRF': {
        'name': 'Graph',
        'description': 'Knowledge graph node',
        'agent': None,
        'color': '#1A1A2E',
        'layer': 'internal'
    },
    'CTX': {
        'name': 'Context',
        'description': 'Context budget manager for small model optimization',
        'agent': None,
        'color': '#00BCD4',
        'layer': 'internal',
        'qualifiers': ['budget', 'projection', 'tier'],
        'doc': 'Manages context window budgets for 30B parameter models (~60K tokens)'
    },
    'MIC': {
        'name': 'Micro',
        'description': 'Micro-agent executor for single-glyph operations',
        'agent': None,
        'color': '#FF5722',
        'layer': 'internal',
        'qualifiers': ['executor', 'task', 'result'],
        'doc': 'Executes one glyph at a time with minimal context overhead'
    },
}

EDGE_TYPES = {
    '=>': {
        'name': 'structural',
        'description': 'Compile-time data dependency',
        'cycles_allowed': False,
        'visual': 'solid'
    },
    '~>': {
        'name': 'reactive',
        'description': 'Runtime feedback loop',
        'cycles_allowed': True,
        'visual': 'dashed'
    },
    '!>': {
        'name': 'side-effect',
        'description': 'External effect (non-blocking)',
        'cycles_allowed': True,
        'visual': 'dotted'
    },
    '->': {
        'name': 'control',
        'description': 'Branch/conditional flow',
        'cycles_allowed': False,
        'visual': 'arrow-branch'
    },
    '::': {
        'name': 'internal',
        'description': 'Orchestrator dependency',
        'cycles_allowed': False,
        'visual': 'thick'
    },
    '@': {
        'name': 'containment',
        'description': 'View contains components',
        'cycles_allowed': False,
        'visual': 'none'
    }
}

BOUNDARY_RULES = [
    # V: is structural only - no data flow operators allowed
    {'from': 'V', 'operator': '=>', 'allowed': False, 'reason': 'Views cannot participate in data flow'},
    {'from': 'V', 'operator': '~>', 'allowed': False, 'reason': 'Views cannot have reactive edges'},
    {'from': 'V', 'operator': '->', 'allowed': False, 'reason': 'Views cannot have control flow'},
    {'from': 'V', 'operator': '!>', 'allowed': False, 'reason': 'Views cannot trigger side-effects'},

    # CMP/STO/EVT boundaries
    {'from': 'CMP', 'to': 'MDL', 'allowed': False, 'reason': 'Components cannot directly access models'},
    {'from': 'STO', 'to': 'MDL', 'allowed': False, 'reason': 'Stores must go through API'},
    {'from': 'EVT', 'to': 'API', 'allowed': False, 'reason': 'Events cannot cross trust boundaries directly'},
    {'from': 'MDL', 'to': 'CMP', 'allowed': False, 'reason': 'Backend cannot reference frontend'},
    {'from': 'FNC:ui', 'to': 'MDL', 'allowed': False, 'reason': 'UI functions cannot touch data layer'},
]


def get_glyph(prefix: str) -> dict | None:
    """Get glyph definition by prefix."""
    return GLYPH_LEGEND.get(prefix)


def get_edge_type(operator: str) -> dict | None:
    """Get edge type definition by operator."""
    return EDGE_TYPES.get(operator)


def is_valid_glyph(prefix: str) -> bool:
    """Check if prefix is a valid glyph."""
    return prefix in GLYPH_LEGEND


def is_valid_operator(operator: str) -> bool:
    """Check if operator is valid."""
    return operator in EDGE_TYPES


def get_agent_glyphs() -> list[str]:
    """Get all glyphs that have associated agents."""
    return [k for k, v in GLYPH_LEGEND.items() if v.get('agent') is not None]


def get_meta_glyphs() -> list[str]:
    """Get all meta glyphs (no code generation)."""
    return [k for k, v in GLYPH_LEGEND.items() if v.get('layer') == 'meta']
