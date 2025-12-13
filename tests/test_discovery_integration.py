#!/usr/bin/env python3
"""Integration tests for UIStateMachineDiscovery.

Tests the full discovery workflow including login, state exploration,
and transition mapping.
"""

import asyncio
import json
import pytest
from pathlib import Path

from aria_state_mapper.discovery import UIStateMachineDiscovery


@pytest.mark.asyncio
@pytest.mark.slow
async def test_basic_discovery():
    """Test basic discovery workflow."""
    tool = UIStateMachineDiscovery(
        base_url="http://127.0.0.1:3000",
        headless=True,
        timeout=10000,
        max_states=10,  # Limit for faster testing
    )
    
    try:
        graph_data = await tool.discover(
            username="admin",
            password="admin",
        )
        
        # Verify graph structure
        assert 'metadata' in graph_data
        assert 'states' in graph_data
        assert 'transitions' in graph_data
        
        # Should have discovered multiple states
        assert len(graph_data['states']) > 1
        
        # Should have at least login transition
        assert len(graph_data['transitions']) > 0
        
        # Verify metadata
        metadata = graph_data['metadata']
        assert metadata['discovery_method'] in ['DFS', 'BFS']
        assert metadata['state_count'] == len(graph_data['states'])
        assert metadata['transition_count'] == len(graph_data['transitions'])
        
        # Verify state structure
        for state in graph_data['states']:
            assert 'state_id' in state
            assert 'state_type' in state
            assert 'fingerprint' in state
            assert 'accessibility_tree' in state['fingerprint']
            assert 'actionable_elements' in state['fingerprint']
        
        # Verify transition structure
        for transition in graph_data['transitions']:
            assert 'from_state_id' in transition
            assert 'to_state_id' in transition
            assert 'action_type' in transition
            
    finally:
        # Cleanup
        pass


@pytest.mark.asyncio
@pytest.mark.slow
async def test_discovery_with_seed():
    """Test discovery with pre-seeded UI map."""
    # First, create a seed file (simplified)
    seed_data = {
        "states": [
            {
                "state_id": "V_LOGIN",
                "state_type": "form",
                "fingerprint": {
                    "url_pattern": "/",
                    "title": "Login",
                },
            }
        ],
        "transitions": [],
    }
    
    seed_file = Path("/tmp/test_seed.json")
    with open(seed_file, 'w') as f:
        json.dump(seed_data, f)
    
    try:
        tool = UIStateMachineDiscovery(
            base_url="http://127.0.0.1:3000",
            headless=True,
            timeout=10000,
            max_states=10,
        )
        
        graph_data = await tool.discover(
            username="admin",
            password="admin",
            seed_file=str(seed_file),
        )
        
        # Should have discovered states beyond the seed
        assert len(graph_data['states']) > 1
        
    finally:
        # Cleanup
        if seed_file.exists():
            seed_file.unlink()


@pytest.mark.asyncio
async def test_discovery_login_flow():
    """Test that login flow is properly captured."""
    tool = UIStateMachineDiscovery(
        base_url="http://127.0.0.1:3000",
        headless=True,
        timeout=10000,
        max_states=5,
    )
    
    graph_data = await tool.discover(
        username="admin",
        password="admin",
    )
    
    # Find login-related states
    state_ids = [s['state_id'] for s in graph_data['states']]
    
    # Should have login form state
    assert any('LOGIN' in sid for sid in state_ids)
    
    # Should have post-login state (dashboard/overview)
    assert any('OVERVIEW' in sid or 'DASHBOARD' in sid for sid in state_ids)
    
    # Should have login transitions
    transitions = graph_data['transitions']
    login_transitions = [
        t for t in transitions
        if 'LOGIN' in t['from_state_id']
    ]
    assert len(login_transitions) > 0


@pytest.mark.asyncio
async def test_discovery_state_classification():
    """Test that states are properly classified."""
    tool = UIStateMachineDiscovery(
        base_url="http://127.0.0.1:3000",
        headless=True,
        timeout=10000,
        max_states=10,
    )
    
    graph_data = await tool.discover(
        username="admin",
        password="admin",
    )
    
    # Collect all state types
    state_types = [s['state_type'] for s in graph_data['states']]
    
    # Should have form type (login)
    assert 'form' in state_types
    
    # Should have other types (dashboard, list, etc.)
    assert len(set(state_types)) > 1


@pytest.mark.asyncio
async def test_discovery_safe_buttons():
    """Test that safe button filtering works."""
    tool = UIStateMachineDiscovery(
        base_url="http://127.0.0.1:3000",
        headless=True,
        timeout=10000,
        max_states=10,
        safe_button_patterns="View,Show,Details",  # Very limited
    )
    
    graph_data = await tool.discover(
        username="admin",
        password="admin",
    )
    
    # Should still discover states (via links)
    assert len(graph_data['states']) > 1
    
    # Verify no dangerous actions recorded
    for transition in graph_data['transitions']:
        action_target = transition.get('action_target', '').lower()
        # Should not have "delete", "remove", etc. (only safe patterns)
        assert 'delete' not in action_target
        assert 'remove' not in action_target


@pytest.mark.asyncio
async def test_discovery_bfs_vs_dfs():
    """Test BFS and DFS produce different (but valid) results."""
    # DFS discovery
    tool_dfs = UIStateMachineDiscovery(
        base_url="http://127.0.0.1:3000",
        headless=True,
        timeout=10000,
        max_states=5,
        use_dfs=True,
    )
    graph_dfs = await tool_dfs.discover(username="admin", password="admin")
    
    # BFS discovery
    tool_bfs = UIStateMachineDiscovery(
        base_url="http://127.0.0.1:3000",
        headless=True,
        timeout=10000,
        max_states=5,
        use_dfs=False,
    )
    graph_bfs = await tool_bfs.discover(username="admin", password="admin")
    
    # Both should discover states
    assert len(graph_dfs['states']) > 1
    assert len(graph_bfs['states']) > 1
    
    # Metadata should reflect method
    assert graph_dfs['metadata']['discovery_method'] == 'DFS'
    assert graph_bfs['metadata']['discovery_method'] == 'BFS'


if __name__ == "__main__":
    # Note: These tests require a running GenieACS instance at http://127.0.0.1:3000
    print("⚠️  Warning: These tests require GenieACS running at http://127.0.0.1:3000")
    print("Run with: pytest test_discovery_integration.py")

