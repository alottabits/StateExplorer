"""
UIState data model.

Represents a discrete UI state with multi-dimensional fingerprint.

In FSM/MBT terminology, this is a 'Vertex' - an assertion/verification point.
It's not just a page, but a specific condition the UI is in.

Examples:
    - V_LOGIN_FORM_EMPTY: Login page ready for input
    - V_LOGIN_FORM_ERROR: Login page showing validation errors
    - V_DASHBOARD_LOADED: Main dashboard after successful login
"""

from __future__ import annotations
from dataclasses import dataclass, field
import time
from typing import Any


@dataclass
class UIState:
    """
    Represents a verifiable UI state.
    
    A state is identified by its multi-dimensional fingerprint which includes
    semantic, functional, structural, content, and style properties.
    
    Attributes:
        state_id: Unique identifier (e.g., "V_LOGIN_FORM_EMPTY", "V_DASHBOARD")
        state_type: Classification (e.g., "form", "page", "dashboard", "error", "modal")
        fingerprint: Multi-dimensional fingerprint for state identification
        verification_logic: Logic for verifying this state
        element_descriptors: List of element descriptors for actionable elements
        discovered_at: Timestamp when state was discovered
        metadata: Additional state-specific metadata
        visited: Whether this state has been explored
        depth: Depth in exploration tree
    """
    
    state_id: str
    state_type: str
    fingerprint: dict[str, Any] = field(default_factory=dict)
    verification_logic: dict[str, Any] = field(default_factory=dict)
    element_descriptors: list[dict[str, Any]] = field(default_factory=list)
    discovered_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)
    visited: bool = False
    depth: int = 0
    
    def __hash__(self) -> int:
        """Allow UIState to be used in sets and as dict keys."""
        return hash(self.state_id)
    
    def __eq__(self, other: object) -> bool:
        """States are equal if they have the same state_id."""
        if not isinstance(other, UIState):
            return NotImplemented
        return self.state_id == other.state_id

