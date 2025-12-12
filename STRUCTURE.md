# StateExplorer Directory Structure

This document provides a detailed overview of the StateExplorer monorepo structure.

## Root Level

```
StateExplorer/
├── .git/                      # Git repository
├── .gitignore                 # Git ignore patterns
├── LICENSE                    # MIT License
├── README.md                  # Main documentation
├── CONTRIBUTING.md            # Contribution guidelines
├── STRUCTURE.md               # This file
├── pyproject.toml             # Root-level dev dependencies
├── packages/                  # All packages (see below)
├── docs/                      # Documentation
└── examples/                  # Usage examples
```

## Package 1: ModelResilienceCore

**Platform-agnostic state fingerprinting and matching algorithms**

```
packages/model-resilience-core/
├── README.md                  # Package documentation
├── pyproject.toml             # Package configuration
├── src/
│   └── model_resilience_core/
│       ├── __init__.py        # Package entry point
│       ├── models/            # Data structures
│       │   ├── __init__.py
│       │   ├── ui_state.py              # UIState dataclass
│       │   └── state_transition.py      # StateTransition dataclass
│       ├── fingerprinting/    # State fingerprint creation
│       │   ├── __init__.py
│       │   ├── state_fingerprinter.py   # Main fingerprinter
│       │   └── accessibility_extractor.py  # A11y tree utilities
│       └── matching/          # State comparison
│           ├── __init__.py
│           ├── state_comparer.py        # Weighted fuzzy matching
│           └── similarity_metrics.py     # Similarity functions
└── tests/
    ├── test_fingerprinting.py
    └── test_matching.py
```

### Key Files

- **ui_state.py**: UIState dataclass with multi-dimensional fingerprint
- **state_transition.py**: StateTransition dataclass for FSM edges
- **state_fingerprinter.py**: Creates fingerprints from a11y trees, URLs, etc.
- **accessibility_extractor.py**: Platform-agnostic a11y tree processing
- **state_comparer.py**: Weighted similarity calculation (60% semantic, 25% functional, ...)
- **similarity_metrics.py**: Jaccard, Levenshtein, numeric similarity functions

## Package 2: AriaStateMapper

**Web application state mapping using Playwright**

```
packages/aria-state-mapper/
├── README.md                  # Package documentation
├── pyproject.toml             # Package configuration
├── src/
│   └── aria_state_mapper/
│       ├── __init__.py        # Package entry point
│       ├── discovery/         # Automatic crawling
│       │   ├── __init__.py
│       │   ├── state_machine_discovery.py  # Main discovery engine
│       │   └── ui_crawler.py               # Low-level crawler
│       ├── playwright_integration/  # Playwright utilities
│       │   ├── __init__.py
│       │   ├── aria_snapshot.py       # ARIA snapshot capture
│       │   └── element_locator.py     # Resilient element location
│       └── recording/         # Manual action recording
│           ├── __init__.py
│           └── manual_action_recorder.py
└── tests/
    ├── test_discovery.py
    └── test_playwright_integration.py
```

### Key Files

- **state_machine_discovery.py**: Main entry point for UI discovery
- **ui_crawler.py**: Low-level browser navigation and interaction
- **aria_snapshot.py**: Captures a11y trees using Playwright's native API
- **element_locator.py**: Priority-based element location (role → label → text → ...)
- **manual_action_recorder.py**: Records user actions for augmentation

### Dependencies

- model-resilience-core (core algorithms)
- playwright (browser automation)
- pyyaml (ARIA snapshot parsing)

## Package 3: AppStateMapper

**Native application state mapping using Appium (Future Development)**

```
packages/app-state-mapper/
├── README.md                  # Package documentation
├── pyproject.toml             # Package configuration
├── src/
│   └── app_state_mapper/
│       ├── __init__.py        # Package entry point (placeholder)
│       ├── discovery/         # Automatic crawling (future)
│       │   └── __init__.py
│       ├── appium_integration/  # Appium utilities (future)
│       │   └── __init__.py
│       └── recording/         # Manual action recording (future)
│           └── __init__.py
└── tests/
```

### Status

🚧 **Under Development** - Placeholder structure for future implementation

### Planned Features

- iOS support (XCUITest)
- Android support (UiAutomator2)
- Linux support (AT-SPI)
- Windows support (UI Automation)

## Documentation

```
docs/
├── README.md                  # Documentation index
├── architecture/              # System design (future)
├── research/                  # Research findings (future)
├── api/                       # API reference (future)
└── guides/                    # User guides (future)
```

## Examples

```
examples/
├── README.md                  # Examples index
├── basic_fingerprinting.py    # (future)
├── simple_discovery.py        # (future)
└── two_stage_pipeline.py      # (future)
```

## Key Design Decisions

### Monorepo Structure

- **Why**: Shared development, easier maintenance, atomic commits across packages
- **Layout**: Separate `packages/` directory with independent `pyproject.toml` per package
- **Benefits**: Each package can be published independently to PyPI

### src/ Layout

- **Why**: Best practice for Python packages, prevents import issues
- **Structure**: `packages/<package>/src/<package_name>/`
- **Benefits**: Ensures tests run against installed package, not source

### Dependency Hierarchy

```
AriaStateMapper ──┐
                  ├──> ModelResilienceCore (core algorithms)
AppStateMapper ───┘
```

- **ModelResilienceCore**: No dependencies on UI frameworks (platform-agnostic)
- **AriaStateMapper**: Depends on ModelResilienceCore + Playwright
- **AppStateMapper**: Will depend on ModelResilienceCore + Appium

### Test Organization

- **Unit tests**: Within each package's `tests/` directory
- **Integration tests**: Root-level `tests/` directory (future)
- **Test data**: Within package or root `examples/` directory

## Installation for Development

```bash
# Install all packages in editable mode
pip install -e packages/model-resilience-core/[dev]
pip install -e packages/aria-state-mapper/[dev]
pip install -e packages/app-state-mapper/[dev]
```

## Next Steps

### For ModelResilienceCore
1. Migrate state fingerprinting code from `ui_mbt_discovery.py`
2. Migrate state matching code from `ui_mbt_discovery.py`
3. Add comprehensive unit tests
4. Document API with examples

### For AriaStateMapper
1. Migrate UI discovery code from `ui_mbt_discovery.py`
2. Integrate with ModelResilienceCore
3. Add integration tests with real browser
4. Create examples and documentation

### For AppStateMapper
1. Research Appium capabilities
2. Design platform-specific abstractions
3. Implement iOS support first
4. Add Android support
5. Consider Linux/Windows support

## Questions?

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

