"""Pytest configuration for StateExplorer tests."""

import pytest


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "requires_server: marks tests that require a running web server"
    )


@pytest.fixture(scope="session")
def base_url():
    """Base URL for test server (GenieACS)."""
    return "http://127.0.0.1:3000"


@pytest.fixture(scope="session")
def test_credentials():
    """Test credentials for login."""
    return {
        "username": "admin",
        "password": "admin",
    }

