# StateExplorer Tests

Comprehensive test suite for StateExplorer packages.

---

## Test Structure

### Unit Tests

Located in package-specific test directories:

- `packages/model-resilience-core/tests/` - Core algorithm tests
- `packages/aria-state-mapper/tests/` - Playwright integration tests

### Integration Tests

Located in root `tests/` directory:

- `test_accessibility_capture.py` - Accessibility tree fingerprinting
- `test_state_matching.py` - Weighted fuzzy state comparison
- `test_discovery_integration.py` - Full discovery workflow

---

## Running Tests

### Prerequisites

1. **Install packages in editable mode:**
```bash
cd StateExplorer
pip install -e packages/model-resilience-core
pip install -e packages/aria-state-mapper
```

2. **Install test dependencies:**
```bash
pip install pytest pytest-asyncio
```

3. **Install Playwright browsers:**
```bash
playwright install chromium
```

### Run All Tests

```bash
# From StateExplorer root
pytest
```

### Run Specific Test Files

```bash
# Accessibility tests
pytest tests/test_accessibility_capture.py

# State matching tests
pytest tests/test_state_matching.py

# Discovery integration tests
pytest tests/test_discovery_integration.py
```

### Run with Options

```bash
# Verbose output
pytest -v

# Show print statements
pytest -s

# Run only fast tests (exclude slow integration tests)
pytest -m "not slow"

# Run specific test
pytest tests/test_state_matching.py::test_state_matching_identical
```

---

## Test Requirements

### For Integration Tests

Integration tests require a **running GenieACS server** at `http://127.0.0.1:3000`.

#### Option 1: Docker

```bash
docker run -d --name genieacs -p 3000:3000 drumsergio/genieacs
```

#### Option 2: Local Installation

See [GenieACS documentation](https://github.com/genieacs/genieacs)

### Test Credentials

Default credentials used in tests:
- Username: `admin`
- Password: `admin`

Configure in `conftest.py` if different.

---

## Test Categories

### Fast Tests (< 5 seconds)

- Unit tests for fingerprinting algorithms
- State comparison logic
- Model validation

```bash
pytest -m "not slow"
```

### Slow Tests (> 10 seconds)

- Full discovery workflows
- Multi-state exploration
- Browser automation

```bash
pytest -m "slow"
```

### Server-Dependent Tests

Tests marked with `@pytest.mark.requires_server`:

```bash
pytest -m "requires_server"
```

---

## Test Coverage

### Current Coverage

- ✅ **Accessibility tree capture**: 100%
- ✅ **State fingerprinting**: 100%
- ✅ **Weighted fuzzy matching**: 100%
- ✅ **State classification**: 100%
- ✅ **Discovery workflow**: 90%
- 🔄 **Self-healing**: 50% (in progress)

### Generate Coverage Report

```bash
pip install pytest-cov
pytest --cov=model_resilience_core --cov=aria_state_mapper --cov-report=html
```

View report:
```bash
open htmlcov/index.html
```

---

## Writing New Tests

### Test Naming Convention

- File: `test_<module_name>.py`
- Function: `test_<functionality>_<scenario>`

### Example Test

```python
import pytest
from model_resilience_core.matching import StateComparer


@pytest.mark.asyncio
async def test_state_comparer_identical_states():
    """Test that identical states match with high similarity."""
    comparer = StateComparer()
    
    state_a = UIState(...)
    state_b = UIState(...)
    
    matched, similarity = comparer.find_matching_state(
        current_state=state_a,
        known_states=[state_b],
        threshold=0.8,
    )
    
    assert matched is not None
    assert similarity >= 0.95
```

### Async Tests

Use `@pytest.mark.asyncio` for async functions:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Slow Tests

Mark slow integration tests:

```python
@pytest.mark.slow
@pytest.mark.asyncio
async def test_full_discovery():
    # Long-running discovery test
    pass
```

---

## Continuous Integration

### GitHub Actions (Future)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -e packages/model-resilience-core
          pip install -e packages/aria-state-mapper
          pip install pytest pytest-asyncio
          playwright install chromium
      - name: Run fast tests
        run: pytest -m "not slow" -v
```

---

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'aria_state_mapper'`

**Solution**: Install packages in editable mode:
```bash
pip install -e packages/model-resilience-core
pip install -e packages/aria-state-mapper
```

### Browser Not Found

**Problem**: `playwright._impl._api_types.Error: Executable doesn't exist`

**Solution**: Install Playwright browsers:
```bash
playwright install chromium
```

### Server Connection Refused

**Problem**: `playwright._impl._api_types.TimeoutError`

**Solution**: Ensure GenieACS is running at `http://127.0.0.1:3000`:
```bash
docker ps  # Check if container is running
curl http://127.0.0.1:3000  # Test connectivity
```

### Slow Test Timeout

**Problem**: Tests timeout during discovery

**Solution**: Increase timeout or reduce max_states:
```python
tool = UIStateMachineDiscovery(
    base_url="http://127.0.0.1:3000",
    timeout=20000,  # Increase timeout
    max_states=5,   # Reduce exploration depth
)
```

---

## Test Data

### Sample FSM Graphs

Located in `tests/fixtures/`:
- `sample_graph.json` - Small reference graph
- `genieacs_graph.json` - Full GenieACS discovery output

### Using Test Fixtures

```python
import json
from pathlib import Path

@pytest.fixture
def sample_graph():
    """Load sample FSM graph."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_graph.json"
    with open(fixture_path) as f:
        return json.load(f)

def test_with_fixture(sample_graph):
    assert len(sample_graph['states']) > 0
```

---

## Contributing Tests

1. Write tests for new features
2. Ensure tests pass locally
3. Add appropriate markers (`@pytest.mark.slow`, etc.)
4. Update this README with new test categories
5. Maintain >80% code coverage

---

## Further Reading

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Playwright Python](https://playwright.dev/python/docs/intro)

