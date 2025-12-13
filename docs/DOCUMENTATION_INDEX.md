# StateExplorer Documentation Index

**Quick reference for all documentation**

---

## 🚀 Getting Started

| Document | Purpose | Audience |
|----------|---------|----------|
| [Getting Started Guide](./guides/GETTING_STARTED.md) | Quick start, installation, first discovery | New users |
| [Migration Guide](./MIGRATION_GUIDE.md) | Migrating from original `ui_mbt_discovery.py` | Existing users |

---

## 📐 Architecture

Core design principles and technical architecture:

| Document | Purpose | Key Topics |
|----------|---------|------------|
| [Fingerprinting Strategy](./architecture/FINGERPRINTING_STRATEGY.md) | How states are identified and matched | Accessibility trees, ARIA states, weighted matching |
| [FSM vs POM](./architecture/FSM_VS_POM.md) | Comparison of modeling approaches | Behavioral vs structural, when to use each |
| [Resilience Principles](./architecture/RESILIENCE_PRINCIPLES.md) | Building maintainable UI tests | Semantic locators, self-healing, anti-patterns |

---

## 🔬 Research

Theoretical foundations and validation:

| Document | Purpose | Key Topics |
|----------|---------|------------|
| [Model-Based Testing](./research/MODEL_BASED_TESTING.md) | MBT theory and algorithms | FSM modeling, graph algorithms, test generation |

---

## 📦 Package Documentation

### ModelResilienceCore

Platform-agnostic core algorithms:

- **Models**: `UIState`, `StateTransition`, `ActionType`
- **Fingerprinting**: Accessibility-based state identification
- **Matching**: Weighted fuzzy comparison

See: [`packages/model-resilience-core/README.md`](../packages/model-resilience-core/README.md)

### AriaStateMapper

Playwright-specific implementation:

- **Discovery**: `UIStateMachineDiscovery` class
- **Playwright Integration**: Async wrappers for browser automation
- **CLI**: `aria-discover` command-line tool

See: [`packages/aria-state-mapper/README.md`](../packages/aria-state-mapper/README.md)

### AppStateMapper (Future)

Appium-based mobile app state discovery:

- **Status**: Planned
- **Target**: iOS and Android apps
- **Integration**: Reuses ModelResilienceCore algorithms

See: [`packages/app-state-mapper/README.md`](../packages/app-state-mapper/README.md)

---

## 📚 Additional Resources

### Examples

Complete working code examples:

- [Simple Discovery](../examples/simple_discovery.py) - Basic discovery script
- More examples: [`examples/`](../examples/)

### Installation

Detailed installation instructions:

- [INSTALLATION.md](../INSTALLATION.md) - Package installation and setup

### Project Status

Current state and roadmap:

- [PROJECT_STATUS.md](../PROJECT_STATUS.md) - Feature completeness
- [MIGRATION_STATUS.md](../MIGRATION_STATUS.md) - Migration tracking

---

## 📖 Reading Paths

### For New Users

1. [Getting Started Guide](./guides/GETTING_STARTED.md)
2. [Fingerprinting Strategy](./architecture/FINGERPRINTING_STRATEGY.md)
3. [FSM vs POM](./architecture/FSM_VS_POM.md)
4. [Examples](../examples/)

### For Researchers

1. [Model-Based Testing](./research/MODEL_BASED_TESTING.md)
2. [Fingerprinting Strategy](./architecture/FINGERPRINTING_STRATEGY.md)
3. [Resilience Principles](./architecture/RESILIENCE_PRINCIPLES.md)

### For Migrating Users

1. [Migration Guide](./MIGRATION_GUIDE.md)
2. [Getting Started Guide](./guides/GETTING_STARTED.md)
3. [Package READMEs](../packages/)

---

## 🔍 Quick Search

### By Topic

- **State identification**: [Fingerprinting Strategy](./architecture/FINGERPRINTING_STRATEGY.md)
- **Accessibility trees**: [Fingerprinting Strategy](./architecture/FINGERPRINTING_STRATEGY.md)
- **ARIA states**: [Fingerprinting Strategy](./architecture/FINGERPRINTING_STRATEGY.md)
- **FSM modeling**: [FSM vs POM](./architecture/FSM_VS_POM.md), [Model-Based Testing](./research/MODEL_BASED_TESTING.md)
- **Playwright**: [Resilience Principles](./architecture/RESILIENCE_PRINCIPLES.md), [Getting Started](./guides/GETTING_STARTED.md)
- **Self-healing**: [Resilience Principles](./architecture/RESILIENCE_PRINCIPLES.md)
- **Installation**: [Getting Started](./guides/GETTING_STARTED.md), [INSTALLATION.md](../INSTALLATION.md)
- **CLI usage**: [Getting Started](./guides/GETTING_STARTED.md)
- **Graph algorithms**: [Model-Based Testing](./research/MODEL_BASED_TESTING.md)

### By Use Case

- **I want to discover my UI**: [Getting Started Guide](./guides/GETTING_STARTED.md)
- **I'm migrating from old tool**: [Migration Guide](./MIGRATION_GUIDE.md)
- **I need to understand the theory**: [Model-Based Testing](./research/MODEL_BASED_TESTING.md)
- **I want resilient tests**: [Resilience Principles](./architecture/RESILIENCE_PRINCIPLES.md)
- **I'm comparing to POM**: [FSM vs POM](./architecture/FSM_VS_POM.md)

---

## 📝 Contributing to Documentation

When adding documentation:

1. Place in appropriate subdirectory (`architecture/`, `guides/`, `research/`)
2. Use Markdown format with clear headings
3. Include code examples where relevant
4. Add to this index
5. Link from related documents

### Documentation Standards

- **Clear structure**: Use headings, tables, code blocks
- **Practical examples**: Show real code, not pseudocode
- **Visual aids**: ASCII diagrams, tables for comparisons
- **Cross-references**: Link to related docs
- **Concise**: Focus on essential information

---

## 🆘 Need Help?

- **Can't find something?** Check [README.md](./README.md)
- **Have questions?** See [Getting Started FAQ](./guides/GETTING_STARTED.md#troubleshooting)
- **Found an issue?** Open an issue on GitHub (URL TBD)

