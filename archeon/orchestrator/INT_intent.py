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
