# ModelResilienceCore

**Platform-agnostic state fingerprinting and matching algorithms**

## Overview

ModelResilienceCore provides the foundational algorithms for resilient UI state identification and comparison. It is completely platform-agnostic and has no dependencies on UI automation frameworks.

## Features

### Multi-Dimensional State Fingerprinting

Creates robust state identifiers using multiple dimensions:
- **Semantic Identity** (60% weight): ARIA landmarks, roles, heading hierarchy
- **Functional Identity** (25% weight): Interactive elements, form fields, actionable components
- **Structural Identity** (10% weight): URL patterns, navigation context
- **Content Identity** (4% weight): Visible text, page titles
- **Style Identity** (1% weight): DOM structure hash (optional)

### Weighted Fuzzy Matching

Compares states using weighted similarity calculation:
- Configurable weights for each dimension
- Multiple similarity metrics (Jaccard, Levenshtein, structural similarity)
- Threshold-based matching (exact, strong, weak)
- Confidence scoring

### State Models

Data structures for representing UI states and transitions:
- `UIState`: Complete state representation with fingerprint
- `StateTransition`: Action-based transitions between states
- `StateGraph`: Graph structure for state machines

## Installation

```bash
pip install model-resilience-core
```

## Usage

```python
from model_resilience_core.fingerprinting import StateFingerprinter
from model_resilience_core.matching import StateComparer
from model_resilience_core.models import UIState

# Create a state fingerprinter
fingerprinter = StateFingerprinter()

# Generate fingerprint from accessibility tree
fingerprint = fingerprinter.create_fingerprint(
    accessibility_tree=a11y_tree,
    url="https://example.com/page",
    title="Example Page"
)

# Create state
state = UIState(
    state_id="example_page",
    fingerprint=fingerprint,
    state_type="page"
)

# Compare two states
comparer = StateComparer()
similarity = comparer.calculate_similarity(state1, state2)
is_match = comparer.is_match(state1, state2, threshold=0.85)
```

## Architecture

```
model_resilience_core/
├── fingerprinting/          # State fingerprint creation
│   ├── state_fingerprinter.py
│   └── accessibility_extractor.py
├── matching/                # State comparison algorithms
│   ├── state_comparer.py
│   └── similarity_metrics.py
└── models/                  # Data structures
    ├── ui_state.py
    └── state_transition.py
```

## Research Validation

This package implements algorithms validated through research on UI test resilience:
- **99% accuracy** for same-state matching
- **87% accuracy** with dynamic data changes
- **2-3x more resilient** than URL-only identification

See `docs/research/` for detailed validation results.

## Dependencies

- Python >=3.10
- pyyaml (for ARIA snapshot parsing)
- No UI automation framework dependencies

## License

See [LICENSE](../../LICENSE) file for details.

