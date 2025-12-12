# StateExplorer Examples

## Overview

This directory contains examples demonstrating how to use the StateExplorer packages.

## Examples by Package

### ModelResilienceCore Examples
- `basic_fingerprinting.py` - Basic state fingerprinting
- `custom_weights.py` - Custom similarity weights
- `state_comparison.py` - Comparing states

### AriaStateMapper Examples
- `simple_discovery.py` - Basic web app discovery
- `custom_config.py` - Custom discovery configuration
- `manual_recording.py` - Recording manual actions
- `two_stage_pipeline.py` - POM + FSM pipeline

### AppStateMapper Examples (Future)
- `ios_discovery.py` - iOS app discovery
- `android_discovery.py` - Android app discovery

## Running Examples

```bash
# Navigate to examples directory
cd examples

# Install dependencies
pip install -e ../packages/model-resilience-core/
pip install -e ../packages/aria-state-mapper/

# Run an example
python basic_fingerprinting.py
```

## Example Structure

Each example includes:
- Clear comments explaining each step
- Expected output description
- Prerequisites and setup instructions
- Links to relevant documentation

## Contributing Examples

When adding examples:
1. Keep examples focused on a single concept
2. Include clear comments
3. Provide expected output
4. Test examples before committing
5. Update this README

## Example Data

Some examples may require test applications or data:
- `test_apps/` - Sample applications for testing
- `test_data/` - Sample data files

## Questions?

See the main documentation in `docs/` for more detailed information.

