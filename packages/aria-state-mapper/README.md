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

### Basic Discovery

```bash
# Run automatic discovery from scratch
aria-discover --url http://localhost:3000 \
  --username admin \
  --password admin \
  --output fsm_graph.json \
  --max-states 50
```

### Incremental Discovery (NEW in v0.2.0)

**Start from an existing FSM graph and expand it:**

```bash
# Continue from manually captured graph
aria-discover --url http://localhost:3000 \
  --username admin \
  --password admin \
  --seed-graph fsm_graph_augmented.json \
  --output fsm_graph_expanded.json \
  --max-states 50
```

**How it works:**
1. **Loads seed graph** into memory (states + transitions)
2. **Reads live UI** via accessibility tree during exploration
3. **Compares** current UI fingerprint against seeded states
4. **Reuses** state_id if similarity > 80% (prevents duplicates)
5. **Creates** new states for UI not in seed graph
6. **Updates** metadata for matched states (detects UI changes)

**Benefits:**
- ✅ Combines manual depth (complex workflows) with automated breadth (coverage)
- ✅ Preserves manually captured metadata (action descriptions)
- ✅ Prevents duplicate states through fingerprint-based deduplication
- ✅ **Detects UI changes** - updates element descriptors if UI evolved
- ✅ **Self-healing** - adapts to URL changes and new elements
- ✅ Enables iterative graph building over time

**Important**: The seed graph is a **knowledge base for comparison**, not a navigation map. Discovery always reads the **live accessibility tree**, comparing it against seeded states to detect matches and changes.

### Python API

```python
from aria_state_mapper import UIStateMachineDiscovery

# Create discovery engine
discovery = UIStateMachineDiscovery(
    base_url="http://localhost:3000",
    headless=True,
    max_states=50
)

# Seed from existing graph (optional)
discovery.seed_from_fsm_graph("fsm_graph_augmented.json")

# Run discovery
await discovery.discover(
    username="admin",
    password="admin"
)

# Export enhanced graph
graph = discovery._export_to_graph()
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

## Common Workflows

### Workflow 1: Manual → Automated Enhancement

Combine manual recording depth with automated breadth:

```bash
# Step 1: Manual recording (using manual_fsm_augmentation.py)
# Result: fsm_graph_augmented.json (21 states with complex interactions)

# Step 2: Automated expansion
aria-discover --url http://localhost:3000 \
  --username admin \
  --password admin \
  --seed-graph fsm_graph_augmented.json \
  --output fsm_graph_full.json \
  --max-states 50

# Result: 40+ states (21 manual + 20+ automated)
```

### Workflow 2: Iterative Development

Build graph incrementally:

```bash
# Week 1: Basic discovery
aria-discover --url http://localhost:3000 \
  --output week1.json --max-states 10

# Week 2: Add manual depth
# (Use manual recording tool on week1.json)

# Week 3: Automated expansion
aria-discover --url http://localhost:3000 \
  --seed-graph week2.json \
  --output week3.json --max-states 30
```

### Workflow 3: Graph Refresh

Update graph as UI evolves:

```bash
# Initial discovery (3 months ago)
aria-discover --url http://prod.example.com \
  --output fsm_v1.json

# Refresh after UI changes
aria-discover --url http://prod.example.com \
  --seed-graph fsm_v1.json \
  --output fsm_v2.json
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

