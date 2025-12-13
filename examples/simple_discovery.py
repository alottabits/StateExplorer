"""
Simple example of UI state machine discovery using AriaStateMapper.

This example demonstrates how to use the UIStateMachineDiscovery tool
to automatically discover states and transitions in a web application.
"""

import asyncio
import json
from aria_state_mapper import UIStateMachineDiscovery


async def main():
    """Run a simple discovery example."""
    
    # Initialize the discovery tool
    tool = UIStateMachineDiscovery(
        base_url="http://127.0.0.1:3000",  # GenieACS default
        headless=False,  # Show browser for demonstration
        timeout=10000,  # 10 second timeout
        max_states=50,  # Discover up to 50 states
        use_dfs=True,  # Use Depth-First Search (recommended)
    )
    
    # Run discovery with login
    print("Starting UI state machine discovery...")
    graph_data = await tool.discover(
        username="admin",
        password="admin",
        discover_login_flow=True,
    )
    
    # Save results
    output_file = "fsm_graph.json"
    with open(output_file, "w") as f:
        json.dump(graph_data, f, indent=2)
    
    # Print summary
    stats = graph_data.get("statistics", {})
    print("\n=== Discovery Complete ===")
    print(f"States discovered: {stats.get('state_count', 0)}")
    print(f"Transitions found: {stats.get('transition_count', 0)}")
    print(f"States explored: {stats.get('visited_states', 0)}")
    print(f"\nResults saved to: {output_file}")
    
    # Print state type distribution
    print("\nState type distribution:")
    for state_type, count in stats.get("state_types", {}).items():
        print(f"  {state_type}: {count}")


if __name__ == "__main__":
    asyncio.run(main())

