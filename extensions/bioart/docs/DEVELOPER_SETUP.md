# Developer Setup Guide

Complete guide for setting up a reproducible development environment for Bioart.

## Quick Start (< 15 minutes)

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (built-in `venv`)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/V1B3hR/bioart.git
   cd bioart
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate (Linux/macOS)
   source .venv/bin/activate
   
   # Activate (Windows)
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Install development dependencies
   pip install -r dev-requirements.txt
   
   # Install pre-commit hooks (optional but recommended)
   pre-commit install
   ```

4. **Verify installation**
   ```bash
   # Run tests
   python -m pytest tests/ -v
   
   # Check coverage
   python -m pytest tests/ --cov=src --cov-report=term-missing
   ```

5. **Try the demos**
   ```bash
   # Run DNA encoding demo
   python examples/dna_demo.py
   
   # Run translator demo
   python examples/translator_demo.py
   
   # Run CLI
   python bioart_cli.py --help
   ```

**Total time: ~10-15 minutes** (depending on download speeds)

## Detailed Setup

### System Requirements

| Component | Requirement |
|-----------|-------------|
| Python | 3.8+ (3.11 recommended) |
| RAM | 2GB minimum, 4GB recommended |
| Disk Space | 500MB for repo + dependencies |
| OS | Linux, macOS, Windows (WSL recommended) |

### Core Dependencies

The project has **no external runtime dependencies** - only Python standard library is required for core functionality.

### Development Dependencies

Development tools (installed via `dev-requirements.txt`):

- **Testing**: pytest, pytest-cov, coverage
- **Code Quality**: black, ruff, mypy
- **Pre-commit**: pre-commit hooks

### Configuration

Bioart uses environment variables for configuration. Create a `.env` file (optional):

```bash
# Logging
BIOART_LOG_LEVEL=INFO
BIOART_LOG_FORMAT=json

# Performance
BIOART_CACHE_TTL=300
BIOART_ENABLE_PROFILING=false

# Cost tracking
BIOART_COST_BUDGET=100.0

# Environment
BIOART_ENV=development
BIOART_DEBUG=false
```

Load with:
```bash
source .env  # or use python-dotenv
```

## Development Workflow

### 1. Code Quality Checks

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/ --fix

# Type check with mypy
mypy src/

# Or use pre-commit to run all checks
pre-commit run --all-files
```

### 2. Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_config.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View HTML coverage report
open htmlcov/index.html
```

### 3. Using Make Commands

```bash
# Run demo
make demo

# Run interpreter
make interpreter

# Run tests (if make test target exists)
make test

# Run full simulation
make all
```

### 4. Using the Logger

```python
from src.core import get_logger, correlation_context

logger = get_logger("my_module")

# With correlation tracking
with correlation_context(job_id="job-123", step_id="encode"):
    logger.info("Processing data", bytes_processed=1024)
```

### 5. Using Configuration

```python
from src.core import get_config, BioartConfig

# Get global config
config = get_config()
print(f"Cache TTL: {config.performance.cache_ttl_seconds}")

# Custom config
custom_config = BioartConfig()
custom_config.vm.memory_size = 512
custom_config.validate()
```

## IDE Setup

### VS Code

Recommended extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)

Settings (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "editor.formatOnSave": true
}
```

### PyCharm

1. Open the project
2. Configure Python interpreter: Settings → Project → Python Interpreter → Select `.venv`
3. Enable pytest: Settings → Tools → Python Integrated Tools → Testing → pytest
4. Install File Watchers plugin for auto-formatting

## Troubleshooting

### Import errors

```bash
# Ensure you're in the project root and venv is activated
cd /path/to/bioart
source .venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Pre-commit hook failures

```bash
# Update hooks
pre-commit autoupdate

# Skip hooks temporarily
git commit --no-verify
```

### Test failures

```bash
# Clear pytest cache
rm -rf .pytest_cache

# Reinstall dependencies
pip install --force-reinstall -r dev-requirements.txt

# Run specific failing test with verbose output
pytest tests/test_name.py::test_function -vv -s
```

### Coverage issues

```bash
# Clear coverage data
coverage erase

# Run with detailed output
pytest tests/ --cov=src --cov-report=term-missing -v
```

## CI/CD Integration

The project uses GitHub Actions for CI/CD. See `.github/workflows/ci.yml` for details.

Local CI simulation:
```bash
# Lint checks
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Tests with coverage
pytest tests/ --cov=src --cov-report=xml --cov-report=html -v
```

## Performance Profiling

Enable profiling in configuration:
```python
config = get_config()
config.performance.enable_profiling = True
```

Or via environment:
```bash
export BIOART_ENABLE_PROFILING=true
```

## Contribution Guidelines

1. **Create a branch**: `git checkout -b feature/your-feature`
2. **Make changes**: Follow code style (black + ruff)
3. **Add tests**: Coverage for new code
4. **Run checks**: `pre-commit run --all-files`
5. **Commit**: Use clear commit messages
6. **Push**: `git push origin feature/your-feature`
7. **PR**: Create pull request with description

## Getting Help

- **Documentation**: See `docs/` directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## Next Steps

After setup:
1. Read `unitymap.md` for the project roadmap
2. Check `CONTRIBUTING.md` for contribution guidelines
3. Explore `docs/` for technical documentation
4. Try running the examples in `examples/`

## Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] Tests pass (>= 95% should pass)
- [ ] Pre-commit hooks working
- [ ] Can run demos successfully
- [ ] IDE configured properly
- [ ] Configuration loads correctly
- [ ] Setup completed in < 15 minutes

**Setup complete! You're ready to develop with Bioart.** 🧬
