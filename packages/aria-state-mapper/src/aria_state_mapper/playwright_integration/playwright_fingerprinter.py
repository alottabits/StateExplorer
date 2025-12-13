"""
Playwright-specific wrapper for state fingerprinting.

This bridges async Playwright operations with ModelResilienceCore's
platform-agnostic fingerprinting algorithms.
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
import logging

from model_resilience_core import StateFingerprinter
from .aria_snapshot import AriaSnapshotCapture

if TYPE_CHECKING:
    from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)


class PlaywrightStateFingerprinter:
    """
    Playwright-specific wrapper for creating state fingerprints.
    
    This class handles the async operations needed to capture data from
    Playwright pages, then uses ModelResilienceCore's StateFingerprinter
    for the actual fingerprint generation.
    """
    
    def __init__(self) -> None:
        """Initialize the Playwright fingerprinter."""
        self.core_fingerprinter = StateFingerprinter()
    
    async def create_fingerprint(self, page: Page) -> dict[str, Any]:
        """Generate accessibility-tree-based state fingerprint from Playwright page.
        
        This is the async entry point that captures data from Playwright,
        then delegates to ModelResilienceCore for processing.
        
        Args:
            page: Playwright Page object
            
        Returns:
            Dictionary with accessibility-first fingerprint dimensions
        """
        # Capture accessibility tree (async Playwright operation)
        a11y_tree = await AriaSnapshotCapture.capture(page)
        
        # Capture other page properties (async)
        url = page.url
        title = await page.title()
        main_heading = await AriaSnapshotCapture.get_main_heading(page)
        
        # Use platform-agnostic fingerprinter (sync operation)
        fingerprint = self.core_fingerprinter.create_fingerprint(
            accessibility_tree=a11y_tree,
            url=url,
            title=title,
            main_heading=main_heading
        )
        
        return fingerprint
    
    async def _get_page_state(self, page: Page) -> dict[str, bool]:
        """Get page loading/ready state indicators.
        
        Args:
            page: Playwright Page object
            
        Returns:
            Dictionary of state indicators
        """
        try:
            has_errors = await page.locator('[role="alert"]').count() > 0
            is_loading = await page.locator('[aria-busy="true"]').count() > 0
            
            return {
                "ready": True,  # If we can query, page is ready
                "has_errors": has_errors,
                "is_loading": is_loading,
            }
        except Exception:
            return {
                "ready": False,
                "has_errors": False,
                "is_loading": True,
            }
    
    async def _create_element_descriptor(self, locator: Locator, elem_type: str) -> dict[str, Any] | None:
        """Create resilient multi-strategy locator descriptor.
        
        Args:
            locator: Playwright Locator object
            elem_type: Element type ("button", "input", "link", etc.)
            
        Returns:
            Element descriptor with prioritized locators, or None
        """
        try:
            descriptor = {
                "element_type": elem_type,
                "locators": {},  # Priority-ordered locators
                "metadata": {}
            }
            
            # Priority 1: data-testid (most stable)
            test_id = await locator.get_attribute('data-testid')
            if test_id:
                descriptor["locators"]["test_id"] = test_id
                descriptor["metadata"]["test_id"] = test_id
            
            # Priority 2: Role + accessible name
            role = await locator.get_attribute('role')
            aria_label = await locator.get_attribute('aria-label')
            if role:
                descriptor["locators"]["role"] = role
            if aria_label:
                descriptor["locators"]["aria_label"] = aria_label
            
            # Priority 3: Semantic attributes
            if elem_type == "input":
                input_type = await locator.get_attribute('type')
                placeholder = await locator.get_attribute('placeholder')
                name = await locator.get_attribute('name')
                if input_type:
                    descriptor["locators"]["input_type"] = input_type
                if placeholder:
                    descriptor["locators"]["placeholder"] = placeholder
                if name:
                    descriptor["locators"]["name"] = name
            
            elif elem_type == "link":
                href = await locator.get_attribute('href')
                if href:
                    descriptor["locators"]["href"] = href
            
            # Priority 4: Text content
            text = await locator.text_content()
            if text and text.strip():
                descriptor["locators"]["text"] = text.strip()
                descriptor["name"] = text.strip()  # For friendlier logging
            
            # Only return if we have at least one locator
            if descriptor["locators"]:
                return descriptor
            return None
            
        except Exception as e:
            logger.debug("Error creating element descriptor: %s", e)
            return None

