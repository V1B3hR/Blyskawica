# Contributing to Nethical Recon

Thank you for your interest in contributing to Nethical Recon! This document provides guidelines for contributing to the project.

## Code Style

This project enforces a consistent coding style using automated formatters and linters.

### Black Formatter

All Python code in this repository is formatted using [Black](https://black.readthedocs.io/), the uncompromising Python code formatter.

**Configuration:**
- Line length: 120 characters
- Target Python version: 3.11+
- Configuration is defined in `pyproject.toml`

**Running Black manually:**

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .

# Show diff of what would be changed
black --check --diff .
```

### Pre-commit Hooks

This project uses pre-commit hooks to automatically enforce code quality standards before commits.

**Setup:**

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install
```

**What runs on commit:**
- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with a newline
- **check-yaml**: Validates YAML files
- **check-json**: Validates JSON files
- **check-toml**: Validates TOML files
- **check-merge-conflict**: Detects merge conflict markers
- **detect-private-key**: Prevents committing private keys
- **black**: Code formatter
- **bandit**: Security vulnerability scanner
- **mypy**: Static type checker

### Other Code Quality Tools

**MyPy** - Type checking:
```bash
mypy .
```

**Bandit** - Security checks:
```bash
bandit -c pyproject.toml -r .
```

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/V1B3hR/nethical-recon.git
cd nethical-recon
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Set up pre-commit hooks:
```bash
pre-commit install
```

## Testing

Run tests using pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nethical_recon

# Run specific test file
pytest tests/test_specific.py
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Make your changes
3. Ensure all code is formatted with Black
4. Run tests and linters
5. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Code Review

All submissions require review before being merged. We look for:
- Adherence to code style guidelines
- Passing tests and linters
- Clear, descriptive commit messages
- Appropriate documentation
- Security best practices

## Questions?

Feel free to open an issue for any questions or concerns!
