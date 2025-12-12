"""
Tests for state fingerprinting.
"""

import pytest
from model_resilience_core.fingerprinting import StateFingerprinter


class TestStateFingerprinter:
    """Test StateFingerprinter functionality."""
    
    def test_create_fingerprint_basic(self):
        """Test basic fingerprint creation."""
        fingerprinter = StateFingerprinter()
        
        fingerprint = fingerprinter.create_fingerprint(
            url="https://example.com/page",
            title="Example Page"
        )
        
        assert "url_pattern" in fingerprint
        assert "title" in fingerprint
        assert fingerprint["title"] == "Example Page"
    
    def test_url_pattern_extraction(self):
        """Test URL pattern extraction."""
        fingerprinter = StateFingerprinter()
        
        pattern = fingerprinter._extract_url_pattern(
            "https://example.com/admin/config?id=123#section"
        )
        
        assert pattern == "/admin/config"

