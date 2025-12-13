## Examples

This directory contains example scripts demonstrating how to use StateExplorer packages.

### Simple Discovery Example

`simple_discovery.py` demonstrates basic usage of AriaStateMapper for discovering UI states and transitions:

```bash
# Make sure you have AriaStateMapper installed
cd /home/rjvisser/projects/req-tst/StateExplorer
pip install -e packages/aria-state-mapper/

# Install Playwright browsers
playwright install firefox

# Run the example (assumes GenieACS running at http://127.0.0.1:3000)
python examples/simple_discovery.py
```

### Command-Line Tool

AriaStateMapper includes a command-line tool for discovery:

```bash
# Basic usage
aria-discover --url http://127.0.0.1:3000 \
              --username admin \
              --password admin \
              --output fsm_graph.json

# With additional options
aria-discover --url http://127.0.0.1:3000 \
              --username admin \
              --password admin \
              --max-states 100 \
              --no-headless \
              --output fsm_graph.json

# See all options
aria-discover --help
```

### Output Format

The discovery tool generates a JSON file with the following structure:

```json
{
  "base_url": "http://127.0.0.1:3000",
  "graph_type": "fsm_mbt",
  "discovery_method": "playwright_state_machine_dfs",
  "nodes": [
    {
      "id": "V_LOGIN_FORM_EMPTY",
      "node_type": "state",
      "state_type": "form",
      "fingerprint": {...},
      "verification_logic": {...},
      "element_descriptors": [...]
    }
  ],
  "edges": [
    {
      "source": "V_LOGIN_FORM_EMPTY",
      "target": "V_OVERVIEW_PAGE",
      "edge_type": "transition",
      "action_type": "submit",
      "trigger_locators": {...}
    }
  ],
  "statistics": {
    "state_count": 32,
    "transition_count": 58,
    "visited_states": 10,
    "state_types": {...}
  }
}
```

### Integration with Test Frameworks

The discovered FSM can be used with test frameworks:

```python
from aria_state_mapper import UIStateMachineDiscovery
import asyncio

async def test_navigation():
    # Load existing FSM
    tool = UIStateMachineDiscovery(base_url="http://127.0.0.1:3000")
    
    # Or discover fresh
    graph = await tool.discover(username="admin", password="admin")
    
    # Use states and transitions in your tests
    assert len(graph["nodes"]) > 0
    assert any(n["state_type"] == "dashboard" for n in graph["nodes"])
```
