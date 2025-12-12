# AppStateMapper

**Native application state mapping using Appium (Future Development)**

## Overview

AppStateMapper will provide state mapping capabilities for native applications on iOS, Android, Linux, and Windows platforms using Appium and native accessibility APIs.

## Status

🚧 **Under Development** - This package is planned for future implementation.

## Planned Features

### Automatic UI Crawling
- **Native accessibility API integration**: Platform-specific accessibility tree capture
- **DFS/BFS exploration strategies**: Configurable traversal
- **Multi-platform support**: iOS, Android, Linux, Windows
- **Form-based semantic modeling**: Compound actions

### State Discovery
- **Multi-dimensional fingerprinting**: Via ModelResilienceCore
- **Weighted fuzzy matching**: Resilient state identification
- **Dynamic state classification**: Activity/view-based state IDs
- **FSM generation**: Native app state machine graphs

### Manual Action Recording
- **Augment automated discovery**: Custom workflows
- **Record user interactions**: Capture manual navigation
- **Hybrid approach**: Automatic + manual exploration

### Appium Integration
- **Native accessibility snapshots**: Platform-specific APIs
- **Resilient locators**: Priority-based fallback
- **Async operations**: Non-blocking exploration
- **Multi-device support**: Physical and emulator devices

## Planned Architecture

```
app_state_mapper/
├── discovery/                    # Automatic crawling
│   ├── app_crawler.py
│   └── state_machine_discovery.py
├── appium_integration/           # Appium utilities
│   ├── accessibility_capture.py
│   ├── element_locator.py
│   └── platform/
│       ├── ios.py
│       ├── android.py
│       ├── linux.py
│       └── windows.py
└── recording/                    # Manual action recording
    └── manual_action_recorder.py
```

## Platform-Specific Considerations

### iOS
- Uses XCUITest accessibility framework
- Accessibility identifier as primary locator
- Support for iOS simulator and physical devices

### Android
- Uses UiAutomator2 accessibility framework
- Resource-id and content-desc as primary locators
- Support for Android emulator and physical devices

### Linux
- Uses AT-SPI (Assistive Technology Service Provider Interface)
- Support for GTK, Qt, and other toolkits

### Windows
- Uses UI Automation API
- Support for WPF, WinForms, and UWP applications

## Dependencies (Planned)

- Python >=3.10
- model-resilience-core (core algorithms)
- appium-python-client (mobile automation)
- Platform-specific drivers (XCUITest, UiAutomator2, etc.)

## Installation (When Available)

```bash
# Install AppStateMapper (includes ModelResilienceCore dependency)
pip install app-state-mapper

# Install Appium server
npm install -g appium

# Install platform-specific drivers
appium driver install xcuitest  # iOS
appium driver install uiautomator2  # Android
```

## Usage (Planned)

```python
from app_state_mapper import AppStateMachineDiscovery

# Create discovery engine for iOS
discovery = AppStateMachineDiscovery(
    platform="ios",
    app_path="/path/to/app.ipa",
    device_name="iPhone 14"
)

# Run discovery
await discovery.discover(
    max_states=50,
    strategy="dfs"
)

# Export FSM graph
graph = discovery.export_graph()
```

## Contributing

This package is open for contributions! If you're interested in helping develop AppStateMapper, please see our contribution guidelines.

## Timeline

Planned for development after AriaStateMapper reaches stable release.

## License

See [LICENSE](../../LICENSE) file for details.

