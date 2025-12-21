"""
INT_intent.py - Archeon Intent Parser

Converts natural language descriptions into proposed glyph chains.
Parses requirements docs, markdown, and task descriptions.

IMPORTANT: This is PROPOSAL ONLY - never auto-adds to graph.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class IntentConfidence(Enum):
    """Confidence level for parsed intent."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ProposedChain:
    """A proposed chain from intent parsing."""
    chain: str
    confidence: IntentConfidence
    source_text: str
    reasoning: list[str] = field(default_factory=list)
    suggested_errors: list[str] = field(default_factory=list)


@dataclass
class IntentResult:
    """Result of intent parsing."""
    proposals: list[ProposedChain] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    source: str = ""
    
    def to_dict(self) -> dict:
        return {
            'proposals': [
                {
                    'chain': p.chain,
                    'confidence': p.confidence.value,
                    'source_text': p.source_text[:100],
                    'reasoning': p.reasoning,
                    'suggested_errors': p.suggested_errors
                }
                for p in self.proposals
            ],
            'warnings': self.warnings,
            'source': self.source
        }


# Intent keyword mappings
NEED_KEYWORDS = {
    'login': 'NED:login',
    'log in': 'NED:login',
    'sign in': 'NED:login',
    'authenticate': 'NED:login',
    'register': 'NED:register',
    'sign up': 'NED:register',
    'signup': 'NED:register',
    'create account': 'NED:register',
    'logout': 'NED:logout',
    'log out': 'NED:logout',
    'sign out': 'NED:logout',
    'view profile': 'NED:viewProfile',
    'see profile': 'NED:viewProfile',
    'edit profile': 'NED:editProfile',
    'update profile': 'NED:editProfile',
    'search': 'NED:search',
    'find': 'NED:search',
    'browse': 'NED:browse',
    'explore': 'NED:browse',
    'purchase': 'NED:purchase',
    'buy': 'NED:purchase',
    'checkout': 'NED:checkout',
    'pay': 'NED:payment',
    'upload': 'NED:upload',
    'download': 'NED:download',
    'share': 'NED:share',
    'send': 'NED:send',
    'message': 'NED:message',
    'chat': 'NED:chat',
    'comment': 'NED:comment',
    'post': 'NED:post',
    'create': 'NED:create',
    'delete': 'NED:delete',
    'remove': 'NED:delete',
    'update': 'NED:update',
    'reset password': 'NED:resetPassword',
    'forgot password': 'NED:resetPassword',
    'change password': 'NED:changePassword',
    'settings': 'NED:settings',
    'configure': 'NED:configure',
    'dashboard': 'NED:dashboard',
    'analytics': 'NED:analytics',
    'report': 'NED:report',
    'export': 'NED:export',
    'import': 'NED:import',
    'notification': 'NED:notification',
    'subscribe': 'NED:subscribe',
    'unsubscribe': 'NED:unsubscribe',
}

TASK_KEYWORDS = {
    'click': 'TSK:click',
    'tap': 'TSK:tap',
    'submit': 'TSK:submit',
    'enter': 'TSK:enter',
    'type': 'TSK:type',
    'fill': 'TSK:fill',
    'select': 'TSK:select',
    'choose': 'TSK:choose',
    'drag': 'TSK:drag',
    'drop': 'TSK:drop',
    'scroll': 'TSK:scroll',
    'swipe': 'TSK:swipe',
    'press': 'TSK:press',
    'toggle': 'TSK:toggle',
    'expand': 'TSK:expand',
    'collapse': 'TSK:collapse',
    'open': 'TSK:open',
    'close': 'TSK:close',
    'confirm': 'TSK:confirm',
    'cancel': 'TSK:cancel',
    'dismiss': 'TSK:dismiss',
    'accept': 'TSK:accept',
    'reject': 'TSK:reject',
    'approve': 'TSK:approve',
    'deny': 'TSK:deny',
}

OUTPUT_KEYWORDS = {
    'show': 'OUT:show',
    'display': 'OUT:display',
    'render': 'OUT:render',
    'redirect': 'OUT:redirect',
    'navigate': 'OUT:navigate',
    'toast': 'OUT:toast',
    'notification': 'OUT:notification',
    'alert': 'OUT:alert',
    'message': 'OUT:message',
    'error': 'OUT:error',
    'success': 'OUT:success',
    'loading': 'OUT:loading',
    'spinner': 'OUT:spinner',
    'modal': 'OUT:modal',
    'popup': 'OUT:popup',
    'download': 'OUT:download',
    'refresh': 'OUT:refresh',
    'update': 'OUT:update',
}

# Component patterns
COMPONENT_PATTERNS = [
    (r'\b(\w+)\s*form\b', 'CMP:{0}Form'),
    (r'\b(\w+)\s*button\b', 'CMP:{0}Button'),
    (r'\b(\w+)\s*modal\b', 'CMP:{0}Modal'),
    (r'\b(\w+)\s*dialog\b', 'CMP:{0}Dialog'),
    (r'\b(\w+)\s*card\b', 'CMP:{0}Card'),
    (r'\b(\w+)\s*list\b', 'CMP:{0}List'),
    (r'\b(\w+)\s*table\b', 'CMP:{0}Table'),
    (r'\b(\w+)\s*grid\b', 'CMP:{0}Grid'),
    (r'\b(\w+)\s*panel\b', 'CMP:{0}Panel'),
    (r'\b(\w+)\s*page\b', 'V:{0}Page'),
    (r'\b(\w+)\s*view\b', 'V:{0}View'),
    (r'\b(\w+)\s*screen\b', 'V:{0}Screen'),
]

# API patterns
API_PATTERNS = [
    (r'post\s+(?:to\s+)?(/?\w+(?:/\w+)*)', 'API:POST{0}'),
    (r'get\s+(?:from\s+)?(/?\w+(?:/\w+)*)', 'API:GET{0}'),
    (r'update\s+(?:via\s+)?(/?\w+(?:/\w+)*)', 'API:PUT{0}'),
    (r'delete\s+(?:from\s+)?(/?\w+(?:/\w+)*)', 'API:DELETE{0}'),
    (r'call\s+(/?\w+(?:/\w+)*)\s+api', 'API:POST{0}'),
    (r'api\s+(/?\w+(?:/\w+)*)', 'API:POST{0}'),
    (r'endpoint\s+(/?\w+(?:/\w+)*)', 'API:POST{0}'),
]

# Error suggestions by context
ERROR_SUGGESTIONS = {
    'auth': [
        'ERR:auth.invalidCreds',
        'ERR:auth.tokenExpired',
        'ERR:auth.rateLimited',
        'ERR:auth.forbidden',
    ],
    'login': [
        'ERR:auth.invalidCreds',
        'ERR:auth.accountLocked',
        'ERR:auth.rateLimited',
    ],
    'register': [
        'ERR:validation.emailTaken',
        'ERR:validation.weakPassword',
        'ERR:validation.invalidEmail',
    ],
    'api': [
        'ERR:system.serverError',
        'ERR:system.timeout',
        'ERR:system.rateLimited',
    ],
    'validation': [
        'ERR:validation.malformed',
        'ERR:validation.required',
        'ERR:validation.invalid',
    ],
    'payment': [
        'ERR:payment.declined',
        'ERR:payment.insufficientFunds',
        'ERR:payment.expired',
    ],
    'upload': [
        'ERR:upload.tooLarge',
        'ERR:upload.invalidType',
        'ERR:upload.failed',
    ],
    'database': [
        'ERR:db.notFound',
        'ERR:db.duplicate',
        'ERR:db.connectionError',
    ],
}


class IntentParser:
    """Parse natural language into proposed glyph chains."""
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns."""
        self.component_patterns = [
            (re.compile(pattern, re.IGNORECASE), template)
            for pattern, template in COMPONENT_PATTERNS
        ]
        self.api_patterns = [
            (re.compile(pattern, re.IGNORECASE), template)
            for pattern, template in API_PATTERNS
        ]
    
    def parse_intent(self, text: str) -> IntentResult:
        """
        Parse natural language text into proposed chains.
        
        Args:
            text: Natural language description
            
        Returns:
            IntentResult with proposals (NEVER auto-adds)
        """
        result = IntentResult(source=text[:200])
        text_lower = text.lower()
        
        # Extract components
        glyphs = []
        reasoning = []
        
        # Find NEEDs
        for keyword, glyph in NEED_KEYWORDS.items():
            if keyword in text_lower:
                glyphs.append(('NED', glyph))
                reasoning.append(f"Found need keyword: '{keyword}'")
                break
        
        # Find TASKs
        for keyword, glyph in TASK_KEYWORDS.items():
            if keyword in text_lower:
                glyphs.append(('TSK', glyph))
                reasoning.append(f"Found task keyword: '{keyword}'")
                break
        
        # Find Components
        for pattern, template in self.component_patterns:
            match = pattern.search(text)
            if match:
                name = match.group(1).capitalize()
                glyph = template.format(name)
                prefix = glyph.split(':')[0]
                glyphs.append((prefix, glyph))
                reasoning.append(f"Found component pattern: '{match.group(0)}'")
        
        # Find APIs
        for pattern, template in self.api_patterns:
            match = pattern.search(text_lower)
            if match:
                route = match.group(1)
                if not route.startswith('/'):
                    route = '/' + route
                glyph = template.format(route)
                glyphs.append(('API', glyph))
                reasoning.append(f"Found API pattern: '{match.group(0)}'")
        
        # Find OUTPUTs
        for keyword, glyph in OUTPUT_KEYWORDS.items():
            if keyword in text_lower:
                glyphs.append(('OUT', glyph))
                reasoning.append(f"Found output keyword: '{keyword}'")
                break
        
        # Build chain if we have enough glyphs
        if glyphs:
            # Order by typical flow: NED -> TSK -> V/CMP -> API -> OUT
            order = {'NED': 0, 'TSK': 1, 'V': 2, 'CMP': 3, 'STO': 4, 'FNC': 5, 'API': 6, 'MDL': 7, 'OUT': 8}
            sorted_glyphs = sorted(glyphs, key=lambda g: order.get(g[0], 5))
            
            # Deduplicate
            seen = set()
            unique_glyphs = []
            for prefix, glyph in sorted_glyphs:
                if glyph not in seen:
                    seen.add(glyph)
                    unique_glyphs.append(glyph)
            
            # Ensure we have OUT
            if not any(g.startswith('OUT:') for g in unique_glyphs):
                unique_glyphs.append('OUT:result')
                reasoning.append("Added default OUT:result (all chains need output)")
            
            # Build chain string
            chain = ' => '.join(unique_glyphs)
            
            # Determine confidence
            confidence = IntentConfidence.HIGH if len(unique_glyphs) >= 3 else (
                IntentConfidence.MEDIUM if len(unique_glyphs) >= 2 else IntentConfidence.LOW
            )
            
            # Suggest errors
            errors = self._suggest_errors(unique_glyphs, text_lower)
            
            result.proposals.append(ProposedChain(
                chain=chain,
                confidence=confidence,
                source_text=text,
                reasoning=reasoning,
                suggested_errors=errors
            ))
        else:
            result.warnings.append("Could not extract intent from text")
        
        return result
    
    def parse_markdown(self, filepath: str) -> IntentResult:
        """
        Parse markdown file for chain definitions and requirements.
        
        Args:
            filepath: Path to markdown file
            
        Returns:
            IntentResult with proposals from document
        """
        result = IntentResult(source=f"file:{filepath}")
        
        try:
            content = Path(filepath).read_text()
        except (OSError, IOError) as e:
            result.warnings.append(f"Could not read file: {e}")
            return result
        
        # Look for existing chain syntax in code blocks
        chain_pattern = re.compile(
            r'```(?:archeon|chain|glyph)?\s*\n(.*?)\n```',
            re.MULTILINE | re.DOTALL
        )
        
        for match in chain_pattern.finditer(content):
            chain_text = match.group(1).strip()
            for line in chain_text.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Validate it looks like a chain
                    if '=>' in line or '->' in line:
                        result.proposals.append(ProposedChain(
                            chain=line,
                            confidence=IntentConfidence.HIGH,
                            source_text=line,
                            reasoning=["Found chain in code block"]
                        ))
        
        # Parse user stories and requirements
        story_patterns = [
            r'as a (\w+),?\s+i want to (.+?)(?:,?\s+so that (.+?))?(?:\.|$)',
            r'user (?:wants?|needs?) to (.+?)(?:\.|$)',
            r'(?:when|if) (?:a |the )?user (.+?),?\s+(?:then |they should )(.+?)(?:\.|$)',
        ]
        
        for pattern in story_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                story_text = match.group(0)
                intent_result = self.parse_intent(story_text)
                for proposal in intent_result.proposals:
                    proposal.reasoning.insert(0, f"Extracted from user story")
                    result.proposals.append(proposal)
        
        # Parse bullet lists that look like requirements
        bullet_pattern = re.compile(r'^[\s-]*[-*]\s+(.+)$', re.MULTILINE)
        for match in bullet_pattern.finditer(content):
            bullet = match.group(1)
            # Only parse if it looks like a requirement
            if any(kw in bullet.lower() for kw in ['user', 'should', 'must', 'can', 'will', 'allow']):
                intent_result = self.parse_intent(bullet)
                for proposal in intent_result.proposals:
                    proposal.confidence = IntentConfidence.LOW  # Lower confidence for bullets
                    proposal.reasoning.insert(0, "Extracted from requirement bullet")
                    result.proposals.append(proposal)
        
        return result
    
    def suggest_errors(self, chain: str) -> list[str]:
        """
        Suggest error paths for a chain.
        
        Args:
            chain: Chain string to analyze
            
        Returns:
            List of suggested ERR: glyphs
        """
        chain_lower = chain.lower()
        glyphs = chain.split()
        
        return self._suggest_errors(glyphs, chain_lower)
    
    def _suggest_errors(self, glyphs: list[str], context: str) -> list[str]:
        """Suggest errors based on glyphs and context."""
        suggestions = set()
        
        # Check for API glyphs
        has_api = any('API:' in g for g in glyphs if isinstance(g, str))
        if has_api:
            suggestions.update(ERROR_SUGGESTIONS['api'])
        
        # Context-based suggestions
        for keyword, errors in ERROR_SUGGESTIONS.items():
            if keyword in context:
                suggestions.update(errors)
        
        # Auth-specific
        if 'auth' in context or 'login' in context or 'password' in context:
            suggestions.update(ERROR_SUGGESTIONS['auth'])
        
        # Validation
        if 'form' in context or 'input' in context or 'validate' in context:
            suggestions.update(ERROR_SUGGESTIONS['validation'])
        
        return sorted(list(suggestions))
    
    def extend_chain(self, existing_chain: str, modification: str) -> IntentResult:
        """
        Extend or modify an existing chain using natural language.
        
        Args:
            existing_chain: The current chain string (e.g., "NED:login => CMP:LoginForm => OUT:result")
            modification: Natural language description of what to add/change
            
        Returns:
            IntentResult with the extended/modified chain proposal
        """
        result = IntentResult(source=f"extend: {modification}")
        modification_lower = modification.lower()
        
        # Extract version tag if present (e.g., "@v1")
        version_tag = ""
        chain_to_parse = existing_chain.strip()
        if chain_to_parse.startswith('@'):
            # Extract version tag
            parts = chain_to_parse.split(' ', 1)
            if len(parts) > 1:
                version_tag = parts[0]  # e.g., "@v1"
                chain_to_parse = parts[1]  # Rest of the chain
        
        # Parse the existing chain to get current glyphs (without version tag)
        existing_glyphs = []
        for part in chain_to_parse.replace(' => ', '|').replace(' -> ', '|').replace(' ~> ', '|').split('|'):
            part = part.strip()
            if part and ':' in part:
                prefix = part.split(':')[0]
                # Skip if it looks like a version tag that slipped through
                if prefix.startswith('@') or prefix in ('v1', 'v2', 'v3'):
                    continue
                existing_glyphs.append((prefix, part))
        
        # Show the clean chain in reasoning
        clean_chain = ' => '.join(g[1] for g in existing_glyphs)
        reasoning = [f"Starting from: {clean_chain}"]
        
        # Parse the modification for new glyphs
        new_glyphs = []
        
        # Check for store/state keywords
        if any(kw in modification_lower for kw in ['store', 'state', 'persist', 'save state', 'auth state', 'user state']):
            # Infer store name from existing chain
            store_name = 'Auth'  # default
            for prefix, glyph in existing_glyphs:
                if prefix == 'NED':
                    need_name = glyph.split(':')[1] if ':' in glyph else ''
                    store_name = need_name.capitalize() if need_name else 'Auth'
                    break
            new_glyphs.append(('STO', f'STO:{store_name}'))
            reasoning.append(f"Adding store: STO:{store_name}")
        
        # Check for API keywords
        if any(kw in modification_lower for kw in ['api', 'endpoint', 'server', 'backend', 'call', 'request', 'post', 'get']):
            # Infer API route from existing chain
            route = '/api'
            method = 'POST'
            for prefix, glyph in existing_glyphs:
                if prefix == 'NED':
                    need_name = glyph.split(':')[1] if ':' in glyph else ''
                    route = f'/{need_name}' if need_name else '/api'
                    break
            
            # Check for specific HTTP method
            if 'get' in modification_lower:
                method = 'GET'
            elif 'put' in modification_lower:
                method = 'PUT'
            elif 'delete' in modification_lower:
                method = 'DELETE'
            
            new_glyphs.append(('API', f'API:{method}{route}'))
            reasoning.append(f"Adding API endpoint: API:{method}{route}")
        
        # Check for database/model keywords
        if any(kw in modification_lower for kw in ['database', 'model', 'db', 'save', 'persist', 'mongo', 'sql', 'table']):
            # Infer model name from existing chain
            model_name = 'user'
            for prefix, glyph in existing_glyphs:
                if prefix == 'NED':
                    need_name = glyph.split(':')[1] if ':' in glyph else ''
                    if need_name in ['login', 'register', 'profile', 'auth']:
                        model_name = 'user'
                    else:
                        model_name = need_name if need_name else 'item'
                    break
            new_glyphs.append(('MDL', f'MDL:{model_name}'))
            reasoning.append(f"Adding model: MDL:{model_name}")
        
        # Check for function keywords
        if any(kw in modification_lower for kw in ['function', 'helper', 'util', 'validate', 'transform', 'hash']):
            fn_name = 'helper'
            if 'validate' in modification_lower:
                fn_name = 'validate'
            elif 'hash' in modification_lower:
                fn_name = 'hashPassword'
            elif 'token' in modification_lower:
                fn_name = 'generateToken'
            new_glyphs.append(('FNC', f'FNC:{fn_name}'))
            reasoning.append(f"Adding function: FNC:{fn_name}")
        
        # Check for event keywords
        if any(kw in modification_lower for kw in ['event', 'emit', 'publish', 'subscribe', 'notify', 'webhook']):
            event_name = 'notify'
            new_glyphs.append(('EVT', f'EVT:{event_name}'))
            reasoning.append(f"Adding event: EVT:{event_name}")
        
        # Check for output/redirect keywords
        if any(kw in modification_lower for kw in ['redirect', 'navigate', 'goto', 'dashboard', 'home', 'success']):
            dest = 'dashboard'
            if 'home' in modification_lower:
                dest = 'home'
            elif 'profile' in modification_lower:
                dest = 'profile'
            new_glyphs.append(('OUT', f"OUT:redirect('/{dest}')"))
            reasoning.append(f"Updating output: redirect to /{dest}")
        
        if not new_glyphs:
            result.warnings.append(f"Could not understand modification: '{modification}'")
            result.warnings.append("Try: 'add a store', 'add API endpoint', 'add database model', 'redirect to dashboard'")
            return result
        
        # Merge existing and new glyphs
        all_glyphs = list(existing_glyphs)
        
        # Remove default OUT:result if we're adding a better output
        if any(g[0] == 'OUT' for g in new_glyphs):
            all_glyphs = [(p, g) for p, g in all_glyphs if not (p == 'OUT' and g == 'OUT:result')]
        
        # Add new glyphs
        for prefix, glyph in new_glyphs:
            if not any(g == glyph for _, g in all_glyphs):
                all_glyphs.append((prefix, glyph))
        
        # Sort by typical flow order (V is a view/page, similar to CMP)
        order = {'NED': 0, 'TSK': 1, 'V': 2, 'CMP': 3, 'STO': 4, 'FNC': 5, 'API': 6, 'MDL': 7, 'EVT': 8, 'OUT': 9, 'ERR': 10}
        sorted_glyphs = sorted(all_glyphs, key=lambda g: order.get(g[0], 5))
        
        # Build the extended chain (without version tag - will be auto-assigned on add)
        chain = ' => '.join(g[1] for g in sorted_glyphs)
        
        result.proposals.append(ProposedChain(
            chain=chain,
            confidence=IntentConfidence.HIGH,
            source_text=modification,
            reasoning=reasoning,
            suggested_errors=self._suggest_errors([g[1] for g in sorted_glyphs], modification_lower)
        ))
        
        return result


# Module-level convenience functions
_parser = IntentParser()


def parse_intent(text: str) -> IntentResult:
    """Parse natural language into proposed chains."""
    return _parser.parse_intent(text)


def parse_markdown(filepath: str) -> IntentResult:
    """Parse markdown file for chains and requirements."""
    return _parser.parse_markdown(filepath)


def suggest_errors(chain: str) -> list[str]:
    """Suggest error paths for a chain."""
    return _parser.suggest_errors(chain)


def extend_chain(existing_chain: str, modification: str) -> IntentResult:
    """Extend or modify an existing chain using natural language."""
    return _parser.extend_chain(existing_chain, modification)
