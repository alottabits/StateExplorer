"""
AriaStateMapper - Web application state mapping using Playwright.

This package provides tools for discovering and mapping UI states in web applications
using Playwright and accessibility tree analysis.
"""

__version__ = "0.1.0"

from .discovery import UIStateMachineDiscovery, StateClassifier, UIMapLoader
from .playwright_integration import (
    AriaSnapshotCapture,
    ElementLocator,
    PlaywrightStateFingerprinter,
)

__all__ = [
    "UIStateMachineDiscovery",
    "StateClassifier",
    "UIMapLoader",
    "AriaSnapshotCapture",
    "ElementLocator",
    "PlaywrightStateFingerprinter",
]

