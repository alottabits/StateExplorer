"""
Tests for UI discovery.
"""

import pytest
from aria_state_mapper.discovery import UIStateMachineDiscovery


class TestUIStateMachineDiscovery:
    """Test UIStateMachineDiscovery functionality."""
    
    def test_initialization(self):
        """Test discovery engine initialization."""
        discovery = UIStateMachineDiscovery(
            base_url="https://example.com",
            username="admin",
            password="password"
        )
        
        assert discovery.base_url == "https://example.com"
        assert discovery.username == "admin"
        assert len(discovery.states) == 0
        assert len(discovery.transitions) == 0
    
    def test_export_empty_graph(self):
        """Test exporting empty graph."""
        discovery = UIStateMachineDiscovery()
        
        graph = discovery.export_graph()
        
        assert "states" in graph
        assert "transitions" in graph
        assert len(graph["states"]) == 0
        assert len(graph["transitions"]) == 0

