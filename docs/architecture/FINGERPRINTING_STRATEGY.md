# State Fingerprinting Strategy

**Status**: ✅ Implemented in ModelResilienceCore & AriaStateMapper

---

## Overview

StateExplorer uses **accessibility tree-based fingerprinting** as the primary strategy for identifying and matching UI states. This approach provides maximum resilience against UI changes while capturing both state identity and available actions.

## Why Accessibility Trees?

### Key Benefits

1. **Semantic Stability**: Captures functional identity (roles, labels) rather than implementation details (CSS, DOM)
2. **Native Browser API**: Standardized across all browsers via Playwright
3. **Complete State Capture**: Includes ARIA states (expanded, selected, checked) for dynamic UIs
4. **Actionable Elements**: Automatically discovers all interactive elements (replaces manual seeding)

### Alignment with Playwright Locator Hierarchy

The accessibility tree natively captures Playwright's most stable locator types:

| Priority | Locator Type | Captured in A11y Tree |
|----------|--------------|----------------------|
| 1 | `getByTestId()` | ❌ (external contract) |
| 2 | `getByRole()` | ✅ Native roles |
| 3 | `getByLabel()`, `getByAltText()` | ✅ Accessible names |
| 4 | ARIA state attributes | ✅ Dynamic states |
| 5 | `getByText()` | ✅ Element names |

---

## Fingerprint Structure

### Multi-Dimensional Identity

State fingerprints use weighted comparison across 5 dimensions:

```python
fingerprint = {
    # 1. SEMANTIC IDENTITY (60% weight)
    "accessibility_tree": {
        "structure_hash": str,         # Tree topology
        "landmark_roles": list[str],   # ["navigation", "main"]
        "heading_hierarchy": list[str],# ["h1: Dashboard", "h2: Stats"]
        "aria_states": dict,           # {expanded: true, selected: false}
    },
    
    # 2. FUNCTIONAL IDENTITY (25% weight)
    "actionable_elements": {
        "buttons": list[dict],         # All buttons with roles/names
        "links": list[dict],           # All navigation links
        "inputs": list[dict],          # All form fields
    },
    
    # 3. STRUCTURAL IDENTITY (10% weight)
    "url_pattern": str,                # Route pattern
    
    # 4. CONTENT IDENTITY (4% weight)
    "title": str,                      # Page title
    "main_heading": str,               # Primary heading
    
    # 5. STYLE IDENTITY (1% weight)
    "dom_structure_hash": str,         # Optional fallback
}
```

### Why Weighted Comparison?

Different attributes have different stability levels:
- **ARIA roles** rarely change (accessibility contract)
- **URLs** can change during refactoring
- **DOM structure** frequently changes with styling updates

---

## ARIA State Attributes

### Critical for FSM Modeling

ARIA states capture **dynamic functional conditions** that distinguish similar pages:

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `aria-expanded` | Collapsible elements | Menu open/closed |
| `aria-selected` | Selection state | Active tab |
| `aria-checked` | Toggle state | Checkbox value |
| `aria-disabled` | Availability | Inactive button |
| `aria-current` | Current item | Active navigation |

### Example: Same URL, Different States

```
URL: #!/admin

State A: Admin menu collapsed
  aria-expanded=false
  actionable_elements: 4 (top-level only)

State B: Admin menu expanded  
  aria-expanded=true
  actionable_elements: 11 (top + 7 submenus)
```

This enables the FSM to model **behavioral states**, not just structural pages.

---

## Implementation

### Playwright Accessibility API

```python
from playwright.async_api import Page

async def capture_state_fingerprint(page: Page) -> dict:
    """Capture complete state fingerprint."""
    # Native Playwright API
    a11y_tree = await page.accessibility.snapshot()
    
    return {
        "accessibility_tree": extract_semantic_features(a11y_tree),
        "actionable_elements": extract_interactive_elements(a11y_tree),
        "url_pattern": normalize_url(page.url),
        "title": await page.title(),
    }
```

### Example Accessibility Tree

```json
{
  "role": "WebArea",
  "name": "Dashboard",
  "children": [
    {
      "role": "navigation",
      "name": "Main menu",
      "children": [
        {
          "role": "link",
          "name": "Overview",
          "value": "#!/overview"
        },
        {
          "role": "button",
          "name": "Admin",
          "expanded": true,
          "children": [
            {"role": "link", "name": "Settings"}
          ]
        }
      ]
    },
    {
      "role": "main",
      "children": [
        {"role": "heading", "level": 1, "name": "Dashboard"},
        {"role": "button", "name": "Create New"}
      ]
    }
  ]
}
```

---

## Comparison with DOM-Based Approaches

### Traditional DOM Fingerprinting (❌ Brittle)

```python
# Low stability - changes with CSS refactoring
fingerprint = {
    "dom_hash": hash(page.content()),  # Breaks on any change
    "element_count": len(elements),     # Unreliable
}
```

### Accessibility-First (✅ Resilient)

```python
# High stability - preserves semantic identity
fingerprint = {
    "landmark_roles": ["navigation", "main"],  # Stable
    "button_roles": ["Create", "Edit"],        # Functional
    "aria_states": {"expanded": true},         # Dynamic
}
```

---

## State Matching Algorithm

### Weighted Fuzzy Matching

States are compared using weighted similarity scores:

```python
def calculate_similarity(state_a: UIState, state_b: UIState) -> float:
    """Calculate weighted similarity between states."""
    scores = {
        "semantic": compare_accessibility_trees(state_a, state_b),  # 60%
        "functional": compare_actionable_elements(state_a, state_b),# 25%
        "structural": compare_url_patterns(state_a, state_b),       # 10%
        "content": compare_text_content(state_a, state_b),          # 4%
        "style": compare_dom_structure(state_a, state_b),           # 1%
    }
    
    weights = {
        "semantic": 0.60,
        "functional": 0.25,
        "structural": 0.10,
        "content": 0.04,
        "style": 0.01,
    }
    
    return sum(scores[k] * weights[k] for k in scores)
```

### Match Threshold

- **≥ 80%**: Same state (reuse existing node)
- **< 80%**: Different state (create new node)

---

## Benefits

### 1. Resilience to UI Changes

- ✅ CSS refactoring: Accessibility tree unchanged
- ✅ DOM restructuring: Semantic roles preserved
- ✅ Text changes: Roles and structure still match

### 2. Automatic Element Discovery

No manual seeding required—all interactive elements discovered automatically:

```python
actionable_elements = extract_from_accessibility_tree(tree)
# Returns: buttons, links, inputs, selects with resilient locators
```

### 3. SPA State Differentiation

Distinguishes states within Single-Page Applications:

```
State 1: Form empty        (aria-invalid=false, value="")
State 2: Form filled       (value="John")
State 3: Form with errors  (aria-invalid=true)
```

---

## Further Reading

- [State Matching Algorithm](./STATE_MATCHING.md)
- [FSM vs POM Comparison](./FSM_VS_POM.md)
- [Playwright Accessibility API](https://playwright.dev/docs/accessibility-testing)
- [ARIA States Specification](https://www.w3.org/TR/wai-aria-1.2/#states_and_properties)

