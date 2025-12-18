# Complete Workflow Guide: Discovery → Manual Recording → Incremental Discovery

**Last Updated**: December 18, 2025  
**Status**: Production Ready ✅

---

## Overview

This guide walks you through the complete workflow for building a comprehensive FSM graph by combining automated discovery, manual recording, and incremental discovery.

**Three-Stage Pipeline:**
1. **Fresh Automated Discovery** - Capture 10-15 base states automatically
2. **Manual Recording** - Add 10-15 complex interaction states (dropdowns, overlays)
3. **Incremental Discovery** - Expand to 40+ states by continuing from augmented graph

**Time Investment**: ~30 minutes total
- Stage 1: ~5 minutes
- Stage 2: ~10-15 minutes (depends on workflow complexity)
- Stage 3: ~5-10 minutes

---

## Prerequisites

### 1. Environment Setup

```bash
cd ~/projects/req-tst
source boardfarm-bdd/.venv-3.12/bin/activate
```

### 2. Verify StateExplorer Installation

```bash
cd StateExplorer

# Install packages (editable mode)
pip install -e packages/model-resilience-core
pip install -e packages/aria-state-mapper

# Verify installation
aria-discover --help
```

### 3. Install Playwright Browsers

```bash
# Install Firefox (used by manual recording tool)
playwright install firefox

# Install Chromium (used by aria-discover)
playwright install chromium
```

### 4. Ensure GenieACS is Running

```bash
# Check if GenieACS is accessible
curl -s http://localhost:3000 | head -n 5

# Or open in browser: http://localhost:3000
```

---

## Stage 1: Fresh Automated Discovery (No Seed)

### Objective
Capture base states through automated discovery without any seed data.

### Command

```bash
cd ~/projects/req-tst/boardfarm-bdd

aria-discover \
  --url http://localhost:3000 \
  --username admin \
  --password admin \
  --max-states 20 \
  --output bf_config/gui_artifacts/genieacs/fsm_graph_fresh.json
```

### Command Options Explained

| Option | Value | Purpose |
|--------|-------|---------|
| `--url` | `http://localhost:3000` | Base URL of the application |
| `--username` | `admin` | Login credentials (if required) |
| `--password` | `admin` | Login credentials (if required) |
| `--max-states` | `20` | Limit discovery to 20 states (adjust as needed) |
| `--output` | `fsm_graph_fresh.json` | Output file path |

### Expected Output

```
Starting FSM/MBT discovery...
2025-12-18 10:00:00 - INFO - Browser launched (Chromium)
2025-12-18 10:00:02 - INFO - Navigating to: http://localhost:3000
2025-12-18 10:00:03 - INFO - Discovered state: V_LOGIN_FORM_EMPTY
2025-12-18 10:00:05 - INFO - Discovered state: V_OVERVIEW_PAGE
2025-12-18 10:00:07 - INFO - Discovered state: V_DEVICES
...
2025-12-18 10:03:30 - INFO - Discovery complete: 10 states, 58 transitions
2025-12-18 10:03:30 - INFO - FSM graph saved to fsm_graph_fresh.json
```

### Typical Results

- **States discovered**: 10-15 (login, overview, devices list, etc.)
- **Transitions found**: 40-60
- **Coverage**: Page-level navigation (60-70% of UI)

### Verification

```bash
# Check statistics
cat bf_config/gui_artifacts/genieacs/fsm_graph_fresh.json | jq '.statistics'

# Count states and transitions
echo "States: $(cat bf_config/gui_artifacts/genieacs/fsm_graph_fresh.json | jq '.nodes | length')"
echo "Transitions: $(cat bf_config/gui_artifacts/genieacs/fsm_graph_fresh.json | jq '.edges | length')"

# View state IDs
cat bf_config/gui_artifacts/genieacs/fsm_graph_fresh.json | jq '.nodes[].id'
```

### Troubleshooting

**Issue**: Login fails
```bash
# Verify credentials
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

**Issue**: No states discovered
- Check if GenieACS is running: `curl http://localhost:3000`
- Check browser console for errors
- Try increasing `--max-states` to 30

---

## Stage 2: Manual Recording to Augment the Graph

### Objective
Capture complex interactions (dropdowns, overlays, multi-step forms) that automated discovery missed.

### Command

```bash
cd ~/projects/req-tst/boardfarm-bdd

python tools/manual_fsm_augmentation.py \
  --url http://localhost:3000 \
  --input bf_config/gui_artifacts/genieacs/fsm_graph_fresh.json \
  --output bf_config/gui_artifacts/genieacs/fsm_graph_augmented.json
```

### Interactive Session

When the browser opens, you'll see:

```
INTERACTIVE RECORDING MODE
======================================================================
The browser is open. You can interact with it normally.
Commands (type in this TERMINAL, not the browser):

  's' + [Enter]     - Capture/Snapshot current browser state
  'q' + [Enter]     - Quit recording and save
======================================================================

Command (s=snapshot, q=quit):
```

### Recording Strategy

**Best Practices:**
1. Type `s` + Enter AFTER each action completes (wait for page to settle)
2. Capture significant states only (not every hover/animation)
3. Provide clear action descriptions when prompted
4. Capture overlays when they APPEAR and after they DISAPPEAR

**States to Capture:**
- ✅ Dropdown menus (open and closed states)
- ✅ Modal overlays (appear and disappear)
- ✅ Multi-step forms (each step)
- ✅ Pop-ups and confirmation dialogs
- ✅ Dynamic UI elements (appear on interaction)

### Example Workflow: Search & Reboot

**1. Login (if needed)**
```
Action: Fill username/password, click Login
Wait: Page loads
Command: s + Enter
Prompt: "logged in with credentials"
```

**2. Navigate to Devices**
```
Action: Click "Devices" link
Wait: Page loads
Command: s + Enter
Prompt: "clicked the Devices link"
```

**3. Open Search Filter Dropdown**
```
Action: Click in search filter field
Wait: Dropdown appears
Command: s + Enter
Prompt: "clicked in search filter field"
```

**4. Select Filter Type**
```
Action: Click "Serial number:" in dropdown
Wait: Dropdown closes
Command: s + Enter
Prompt: "selected Serial number from dropdown"
```

**5. Search for Device**
```
Action: Enter serial number (e.g., "SN665A3BA8824A")
Wait: Press Enter, results appear
Command: s + Enter
Prompt: "entered serial number and pressed Enter"
```

**6. Open Device Details**
```
Action: Click device link in results
Wait: Details page loads
Command: s + Enter
Prompt: "clicked device link to view details"
```

**7. Open Reboot Overlay**
```
Action: Click "Reboot" button
Wait: Confirmation overlay appears
Command: s + Enter
Prompt: "pressed Reboot button"
```

**8. Confirm Reboot**
```
Action: Click "Commit" button in overlay
Wait: Task pending state appears
Command: s + Enter
Prompt: "pressed Commit button to confirm reboot"
```

**9. Quit and Save**
```
Command: q + Enter
```

### Expected Output

```
Recording started...
State captured: V_STATE_001 (login)
Transition created: V_LOGIN_FORM_EMPTY → V_STATE_001

State captured: V_STATE_002 (devices)
Transition created: V_STATE_001 → V_STATE_002

State captured: V_STATE_003 (dropdown open)
Transition created: V_STATE_002 → V_STATE_003
...

MERGING WITH EXISTING GRAPH
============================================================
Existing graph: 10 states, 58 transitions
Computed 10 fingerprints from existing states

  Duplicate detected: V_STATE_001 matches existing V_OVERVIEW_PAGE
  Duplicate detected: V_STATE_002 matches existing V_DEVICES

Added 11 new states
Skipped 2 duplicate states

DEDUPLICATION SUMMARY
------------------------------------------------------------
Manually captured: 13 states, 12 transitions
Duplicates found: 2 states, 1 transitions
Actually added: 11 states, 11 transitions

FINAL GRAPH STATISTICS
------------------------------------------------------------
Total states: 21 (10 automated + 11 manual)
Total transitions: 69 (58 automated + 11 manual)
Manually augmented: true

Saved to: bf_config/gui_artifacts/genieacs/fsm_graph_augmented.json
```

### Verification

```bash
# Check augmented graph statistics
cat bf_config/gui_artifacts/genieacs/fsm_graph_augmented.json | jq '.statistics'

# Count manually recorded states
cat bf_config/gui_artifacts/genieacs/fsm_graph_augmented.json | jq '[.nodes[] | select(.discovered_manually == true)] | length'

# View manually recorded state types
cat bf_config/gui_artifacts/genieacs/fsm_graph_augmented.json | jq '.nodes[] | select(.discovered_manually == true) | {id, state_type}'
```

### Troubleshooting

**Issue**: "Unknown command" errors during action description
- **Fixed in current version** - Use pure asyncio (no threading race)
- Update to latest `manual_fsm_augmentation.py` if issue persists

**Issue**: Duplicates added to graph
- Check merge output for "Duplicate detected" messages
- Verify fingerprint-based deduplication is enabled
- Review statistics for `duplicate_states_skipped` count

**Issue**: Browser doesn't open
```bash
# Verify Playwright installation
playwright install firefox

# Test Firefox
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.firefox.launch(headless=False); b.close(); p.stop()"
```

---

## Stage 3: Incremental Discovery with Augmented Graph

### Objective
Continue automated discovery from the augmented graph to achieve comprehensive coverage.

### Command

```bash
cd ~/projects/req-tst/boardfarm-bdd

aria-discover \
  --url http://localhost:3000 \
  --username admin \
  --password admin \
  --seed-graph bf_config/gui_artifacts/genieacs/fsm_graph_augmented.json \
  --output bf_config/gui_artifacts/genieacs/fsm_graph_expanded.json \
  --max-states 50
```

### Command Options Explained

| Option | Value | Purpose |
|--------|-------|---------|
| `--seed-graph` | `fsm_graph_augmented.json` | Load 21 states from augmented graph |
| `--max-states` | `50` | Allow discovery of 30+ additional states |
| `--output` | `fsm_graph_expanded.json` | Save expanded graph |

### Expected Output

```
Loading seed graph from: fsm_graph_augmented.json
2025-12-18 10:15:00 - INFO - Seeded FSM from graph: 21 states, 69 transitions
2025-12-18 10:15:00 - INFO - Incremental discovery will continue from these states
2025-12-18 10:15:00 - INFO - Incremental discovery mode enabled

Starting FSM/MBT discovery...
2025-12-18 10:15:02 - INFO - Found matching state: V_LOGIN_FORM_EMPTY (99.0% similar)
2025-12-18 10:15:02 - INFO - Matched existing state: V_LOGIN_FORM_EMPTY
2025-12-18 10:15:05 - INFO - Found matching state: V_OVERVIEW_PAGE (95.5% similar)
2025-12-18 10:15:05 - INFO - Matched existing state: V_OVERVIEW_PAGE
...
2025-12-18 10:15:30 - INFO - Exploring from V_STATE_003 (dropdown state)
2025-12-18 10:15:35 - INFO - Discovered new state: V_STATE_022
2025-12-18 10:15:40 - INFO - Discovered new state: V_STATE_023
...
2025-12-18 10:18:30 - INFO - Discovery complete: 46 states, 125 transitions
2025-12-18 10:18:30 - INFO - FSM graph saved to fsm_graph_expanded.json
2025-12-18 10:18:30 - INFO -   - States discovered: 46 (21 seeded + 25 new)
2025-12-18 10:18:30 - INFO -   - Transitions found: 125 (69 seeded + 56 new)
2025-12-18 10:18:30 - INFO -   - States explored: 30
```

### Typical Results

- **States**: 40-50 (21 seeded + 20-30 new)
- **Transitions**: 100-150
- **Coverage**: 90%+ of UI (base navigation + complex interactions + discovered variations)

### Verification

```bash
# Compare all three stages
echo "=== Graph Evolution ==="
echo "Fresh:      $(cat bf_config/gui_artifacts/genieacs/fsm_graph_fresh.json | jq '.nodes | length') states, $(cat bf_config/gui_artifacts/genieacs/fsm_graph_fresh.json | jq '.edges | length') transitions"
echo "Augmented:  $(cat bf_config/gui_artifacts/genieacs/fsm_graph_augmented.json | jq '.nodes | length') states, $(cat bf_config/gui_artifacts/genieacs/fsm_graph_augmented.json | jq '.edges | length') transitions"
echo "Expanded:   $(cat bf_config/gui_artifacts/genieacs/fsm_graph_expanded.json | jq '.nodes | length') states, $(cat bf_config/gui_artifacts/genieacs/fsm_graph_expanded.json | jq '.edges | length') transitions"

# Check for duplicates (should be 0)
echo ""
echo "=== Duplicate Check ==="
cat bf_config/gui_artifacts/genieacs/fsm_graph_expanded.json | jq '.statistics.duplicate_states_skipped // 0'

# View state type distribution
echo ""
echo "=== State Types ==="
cat bf_config/gui_artifacts/genieacs/fsm_graph_expanded.json | jq '[.nodes[].state_type] | group_by(.) | map({(.[0]): length}) | add'
```

### Troubleshooting

**Issue**: No new states discovered
- Check `max-states` limit (increase to 100)
- Review seeded graph completeness
- Check if UI has more pages to discover

**Issue**: Many duplicate warnings
- Expected behavior if UI has limited variations
- Fingerprint matching working correctly
- Not a problem unless states are actually different

---

## Summary of Generated Files

```
~/projects/req-tst/boardfarm-bdd/bf_config/gui_artifacts/genieacs/

├── fsm_graph_fresh.json        # Stage 1: Fresh discovery
│   ├── States: ~10-15          #   - Automated base states
│   └── Transitions: ~40-60     #   - Page-level navigation
│
├── fsm_graph_augmented.json    # Stage 2: Manual recording
│   ├── States: ~21             #   - Base + complex interactions
│   ├── Transitions: ~69        #   - Dropdowns, overlays, forms
│   └── New: 11 states          #   - Intelligent deduplication
│
└── fsm_graph_expanded.json     # Stage 3: Incremental discovery
    ├── States: ~40-50          #   - Comprehensive coverage
    ├── Transitions: ~100-150   #   - All variations discovered
    └── New: 20-30 states       #   - Automated expansion
```

---

## Quick Verification Commands

### Compare Growth Across Stages

```bash
cd ~/projects/req-tst/boardfarm-bdd

# Function to extract stats
check_graph() {
    local file=$1
    local name=$2
    echo "$name:"
    echo "  States:      $(cat $file | jq '.nodes | length')"
    echo "  Transitions: $(cat $file | jq '.edges | length')"
    echo "  Manual:      $(cat $file | jq '[.nodes[] | select(.discovered_manually == true)] | length')"
}

# Compare all three
check_graph "bf_config/gui_artifacts/genieacs/fsm_graph_fresh.json" "Fresh     "
check_graph "bf_config/gui_artifacts/genieacs/fsm_graph_augmented.json" "Augmented "
check_graph "bf_config/gui_artifacts/genieacs/fsm_graph_expanded.json" "Expanded  "
```

### Validate Graph Quality

```bash
# Check for required fields
cat bf_config/gui_artifacts/genieacs/fsm_graph_expanded.json | jq '
{
  has_base_url: (.base_url != null),
  has_graph_type: (.graph_type != null),
  has_nodes: ((.nodes | length) > 0),
  has_edges: ((.edges | length) > 0),
  has_statistics: (.statistics != null)
}'

# Check state fingerprints (should all have them)
cat bf_config/gui_artifacts/genieacs/fsm_graph_expanded.json | jq '[.nodes[] | select(.fingerprint == null)] | length'
# Should output: 0

# Check transition metadata
cat bf_config/gui_artifacts/genieacs/fsm_graph_expanded.json | jq '[.edges[] | select(.action_type == null)] | length'
# Should output: 0
```

---

## Next Steps After Completion

### 1. Update STATE_REGISTRY in GenieAcsGUI

```python
# File: boardfarm/boardfarm3/devices/genie_acs.py

STATE_REGISTRY = {
    # Existing states
    "login": "V_LOGIN_FORM_EMPTY",
    "overview": "V_OVERVIEW_PAGE",
    "devices": "V_DEVICES",
    
    # Add manually recorded states
    "devices_dropdown_open": "V_STATE_003",
    "devices_filter_selected": "V_STATE_004",
    "device_search_results": "V_STATE_005",
    "device_details": "V_STATE_006",
    "reboot_overlay": "V_STATE_007",
    "reboot_pending": "V_STATE_008",
    # ... add more as needed
}
```

### 2. Refactor Step Definitions

Replace direct Playwright locators with FSM navigation:

```python
# Before (brittle)
page.locator('[placeholder="Search"]').fill(serial_number)
page.locator('text=Serial number:').click()

# After (resilient)
acs.gui.fsm.navigate_to_state("devices_dropdown_open")
element = acs.gui.fsm.find_element(role="option", name="Serial number:")
element.click()
```

### 3. Capture Visual Regression Baselines

```python
# In test code
acs.gui.capture_reference_screenshots([
    "login",
    "overview", 
    "devices",
    "device_details"
])
```

### 4. Run Tests

```bash
cd ~/projects/req-tst/boardfarm-bdd
source .venv-3.12/bin/activate

pytest --board-name prplos-docker-1 \
       --env-config ./bf_config/boardfarm_env_example.json \
       --inventory-config ./bf_config/boardfarm_config_example.json \
       -k "UC-ACS-GUI" -v
```

---

## Advanced Usage

### Periodic Graph Refresh

```bash
# Initial discovery (Month 1)
aria-discover --url http://prod.example.com \
  --output fsm_v1.0.0.json

# UI evolved (Month 4) - refresh graph
aria-discover --url http://prod.example.com \
  --seed-graph fsm_v1.0.0.json \
  --output fsm_v1.1.0.json
```

### Targeted Discovery

```bash
# Focus on specific workflow
aria-discover --url http://localhost:3000 \
  --seed-graph fsm_graph_augmented.json \
  --max-states 30 \
  --output fsm_graph_devices_only.json
  # Manually stop after devices workflow complete
```

### CI/CD Integration

```bash
# Automated nightly graph refresh
#!/bin/bash
DATE=$(date +%Y%m%d)
aria-discover --url http://staging.example.com \
  --seed-graph fsm_graph_production.json \
  --output fsm_graph_staging_${DATE}.json \
  --max-states 100

# Compare graphs
./compare_graphs.sh fsm_graph_production.json fsm_graph_staging_${DATE}.json
```

---

## Troubleshooting Reference

### Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Login fails** | Discovery stops at login page | Verify credentials, check GenieACS auth |
| **Browser doesn't open** | No browser window | Install Playwright browsers: `playwright install` |
| **Duplicates added** | Graph size = manually captured count | Update to latest tool with fingerprint deduplication |
| **No new states found** | Stage 3 adds 0 states | Increase `--max-states`, verify UI has more pages |
| **Action description errors** | Threading race warnings | Update to latest tool with asyncio fix |

### Debug Commands

```bash
# Check if GenieACS is accessible
curl -s http://localhost:3000 | head -n 10

# Verify Playwright installation
playwright --version
python -c "from playwright.sync_api import sync_playwright; print('OK')"

# Test graph JSON validity
cat fsm_graph_expanded.json | jq . > /dev/null && echo "Valid JSON" || echo "Invalid JSON"

# Check Python environment
which python
pip list | grep -E "playwright|aria-state-mapper|model-resilience"
```

---

## Related Documentation

- **Manual Recording Tool**: `/home/rjvisser/projects/req-tst/boardfarm-bdd/tools/README.md`
- **FSM Seed Support**: `/home/rjvisser/projects/req-tst/StateExplorer/PHASE_1_COMPLETE.md`
- **Seed Verification**: `/home/rjvisser/projects/req-tst/StateExplorer/PHASE_1.5_COMPLETE.md`
- **Guard Conditions**: `/home/rjvisser/projects/req-tst/StateExplorer/PHASE_1.7_COMPLETE.md`
- **FSM Implementation**: `/home/rjvisser/projects/req-tst/boardfarm-bdd/docs/FSM_IMPLEMENTATION_GUIDE.md`

---

## Success Criteria

✅ **Fresh Discovery**
- 10-15 states discovered
- Login flow captured
- Main navigation pages mapped

✅ **Manual Recording**
- 11+ new states added (dropdowns, overlays)
- Intelligent deduplication working (2+ duplicates detected)
- Action descriptions captured for all transitions

✅ **Incremental Discovery**
- 20-30+ new states discovered
- All seeded states preserved
- No duplicate states created
- Total coverage: 40-50 states, 100-150 transitions

✅ **Quality**
- All states have fingerprints
- All transitions have action metadata
- Graph validates as valid JSON
- Statistics section populated

---

**Last Updated**: December 18, 2025  
**Version**: StateExplorer v0.2.1 + Manual FSM Augmentation Tool v1.0  
**Status**: ✅ Production Ready

