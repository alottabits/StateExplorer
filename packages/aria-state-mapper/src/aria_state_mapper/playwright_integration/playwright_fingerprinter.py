"""
Playwright-specific wrapper for state fingerprinting.

This bridges async Playwright operations with ModelResilienceCore's
platform-agnostic fingerprinting algorithms.
"""

from __future__ import annotations
from typing import Any, TYPE_CHECKING

from model_resilience_core import StateFingerprinter
from .aria_snapshot import AriaSnapshotCapture

if TYPE_CHECKING:
    from playwright.async_api import Page


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

