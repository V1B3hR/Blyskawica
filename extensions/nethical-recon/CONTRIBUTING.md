# Contributing to Nethical Recon

Thank you for your interest in contributing to Nethical Recon! 🎉

We welcome contributions from security professionals, developers, researchers, and enthusiasts. This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Contributor License Agreement](#contributor-license-agreement)
- [Recognition](#recognition)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

### Our Standards

✅ **Be respectful and inclusive** of all contributors
✅ **Accept constructive criticism** gracefully
✅ **Focus on what's best** for the community
✅ **Show empathy** towards other community members
✅ **Use welcoming and inclusive language**

❌ **Harassment, discrimination, or unprofessional conduct will NOT be tolerated.**

If you witness or experience unacceptable behavior, please report it to conduct@nethical-recon.example.

## How to Contribute

We appreciate various types of contributions:

### 🐛 Bug Reports

**Found a bug?** Help us improve by reporting it!

1. **Search** [existing issues](https://github.com/V1B3hR/nethical-recon/issues) first to avoid duplicates
2. **Use** the bug report template when creating a new issue
3. **Provide** detailed information:
   - Version of Nethical Recon
   - Operating system and version
   - Steps to reproduce the bug
   - Expected vs. actual behavior
   - Relevant logs, screenshots, or error messages
   - Configuration details (sanitized of sensitive data)

### ✨ Feature Requests

**Have an idea for a new feature?**

1. **Open** a [GitHub Discussion](https://github.com/V1B3hR/nethical-recon/discussions) first for major features
2. **Explain** the use case and benefits
3. **Consider** backward compatibility and impact
4. **Be open** to feedback and alternative approaches

For minor features, you can open an issue directly using the feature request template.

### 🔧 Code Contributions

**Ready to contribute code?**

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature-name`
3. **Make** your changes following our coding standards
4. **Write** tests for new code (see [Testing](#testing))
5. **Ensure** all tests pass and code is formatted
6. **Commit** with clear, descriptive messages
7. **Submit** a Pull Request

### 📚 Documentation

Documentation improvements are always welcome!

- Fix typos, grammatical errors, or unclear explanations
- Add examples and tutorials
- Update outdated information
- Improve API documentation
- Translate documentation (future)

### 🔒 Security Contributions

**Found a security vulnerability?**

⚠️ **DO NOT** open a public issue!

Follow our [Security Policy](SECURITY.md) for responsible disclosure:

- Report via GitHub Security Advisories (preferred)
- Or email security@nethical-recon.example
- Use PGP encryption for sensitive information

For security-related code improvements that don't involve vulnerabilities, submit a PR as usual but mark it as security-related.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/V1B3hR/nethical-recon.git
cd nethical-recon

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Install development dependencies
pip install -r requirements-dev.txt
# Or if using pyproject.toml:
pip install -e ".[dev]"

# 6. Install pre-commit hooks
pre-commit install

# 7. Verify installation
python -m pytest --version
black --version
mypy --version
```

### Environment Configuration

Copy `.env.example` to `.env` and configure as needed:

```bash
cp .env.example .env
# Edit .env with your settings
```

## Coding Standards

We enforce strict coding standards to maintain code quality and consistency.

### Python Style Guide

- **PEP 8** compliance (enforced by Black)
- **Type hints** for all functions and methods (enforced by mypy)
- **Docstrings** for all public modules, classes, and functions (Google style)
- **Line length**: 120 characters (configured in pyproject.toml)

### Code Formatting

**Black** is our code formatter:

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .

# Show diff of what would be changed
black --check --diff .
```

Black runs automatically via pre-commit hooks.

### Type Checking

**mypy** enforces static type checking:

```bash
# Type check all code
mypy .

# Type check specific file
mypy src/nethical_recon/module.py
```

### Security Scanning

**Bandit** scans for security vulnerabilities:

```bash
# Scan all code
bandit -c pyproject.toml -r .

# Scan specific directory
bandit -r src/
```

### Pre-commit Hooks

Pre-commit hooks automatically run on `git commit`:

- **trailing-whitespace**: Removes trailing whitespace
- **end-of-file-fixer**: Ensures files end with newline
- **check-yaml**: Validates YAML files
- **check-json**: Validates JSON files
- **check-toml**: Validates TOML files
- **check-merge-conflict**: Detects merge conflict markers
- **detect-private-key**: Prevents committing private keys
- **black**: Code formatter
- **bandit**: Security vulnerability scanner
- **mypy**: Static type checker

To run manually:

```bash
# Run on all files
pre-commit run --all-files

# Run on staged files
pre-commit run
```

### Testing

**pytest** is our testing framework:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=nethical_recon --cov-report=html

# Run specific test file
pytest tests/test_specific.py

# Run specific test function
pytest tests/test_specific.py::test_function_name

# Run with verbose output
pytest -v

# Run in parallel (if pytest-xdist installed)
pytest -n auto
```

**Test Coverage Requirements:**

- New features must include tests
- Aim for >80% code coverage
- Critical paths should have 100% coverage
- Tests should be meaningful, not just for coverage

**Test Structure:**

```python
"""
Test module for [feature name].
"""
import pytest
from nethical_recon import module


class TestFeatureName:
    """Test suite for [feature]."""

    def test_basic_functionality(self):
        """Test basic functionality."""
        # Arrange
        expected = "result"

        # Act
        actual = module.function()

        # Assert
        assert actual == expected

    def test_edge_case(self):
        """Test edge case handling."""
        with pytest.raises(ValueError):
            module.function(invalid_input)
```

## Pull Request Process

### Before Submitting

**Complete this checklist:**

- [ ] Code follows project style (Black formatted)
- [ ] All tests pass (`pytest`)
- [ ] New features have tests (coverage >80%)
- [ ] Type hints added (mypy passes)
- [ ] Security scan passes (bandit)
- [ ] Documentation updated (if applicable)
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts with main branch
- [ ] Pre-commit hooks pass
- [ ] CHANGELOG.md updated (for significant changes)

### PR Template

Use the provided PR template and include:

1. **Description**: What does this PR do?
2. **Motivation**: Why is this change needed?
3. **Related Issues**: Link to related issues (Fixes #123)
4. **Type of Change**: Bug fix, new feature, documentation, etc.
5. **Testing**: How was this tested?
6. **Breaking Changes**: Any breaking changes?
7. **Checklist**: Complete the checklist

### Review Process

1. **Automated Checks**: CI/CD pipeline will run automatically
2. **Code Review**: Maintainers will review your PR within 7 days
3. **Feedback**: Address any requested changes
4. **Approval**: At least one maintainer approval required
5. **Merge**: Maintainer will merge once approved

### Commit Messages

Follow these guidelines:

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or auxiliary tool changes
- `security`: Security improvements

**Examples:**
```
feat(cameras): add subdomain enumeration camera

Implements subdomain enumeration using multiple DNS techniques.
Includes support for wildcard detection and rate limiting.

Closes #123
```

```
fix(api): handle timeout errors in scan endpoints

Previously, long-running scans would timeout without proper error handling.
This adds retry logic and better error messages.

Fixes #456
```

## Contributor License Agreement (CLA)

By submitting a contribution to this project, you agree to the following:

### Your Agreement

✅ **Original Work**: Your contribution is your original work or you have rights to contribute it
✅ **License Grant**: You grant a perpetual, worldwide, non-exclusive, royalty-free license to your contribution under the Apache 2.0 license
✅ **Patent Grant**: You grant a patent license for any patents you own that cover your contribution
✅ **No Obligation**: You understand your contribution may be used, modified, or not used at all
✅ **Relicensing**: You understand the project may be relicensed in the future (with community notice)

### No Separate Signature Required

**Implicit CLA via Pull Request submission** - No separate CLA signature is required. By submitting a PR, you agree to these terms.

### Corporate Contributions

If you are contributing on behalf of your employer, ensure you have the right to contribute under your employment agreement.

## Recognition

We value and recognize all contributors!

### CONTRIBUTORS.md

All contributors are listed in [CONTRIBUTORS.md](CONTRIBUTORS.md) (to be created).

### Release Notes

Significant contributions are acknowledged in release notes and CHANGELOG.md.

### GitHub Profile

Your contributions will appear on your GitHub profile.

### Maintainer Status

Active contributors may be invited to become project maintainers with additional privileges:

🌟 **Maintainer Benefits:**
- Commit access to the repository
- Participation in project decisions
- Ability to review and merge PRs
- Recognition as a core team member

**Path to Maintainership:**
1. Consistent quality contributions over time
2. Demonstrated understanding of project goals
3. Active participation in discussions and reviews
4. Community support and collaboration

## Development Workflow

### Branching Strategy

- **main**: Stable production-ready code
- **develop**: Integration branch for features (if used)
- **feature/**: Feature branches (e.g., `feature/add-camera`)
- **fix/**: Bug fix branches (e.g., `fix/scanner-timeout`)
- **docs/**: Documentation branches
- **security/**: Security-related branches

### Release Process

1. Feature freeze
2. Release candidate (RC) testing
3. Version bump
4. CHANGELOG.md update
5. Tag release
6. Deploy to production
7. Announcement

## Getting Help

### Questions?

- **GitHub Discussions**: For general questions and discussions
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Check docs/ directory
- **Examples**: Check examples/ directory

### Stuck?

Don't hesitate to ask for help!

- Comment on the issue or PR
- Ask in GitHub Discussions
- Reach out to maintainers

We're here to help you succeed with your contribution!

## Style and Best Practices

### Code Quality

- **DRY** (Don't Repeat Yourself): Avoid code duplication
- **KISS** (Keep It Simple, Stupid): Prefer simple solutions
- **YAGNI** (You Aren't Gonna Need It): Don't add unnecessary features
- **SOLID** principles for object-oriented code
- **Fail fast**: Validate inputs early
- **Defensive programming**: Handle errors gracefully

### Security Best Practices

- **Never hardcode secrets**: Use environment variables
- **Validate all inputs**: Sanitize user input
- **Use parameterized queries**: Prevent SQL injection
- **Escape output**: Prevent XSS
- **Least privilege**: Request minimum necessary permissions
- **Security by default**: Secure defaults, not opt-in security

### Performance Considerations

- Profile before optimizing
- Use appropriate data structures
- Consider memory usage for large datasets
- Add caching where beneficial
- Use async/await for I/O-bound operations

## Additional Resources

- [Apache 2.0 License](LICENSE)
- [Security Policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Changelog](docs/CHANGELOG.md)
- [Documentation](docs/)

## Thank You! 🙏

Every contribution, no matter how small, makes Nethical Recon better. Thank you for being part of our community!

---

**Last Updated**: January 2026
**Version**: 6.0
