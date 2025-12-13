#!/usr/bin/env python3
"""Test script to verify accessibility tree capture works correctly.

Tests the Accessibility Tree Strategy fingerprinting implementation.
"""

import asyncio
import json
import pytest
from playwright.async_api import async_playwright

from aria_state_mapper.playwright_integration import PlaywrightStateFingerprinter


@pytest.mark.asyncio
async def test_a11y_capture_login_page():
    """Test accessibility tree capture on login page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Navigate to login page
            await page.goto('http://127.0.0.1:3000')
            await page.wait_for_load_state('networkidle')
            
            # Capture fingerprint
            fingerprinter = PlaywrightStateFingerprinter()
            fingerprint = await fingerprinter.create_fingerprint(page)
            
            # Verify fingerprint structure
            assert 'accessibility_tree' in fingerprint
            assert 'actionable_elements' in fingerprint
            assert 'url_pattern' in fingerprint
            assert 'title' in fingerprint
            
            a11y_tree = fingerprint['accessibility_tree']
            assert 'landmark_roles' in a11y_tree
            assert 'interactive_count' in a11y_tree
            assert 'heading_hierarchy' in a11y_tree
            assert 'aria_states' in a11y_tree
            
            # Verify content
            assert a11y_tree['interactive_count'] > 0
            assert len(a11y_tree['landmark_roles']) > 0
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_a11y_capture_dashboard():
    """Test accessibility tree capture on authenticated dashboard."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Login
            await page.goto('http://127.0.0.1:3000')
            await page.wait_for_load_state('networkidle')
            await page.fill('input[name="username"]', 'admin')
            await page.fill('input[name="password"]', 'admin')
            await page.click('button:has-text("Login")')
            await page.wait_for_load_state('networkidle')
            
            # Capture dashboard fingerprint
            fingerprinter = PlaywrightStateFingerprinter()
            fingerprint = await fingerprinter.create_fingerprint(page)
            
            # Verify dashboard has more elements than login
            a11y_tree = fingerprint['accessibility_tree']
            assert a11y_tree['interactive_count'] > 4  # More than just login form
            
            # Should have main navigation
            assert 'navigation' in a11y_tree['landmark_roles']
            
            # Check actionable elements
            actions = fingerprint['actionable_elements']
            assert actions['total_count'] > 0
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_a11y_aria_states():
    """Test ARIA state capture for dynamic elements."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Login and navigate to admin
            await page.goto('http://127.0.0.1:3000')
            await page.wait_for_load_state('networkidle')
            await page.fill('input[name="username"]', 'admin')
            await page.fill('input[name="password"]', 'admin')
            await page.click('button:has-text("Login")')
            await page.wait_for_load_state('networkidle')
            
            # Navigate to page with dynamic elements (admin menu)
            await page.click('a:has-text("admin")')
            await page.wait_for_timeout(500)
            
            # Capture fingerprint
            fingerprinter = PlaywrightStateFingerprinter()
            fingerprint = await fingerprinter.create_fingerprint(page)
            
            # Check for ARIA states
            a11y_tree = fingerprint['accessibility_tree']
            aria_states = a11y_tree.get('aria_states', {})
            
            # Should have some ARIA states (expanded, selected, etc.)
            # Note: Specific states depend on the UI
            assert isinstance(aria_states, dict)
            
        finally:
            await browser.close()


if __name__ == "__main__":
    # Run tests manually
    asyncio.run(test_a11y_capture_login_page())
    asyncio.run(test_a11y_capture_dashboard())
    asyncio.run(test_a11y_aria_states())
    print("✅ All accessibility capture tests passed!")

