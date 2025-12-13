# FSM vs POM: Two Approaches to UI Modeling

**Status**: StateExplorer uses FSM (Finite State Machine) approach

---

## Overview

StateExplorer implements a **Finite State Machine (FSM)** model for UI discovery, which differs fundamentally from the traditional **Page Object Model (POM)** approach.

## Quick Comparison

| Aspect | POM (Page Object Model) | FSM (Finite State Machine) |
|--------|-------------------------|----------------------------|
| **Focus** | Structural (pages) | Behavioral (states) |
| **Nodes** | Physical pages/URLs | Verifiable states |
| **Edges** | Navigation links | User actions/transitions |
| **Granularity** | Page-level | Interaction-level |
| **State Identity** | URL-based | Multi-dimensional fingerprint |
| **Best For** | Static sites | Dynamic SPAs |

---

## Page Object Model (POM)

### Structure-Centric Approach

```
┌─────────────────────────────────────┐
│ POM: Pages as Nodes                 │
│                                      │
│  [Login Page] ──click──> [Dashboard]│
│      │                        │      │
│      └────────────────────────┘      │
│           (URL-based identity)       │
└─────────────────────────────────────┘
```

### Characteristics

- **Nodes**: Physical pages (1 node = 1 URL)
- **Edges**: Navigation links between pages
- **Identity**: URL patterns
- **Locators**: CSS/XPath selectors

### Example POM Graph

```json
{
  "nodes": [
    {
      "id": "page_1",
      "url": "http://app.com/login",
      "elements": {
        "username_input": "#username",
        "password_input": "#password",
        "submit_button": ".btn-login"
      }
    },
    {
      "id": "page_2", 
      "url": "http://app.com/dashboard",
      "elements": {
        "nav_menu": ".sidebar",
        "content_area": "#main"
      }
    }
  ],
  "edges": [
    {
      "from": "page_1",
      "to": "page_2",
      "action": "click_link",
      "element": ".login-link"
    }
  ]
}
```

### Limitations

❌ **URL-only identity**: Same URL can represent different functional states  
❌ **No intermediate states**: Misses "form half-filled" or "menu expanded"  
❌ **Brittle locators**: CSS/XPath breaks with refactoring  
❌ **Poor SPA support**: Single-page apps don't change URLs  

---

## Finite State Machine (FSM)

### Behavior-Centric Approach

```
┌──────────────────────────────────────────────────┐
│ FSM: States as Nodes                             │
│                                                   │
│  [Empty Form] ──type username──> [Username Entered]│
│       │                               │           │
│       │                               v           │
│       └──────────> [Form Complete] ──submit──>   │
│                    [Dashboard]                    │
│                                                   │
│  (Multi-dimensional fingerprint identity)        │
└──────────────────────────────────────────────────┘
```

### Characteristics

- **Nodes**: Verifiable states (semantic fingerprints)
- **Edges**: User actions (clicks, types, submits)
- **Identity**: Accessibility tree + ARIA states + URL
- **Locators**: Multi-strategy resilient descriptors

### Example FSM Graph

```json
{
  "states": [
    {
      "state_id": "V_LOGIN_FORM_EMPTY",
      "state_type": "form",
      "fingerprint": {
        "accessibility_tree": {
          "landmark_roles": ["navigation", "main"],
          "aria_states": {},
          "interactive_count": 4
        },
        "actionable_elements": {
          "buttons": [{"role": "button", "name": "Sign In"}],
          "inputs": [
            {"role": "textbox", "name": "Username"},
            {"role": "textbox", "name": "Password", "type": "password"}
          ]
        },
        "url_pattern": "/login"
      }
    },
    {
      "state_id": "V_LOGIN_USERNAME_FILLED",
      "state_type": "form",
      "fingerprint": {
        "accessibility_tree": {
          "aria_states": {"invalid": false},
          "interactive_count": 4
        },
        "actionable_elements": {
          "buttons": [{"role": "button", "name": "Sign In", "disabled": false}]
        },
        "url_pattern": "/login"
      }
    }
  ],
  "transitions": [
    {
      "from_state_id": "V_LOGIN_FORM_EMPTY",
      "to_state_id": "V_LOGIN_USERNAME_FILLED",
      "action_type": "fill",
      "action_target": "Username",
      "action_value": "admin"
    }
  ]
}
```

### Advantages

✅ **Multi-dimensional identity**: Semantic + functional + structural  
✅ **Intermediate states**: Captures workflow granularity  
✅ **Resilient locators**: Accessibility-based (stable)  
✅ **Excellent SPA support**: ARIA states differentiate same-URL states  

---

## Real-World Example

### Scenario: Admin Menu Interaction

#### POM Approach (1 Node)

```json
{
  "node": {
    "id": "admin_page",
    "url": "#!/admin",
    "elements": {
      "menu_button": "button[aria-label='Admin']",
      "submenu_items": ".admin-submenu a"
    }
  }
}
```

**Problem**: Doesn't distinguish between menu collapsed vs expanded.

#### FSM Approach (2 States)

```json
{
  "states": [
    {
      "state_id": "V_ADMIN_MENU_COLLAPSED",
      "fingerprint": {
        "aria_states": {"expanded": false},
        "actionable_elements": {
          "buttons": [{"name": "Admin", "expanded": false}],
          "links": []
        }
      }
    },
    {
      "state_id": "V_ADMIN_MENU_EXPANDED",
      "fingerprint": {
        "aria_states": {"expanded": true},
        "actionable_elements": {
          "buttons": [{"name": "Admin", "expanded": true}],
          "links": [
            {"name": "Presets"},
            {"name": "Provisions"},
            {"name": "Config"}
          ]
        }
      }
    }
  ],
  "transitions": [
    {
      "from_state_id": "V_ADMIN_MENU_COLLAPSED",
      "to_state_id": "V_ADMIN_MENU_EXPANDED",
      "action_type": "click",
      "action_target": "Admin"
    }
  ]
}
```

**Benefit**: Models actual user interaction and distinguishes functional states.

---

## When to Use Each

### Use POM When:
- Simple multi-page applications
- URLs reliably indicate state
- No complex interactions needed
- Fast structural mapping required

### Use FSM When:
- Single-Page Applications (SPAs)
- Complex user workflows
- Dynamic UI states (modals, forms, menus)
- Model-Based Testing needed
- Maximum resilience required

---

## StateExplorer's Choice

StateExplorer uses **FSM** because:

1. **Modern UIs are SPAs**: Most apps use React/Vue/Angular with minimal URL changes
2. **Behavioral testing**: Need to model user workflows, not just navigation
3. **Resilience**: Accessibility-based fingerprints survive refactoring
4. **Model-Based Testing**: FSM enables algorithmic test generation

---

## Hybrid Approach (Optional)

Some teams use a two-stage process:

1. **Stage 1**: Fast POM crawl to discover all pages (2-3 minutes)
2. **Stage 2**: Deep FSM exploration of critical flows (10-15 minutes)

This combines speed (POM) with depth (FSM).

---

## Further Reading

- [State Fingerprinting Strategy](./FINGERPRINTING_STRATEGY.md)
- [Model-Based Testing Overview](../research/MODEL_BASED_TESTING.md)
- [GraphWalker Documentation](https://graphwalker.github.io/)

