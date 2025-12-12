# Contributing to StateExplorer

Thank you for your interest in contributing to StateExplorer! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites
- Python 3.10 or higher
- Git
- Playwright (for AriaStateMapper)
- Appium (for AppStateMapper - future)

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd StateExplorer

# Install all packages in development mode
pip install -e packages/model-resilience-core/[dev]
pip install -e packages/aria-state-mapper/[dev]
pip install -e packages/app-state-mapper/[dev]

# Install Playwright browsers (for AriaStateMapper)
playwright install firefox

# Run tests to verify setup
pytest packages/
```

## Project Structure

StateExplorer is a monorepo containing three packages:

```
StateExplorer/
├── packages/
│   ├── model-resilience-core/    # Core algorithms (platform-agnostic)
│   ├── aria-state-mapper/         # Web app mapping (Playwright)
│   └── app-state-mapper/          # Native app mapping (Appium - future)
├── docs/                          # Documentation
├── examples/                      # Usage examples
└── tests/                         # Integration tests (future)
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following our style guidelines
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest packages/

# Run tests for specific package
pytest packages/model-resilience-core/
pytest packages/aria-state-mapper/

# Run with coverage
pytest --cov=model_resilience_core packages/model-resilience-core/
```

### 4. Format Code

```bash
# Format with black
black packages/

# Sort imports
isort packages/

# Lint with ruff
ruff check packages/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: your feature description"
```

We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python Style Guide

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use Black for formatting
- Use Ruff for linting

### Documentation Style

- Write docstrings for all public functions/classes
- Follow Google docstring style
- Include examples in docstrings where helpful
- Keep README files up to date

### Testing Guidelines

- Write tests for all new functionality
- Aim for >80% code coverage
- Use pytest fixtures for common setup
- Use descriptive test names
- Test both success and failure cases

## Package-Specific Guidelines

### ModelResilienceCore

- Must remain platform-agnostic
- No UI automation dependencies
- Focus on algorithm correctness
- Comprehensive unit tests required
- Performance benchmarks for critical algorithms

### AriaStateMapper

- Playwright-specific implementations
- Async/await throughout
- Integration tests with real browsers
- Document browser compatibility
- Consider performance for large UIs

### AppStateMapper (Future)

- Appium-specific implementations
- Platform-specific code in separate modules
- Test on multiple platforms when possible
- Document device/emulator requirements

## Documentation

When adding features:
1. Update package README if API changes
2. Add/update docstrings
3. Add examples to `examples/` directory
4. Update main README if necessary
5. Add entry to CHANGELOG

## Testing

### Unit Tests
- Located in `tests/` within each package
- Test individual functions/classes
- Mock external dependencies

### Integration Tests
- Located in root `tests/` directory (future)
- Test package interactions
- Test with real browsers/devices

### Running Tests

```bash
# All tests
pytest

# Specific package
pytest packages/model-resilience-core/

# With coverage
pytest --cov

# With verbose output
pytest -v

# Stop on first failure
pytest -x
```

## Pull Request Process

1. Ensure all tests pass
2. Update documentation
3. Add changelog entry
4. Request review from maintainers
5. Address review feedback
6. Squash commits if requested

## Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Update CHANGELOG
3. Create git tag
4. Build package: `python -m build`
5. Publish to PyPI: `twine upload dist/*`

## Getting Help

- Open an issue for bugs/features
- Ask questions in discussions
- Join our community chat (link TBD)

## Code of Conduct

Be respectful and inclusive. We're all here to learn and improve.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## Questions?

Open an issue or reach out to the maintainers!

