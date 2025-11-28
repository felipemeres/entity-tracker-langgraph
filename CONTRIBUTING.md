# Contributing to Entity Tracker

Thank you for considering contributing to Entity Tracker! This document provides guidelines and instructions for contributing.

## Development Setup

1. **Fork and clone the repository**:
```bash
git clone https://github.com/your-username/entity-tracker-langgraph.git
cd entity-tracker-langgraph
```

2. **Set up development environment**:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .  # Install in editable mode
```

3. **Configure environment**:
```bash
cp .env.example .env
# Add your API keys for testing
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=entity_tracker --cov-report=html

# Run specific test file
pytest tests/test_agent.py

# Run integration tests only
pytest -m integration
```

## Code Style

We follow PEP 8 style guidelines:

```bash
# Format code with black
black entity_tracker/ tests/

# Check with flake8
flake8 entity_tracker/ tests/

# Type checking with mypy
mypy entity_tracker/
```

## Making Changes

1. **Create a feature branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes** following these guidelines:
   - Write clear, descriptive commit messages
   - Add tests for new features
   - Update documentation as needed
   - Keep changes focused and atomic

3. **Test your changes**:
```bash
pytest
```

4. **Commit and push**:
```bash
git add .
git commit -m "Add: descriptive message about your changes"
git push origin feature/your-feature-name
```

5. **Create a Pull Request**:
   - Go to GitHub and create a PR
   - Describe your changes clearly
   - Link any related issues
   - Wait for review

## Areas for Contribution

### High Priority

- **Search Provider Integrations**: Add support for more search providers (Exa, DuckDuckGo, Brave)
- **Database Backends**: Implement PostgreSQL, MongoDB, or other database backends
- **Performance Optimization**: Improve query efficiency and caching
- **Documentation**: Improve examples, tutorials, and API documentation

### Features

- **Entity Network Visualization**: Graph visualization of entity relationships
- **Sentiment Analysis**: Track sentiment about entities over time
- **Export Capabilities**: PDF, JSON, CSV export formats
- **REST API**: HTTP API for external integrations
- **Multi-language Support**: Support for non-English entities
- **Real-time Monitoring**: Webhook-based real-time updates

### Testing

- **Integration Tests**: More comprehensive integration test coverage
- **Performance Tests**: Benchmarking and performance regression tests
- **Mock Improvements**: Better mock implementations for testing

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Should Include

1. **What**: Brief description of changes
2. **Why**: Rationale for the changes
3. **How**: Technical approach taken
4. **Testing**: How you tested the changes
5. **Screenshots**: If applicable (for UI changes)

### Example PR Description

```markdown
## What
Add support for Exa.ai search provider

## Why
Exa provides high-quality AI-powered search results that are particularly 
good for entity research and fact-finding.

## How
- Created `tools/exa_search.py` with EXA API integration
- Added configuration options to `configuration.py`
- Implemented search and review nodes in graph
- Added tests for Exa integration

## Testing
- Added unit tests in `tests/test_exa_search.py`
- Manually tested with various entity types
- Verified search results quality
```

## Code Review Process

1. **Initial Review**: Maintainers will review within 2-3 business days
2. **Feedback**: Address any feedback or requested changes
3. **Approval**: Once approved, PR will be merged
4. **Release**: Changes will be included in the next release

## Questions?

- **GitHub Discussions**: For general questions
- **GitHub Issues**: For bugs and feature requests
- **Discord**: Join our community (link in README)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

**Thank you for contributing! 🙏**

