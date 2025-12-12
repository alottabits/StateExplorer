"""
UI State Machine Discovery.

Main discovery engine for exploring web applications and building FSM graphs.
"""

from typing import Any
from model_resilience_core import UIState, StateTransition


class UIStateMachineDiscovery:
    """
    Discovers UI states and transitions to build a Finite State Machine graph.
    
    This is the main entry point for automatic UI discovery. It uses Playwright
    to navigate the application and ModelResilienceCore for state identification.
    """
    
    def __init__(
        self,
        base_url: str = "",
        username: str = "",
        password: str = "",
        config: dict[str, Any] | None = None
    ) -> None:
        """
        Initialize the discovery engine.
        
        Args:
            base_url: Base URL of the application
            username: Login username (optional)
            password: Login password (optional)
            config: Additional configuration options
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.config = config or {}
        
        self.states: dict[str, UIState] = {}
        self.transitions: list[StateTransition] = []
    
    async def discover(
        self,
        max_states: int = 50,
        strategy: str = "dfs"
    ) -> None:
        """
        Run automatic discovery.
        
        Args:
            max_states: Maximum number of states to discover
            strategy: Exploration strategy ("dfs" or "bfs")
        """
        # Placeholder - will be populated when moving code from ui_mbt_discovery.py
        pass
    
    def export_graph(self) -> dict[str, Any]:
        """
        Export the discovered FSM graph.
        
        Returns:
            Dictionary representation of the FSM graph
        """
        return {
            "states": [
                {
                    "state_id": state.state_id,
                    "state_type": state.state_type,
                    "fingerprint": state.fingerprint,
                    "visited": state.visited,
                    "depth": state.depth,
                }
                for state in self.states.values()
            ],
            "transitions": [
                {
                    "from_state_id": trans.from_state_id,
                    "to_state_id": trans.to_state_id,
                    "action_type": trans.action_type,
                    "trigger": trans.trigger,
                }
                for trans in self.transitions
            ],
        }

