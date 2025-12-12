"""
Tests for Playwright integration.
"""

import pytest
from aria_state_mapper.playwright_integration import AriaSnapshotCapture


class TestAriaSnapshotCapture:
    """Test AriaSnapshotCapture functionality."""
    
    def test_parse_simple_yaml(self):
        """Test parsing simple ARIA snapshot YAML."""
        yaml_str = """
        - button: Click Me
        """
        
        tree = AriaSnapshotCapture._parse_yaml_snapshot(yaml_str)
        
        assert tree is not None
        assert "role" in tree
    
    def test_parse_empty_yaml(self):
        """Test parsing empty YAML."""
        yaml_str = ""
        
        tree = AriaSnapshotCapture._parse_yaml_snapshot(yaml_str)
        
        assert tree == {}

