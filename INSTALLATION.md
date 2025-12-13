# Installation Guide - StateExplorer

## Quick Start

StateExplorer consists of two independently installable packages:

1. **ModelResilienceCore** - Platform-agnostic state fingerprinting and matching
2. **AriaStateMapper** - Playwright-based web application state discovery

### Prerequisites

- Python 3.10 or higher
- pip
- For AriaStateMapper: Playwright browsers

### Installation

#### Install Both Packages (Recommended)

```bash
cd /home/rjvisser/projects/req-tst/StateExplorer

# Install ModelResilienceCore (required dependency)
pip install -e packages/model-resilience-core/

# Install AriaStateMapper (includes ModelResilienceCore)
pip install -e packages/aria-state-mapper/

# Install Playwright browsers (required for AriaStateMapper)
playwright install firefox
```

#### Install Only ModelResilienceCore

If you only need the platform-agnostic algorithms:

```bash
cd /home/rjvisser/projects/req-tst/StateExplorer
pip install -e packages/model-resilience-core/
```

### Verify Installation

```bash
# Test ModelResilienceCore
python -c "from model_resilience_core import UIState, StateFingerprinter, StateComparer; print('✅ Core works')"

# Test AriaStateMapper
python -c "from aria_state_mapper import UIStateMachineDiscovery; print('✅ AriaStateMapper works')"

# Check CLI tool
aria-discover --help
```

## Development Installation

For development with testing tools:

```bash
# Install with dev dependencies
pip install -e packages/model-resilience-core/[dev]
pip install -e packages/aria-state-mapper/[dev]

# Install Playwright browsers
playwright install firefox
```

## Usage Examples

### Basic Discovery

```python
import asyncio
from aria_state_mapper import UIStateMachineDiscovery

async def discover():
    tool = UIStateMachineDiscovery(
        base_url="http://127.0.0.1:3000",
        headless=True,
        max_states=50,
    )
    
    graph = await tool.discover(
        username="admin",
        password="admin",
    )
    
    print(f"Discovered {len(graph['nodes'])} states")

asyncio.run(discover())
```

### Using the CLI

```bash
# Basic discovery
aria-discover --url http://127.0.0.1:3000 \
              --username admin \
              --password admin \
              --output fsm_graph.json

# With custom options
aria-discover --url http://127.0.0.1:3000 \
              --username admin \
              --password admin \
              --max-states 100 \
              --no-headless \
              --output fsm_graph.json
```

### Using ModelResilienceCore Alone

```python
from model_resilience_core import StateFingerprinter, StateComparer

# Platform-agnostic fingerprinting
fingerprinter = StateFingerprinter()
fingerprint = fingerprinter.create_fingerprint(
    accessibility_tree={"landmark_roles": ["navigation", "main"]},
    url="http://example.com/page",
    title="Example Page"
)

# Fuzzy state matching
comparer = StateComparer()
similarity = comparer.calculate_similarity(fingerprint1, fingerprint2)
is_match = comparer.is_match(fingerprint1, fingerprint2, threshold=0.80)
```

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`:

```bash
# Make sure packages are installed in editable mode
pip list | grep model-resilience-core
pip list | grep aria-state-mapper

# Reinstall if needed
pip install -e packages/model-resilience-core/
pip install -e packages/aria-state-mapper/
```

### Playwright Errors

If Playwright browsers are missing:

```bash
playwright install firefox
# or for all browsers
playwright install
```

### Permission Issues

If you get permission errors:

```bash
# Use --user flag
pip install --user -e packages/model-resilience-core/
pip install --user -e packages/aria-state-mapper/
```

## Next Steps

- See `examples/` directory for working examples
- Check `examples/README.md` for detailed usage
- Read package READMEs for API documentation:
  - `packages/model-resilience-core/README.md`
  - `packages/aria-state-mapper/README.md`

## Uninstallation

```bash
pip uninstall aria-state-mapper model-resilience-core
```

## Dependencies

### ModelResilienceCore
- pyyaml >= 6.0

### AriaStateMapper
- model-resilience-core >= 0.1.0
- playwright >= 1.40.0
- pyyaml >= 6.0

All dependencies are automatically installed with the packages.

