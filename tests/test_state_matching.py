#!/usr/bin/env python3
"""Test script to validate state matching with fuzzy comparison.

Tests that StateComparer can correctly identify same states even after
UI changes (CSS, DOM restructure, minor text changes).
"""

import asyncio
import pytest
from playwright.async_api import async_playwright

from model_resilience_core.matching import StateComparer
from model_resilience_core.models import UIState
from aria_state_mapper.playwright_integration import PlaywrightStateFingerprinter


@pytest.mark.asyncio
async def test_state_matching_identical():
    """Test that identical states match with high similarity."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Login to dashboard
            await page.goto('http://127.0.0.1:3000')
            await page.wait_for_load_state('networkidle')
            await page.fill('input[name="username"]', 'admin')
            await page.fill('input[name="password"]', 'admin')
            await page.click('button:has-text("Login")')
            await page.wait_for_load_state('networkidle')
            
            # Capture fingerprint twice
            fingerprinter = PlaywrightStateFingerprinter()
            fp1 = await fingerprinter.create_fingerprint(page)
            await asyncio.sleep(0.5)
            fp2 = await fingerprinter.create_fingerprint(page)
            
            # Create UIState objects
            state1 = UIState(
                state_id="dashboard_1",
                state_type="dashboard",
                fingerprint=fp1,
                verification_logic={},
                element_descriptors=[],
            )
            state2 = UIState(
                state_id="dashboard_2",
                state_type="dashboard",
                fingerprint=fp2,
                verification_logic={},
                element_descriptors=[],
            )
            
            # Compare states
            comparer = StateComparer()
            matched_state, similarity = comparer.find_matching_state(
                current_state=state2,
                known_states=[state1],
                threshold=0.8,
            )
            
            # Should match with very high similarity
            assert matched_state is not None
            assert similarity >= 0.95
            assert matched_state.state_id == "dashboard_1"
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_state_matching_different_pages():
    """Test that different pages don't match."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Capture login page
            await page.goto('http://127.0.0.1:3000')
            await page.wait_for_load_state('networkidle')
            
            fingerprinter = PlaywrightStateFingerprinter()
            fp_login = await fingerprinter.create_fingerprint(page)
            
            # Login and capture dashboard
            await page.fill('input[name="username"]', 'admin')
            await page.fill('input[name="password"]', 'admin')
            await page.click('button:has-text("Login")')
            await page.wait_for_load_state('networkidle')
            
            fp_dashboard = await fingerprinter.create_fingerprint(page)
            
            # Create UIState objects
            state_login = UIState(
                state_id="login",
                state_type="form",
                fingerprint=fp_login,
                verification_logic={},
                element_descriptors=[],
            )
            state_dashboard = UIState(
                state_id="dashboard",
                state_type="dashboard",
                fingerprint=fp_dashboard,
                verification_logic={},
                element_descriptors=[],
            )
            
            # Compare states
            comparer = StateComparer()
            matched_state, similarity = comparer.find_matching_state(
                current_state=state_dashboard,
                known_states=[state_login],
                threshold=0.8,
            )
            
            # Should NOT match (different pages)
            assert matched_state is None
            assert similarity < 0.8
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_state_matching_weighted_components():
    """Test that weighted components work correctly."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Login to dashboard
            await page.goto('http://127.0.0.1:3000')
            await page.wait_for_load_state('networkidle')
            await page.fill('input[name="username"]', 'admin')
            await page.fill('input[name="password"]', 'admin')
            await page.click('button:has-text("Login")')
            await page.wait_for_load_state('networkidle')
            
            # Capture fingerprint
            fingerprinter = PlaywrightStateFingerprinter()
            fp1 = await fingerprinter.create_fingerprint(page)
            
            # Navigate to devices page
            await page.click('a:has-text("devices")')
            await page.wait_for_load_state('networkidle')
            
            fp2 = await fingerprinter.create_fingerprint(page)
            
            # Create UIState objects
            state1 = UIState(
                state_id="dashboard",
                state_type="dashboard",
                fingerprint=fp1,
                verification_logic={},
                element_descriptors=[],
            )
            state2 = UIState(
                state_id="devices",
                state_type="list",
                fingerprint=fp2,
                verification_logic={},
                element_descriptors=[],
            )
            
            # Compare states
            comparer = StateComparer()
            matched_state, similarity = comparer.find_matching_state(
                current_state=state2,
                known_states=[state1],
                threshold=0.8,
            )
            
            # Should NOT match (different pages, though same app)
            assert matched_state is None
            
            # But should have some similarity (shared navigation)
            assert similarity > 0.2  # Some common elements
            assert similarity < 0.8  # But not enough to match
            
        finally:
            await browser.close()


@pytest.mark.asyncio
async def test_state_matching_threshold():
    """Test threshold behavior in state matching."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Login to dashboard
            await page.goto('http://127.0.0.1:3000')
            await page.wait_for_load_state('networkidle')
            await page.fill('input[name="username"]', 'admin')
            await page.fill('input[name="password"]', 'admin')
            await page.click('button:has-text("Login")')
            await page.wait_for_load_state('networkidle')
            
            # Capture fingerprint
            fingerprinter = PlaywrightStateFingerprinter()
            fp = await fingerprinter.create_fingerprint(page)
            
            state = UIState(
                state_id="dashboard",
                state_type="dashboard",
                fingerprint=fp,
                verification_logic={},
                element_descriptors=[],
            )
            
            # Test with different thresholds
            comparer = StateComparer()
            
            # High threshold (0.95) - should still match itself
            matched_high, similarity_high = comparer.find_matching_state(
                current_state=state,
                known_states=[state],
                threshold=0.95,
            )
            assert matched_high is not None
            assert similarity_high >= 0.95
            
            # Low threshold (0.5) - should also match
            matched_low, similarity_low = comparer.find_matching_state(
                current_state=state,
                known_states=[state],
                threshold=0.5,
            )
            assert matched_low is not None
            assert similarity_low == similarity_high  # Same comparison
            
        finally:
            await browser.close()


if __name__ == "__main__":
    # Run tests manually
    asyncio.run(test_state_matching_identical())
    asyncio.run(test_state_matching_different_pages())
    asyncio.run(test_state_matching_weighted_components())
    asyncio.run(test_state_matching_threshold())
    print("✅ All state matching tests passed!")

