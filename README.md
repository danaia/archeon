# Archeon

> Glyph-based architecture notation system for AI-orchestrated software development.

Archeon provides a hyper-compressed, human-readable **intermediate representation (IR)** that serves as both documentation and executable specification.

## Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# Initialize a new project
archeon init

# Parse and add a chain
archeon parse "NED:login => TSK:submit => CMP:LoginForm => API:POST/auth => OUT:redirect"

# Validate the knowledge graph
archeon validate

# Show status
archeon status

# View glyph legend
archeon legend
```

## Glyph Notation

| Prefix | Name | Description |
|--------|------|-------------|
| `NED:` | Need | User intent/motivation |
| `TSK:` | Task | User action |
| `CMP:` | Component | UI component |
| `STO:` | Store | Client state store |
| `API:` | API | HTTP endpoint |
| `MDL:` | Model | Database query/schema |
| `OUT:` | Output | Feedback layer |
| `ERR:` | Error | Failure/exception path |

## Edge Types

| Operator | Type | Cycles |
|----------|------|--------|
| `=>` | Structural | No |
| `~>` | Reactive | Yes |
| `!>` | Side-effect | Yes |
| `->` | Control/Branch | No |

## License

MIT
