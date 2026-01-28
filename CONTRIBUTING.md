# Contributing to ChronosArchiver

Thank you for your interest in contributing to ChronosArchiver! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/dodopok/ChronosArchiver/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS
   - Relevant logs or screenshots

### Suggesting Features

1. Check existing issues and discussions
2. Create a new issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/dodopok/ChronosArchiver.git
   cd ChronosArchiver
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

5. **Run tests and linting**
   ```bash
   # Format code
   black src/ tests/
   isort src/ tests/
   
   # Lint
   flake8 src/ tests/
   mypy src/
   
   # Run tests
   pytest
   pytest --cov=chronos_archiver --cov-report=html
   ```

6. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```
   
   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions/changes
   - `refactor:` Code refactoring
   - `chore:` Maintenance tasks

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Link related issues

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Write docstrings for all public functions/classes
- Keep functions focused and small
- Maximum line length: 100 characters

### Testing

- Write unit tests for all new code
- Aim for >80% code coverage
- Use pytest fixtures for common setup
- Mock external dependencies (HTTP calls, file I/O)
- Test both success and failure cases

### Documentation

- Update README.md for user-facing changes
- Update API documentation in docs/api.md
- Add docstrings with examples
- Include type information

### Async Code

- Use `async`/`await` for I/O operations
- Properly handle async context managers
- Use `asyncio.gather()` for concurrent operations
- Handle cancellation gracefully

### Error Handling

- Use specific exception types
- Provide meaningful error messages
- Log errors with appropriate levels
- Clean up resources in finally blocks

## Project Structure

```
src/chronos_archiver/
├── __init__.py          # Package exports
├── __main__.py          # CLI entry point
├── cli.py               # Click command definitions
├── config.py            # Configuration loading/validation
├── discovery.py         # CDX API integration
├── ingestion.py         # Content downloading
├── transformation.py    # Link rewriting, metadata
├── indexing.py          # Storage and search
├── queue_manager.py     # Async queue management
├── models.py            # Pydantic data models
└── utils.py             # Helper functions
```

## Testing Strategy

### Unit Tests
- Test individual functions in isolation
- Mock external dependencies
- Focus on edge cases

### Integration Tests
- Test component interactions
- Use test fixtures for setup
- Validate end-to-end workflows

### Example Test

```python
import pytest
from chronos_archiver.discovery import WaybackDiscovery

@pytest.mark.asyncio
async def test_discovery_finds_snapshots(mock_cdx_response):
    """Test that discovery correctly parses CDX responses."""
    discovery = WaybackDiscovery()
    
    snapshots = await discovery.find_snapshots(
        "http://www.example.com"
    )
    
    assert len(snapshots) > 0
    assert all(s.url for s in snapshots)
    assert all(s.timestamp for s in snapshots)
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release branch: `git checkout -b release/v1.x.x`
4. Run full test suite
5. Create PR to main
6. After merge, tag release: `git tag v1.x.x`
7. Push tag: `git push origin v1.x.x`

## Questions?

Feel free to:
- Open a [Discussion](https://github.com/dodopok/ChronosArchiver/discussions)
- Ask in existing issues
- Reach out to maintainers

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to ChronosArchiver! 🎉