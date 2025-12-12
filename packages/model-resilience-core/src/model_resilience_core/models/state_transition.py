"""
StateTransition data model.

Represents an action-based transition between UI states.

In FSM/MBT terminology, this is an 'Edge' - the executable action
that moves the system from one verifiable state to another.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ActionType(str, Enum):
    """Standard action types for state transitions."""
    CLICK = "click"
    FILL_FORM = "fill_form"
    NAVIGATE = "navigate"


@dataclass
class StateTransition:
    """
    Represents a transition between two UI states triggered by an action.
    
    Attributes:
        transition_id: Unique identifier for this transition
        from_state_id: ID of the source state
        to_state_id: ID of the destination state
        action_type: Type of action ("click", "fill_form", "navigate")
        trigger_locators: Locator strategies for finding the trigger element
        action_data: Optional data for the action (e.g., form fill values)
        success_rate: Historical success rate of this transition (0.0-1.0)
        metadata: Additional transition-specific metadata
        timestamp: When this transition was discovered
    """
    
    transition_id: str
    from_state_id: str
    to_state_id: str
    action_type: ActionType | str
    trigger_locators: dict[str, Any] = field(default_factory=dict)
    action_data: Optional[dict[str, Any]] = None
    success_rate: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: float | None = None
    
    # Legacy: Support for 'trigger' as an alias for 'trigger_locators'
    @property
    def trigger(self) -> dict[str, Any]:
        """Alias for trigger_locators (backward compatibility)."""
        return self.trigger_locators
    
    @trigger.setter
    def trigger(self, value: dict[str, Any]) -> None:
        """Alias for trigger_locators (backward compatibility)."""
        self.trigger_locators = value
    
    def __hash__(self) -> int:
        """Allow StateTransition to be used in sets and as dict keys."""
        return hash((self.from_state_id, str(self.action_type), self.to_state_id))
    
    def __eq__(self, other: object) -> bool:
        """Transitions are equal if they connect same states via same action type."""
        if not isinstance(other, StateTransition):
            return NotImplemented
        return (
            self.from_state_id == other.from_state_id
            and self.to_state_id == other.to_state_id
            and str(self.action_type) == str(other.action_type)
        )

