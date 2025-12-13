# Migration Guide: From Original to StateExplorer

**For users migrating from the original `ui_mbt_discovery.py` to StateExplorer packages**

---

## Overview

The original `ui_mbt_discovery.py` (3,477 lines) has been refactored into a modular monorepo structure with two packages:

1. **ModelResilienceCore**: Platform-agnostic algorithms
2. **AriaStateMapper**: Playwright-specific implementation + CLI

---

## What Changed?

### Package Structure

**Before** (single file):
```
boardfarm-bdd/tests/ui_helpers/
└── ui_mbt_discovery.py (3,477 lines)
```

**After** (monorepo):
```
StateExplorer/
├── packages/
│   ├── model-resilience-core/    # Platform-agnostic
│   │   ├── models/                # UIState, StateTransition
│   │   ├── fingerprinting/        # StateFingerprinter
│   │   └── matching/              # StateComparer
│   │
│   └── aria-state-mapper/         # Playwright-specific
│       ├── discovery/             # UIStateMachineDiscovery
│       ├── playwright_integration/# Async wrappers
│       └── cli.py                 # aria-discover command
```

### Import Changes

**Before**:
```python
from ui_mbt_discovery import (
    UIStateMachineDiscovery,
    UIState,
    StateTransition,
    ActionType,
)
```

**After**:
```python
# Core models (platform-agnostic)
from model_resilience_core.models import UIState, StateTransition, ActionType
from model_resilience_core.matching import StateComparer
from model_resilience_core.fingerprinting import StateFingerprinter

# Playwright implementation
from aria_state_mapper.discovery import UIStateMachineDiscovery
from aria_state_mapper.playwright_integration import PlaywrightStateFingerprinter
```

### CLI Changes

**Before**:
```bash
python ui_mbt_discovery.py \
  --url http://localhost:3000 \
  --username admin \
  --password admin \
  --output fsm_graph.json
```

**After**:
```bash
aria-discover \
  --url http://localhost:3000 \
  --username admin \
  --password admin \
  --output fsm_graph.json
```

---

## Installation

### Step 1: Install Packages

```bash
cd StateExplorer

# Install model-resilience-core
pip install -e packages/model-resilience-core

# Install aria-state-mapper (includes CLI)
pip install -e packages/aria-state-mapper
```

### Step 2: Verify

```bash
# CLI should be available
aria-discover --help

# Python imports should work
python -c "from aria_state_mapper import UIStateMachineDiscovery; print('✓ OK')"
```

---

## Code Migration Examples

### Example 1: Basic Discovery

**Before**:
```python
import asyncio
from ui_mbt_discovery import UIStateMachineDiscovery

async def main():
    tool = UIStateMachineDiscovery(
        base_url="http://localhost:3000",
        headless=True,
        timeout=10000,
    )
    
    graph_data = await tool.discover(
        username="admin",
        password="admin",
    )
    
    print(f"Discovered {len(graph_data['states'])} states")

if __name__ == "__main__":
    asyncio.run(main())
```

**After** (identical!):
```python
import asyncio
from aria_state_mapper import UIStateMachineDiscovery  # Changed import

async def main():
    tool = UIStateMachineDiscovery(
        base_url="http://localhost:3000",
        headless=True,
        timeout=10000,
    )
    
    graph_data = await tool.discover(
        username="admin",
        password="admin",
    )
    
    print(f"Discovered {len(graph_data['states'])} states")

if __name__ == "__main__":
    asyncio.run(main())
```

**Change**: Only the import statement!

### Example 2: Custom State Matching

**Before**:
```python
from ui_mbt_discovery import StateComparer, UIState

comparer = StateComparer()
state_a = UIState(...)
state_b = UIState(...)

matched_state, similarity = StateComparer.find_matching_state(
    current_state=state_a,
    known_states=[state_b],
    threshold=0.8,
)
```

**After**:
```python
from model_resilience_core.matching import StateComparer  # Changed import
from model_resilience_core.models import UIState         # Changed import

comparer = StateComparer()
state_a = UIState(...)
state_b = UIState(...)

# Changed: Now uses instance method
matched_state, similarity = comparer.find_matching_state(
    current_state=state_a,
    known_states=[state_b],
    threshold=0.8,
)
```

**Changes**:
1. Import from `model_resilience_core` packages
2. `StateComparer` is now instance-based (not static)

### Example 3: State Fingerprinting

**Before**:
```python
from ui_mbt_discovery import StateFingerprinter

# Direct usage (not possible - was internal)
fingerprint = StateFingerprinter._create_fingerprint(page)
```

**After**:
```python
from aria_state_mapper.playwright_integration import PlaywrightStateFingerprinter

# Proper async API
fingerprinter = PlaywrightStateFingerprinter()
fingerprint = await fingerprinter.create_fingerprint(page)
```

**Changes**:
1. Use `PlaywrightStateFingerprinter` (async wrapper)
2. Proper public API with async support

---

## Breaking Changes

### 1. StateComparer is Instance-Based

**Before** (static):
```python
StateComparer.find_matching_state(...)
```

**After** (instance):
```python
comparer = StateComparer()
comparer.find_matching_state(...)
```

### 2. StateTransition Constructor Arguments

**Before**:
```python
transition = StateTransition(
    from_state="V_LOGIN",
    to_state="V_DASHBOARD",
    action_type=ActionType.CLICK,
)
```

**After**:
```python
transition = StateTransition(
    from_state_id="V_LOGIN",      # Changed: from_state → from_state_id
    to_state_id="V_DASHBOARD",    # Changed: to_state → to_state_id
    action_type=ActionType.CLICK,
)
```

### 3. Fingerprinting Method Split

**Before** (single class):
```python
# StateFingerprinter had both platform-agnostic and Playwright code
```

**After** (split):
```python
# Platform-agnostic core
from model_resilience_core.fingerprinting import StateFingerprinter

# Playwright-specific wrapper
from aria_state_mapper.playwright_integration import PlaywrightStateFingerprinter
```

---

## Feature Improvements

### 1. Better State Matching

**New**: 10 states instead of 32 for the same UI

- More logical state grouping
- ARIA state differentiation
- Weighted fuzzy matching

### 2. Smaller Graph Files

**New**: 215 KB instead of 833 KB

- Accessibility tree is more compact than DOM
- Semantic focus reduces noise

### 3. Cleaner Architecture

- Separation of concerns (core vs Playwright)
- Reusable components
- Easier testing

---

## Migration Checklist

### Code Changes

- [ ] Update imports from `ui_mbt_discovery` to `model_resilience_core` / `aria_state_mapper`
- [ ] Change `StateComparer` calls from static to instance methods
- [ ] Update `StateTransition` to use `from_state_id` / `to_state_id`
- [ ] Replace direct `StateFingerprinter` usage with `PlaywrightStateFingerprinter`

### CLI Changes

- [ ] Replace `python ui_mbt_discovery.py` with `aria-discover` command
- [ ] Update CI/CD pipelines
- [ ] Update documentation/README

### Testing

- [ ] Run discovery on test application
- [ ] Compare output with original tool
- [ ] Verify similarity scores and state counts
- [ ] Test in headless and headful modes

### Cleanup

- [ ] Remove old `ui_mbt_discovery.py` file (if desired)
- [ ] Archive old FSM graphs with `_old` suffix
- [ ] Update team documentation

---

## Compatibility Notes

### Python Version

- **Minimum**: Python 3.11+
- **Recommended**: Python 3.12+

### Dependencies

All dependencies are managed via `pyproject.toml`:

```bash
# Install automatically handles dependencies
pip install -e packages/aria-state-mapper
```

Required:
- `playwright >= 1.40.0`
- `networkx >= 3.0`

### Output Format

FSM graph JSON format is **fully compatible** with original tool. Existing parsers/consumers will work unchanged.

---

## Troubleshooting

### Import Error: `ModuleNotFoundError`

**Problem**:
```python
ModuleNotFoundError: No module named 'aria_state_mapper'
```

**Solution**:
```bash
# Ensure packages are installed in editable mode
cd StateExplorer
pip install -e packages/model-resilience-core
pip install -e packages/aria-state-mapper
```

### CLI Not Found: `aria-discover: command not found`

**Problem**: CLI script not registered

**Solution**:
```bash
# Reinstall with scripts
pip install -e packages/aria-state-mapper --force-reinstall

# Verify
which aria-discover
```

### TypeError: `find_matching_state() missing 1 required positional argument`

**Problem**: Using static method syntax on instance method

**Solution**:
```python
# Before (wrong)
StateComparer.find_matching_state(...)

# After (correct)
comparer = StateComparer()
comparer.find_matching_state(...)
```

---

## Support

### Documentation

- [Getting Started Guide](./guides/GETTING_STARTED.md)
- [Architecture Overview](./architecture/)
- [Examples](../examples/)

### Issues

Report migration issues at: (GitHub URL - TBD)

---

## Summary

The migration is straightforward:

1. ✅ **Install** new packages
2. ✅ **Update imports** (mostly mechanical)
3. ✅ **Fix breaking changes** (StateComparer, StateTransition args)
4. ✅ **Test** with your application
5. ✅ **Enjoy** better architecture and performance!

**Result**: Same functionality, better code organization, improved maintainability.

