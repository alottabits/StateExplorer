"""
ModelResilienceCore - Platform-agnostic state fingerprinting and matching algorithms.

This package provides the core algorithms for resilient UI state identification
and comparison, with no dependencies on specific UI automation frameworks.

Key Features:
- Multi-dimensional state fingerprinting (60% semantic, 25% functional, ...)
- Weighted fuzzy matching for resilient state comparison
- Platform-agnostic accessibility tree processing
- No UI framework dependencies (works with Playwright, Appium, etc.)
"""

__version__ = "0.1.0"

from .models import UIState, StateTransition, ActionType
from .fingerprinting import StateFingerprinter, AccessibilityExtractor
from .matching import StateComparer, SimilarityMetrics

__all__ = [
    "UIState",
    "StateTransition",
    "ActionType",
    "StateFingerprinter",
    "AccessibilityExtractor",
    "StateComparer",
    "SimilarityMetrics",
]

