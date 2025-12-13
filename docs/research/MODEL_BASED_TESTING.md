# Model-Based Testing (MBT) Overview

**Purpose**: Understand the theoretical foundation of StateExplorer's approach

---

## What is Model-Based Testing?

Model-Based Testing (MBT) is a software testing technique where:

1. **A model is created** representing the system's behavior (states and transitions)
2. **Test cases are generated automatically** from the model using algorithms
3. **Tests are executed** against the actual system
4. **Results are compared** to model predictions

### Key Distinction

- **Traditional testing**: Manual test case design
- **Model-Based testing**: Algorithmic test generation from behavioral model

---

## Why MBT for UI Testing?

### The Problem with Traditional Approaches

❌ **Manual test authoring** is slow and incomplete:
- Impossible to cover all paths manually
- Tests become outdated as UI evolves
- No systematic coverage metrics

❌ **Record & replay** is brittle:
- Breaks with any UI change
- No abstraction layer
- Hard-coded selectors

### The MBT Solution

✅ **Systematic coverage**:
- Graph algorithms ensure all paths are tested
- Coverage metrics (edge coverage, state coverage)
- Automatic test generation

✅ **Maintainability**:
- Model separates test logic from implementation
- UI changes only require model updates
- Self-healing via fuzzy matching

---

## Core Concepts

### 1. Finite State Machine (FSM)

A mathematical model consisting of:

- **States (S)**: Distinct, verifiable conditions of the system
- **Transitions (T)**: Actions that move between states
- **Initial State (S₀)**: Starting point
- **Final States (Sₓ)**: Terminal states (optional)

**Example FSM**:

```
S = {Login, Dashboard, Settings, Logout}
T = {
  (Login, Dashboard, "click login"),
  (Dashboard, Settings, "click settings"),
  (Settings, Dashboard, "click back"),
  (Dashboard, Logout, "click logout")
}
S₀ = Login
```

### 2. Graph Representation

FSMs map naturally to directed graphs:

```
┌────────┐  click login   ┌───────────┐
│ Login  │───────────────>│ Dashboard │
└────────┘                └─────┬─────┘
                                │
                    click       │       click
                    settings    │       back
                                │
                          ┌─────▼──────┐
                          │  Settings  │
                          └────────────┘
```

### 3. Path Coverage

Test generation algorithms ensure coverage:

- **State coverage**: Visit every state at least once
- **Edge coverage**: Execute every transition at least once
- **Path coverage**: Test all possible paths (may be infinite)

---

## StateExplorer's Implementation

### Discovery Phase

**Input**: Base URL, credentials  
**Process**: Automated exploration (DFS/BFS)  
**Output**: FSM graph (JSON)

```python
async def discover() -> dict:
    """Automatically discover FSM model."""
    states = set()
    transitions = []
    
    # Start from initial state
    current_state = await capture_state(page)
    states.add(current_state)
    
    # Explore all reachable states
    while not explored_all(states):
        actions = discover_actions(current_state)
        
        for action in actions:
            next_state = await execute_action(action)
            
            if next_state not in states:
                states.add(next_state)
                transitions.append((current_state, next_state, action))
            
            current_state = next_state
    
    return {"states": states, "transitions": transitions}
```

### Execution Phase (Future)

**Input**: FSM graph  
**Process**: Graph traversal algorithm  
**Output**: Test execution results

```python
def generate_tests(fsm: FSMGraph) -> list[TestCase]:
    """Generate tests using graph algorithms."""
    test_cases = []
    
    # Example: Edge coverage strategy
    for edge in fsm.transitions:
        path = find_shortest_path(fsm.initial_state, edge.from_state)
        path.append(edge)
        test_cases.append(TestCase(path))
    
    return test_cases
```

---

## Graph Algorithms for Test Generation

### 1. Edge Coverage (Basic)

**Goal**: Execute every transition at least once

```python
def edge_coverage_tests(fsm: FSMGraph) -> list[TestCase]:
    """Generate tests to cover all edges."""
    tests = []
    
    for edge in fsm.transitions:
        # Find path from initial state to edge's source
        prefix = shortest_path(fsm.initial_state, edge.from_state)
        
        # Add the edge itself
        tests.append(prefix + [edge])
    
    return tests
```

**Pros**: Simple, guaranteed coverage  
**Cons**: May test same paths multiple times

### 2. Chinese Postman Problem (Optimized)

**Goal**: Cover all edges with minimum path length

```python
def chinese_postman_tests(fsm: FSMGraph) -> list[TestCase]:
    """Generate minimum-cost path covering all edges."""
    # Find optimal tour that covers all edges
    tour = find_eulerian_path(fsm)
    
    # Split tour into test cases
    return split_into_tests(tour)
```

**Pros**: Efficient, minimal redundancy  
**Cons**: More complex algorithm

### 3. Random Walk (Exploratory)

**Goal**: Random exploration for edge cases

```python
def random_walk_tests(fsm: FSMGraph, n: int) -> list[TestCase]:
    """Generate N random paths through FSM."""
    tests = []
    
    for _ in range(n):
        path = [fsm.initial_state]
        current = fsm.initial_state
        
        while not is_terminal(current):
            edges = fsm.get_outgoing_edges(current)
            next_edge = random.choice(edges)
            path.append(next_edge)
            current = next_edge.to_state
        
        tests.append(path)
    
    return tests
```

**Pros**: Finds unexpected bugs  
**Cons**: Non-systematic coverage

---

## Comparison with GraphWalker

[GraphWalker](https://graphwalker.github.io/) is a popular MBT tool that influenced StateExplorer.

### Similarities

✅ **FSM-based modeling**  
✅ **Graph traversal for test generation**  
✅ **Stop conditions** (edge coverage, state coverage, time limit)  
✅ **Generators** (shortest path, random walk, A*)

### Differences

| Aspect | GraphWalker | StateExplorer |
|--------|-------------|---------------|
| **Model creation** | Manual (JSON/GraphML) | Automated (discovery) |
| **Technology** | Java | Python + Playwright |
| **Element locators** | External (Page Objects) | Integrated (accessibility tree) |
| **Self-healing** | No | Yes (fuzzy matching) |
| **Target** | General MBT | UI testing specific |

---

## Benefits of MBT for UI Testing

### 1. Comprehensive Coverage

```
Traditional: 20 manual test cases (maybe 40% coverage)
MBT: 200+ generated test cases (95%+ coverage)
```

### 2. Automated Maintenance

When UI changes:
- **Traditional**: Update 20 test scripts manually
- **MBT**: Update model once, regenerate tests

### 3. Objective Metrics

- **State coverage**: 95% (19/20 states visited)
- **Edge coverage**: 100% (58/58 transitions tested)
- **Path coverage**: 85% (partial)

### 4. Bug Detection

Graph algorithms explore paths humans might miss:

```
Example: Found edge case via random walk
  Login -> Dashboard -> Admin -> Files -> Back -> Back -> Devices (ERROR)
```

---

## Challenges & Limitations

### 1. Model Accuracy

**Challenge**: Model must match actual system  
**Solution**: Automated discovery + periodic re-discovery

### 2. State Explosion

**Challenge**: Complex UIs have thousands of states  
**Solution**: State abstraction, prioritization

### 3. Non-Determinism

**Challenge**: System behavior is random (ads, recommendations)  
**Solution**: Normalize states, accept similarity thresholds

### 4. Learning Curve

**Challenge**: Team needs to understand FSM concepts  
**Solution**: Good documentation, examples, training

---

## Real-World Application

### Example: E-Commerce Checkout

**Manual approach**: Write 5 tests
1. Happy path
2. Invalid credit card
3. Expired card
4. Wrong CVV
5. Cancel checkout

**MBT approach**: Generate 30+ tests
- All manual cases
- Plus: back button edge cases, form validation combinations, session timeout, etc.

**Result**: Found 3 bugs in "back button during payment processing" flow that manual tests missed.

---

## Future Enhancements

StateExplorer roadmap:

1. ✅ **Discovery**: Automated FSM generation (complete)
2. 🔄 **Execution**: Graph-based test generation (in progress)
3. 📅 **Oracles**: Automatic assertion generation
4. 📅 **Optimization**: Multi-objective test suite optimization
5. 📅 **Visualization**: Interactive FSM editor

---

## Further Reading

### Academic Papers
- Utting, M., & Legeard, B. (2007). *Practical Model-Based Testing*
- Binder, R. V. (1999). *Testing Object-Oriented Systems: Models, Patterns, and Tools*

### Tools
- [GraphWalker](https://graphwalker.github.io/) - Java-based MBT tool
- [Spec Explorer](https://www.microsoft.com/en-us/research/project/spec-explorer/) - Microsoft's MBT tool
- [TorX](http://www.cs.ru.nl/~pieter/TorX/) - Model-based testing tool

### StateExplorer Docs
- [Architecture: FSM vs POM](../architecture/FSM_VS_POM.md)
- [Getting Started Guide](../guides/GETTING_STARTED.md)

