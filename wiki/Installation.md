# Installation

## System Requirements

- **Python**: 3.10 or higher
- **OS**: macOS, Linux, or Windows (WSL recommended)
- **Git**: For cloning the repository

## Install from Source (Recommended)

The recommended way to install Archeon is directly from the source repository in editable mode:

```bash
# Clone the repository
git clone https://github.com/danaia/Archeon.git
cd Archeon

# Install in editable mode globally
pip install -e .

# Verify installation
arc --version
```

### Why Editable Mode?

Installing with `-e` (editable mode) allows you to:
- Pull updates without reinstalling: `git pull`
- Modify templates and have changes take effect immediately
- Contribute back to the project easily

## Install from PyPI (Coming Soon)

Once published, you'll be able to install via:

```bash
pip install archeon
```

## Verify Installation

Check that the CLI is available:

```bash
arc --version
# or
archeon --version
```

You should see output like:
```
archeon version 0.1.0
```

## Update Archeon

If installed from source in editable mode:

```bash
cd Archeon
git pull origin main
```

No reinstallation needed! Changes take effect immediately.

## Uninstall

```bash
pip uninstall archeon
```

## Troubleshooting

### Command Not Found

If `arc` command is not found after installation:

1. **Check pip installation location:**
   ```bash
   pip show archeon
   ```

2. **Ensure pip's bin directory is in PATH:**
   ```bash
   # On macOS/Linux
   echo $PATH
   
   # Add to ~/.zshrc or ~/.bashrc if needed:
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. **Use python -m instead:**
   ```bash
   python -m archeon --version
   ```

### Permission Errors

If you get permission errors during installation:

```bash
# Use --user flag
pip install --user -e .

# Or use a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Python Version Issues

Archeon requires Python 3.10+. Check your version:

```bash
python --version
```

If you have an older version:

**macOS (using Homebrew):**
```bash
brew install python@3.11
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

## Dependencies

Archeon automatically installs these dependencies:

- **typer** - CLI framework
- **pydantic** - Data validation
- **pytest** - Testing framework
- **rich** - Terminal formatting

## Development Install

For contributing or development:

```bash
git clone https://github.com/danaia/Archeon.git
cd Archeon

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check archeon/
```

## Next Steps

- 📖 [Quick Start](Quick-Start) - Create your first project
- 🔤 [Glyph Reference](Glyph-Reference) - Learn the glyph system
- 💻 [CLI Commands](CLI-Commands) - Explore available commands
