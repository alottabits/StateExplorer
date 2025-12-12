# AriaStateMapper

**Web application state mapping using Playwright and accessibility trees**

## Overview

AriaStateMapper is a Playwright-based tool for discovering and mapping UI states in web applications. It uses accessibility tree analysis for robust state identification and supports both automatic crawling and manual action recording.

## Features

### Automatic UI Crawling
- **Accessibility-driven navigation**: Uses ARIA roles and semantic elements
- **DFS/BFS exploration strategies**: Configurable depth-first or breadth-first traversal
- **SPA-aware navigation**: Browser back for state preservation
- **Form-based semantic modeling**: Compound actions (fill + submit)
- **Transition deduplication**: Prevents recording duplicate transitions

### State Discovery
- **Multi-dimensional fingerprinting**: Via ModelResilienceCore
- **Weighted fuzzy matching**: 99% same-state accuracy, 87% with data changes
- **Dynamic state classification**: URL-based state IDs
- **FSM generation**: Creates Finite State Machine graphs

### Manual Action Recording
- **Augment automated discovery**: Add custom workflows
- **Record user interactions**: Capture manual navigation paths
- **Hybrid approach**: Combine automatic + manual exploration

### Playwright Integration
- **Native ARIA snapshot API**: Uses `locator.aria_snapshot()`
- **Resilient locators**: Priority-based fallback strategies
- **Async operations**: Non-blocking exploration
- **Headless or visible**: Configurable browser mode

## Installation

```bash
# Install AriaStateMapper (includes ModelResilienceCore dependency)
pip install aria-state-mapper

# Install Playwright browsers
playwright install firefox
```

## Usage

### Automatic Discovery

```python
from aria_state_mapper import UIStateMachineDiscovery

# Create discovery engine
discovery = UIStateMachineDiscovery(
    base_url="https://example.com",
    username="admin",
    password="password"
)

# Run discovery
await discovery.discover(
    max_states=50,
    strategy="dfs"  # or "bfs"
)

# Export FSM graph
graph = discovery.export_graph()
```

### Command Line

```bash
# Run automatic discovery
python -m aria_state_mapper.discovery \
  --url https://example.com \
  --username admin \
  --password password \
  --output fsm_graph.json \
  --max-states 50

# With manual action recording
python -m aria_state_mapper.recording \
  --url https://example.com \
  --output manual_actions.json
```

## Architecture

```
aria_state_mapper/
├── discovery/                    # Automatic crawling
│   ├── ui_crawler.py
│   └── state_machine_discovery.py
├── playwright_integration/       # Playwright utilities
│   ├── aria_snapshot.py
│   └── element_locator.py
└── recording/                    # Manual action recording
    └── manual_action_recorder.py
```

## Configuration

```python
# Discovery configuration
config = {
    "max_states": 100,
    "max_depth": 10,
    "strategy": "dfs",  # or "bfs"
    "headless": True,
    "timeout": 30000,
    "skip_loading_states": True,
    "deduplicate_transitions": True,
}

discovery = UIStateMachineDiscovery(config=config)
```

## Two-Stage Pipeline

AriaStateMapper can be used in a two-stage pipeline:

1. **Stage 1**: Fast structural crawl (POM approach)
2. **Stage 2**: Deep behavioral modeling (FSM approach)

```bash
# Stage 1: Quick structural discovery
python -m aria_state_mapper.discovery --quick --output ui_map.json

# Stage 2: Deep FSM modeling (seeded from Stage 1)
python -m aria_state_mapper.discovery --seed ui_map.json --output fsm_graph.json
```

## Research Validation

AriaStateMapper implements algorithms validated through research:
- **Browser back navigation**: Zero element location failures
- **58 transitions discovered**: 3.2x improvement over goto()
- **10 states explored**: 67% improvement in depth
- **Depth 8 exploration**: Successful deep traversal
- **86% admin coverage**: 6/7 admin pages discovered

See `docs/research/` for detailed validation results.

## Dependencies

- Python >=3.10
- model-resilience-core (core algorithms)
- playwright >=1.40.0 (browser automation)
- pyyaml >=6.0 (ARIA snapshot parsing)

## License

See [LICENSE](../../LICENSE) file for details.

