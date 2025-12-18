# StateExplorer

A monorepo for resilient UI state mapping and model-based testing tools.

## Packages

### 1. ModelResilienceCore
**Platform-agnostic state fingerprinting and matching algorithms**

The core package containing sophisticated algorithms for:
- Multi-dimensional state fingerprinting (accessibility tree, semantic structure, functional identity)
- Weighted fuzzy matching for state comparison
- Resilience hierarchy implementation (semantic → functional → structural → content → style)

This package has no UI automation dependencies and can be used independently.

**Location**: `packages/model-resilience-core/`

### 2. AriaStateMapper
**Web application state mapping using Playwright**

Playwright-based state mapper for web applications:
- Automatic UI crawling using accessibility tree navigation
- ARIA snapshot capture and processing
- Manual action recording and augmentation
- FSM (Finite State Machine) discovery and graph generation
- Integration with ModelResilienceCore for resilient state matching

**Location**: `packages/aria-state-mapper/`

**Dependencies**: ModelResilienceCore, Playwright

### 3. AppStateMapper
**Native application state mapping using Appium**

Appium-based state mapper for native applications (iOS, Android, Linux, Windows):
- Automatic UI crawling using native accessibility APIs
- Manual action recording and augmentation
- FSM discovery for native apps
- Integration with ModelResilienceCore for resilient state matching

**Location**: `packages/app-state-mapper/`

**Status**: Future development

**Dependencies**: ModelResilienceCore, Appium

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Applications/Tests                        │
└────────────────┬───────────────────────┬────────────────────┘
                 │                       │
        ┌────────▼────────┐     ┌───────▼──────────┐
        │ AriaStateMapper │     │ AppStateMapper   │
        │  (Playwright)   │     │    (Appium)      │
        └────────┬────────┘     └───────┬──────────┘
                 │                       │
                 └───────────┬───────────┘
                             │
                    ┌────────▼─────────┐
                    │ModelResilienceCore│
                    │  (Core Algorithms)│
                    └──────────────────┘
```

## Quick Start

### Complete End-to-End Workflow

For a **step-by-step guide** covering the complete workflow from fresh discovery to manual recording to incremental discovery, see:

📖 **[Complete Workflow Guide](COMPLETE_WORKFLOW_GUIDE.md)**

This comprehensive guide walks you through:
1. **Fresh Automated Discovery** - Capture base states (10-15 states)
2. **Manual Recording** - Add complex interactions (dropdowns, overlays)
3. **Incremental Discovery** - Expand to comprehensive coverage (40+ states)

**Time**: ~30 minutes total | **Result**: Production-ready FSM graph

### Basic Usage

```bash
# 1. Install packages
pip install -e packages/model-resilience-core/
pip install -e packages/aria-state-mapper/

# 2. Install Playwright browsers
playwright install chromium firefox

# 3. Run automated discovery
aria-discover --url http://localhost:3000 --output fsm_graph.json

# 4. Manual recording (optional - for complex interactions)
python tools/manual_fsm_augmentation.py \
  --input fsm_graph.json \
  --output fsm_graph_augmented.json

# 5. Incremental discovery (optional - expand coverage)
aria-discover --seed-graph fsm_graph_augmented.json \
  --output fsm_graph_expanded.json
```

## Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd StateExplorer

# Install development dependencies (from root)
pip install -e packages/model-resilience-core/
pip install -e packages/aria-state-mapper/
pip install -e packages/app-state-mapper/

# Or install all packages in development mode
pip install -e packages/model-resilience-core/ -e packages/aria-state-mapper/ -e packages/app-state-mapper/
```

## Running Tests

```bash
# Test all packages
pytest packages/

# Test individual package
pytest packages/model-resilience-core/
pytest packages/aria-state-mapper/
pytest packages/app-state-mapper/
```

## Package Distribution

Each package can be built and published independently:

```bash
# Build a specific package
cd packages/model-resilience-core/
python -m build

# Publish to PyPI
python -m twine upload dist/*
```

## Documentation

See `docs/` directory for comprehensive documentation:
- Architecture overview
- API reference
- Examples and tutorials
- Research and validation results

## Examples

See `examples/` directory for usage examples:
- Basic state fingerprinting
- Web application crawling
- Custom state matching strategies
- Integration examples

## License

See [LICENSE](LICENSE) file for details.

## Research Background

This project builds on research into Model-Based Testing (MBT) and Finite State Machine (FSM) approaches for UI test automation, with a focus on maximizing resilience to UI changes through multi-dimensional state fingerprinting and weighted fuzzy matching.

Key innovations:
- **Accessibility tree-based fingerprinting** (60% weight on semantic identity)
- **Browser back navigation** for SPA state preservation
- **Hybrid two-stage pipeline** (structural crawl + behavioral modeling)
- **Validated results**: 99% same-state matching accuracy, 87% with data changes

