# StateExplorer Migration Status

**Date**: December 12, 2025 (Evening)  
**Overall Progress**: 35% Complete (1,200 / 3,400 lines migrated)

---

## Quick Status

### ✅ COMPLETE: ModelResilienceCore (100%)
- All data models, fingerprinting, and matching algorithms migrated
- Platform-agnostic, zero UI framework dependencies
- ~1,000 lines migrated from `ui_mbt_discovery.py`
- **Ready for use!**

### 🔄 IN PROGRESS: AriaStateMapper (20%)
- ARIA snapshot capture: ✅ Done
- Playwright async wrapper: ✅ Done
- **Main discovery engine: 🔄 NEXT (1,800 lines)**
- State classifier: ⏸️ Pending (250 lines)

### ⏸️ PENDING: Tests & Docs (0%)
- Tests: ~800 lines to migrate
- Documentation: ~4,000 lines to organize
- Examples: ~500 lines to create

---

## Next Session Priority

### 1. Migrate UIStateMachineDiscovery (~1,800 lines) **← START HERE**

**Source**: 
- File: `boardfarm-bdd/tests/ui_helpers/ui_mbt_discovery.py`
- Lines: 1606-3400

**Target**:
- File: `StateExplorer/packages/aria-state-mapper/src/aria_state_mapper/discovery/state_machine_discovery.py`

**Key Components to Migrate**:
- Main UIStateMachineDiscovery class
- `__init__()`, `discover()` methods
- DFS/BFS exploration strategies
- `_explore_state_dfs()`, `_explore_state_bfs()`
- Browser navigation with back button support
- Form identification: `_identify_forms()`, `_extract_form_fields()`
- Element interaction: `_execute_link_click()`, `_execute_button_click()`, `_execute_form_fill()`
- Transition recording: `_record_transition()`
- State/transition deduplication logic
- Helper methods: `_discover_current_state()`, `_create_state_from_fingerprint()`

**Dependencies Needed**:
```python
from model_resilience_core import UIState, StateTransition, StateComparer, ActionType
from ..playwright_integration import PlaywrightStateFingerprinter, AriaSnapshotCapture
from playwright.async_api import async_playwright, Page
```

**Estimated Time**: 2-3 hours

### 2. Migrate StateClassifier (~250 lines)

**Source**: 
- File: `boardfarm-bdd/tests/ui_helpers/ui_mbt_discovery.py`
- Lines: 1349-1600

**Target**:
- File: `StateExplorer/packages/aria-state-mapper/src/aria_state_mapper/discovery/state_classifier.py`

**What it Does**:
- Dynamic state type classification
- URL-based state ID generation (admin/config → V_ADMIN_CONFIG)
- Application-specific logic (can be overridden)

**Estimated Time**: 30 minutes

### 3. Create Working Example

**Create**: `StateExplorer/examples/simple_discovery.py`

**Goal**: Validate end-to-end functionality

```python
from aria_state_mapper import UIStateMachineDiscovery
import asyncio

async def main():
    discovery = UIStateMachineDiscovery(
        base_url="http://127.0.0.1:3000",
        username="admin",
        password="admin"
    )
    
    await discovery.discover(max_states=50, strategy="dfs")
    
    graph = discovery.export_graph()
    with open("fsm_graph.json", "w") as f:
        json.dump(graph, f, indent=2)
    
    print(f"Discovered {len(graph['states'])} states")
    print(f"Discovered {len(graph['transitions'])} transitions")

asyncio.run(main())
```

**Estimated Time**: 1 hour

---

## File Locations Reference

### Source Files (Migration Source)
```
/home/rjvisser/projects/req-tst/boardfarm-bdd/tests/ui_helpers/
├── ui_mbt_discovery.py (3,477 lines)
│   ├── Lines 1606-3400: UIStateMachineDiscovery  ← MIGRATE NEXT
│   └── Lines 1349-1600: StateClassifier         ← THEN THIS
├── test_a11y_capture.py
├── test_state_matching.py
└── ACCESSIBILITY_TREE_STRATEGY.md
```

### Target Files (Migration Destination)
```
/home/rjvisser/projects/req-tst/StateExplorer/packages/aria-state-mapper/
├── src/aria_state_mapper/
│   ├── discovery/
│   │   ├── state_machine_discovery.py  ← CREATE/POPULATE
│   │   ├── state_classifier.py         ← CREATE
│   │   └── __init__.py                 ← UPDATE
│   ├── playwright_integration/
│   │   ├── aria_snapshot.py           ✅ Done
│   │   └── playwright_fingerprinter.py ✅ Done
│   └── __init__.py                    ← UPDATE
└── tests/
    └── test_discovery.py              ← UPDATE
```

---

## Commands for Next Session

### Navigate to Project
```bash
cd /home/rjvisser/projects/req-tst/StateExplorer
```

### View Source Code
```bash
# See what to migrate
head -100 /home/rjvisser/projects/req-tst/boardfarm-bdd/tests/ui_helpers/ui_mbt_discovery.py | grep -A 10 "class UIStateMachineDiscovery"

# See full class definition
sed -n '1606,1700p' /home/rjvisser/projects/req-tst/boardfarm-bdd/tests/ui_helpers/ui_mbt_discovery.py
```

### Create Target File
```bash
# Edit target file
code packages/aria-state-mapper/src/aria_state_mapper/discovery/state_machine_discovery.py
```

### Test Installation
```bash
# Install packages
pip install -e packages/model-resilience-core/[dev]
pip install -e packages/aria-state-mapper/[dev]

# Test imports
python -c "from model_resilience_core import UIState, StateComparer; print('✅ Core works')"
python -c "from aria_state_mapper.playwright_integration import AriaSnapshotCapture; print('✅ Playwright integration works')"
```

---

## Migration Checklist

### UIStateMachineDiscovery Migration

**Setup**:
- [ ] Create `state_machine_discovery.py` file
- [ ] Add imports from ModelResilienceCore
- [ ] Add imports from playwright_integration
- [ ] Add Playwright async imports

**Core Class**:
- [ ] Class definition and __init__
- [ ] State/transition tracking attributes
- [ ] Configuration attributes

**Discovery Methods**:
- [ ] Main `discover()` method
- [ ] DFS exploration: `_explore_state_dfs()`
- [ ] BFS exploration: `_explore_state_bfs()`
- [ ] State discovery: `_discover_current_state()`
- [ ] Transition discovery: `_discover_transitions_from_state()`

**Browser Interaction**:
- [ ] Form methods: `_identify_forms()`, `_extract_form_fields()`, `_execute_form_fill()`
- [ ] Link methods: `_execute_link_click()`
- [ ] Button methods: `_execute_button_click()`
- [ ] Navigation: Browser back support

**State Management**:
- [ ] State creation: `_create_state_from_fingerprint()`
- [ ] State matching with StateComparer
- [ ] Transition recording: `_record_transition()`
- [ ] Deduplication logic

**Export**:
- [ ] Graph export: `export_graph()`
- [ ] JSON serialization

**Testing**:
- [ ] Update __init__.py imports
- [ ] Create basic test
- [ ] Verify end-to-end workflow

---

## Success Criteria

### Minimum Viable
- [ ] UIStateMachineDiscovery class migrated
- [ ] Basic discovery works end-to-end
- [ ] Can export FSM graph
- [ ] At least one example works

### Complete
- [ ] StateClassifier migrated
- [ ] All methods working
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Multiple examples

---

## Estimated Timeline

| Task | Time | Status |
|------|------|--------|
| UIStateMachineDiscovery | 2-3 hrs | 🔄 Next |
| StateClassifier | 30 min | ⏸️ |
| Example | 1 hr | ⏸️ |
| Tests | 2 hrs | ⏸️ |
| Docs | 1-2 hrs | ⏸️ |
| **TOTAL** | **6-8 hrs** | |

---

## Key Design Decisions

### Already Decided
1. ✅ Platform-agnostic core (ModelResilienceCore)
2. ✅ Playwright-specific in AriaStateMapper
3. ✅ Async/await throughout AriaStateMapper
4. ✅ Use PlaywrightStateFingerprinter wrapper

### To Decide Tomorrow
1. StateClassifier: Keep application-specific or make generic?
2. UIMapLoader: Still needed for seeding?
3. CLI interface: Create command-line tool?
4. Configuration: YAML config files?

---

## Quick Reference

### Import Pattern for AriaStateMapper
```python
from model_resilience_core import (
    UIState, 
    StateTransition, 
    ActionType,
    StateComparer,
    StateFingerprinter
)
from ..playwright_integration import (
    PlaywrightStateFingerprinter,
    AriaSnapshotCapture,
    ElementLocator
)
```

### Key Classes
- `UIState` - State representation (ModelResilienceCore)
- `StateTransition` - Transition representation (ModelResilienceCore)
- `StateComparer` - Fuzzy matching (ModelResilienceCore)
- `PlaywrightStateFingerprinter` - Async fingerprinting (AriaStateMapper)
- `UIStateMachineDiscovery` - Main discovery engine (AriaStateMapper - TO MIGRATE)

---

**Ready to start!** Open `state_machine_discovery.py` and begin migration from line 1606 of `ui_mbt_discovery.py`. 🚀

