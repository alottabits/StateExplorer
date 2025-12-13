"""Command-line interface for FSM/MBT UI discovery tool."""

import argparse
import asyncio
import json
import logging
from pathlib import Path

from aria_state_mapper import UIStateMachineDiscovery

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Command-line interface for FSM/MBT UI discovery tool."""
    parser = argparse.ArgumentParser(
        description="Discover UI states and transitions using FSM/MBT approach with Playwright"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Base URL of the application to crawl",
    )
    parser.add_argument(
        "--output",
        default="ui_state_machine.json",
        help="Output file for FSM graph (default: ui_state_machine.json)",
    )
    parser.add_argument(
        "--username",
        help="Login username (optional)",
    )
    parser.add_argument(
        "--password",
        help="Login password (optional)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Run browser with GUI",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10000,
        help="Default timeout in milliseconds (default: 10000)",
    )
    parser.add_argument(
        "--max-states",
        type=int,
        default=100,
        help="Maximum number of states to discover (default: 100)",
    )
    parser.add_argument(
        "--safe-buttons",
        default="New,Add,Edit,View,Show,Cancel,Close,Search,Filter",
        help="Comma-separated button text patterns safe to click",
    )
    parser.add_argument(
        "--skip-login-discovery",
        action="store_true",
        help="Skip discovering login flow states",
    )
    parser.add_argument(
        "--use-bfs",
        action="store_true",
        help="Use Breadth-First Search instead of Depth-First Search (default: DFS)",
    )
    parser.add_argument(
        "--seed-map",
        help="Path to ui_map.json to seed the FSM with known states",
    )

    args = parser.parse_args()

    # Create discovery tool
    tool = UIStateMachineDiscovery(
        base_url=args.url,
        headless=args.headless,
        timeout=args.timeout,
        max_states=args.max_states,
        safe_button_patterns=args.safe_buttons,
        use_dfs=not args.use_bfs,  # Default to DFS
    )
    
    # Seed from map if provided
    if args.seed_map:
        tool.seed_from_map(args.seed_map)


    # Run discovery
    logger.info("Starting FSM/MBT discovery for %s", args.url)
    graph_data = asyncio.run(tool.discover(
        username=args.username,
        password=args.password,
        discover_login_flow=not args.skip_login_discovery,
    ))

    # Save to file
    output_path = Path(args.output)
    with output_path.open("w") as f:
        json.dump(graph_data, f, indent=2)

    logger.info("FSM graph saved to %s", output_path)
    
    # Log statistics
    stats = graph_data.get("statistics", {})
    logger.info("Discovery complete:")
    logger.info("  - States discovered: %d", stats.get("state_count", 0))
    logger.info("  - Transitions found: %d", stats.get("transition_count", 0))
    logger.info("  - States explored: %d", stats.get("visited_states", 0))
    logger.info("  - State type distribution:")
    for state_type, count in stats.get("state_types", {}).items():
        logger.info("      %s: %d", state_type, count)


if __name__ == "__main__":
    main()

