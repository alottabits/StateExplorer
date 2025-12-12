"""
Tests for state matching.
"""

import pytest
from model_resilience_core.models import UIState
from model_resilience_core.matching import StateComparer


class TestStateComparer:
    """Test StateComparer functionality."""
    
    def test_identical_states(self):
        """Test that identical states have 100% similarity."""
        state1 = UIState(
            state_id="page1",
            state_type="page",
            fingerprint={
                "url_pattern": "/admin",
                "title": "Admin Page"
            }
        )
        
        state2 = UIState(
            state_id="page2",
            state_type="page",
            fingerprint={
                "url_pattern": "/admin",
                "title": "Admin Page"
            }
        )
        
        comparer = StateComparer()
        similarity = comparer.calculate_similarity(state1, state2)
        
        assert similarity == 1.0
    
    def test_different_states(self):
        """Test that different states have low similarity."""
        state1 = UIState(
            state_id="page1",
            state_type="page",
            fingerprint={
                "url_pattern": "/admin",
                "title": "Admin Page"
            }
        )
        
        state2 = UIState(
            state_id="page2",
            state_type="page",
            fingerprint={
                "url_pattern": "/login",
                "title": "Login Page"
            }
        )
        
        comparer = StateComparer()
        similarity = comparer.calculate_similarity(state1, state2)
        
        assert similarity < 0.5

