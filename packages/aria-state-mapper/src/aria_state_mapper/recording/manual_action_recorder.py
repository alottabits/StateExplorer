"""
Manual action recorder.

Records user interactions for augmenting automatic discovery.
"""

from typing import Any


class ManualActionRecorder:
    """
    Records manual user actions for later playback.
    
    Captures:
    - Element interactions (clicks, form fills)
    - Navigation sequences
    - State transitions
    
    Recordings can be used to augment automatic discovery with
    custom workflows that are hard to discover automatically.
    """
    
    def __init__(self) -> None:
        """Initialize the action recorder."""
        self.actions: list[dict[str, Any]] = []
    
    async def start_recording(self) -> None:
        """Start recording user actions."""
        # Placeholder - will integrate with Playwright
        pass
    
    async def stop_recording(self) -> None:
        """Stop recording and save actions."""
        # Placeholder
        pass
    
    def add_action(self, action: dict[str, Any]) -> None:
        """
        Add a recorded action.
        
        Args:
            action: Action dictionary with type and parameters
        """
        self.actions.append(action)
    
    def export_actions(self) -> list[dict[str, Any]]:
        """
        Export recorded actions.
        
        Returns:
            List of action dictionaries
        """
        return self.actions.copy()
    
    async def playback(self) -> None:
        """Playback recorded actions."""
        # Placeholder
        pass

