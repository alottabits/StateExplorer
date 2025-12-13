# StateExplorer Documentation

## Overview

Welcome to the StateExplorer documentation. This directory contains comprehensive documentation for all packages in the monorepo.

## Quick Start

- **New users**: Start with [Getting Started Guide](./guides/GETTING_STARTED.md)
- **Migrating from original**: See [Migration Guide](./MIGRATION_GUIDE.md)
- **Understanding the approach**: Read [Architecture Overview](./architecture/)

## Documentation Structure

### Architecture
Core design principles and system architecture:

- [Fingerprinting Strategy](./architecture/FINGERPRINTING_STRATEGY.md) - Accessibility tree-based state identification
- [FSM vs POM](./architecture/FSM_VS_POM.md) - Behavioral vs structural modeling comparison
- [Resilience Principles](./architecture/RESILIENCE_PRINCIPLES.md) - Building maintainable UI tests

### Guides
Practical how-to documentation:

- [Getting Started](./guides/GETTING_STARTED.md) - Quick start and basic usage
- [Migration Guide](./MIGRATION_GUIDE.md) - Migrating from original `ui_mbt_discovery.py`

### Research
Theoretical foundations and validation:

- [Model-Based Testing](./research/MODEL_BASED_TESTING.md) - MBT principles and algorithms

### Examples
- See `../examples/` directory for complete code examples

## Quick Links

- [ModelResilienceCore Package](../packages/model-resilience-core/README.md)
- [AriaStateMapper Package](../packages/aria-state-mapper/README.md)
- [AppStateMapper Package](../packages/app-state-mapper/README.md)
- [Main README](../README.md)

## Contributing

When adding documentation:
1. Place in appropriate subdirectory
2. Use Markdown format
3. Include code examples where relevant
4. Keep formatting consistent
5. Update this index

## Documentation Standards

- Use clear, concise language
- Include diagrams where helpful
- Provide code examples
- Keep documentation synchronized with code
- Version documentation with releases

