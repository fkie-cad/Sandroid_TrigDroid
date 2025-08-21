# TrigDroid Tests

This directory contains comprehensive tests for the TrigDroid Android security testing framework.

## Test Structure

```
tests/
├── conftest.py                  # Shared pytest configuration and fixtures
├── unit/                        # Unit tests (fast, isolated)
│   ├── test_config.py          # TestConfiguration class tests
│   ├── test_enums.py           # Enum classes tests
│   ├── test_test_runners.py    # Test runner classes tests
│   └── test_dependency_injection.py # DI container tests
├── integration/                 # Integration tests (require setup)
│   ├── test_api_integration.py # API integration tests
│   └── test_device_integration.py # Device management integration tests
└── utils/                       # Test utilities and helpers
    └── test_helpers.py         # Helper classes and functions
```

## Running Tests

### All Tests
```bash
pytest
```

### Unit Tests Only (Fast)
```bash
pytest -m unit
```

### Integration Tests
```bash
pytest -m integration
```

### Tests Requiring Android Device
```bash
pytest -m requires_device
```

### Tests Requiring Frida
```bash
pytest -m requires_frida
```

### Exclude Slow Tests
```bash
pytest -m "not slow"
```

### With Coverage Report
```bash
pytest --cov=src/trigdroid --cov-report=html
```

## Test Categories

### Unit Tests
- **Fast execution** (< 1 second per test)
- **No external dependencies** (mocked)
- **High coverage** of core logic
- **Isolated components** testing

### Integration Tests
- **Component interaction** testing
- **May require setup** (Android device, Frida)
- **Real environment** testing when possible
- **End-to-end workflows**

## Test Markers

Tests are marked with pytest markers for easy filtering:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Slow tests (may take > 10 seconds)
- `@pytest.mark.requires_device` - Requires Android device/emulator
- `@pytest.mark.requires_frida` - Requires Frida instrumentation
- `@pytest.mark.requires_root` - Requires root/admin access

## Test Utilities

The `tests/utils/` directory contains helper classes and functions:

### Builders
- `ConfigurationBuilder` - Fluent interface for creating test configurations
- `MockDeviceBuilder` - Builder for mock Android devices with specific behaviors
- `TestResultBuilder` - Builder for test result objects

### Helpers
- `TestAPKBuilder` - Create test APK files
- `ProcessHelper` - External process management
- `TimeHelper` - Time-related utilities
- `LogCapture` - Capture and analyze log output
- `AssertionHelpers` - Custom assertion methods

### Example Usage
```python
# Create a mock device with specific packages
device = (MockDeviceBuilder()
          .with_device_id("emulator-5554")
          .with_installed_packages(["com.example.test"])
          .build())

# Create an advanced test configuration
config = (ConfigurationBuilder()
          .with_package("com.example.test")
          .with_sensors(acceleration=8, gyroscope=5)
          .with_frida(True)
          .build())

# Capture log output
logger = LogCapture()
# ... run code that logs
assert logger.has_message("INFO", "Test completed")
```

## Fixtures

The `conftest.py` file provides shared fixtures:

- `mock_logger` - Mock logger implementation
- `mock_android_device` - Mock Android device
- `mock_test_context` - Mock test context
- `basic_test_configuration` - Basic test configuration
- `advanced_test_configuration` - Advanced test configuration
- `real_android_device` - Real device for integration tests (requires device)

## Requirements for Device Tests

Tests marked with `@pytest.mark.requires_device` require:

1. **Android device or emulator** connected via USB or running locally
2. **USB debugging enabled** on the device
3. **ADB accessible** in system PATH
4. **Device authorized** for debugging

Tests marked with `@pytest.mark.requires_frida` require:

1. **Frida installed** (`pip install frida`)
2. **Frida server** running on target device (for device tests)
3. **Root access** may be required for some Frida operations

## CI/CD Integration

Tests are designed to work in CI/CD environments:

- **Unit tests** run in any environment
- **Integration tests** can be skipped if requirements not met
- **Device tests** automatically skip if no device available
- **Coverage reports** generated for analysis

## Writing New Tests

When adding new tests:

1. **Follow naming convention**: `test_*.py` files, `test_*` functions
2. **Use appropriate markers** for test categorization
3. **Mock external dependencies** in unit tests
4. **Use provided fixtures** and helpers when possible
5. **Write descriptive test names** that explain the scenario
6. **Test both happy path and edge cases**
7. **Ensure proper cleanup** in integration tests

### Test Structure Template
```python
def test_component_should_behave_correctly_when_condition():
    """Test component behavior under specific conditions."""
    # Arrange
    setup_test_data()
    
    # Act
    result = perform_action()
    
    # Assert
    assert result == expected_value
    verify_side_effects()
```

## Debugging Tests

For debugging failed tests:

```bash
# Run with verbose output
pytest -v

# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Show local variables in tracebacks
pytest -l

# Run specific test
pytest tests/unit/test_config.py::TestTestConfiguration::test_create_basic_configuration_should_succeed
```

## Performance

Test performance guidelines:

- **Unit tests** should complete in < 1 second
- **Integration tests** should complete in < 30 seconds
- **Device tests** may take longer but should have reasonable timeouts
- **Use mocks** to avoid slow operations in unit tests
- **Mark slow tests** appropriately for optional execution