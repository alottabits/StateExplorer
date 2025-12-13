# Getting Started with StateExplorer

**Quick start guide for discovering and modeling UI states**

---

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Node.js**: 18+ (for Playwright browsers)
- **OS**: Linux, macOS, or Windows

### Installation

#### 1. Install Playwright Browsers

```bash
# Install Playwright system dependencies
pip install playwright
playwright install chromium
```

#### 2. Install StateExplorer Packages

```bash
# From the StateExplorer directory
cd StateExplorer

# Install model-resilience-core
pip install -e packages/model-resilience-core

# Install aria-state-mapper (includes CLI)
pip install -e packages/aria-state-mapper
```

#### 3. Verify Installation

```bash
aria-discover --help
```

---

## Quick Start: Discover Your First UI

### Basic Discovery

```bash
aria-discover \
  --url http://localhost:3000 \
  --username admin \
  --password admin \
  --output fsm_graph.json
```

### What Happens:

1. **Login flow discovery**: Maps the authentication workflow
2. **State exploration**: Uses DFS to discover all reachable states
3. **Transition mapping**: Records all actions between states
4. **Element extraction**: Finds all interactive elements via accessibility tree
5. **Graph generation**: Creates FSM model in JSON format

### Expected Output:

```
2025-12-13 09:34:34 - INFO - Starting FSM discovery for http://localhost:3000
2025-12-13 09:34:37 - INFO - Created NEW state: V_LOGIN_FORM_EMPTY (actions: 4)
2025-12-13 09:34:40 - INFO - Created NEW state: V_OVERVIEW_PAGE (actions: 10)
2025-12-13 09:34:41 - INFO - Created NEW state: V_DEVICES (actions: 20)
...
2025-12-13 09:35:10 - INFO - Discovery complete: 10 states, 58 transitions
2025-12-13 09:35:10 - INFO - Graph saved to: fsm_graph.json
```

---

## Understanding the Output

### FSM Graph Structure

```json
{
  "metadata": {
    "discovery_method": "DFS",
    "state_count": 10,
    "transition_count": 58,
    "discovery_time": 35.2
  },
  "states": [
    {
      "state_id": "V_LOGIN_FORM_EMPTY",
      "state_type": "form",
      "fingerprint": {
        "accessibility_tree": {...},
        "actionable_elements": {...},
        "url_pattern": "/login"
      },
      "element_descriptors": [...]
    }
  ],
  "transitions": [
    {
      "from_state_id": "V_LOGIN_FORM_EMPTY",
      "to_state_id": "V_OVERVIEW_PAGE",
      "action_type": "click",
      "action_target": "Sign In",
      "similarity_score": 0.99
    }
  ]
}
```

### State Types

- **`form`**: Login page, data entry
- **`dashboard`**: Overview, summary page
- **`list`**: Table, grid view
- **`detail`**: Single item view
- **`error`**: Error state, validation failure

### Key Metrics

- **State count**: Total unique states discovered
- **Transition count**: Total actions mapped
- **Similarity scores**: How confidently states were matched (≥0.8 = high confidence)

---

## Common Use Cases

### 1. Discover Full Application

```bash
aria-discover \
  --url http://localhost:3000 \
  --username admin \
  --password admin \
  --output full_app.json \
  --max-states 100
```

### 2. Discover Specific Flow

Use seeding to focus on a specific area:

```bash
# Create seed file (ui_map.json) with known states
aria-discover \
  --url http://localhost:3000 \
  --username admin \
  --password admin \
  --seed-file ui_map.json \
  --output admin_flow.json
```

### 3. Headful Mode (Visual Debugging)

```bash
aria-discover \
  --url http://localhost:3000 \
  --username admin \
  --password admin \
  --headless false
```

Watch the browser as it explores!

### 4. Use BFS Instead of DFS

```bash
aria-discover \
  --url http://localhost:3000 \
  --username admin \
  --password admin \
  --use-bfs
```

**BFS** (Breadth-First): Explores level by level (good for wide, shallow apps)  
**DFS** (Depth-First): Explores deeply before backtracking (good for deep flows)

---

## Command-Line Options

### Required

- `--url`: Base URL of the application to explore

### Authentication

- `--username`: Login username (if auth required)
- `--password`: Login password
- `--no-login`: Skip login flow entirely

### Discovery Options

- `--output`: Output file (default: `fsm_graph.json`)
- `--max-states`: Maximum states to discover (default: 100)
- `--use-bfs`: Use breadth-first search (default: DFS)
- `--seed-file`: Pre-discovered UI map for faster exploration

### Browser Options

- `--headless`: Run in headless mode (default: `true`)
- `--timeout`: Page load timeout in ms (default: 10000)

### Safety Options

- `--safe-buttons`: Comma-separated button text patterns to click
  ```bash
  --safe-buttons "New,Add,Edit,View,Show,Cancel,Close,Search,Filter"
  ```

---

## Next Steps

### Using the FSM Graph

Once you have an FSM graph, you can:

1. **Generate tests**: Use graph algorithms to create test paths
2. **Visualize states**: Convert to GraphML for visualization tools
3. **Update manually**: Edit JSON to refine state definitions
4. **Seed future runs**: Use as input for faster re-discovery

### Example: Using in Tests

```python
from aria_state_mapper import UIStateMachineDiscovery
import asyncio
import json

async def test_user_flow():
    # Load discovered graph
    with open("fsm_graph.json") as f:
        graph_data = json.load(f)
    
    # Navigate through known states
    tool = UIStateMachineDiscovery(base_url="http://localhost:3000")
    # ... use graph_data to guide test execution
```

---

## Troubleshooting

### Issue: Discovery hangs

**Solution**: Reduce `--max-states` or check for infinite navigation loops

```bash
aria-discover --url http://localhost:3000 --max-states 20
```

### Issue: Too many similar states

**Solution**: Adjust similarity threshold (future feature) or refine `--safe-buttons`

### Issue: Login fails

**Solution**: Verify credentials and check login URL pattern

```bash
# Try headful mode to see what's happening
aria-discover --url http://localhost:3000 --headless false
```

### Issue: States not differentiated

**Solution**: Ensure ARIA states are properly set in your app (accessibility best practice!)

---

## Best Practices

### 1. Start Small

Don't try to discover everything at once:

```bash
# Start with 20 states to understand your app
aria-discover --url http://localhost:3000 --max-states 20
```

### 2. Use Descriptive Safe Buttons

Customize for your app's button patterns:

```bash
--safe-buttons "View,Show,Details,Open,Expand,Filter,Search,Refresh"
```

### 3. Seed for Speed

After first discovery, use the graph as seed for faster runs:

```bash
# First run (slow)
aria-discover --url http://localhost:3000 --output baseline.json

# Subsequent runs (faster)
aria-discover --url http://localhost:3000 --seed-file baseline.json --output updated.json
```

### 4. Version Control Your Graphs

Commit FSM graphs to track UI changes over time:

```bash
git add fsm_graph.json
git commit -m "Update FSM after navigation refactor"
```

---

## Further Reading

- [Architecture: Fingerprinting Strategy](../architecture/FINGERPRINTING_STRATEGY.md)
- [Architecture: FSM vs POM](../architecture/FSM_VS_POM.md)
- [Research: Model-Based Testing](../research/MODEL_BASED_TESTING.md)
- [Examples: Python Scripts](../../examples/)

