# TrigDroid

**Android Sandbox Payload Trigger Framework for Security Research**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-90%25-green.svg)]()

TrigDroid is a modern Android security testing framework designed to trigger payloads in potentially malicious Android applications through sophisticated environmental manipulation. Built for security researchers, malware analysts, and penetration testers, it provides both a powerful command-line interface and a flexible Python API. It is part of the Android Sandbox Sandroid.

## Key Features

- **Payload Trigger Detection**: Sophisticated environmental manipulation to trigger hidden malicious behaviors
- **Multi-Device Support**: Works with physical devices and emulators
- **Dual Interface**: Both CLI and Python API for maximum flexibility  
- **Frida Integration**: Advanced runtime instrumentation with TypeScript hooks
- **Network Manipulation**: WiFi, mobile data, and Bluetooth state changes
- **Sensor Simulation**: Accelerometer, gyroscope, light, pressure, and more
- **Battery Simulation**: Dynamic battery level and charging state changes
- **Comprehensive Reporting**: Detailed test results with timing and metrics
- **Modern Architecture**: Built with SOLID principles and type safety

## Quick Start

### Installation

```bash
# Install TrigDroid with full features
pip install trigdroid[full]

# Install minimal version
pip install trigdroid

# Install with specific features
pip install trigdroid[frida]  # Just Frida support
pip install trigdroid[dev]    # Development tools
```

### Prerequisites

- **Python 3.9+**
- **Android Debug Bridge (ADB)**
- **Android device or emulator** with USB debugging enabled
- **Node.js** (optional, for TypeScript Frida hooks)

### Basic Usage

```bash
# Test an Android app with basic payload triggers
trigdroid -p com.example.app

# Advanced testing with sensor manipulation
trigdroid -p com.suspicious.app --acceleration 8 --battery 3 --wifi

# List available Android devices
trigdroid devices

# Get detailed app information
trigdroid info com.example.app
```

## Command Line Interface

### Core Commands

```bash
# Basic app analysis
trigdroid -p <package_name>

# Advanced options
trigdroid -p com.example.app \
  --acceleration 5 \           # Sensor elaborateness (0-10)
  --battery 3 \               # Battery rotation level (0-4)
  --wifi \                    # Enable WiFi state changes
  --data \                    # Enable mobile data changes
  --frida \                   # Enable Frida hooks
  --timeout 600               # Test timeout in seconds
```

### Device Management

```bash
# List all connected devices
trigdroid devices

# Get detailed device information
trigdroid devices --verbose

# Test specific device
trigdroid -p com.example.app -d emulator-5554
```

### Configuration Files

```bash
# Create configuration template
trigdroid --create-config default

# Use configuration file
trigdroid test-config config.yaml
```

### Example Configuration (config.yaml)

```yaml
package: "com.example.app"
acceleration: 5
sensors:
  - accelerometer
  - gyroscope
  - light
network_states:
  - wifi
  - data
battery_rotation: 3
frida_hooks: true
timeout: 300
verbose: true
```

## Python API

### Simple Usage

```python
from trigdroid import quick_test

# Quick test with default settings
result = quick_test("com.example.app")
print(f"Test successful: {result.success}")
```

### Advanced Usage

```python
from trigdroid import TrigDroidAPI, TestConfiguration

# Create detailed configuration
config = TestConfiguration(
    package="com.suspicious.app",
    acceleration=8,                    # High sensor activity
    sensors=["accelerometer", "gyroscope", "light"],
    network_states=["wifi", "data"],   # Network state changes
    battery_rotation=3,                # Battery level simulation
    frida_hooks=True,                  # Enable runtime instrumentation
    timeout=600,                       # 10 minute timeout
    verbose=True
)

# Run comprehensive test
with TrigDroidAPI() as trigdroid:
    trigdroid.configure(config)
    result = trigdroid.run_tests()
    
    # Analyze results
    if result.success:
        print(f"Test completed in {result.duration_seconds:.1f}s")
        print(f"Tests run: {result.total_tests}")
        print(f"Passed: {result.passed_tests}")
        print(f"Failed: {result.failed_tests}")
    else:
        print(f"Test failed: {result.error}")
        
    # Check for suspicious behavior
    if result.app_crashed:
        print("App crashed during testing")
    if result.frida_errors:
        print(f"Frida instrumentation issues: {result.frida_errors}")
    
    # Access detailed metrics
    print(f"Sensor tests: {len(result.sensor_tests_executed)}")
    print(f"Network changes: {len(result.network_state_changes)}")
    print(f"Background time: {result.app_background_time:.1f}s")
```

### Device Management API

```python
from trigdroid import DeviceManager, scan_devices

# Scan for available devices
devices = scan_devices()
for device in devices:
    print(f"Device: {device['id']} ({device['status']})")

# Advanced device management
manager = DeviceManager()
device = manager.connect_to_device("emulator-5554")

if device:
    print(f"Connected to: {device.device_id}")
    info = device.get_device_info()
    print(f"Model: {info.get('model', 'Unknown')}")
    print(f"Android: {info.get('version', 'Unknown')}")
```

### Environment Validation

```python
from trigdroid.api.quick_start import validate_environment, setup_environment

# Check if environment is ready
status = validate_environment()
if all(status.values()):
    print("Environment is ready!")
else:
    print("Issues found:")
    for check, result in status.items():
        if not result:
            print(f"  • {check}")

# Automatically setup environment
if setup_environment():
    print("Environment setup complete")
```

## Advanced Features

### Sensor Manipulation

TrigDroid can simulate various Android sensors to trigger environment-dependent payloads:

- **Accelerometer**: Motion detection triggers
- **Gyroscope**: Rotation-based activations  
- **Light Sensor**: Ambient light conditions
- **Pressure**: Atmospheric pressure changes
- **Magnetometer**: Magnetic field variations
- **Proximity**: Near/far object detection

```bash
# Fine-tuned sensor testing
trigdroid -p com.example.app \
  --acceleration 7 \
  --gyroscope 5 \
  --light 3 \
  --pressure 4
```

### Network State Manipulation

Simulate different connectivity scenarios:

```bash
# Test with network state changes
trigdroid -p com.example.app --wifi --data --bluetooth
```

### Frida Runtime Instrumentation

TrigDroid includes sophisticated Frida hooks written in TypeScript:

- **Method interception**: Hook critical Android APIs
- **Parameter modification**: Alter method arguments and return values
- **Behavior monitoring**: Track app interactions with system APIs
- **Anti-analysis detection**: Identify evasion techniques

### Scripts API (Programmatic Access to Frida Hooks)

TrigDroid provides a Python API for accessing compiled Frida scripts:

```python
from trigdroid.scripts import (
    get_bypass_script_path,    # Get bypass script path
    get_main_script_path,      # Get main script path
    get_hook_script_path,      # Get individual hook script path
    list_available_scripts,    # List all available scripts
    list_available_hooks,      # List available hook names
    read_script,               # Read script contents as string
)

# Get the bypass script for objection integration
bypass_path = get_bypass_script_path()
subprocess.run(["objection", "-g", package, "-s", bypass_path, "explore"])

# Get individual hooks
ssl_hook = get_hook_script_path("ssl-unpinning")
root_hook = get_hook_script_path("root-detection")

# List available hooks
hooks = list_available_hooks()
# ['ssl-unpinning', 'root-detection', 'frida-detection',
#  'emulator-detection', 'debug-detection', 'android-build', 'android-sensors']

# Load script with Frida
from trigdroid.scripts import read_script
script_source = read_script("trigdroid_bypass_bundle.js")
script = session.create_script(script_source)
```

### Bypass Script RPC API

The bypass script provides runtime-controllable bypass functionality:

```python
import frida
from trigdroid.scripts import get_bypass_script_path

# Load bypass script
session = frida.attach(pid)
with open(get_bypass_script_path()) as f:
    script = session.create_script(f.read())
script.load()

# Enable individual bypasses
script.exports_sync.enableSSLUnpinning()
script.exports_sync.enableRootBypass()
script.exports_sync.enableFridaBypass()
script.exports_sync.enableEmulatorBypass({'device_profile': 'pixel_6_pro'})
script.exports_sync.enableDebugBypass()

# Or batch enable multiple bypasses
script.exports_sync.enableBypasses({
    'ssl': True,
    'root': True,
    'emulator': {'device_profile': 'samsung_s21'}
})

# Check bypass status
status = script.exports_sync.getStatus()
print(f"SSL unpinning: {status['ssl_unpinning']}")
print(f"Root bypass: {status['root_detection']}")

# Get available device profiles for emulator bypass
profiles = script.exports_sync.getDeviceProfiles()
# ['pixel_4_xl', 'pixel_6_pro', 'samsung_s21', 'oneplus_9', 'generic']
```

### Battery and System Simulation

```bash
# Simulate battery level changes and system states
trigdroid -p com.example.app \
  --battery 4 \              # Maximum battery simulation
  --background-time 30 \     # 30 seconds in background
  --min-runtime 5            # Minimum 5 minutes runtime
```

## Understanding Results

### Test Result Structure

```python
# Example result analysis
result = api.run_tests()

# Basic status
print(f"Success: {result.success}")
print(f"Phase: {result.phase}")  # setup, execution, teardown
print(f"Duration: {result.duration_seconds}s")

# Test statistics
print(f"Total tests: {result.total_tests}")
print(f"Success rate: {result.success_rate:.1f}%")

# App behavior analysis
print(f"App started: {result.app_started}")
print(f"App crashed: {result.app_crashed}")
print(f"Background time: {result.app_background_time}s")

# Instrumentation results
print(f"Frida hooks loaded: {result.frida_hooks_loaded}")
print(f"Frida hooks active: {result.frida_hooks_active}")

# Sensor test results
for sensor, changed in result.sensor_values_changed.items():
    print(f"Sensor {sensor}: {changed} value changes")

# Export results
result_dict = result.to_dict()
summary = result.summary()  # Human-readable summary
```

### Interpreting Security Findings

**Suspicious Indicators:**
- App crashes during sensor manipulation
- Unexpected network activity during state changes
- Frida hook detection or evasion attempts
- Unusual battery usage patterns
- Background behavior changes

**Normal Behavior:**
- Consistent app performance across all tests
- No crashes or errors
- Predictable sensor responses
- Standard network usage patterns

## Development and Integration

### Third-Party Project Integration

```python
# In your security analysis tool
from trigdroid import TrigDroidAPI, TestConfiguration

def analyze_apk(package_name: str) -> dict:
    """Analyze an APK for malicious behavior."""
    config = TestConfiguration(
        package=package_name,
        acceleration=8,  # High intensity testing
        timeout=600,
        frida_hooks=True
    )
    
    with TrigDroidAPI() as trigdroid:
        result = trigdroid.run_tests()
        
        return {
            "malicious": not result.success,
            "confidence": result.success_rate,
            "indicators": {
                "crashed": result.app_crashed,
                "evasion_detected": len(result.frida_errors) > 0,
                "suspicious_network": len(result.network_state_changes) > 5
            },
            "report": result.summary()
        }

# Usage
analysis = analyze_apk("com.suspicious.app")
if analysis["malicious"]:
    print(f"WARNING: Malicious behavior detected (confidence: {analysis['confidence']:.1f}%)")
```

### CI/CD Integration

```yaml
# .github/workflows/security-scan.yml
name: Android Security Scan

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install TrigDroid
      run: pip install trigdroid[frida]
      
    - name: Setup Android Emulator
      uses: reactivecircus/android-emulator-runner@v2
      with:
        api-level: 29
        script: |
          adb devices
          trigdroid devices
          
    - name: Security Analysis
      run: |
        trigdroid -p com.example.testapp \
          --acceleration 5 \
          --timeout 300 \
          --frida
```


## Troubleshooting

### Common Issues

**Device Not Found**
```bash
# Check ADB connection
adb devices

# Restart ADB server
adb kill-server && adb start-server

# Enable USB debugging on device
# Developer options → USB debugging
```

**Frida Hooks Fail to Load**
```bash
# Check Frida installation
python -c "import frida; print(frida.__version__)"

# Reinstall Frida
pip install --upgrade frida frida-tools

# Check device architecture
adb shell getprop ro.product.cpu.abi
```

**TypeScript Compilation Errors**
```bash
# Check Node.js installation
node --version && npm --version

# Rebuild TypeScript hooks
cd frida-hooks
rm -rf node_modules dist
npm install && npm run build
```

**Permission Errors**
```bash
# Grant app permissions manually
adb shell pm grant com.example.app android.permission.READ_PHONE_STATE

# Use TrigDroid's permission management
trigdroid -p com.example.app --grant-permission android.permission.CAMERA
```

### Getting Help

- **Documentation**: Full documentation at [docs.trigdroid.org](https://docs.trigdroid.org)
- **Issues**: Report bugs at [GitHub Issues](https://github.com/trigdroid/trigdroid/issues)
- **Discussions**: Join the community at [GitHub Discussions](https://github.com/trigdroid/trigdroid/discussions)

## Contributing


```bash
# Development setup
git clone https://github.com/trigdroid/trigdroid.git
cd trigdroid
pip install -e ".[dev]"

# Run tests
pytest tests/

# Code quality checks
black src/ tests/
mypy src/
ruff check src/ tests/
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## License

TrigDroid is released under the [MIT License](LICENSE). See LICENSE file for details.

## Development Guide

### Modern Architecture Overview

TrigDroid has been completely refactored following **SOLID principles** with a clean dual-layer architecture:

```
├── src/                   # New Refactored Code (SOLID Architecture)
│   ├── trigdroid/          # Modern Public API Layer (lowercase)
│   │   ├── api/            # External interface with context managers
│   │   │   ├── main.py     # TrigDroidAPI class
│   │   │   ├── config.py   # Type-safe TestConfiguration
│   │   │   ├── results.py  # Comprehensive TestResult classes
│   │   │   ├── devices.py  # Device management wrapper
│   │   │   ├── runners.py  # Test runner wrapper
│   │   │   └── quick_start.py  # Convenience functions
│   │   ├── cli/            # Rich CLI interface using Click
│   │   │   └── main.py     # Modern CLI with subcommands
│   │   ├── core/           # Core utilities and enums
│   │   │   ├── enums.py    # Type-safe enumerations
│   │   │   └── cleanup.py  # Resource management
│   │   └── exceptions.py   # Exception hierarchy
│   └── TrigDroid_Infrastructure/  # Infrastructure Layer (SOLID)
│       ├── interfaces/     # Protocol-based abstractions
│       │   └── __init__.py # ILogger, ITestRunner, IAndroidDevice, etc.
│       ├── infrastructure/ # Dependency injection + implementations
│       │   ├── dependency_injection.py  # DI container
│       │   ├── configuration.py         # Config providers
│       │   ├── logging.py              # Logger implementations
│       │   └── android.py              # Device management
│       ├── application/    # Application orchestration
│       │   └── orchestrator.py # Main workflow coordinator
│       └── test_runners/   # Test execution implementations
├── src/                    # Legacy Code (Original Implementation)
│   └── TrigDroid/          # Legacy TrigDroid (preserved for compatibility)
│       ├── logger/         # Original logging utilities
│       ├── interaction/    # Legacy UI components  
│       ├── utils/          # Legacy utility functions
│       ├── frida/          # Legacy JavaScript hooks
│       └── ...             # Other legacy components
├── frida-hooks/            # TypeScript Frida Hooks (New)
│   ├── main.ts            # Hook entry point
│   ├── hooks/             # Individual hook modules
│   │   ├── android-sensors.ts
│   │   └── android-build.ts
│   ├── types.ts           # TypeScript type definitions
│   ├── utils.ts           # Common hook utilities
│   ├── package.json       # Node.js build configuration
│   └── tsconfig.json      # TypeScript compiler settings
├── scripts/               # Build and installation scripts
│   ├── build.py          # Cross-platform build script
│   └── install.sh        # Automated installation
├── pyproject.toml        # Modern Python packaging (PEP 621)
└── Makefile             # Development workflow commands
```

### SOLID Principles Implementation

#### **1. Single Responsibility Principle**
Each class has one reason to change:
- `AndroidDevice`: Only handles device operations
- `StandardLogger`: Only handles logging
- `SensorTestRunner`: Only executes sensor tests

#### **2. Open/Closed Principle**
Extend functionality without modifying existing code:
```python
# Add new test runner without changing existing ones
class CustomTestRunner(TestRunnerBase):
    def can_run(self, test_type: str) -> bool:
        return test_type == "custom"
        
    def _execute_internal(self, context: ITestContext) -> TestResult:
        # Custom test logic
        return TestResult.SUCCESS

# Register in DI container
container.register_transient(ITestRunner, CustomTestRunner, "custom")
```

#### **3. Liskov Substitution Principle**
All implementations follow their interfaces:
```python
# Any ILogger implementation works seamlessly
logger: ILogger = StandardLogger()  # or FilteredLogger()
logger.info("Test message")  # Works the same way
```

#### **4. Interface Segregation Principle**
Small, focused interfaces instead of large monolithic ones:
```python
class ILogger(Protocol):
    def debug(self, message: str) -> None: ...
    def info(self, message: str) -> None: ...
    
class IConfigurationProvider(Protocol):
    def get_value(self, key: str) -> ConfigValue: ...
    def set_value(self, key: str, value: ConfigValue) -> None: ...
```

#### **5. Dependency Inversion Principle**
Depend on abstractions, inject dependencies:
```python
class SensorTestRunner(TestRunnerBase):
    def __init__(self, logger: ILogger, device: IAndroidDevice):
        super().__init__(logger)
        self._device = device  # Injected dependency
```

### Development Environment Setup

#### **Quick Development Setup**
```bash
# 1. Clone and setup development environment
git clone https://github.com/trigdroid/trigdroid.git
cd trigdroid

# 2. Use our automated installer
./scripts/install.sh --mode dev

# 3. Alternative: Manual setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[full,dev,test,docs]"

# 4. Build TypeScript hooks
cd frida-hooks
npm install && npm run build
cd ..

# 5. Verify installation
trigdroid --version
pytest tests/ -v
```

#### **Development Workflow Commands**
```bash
# Development commands (see Makefile)
make setup-dev-env        # Initial environment setup
make dev-install          # Install in development mode
make build               # Build all components (Python + TypeScript)

# Code quality
make format              # Auto-format with black + isort
make lint               # Type checking with mypy + ruff
make check              # Run all quality checks
make pre-commit         # Format + lint + fast tests

# Testing
make test               # All tests
make test-unit          # Unit tests only
make test-integration   # Integration tests
make test-fast          # Skip slow tests
make coverage           # Generate coverage report

# Build and distribution
make package            # Build wheel/sdist
make hooks              # Build TypeScript hooks only
make clean              # Clean build artifacts
```

### Adding New Features

#### **1. Create New Test Runner**
```python
# src2/TrigDroid_Infrastructure/test_runners/custom_test_runner.py  
from ..interfaces import ITestRunner, ITestContext, TestResult, TestRunnerBase

class CustomTestRunner(TestRunnerBase):
    """Example custom test runner."""
    
    def can_run(self, test_type: str) -> bool:
        return test_type == "custom"
    
    def _execute_internal(self, context: ITestContext) -> TestResult:
        # Implement your test logic
        self._logger.info("Running custom test")
        
        # Access dependencies through context
        device = context.device
        config = context.config
        package = context.package_name
        
        # Your test implementation
        success = self._run_custom_test(device, package)
        
        return TestResult.SUCCESS if success else TestResult.FAILURE
    
    def _run_custom_test(self, device, package) -> bool:
        # Custom test implementation
        return True

# Register in dependency_injection.py
container.register_transient(ITestRunner, CustomTestRunner, "custom")
```

#### **2. Add New Configuration Provider**
```python
# src2/TrigDroid_Infrastructure/infrastructure/configuration.py
class DatabaseConfigProvider(ConfigurationProviderBase):
    """Load configuration from database."""
    
    def _load_configuration(self) -> Dict[str, ConfigValue]:
        # Load from database
        return {"custom_setting": "value"}

# Register in configure_container()
container.register_transient(IConfigurationProvider, DatabaseConfigProvider, "database")
```

#### **3. Create TypeScript Frida Hook**
```typescript
// frida-hooks/hooks/custom-hook.ts
import { HookManager } from '../utils';

export class CustomHook extends HookManager {
    public hookCustomAPI(): void {
        const SomeClass = Java.use("com.example.SomeClass");
        
        SomeClass.someMethod.implementation = function(...args) {
            console.log("[TrigDroid] Custom hook triggered");
            this.logToChangelog("SomeClass.someMethod", "original", "hooked");
            
            // Call original method
            return this.someMethod.apply(this, args);
        };
    }
}

// Add to main.ts
import { CustomHook } from './hooks/custom-hook';

function main() {
    const customHook = new CustomHook();
    customHook.hookCustomAPI();
}
```

### Building Frida Hooks from Source

If you want to modify the Frida hooks, you'll need to rebuild them:

#### **Prerequisites**
```bash
# Node.js >= 16.0.0
node --version

# Install frida-compile (required for bundling)
pip install frida-tools
```

#### **Build Commands**
```bash
cd frida_hooks

# Install dependencies
npm install

# Build everything (recommended)
npm run build:all

# Or build individually:
npm run build          # Main hooks only
npm run build:bypass   # Bypass script only

# Development mode
npm run watch          # Watch for changes (TypeScript only)

# Clean rebuild
npm run rebuild        # Clean + build:all
```

#### **Build Output**
After building, scripts are automatically copied to `src/trigdroid/scripts/`:
```
src/trigdroid/scripts/
├── main_bundle.js               # Bundled main script (self-contained)
├── main.js                      # Unbundled main script
├── trigdroid_bypass_bundle.js   # Bundled bypass script (self-contained)
├── trigdroid_bypass_rpc.js      # Unbundled bypass script
├── types.js, utils.js           # Utilities
└── hooks/                       # Individual hook scripts
    ├── ssl-unpinning.js
    ├── root-detection.js
    ├── frida-detection.js
    ├── emulator-detection.js
    ├── debug-detection.js
    ├── android-build.js
    └── android-sensors.js
```

See [frida_hooks/README.md](frida_hooks/README.md) for detailed development documentation.

### TypeScript Hook Development

#### **Adding Custom Hooks**
```bash
# Build hooks automatically during pip install
pip install -e .

# Manual hook building
cd frida_hooks
npm install      # Install dependencies
npm run build    # Compile TypeScript to JavaScript
npm run watch    # Watch mode for development
```

#### **Hook Development Patterns**
```typescript
// frida-hooks/hooks/android-example.ts
import { AndroidSensorType } from '../types';
import { HookUtils } from '../utils';

export class AndroidExampleHook {
    private hookUtils: HookUtils;
    
    constructor() {
        this.hookUtils = new HookUtils();
    }
    
    public hookSensorManager(): void {
        try {
            const SensorManager = Java.use("android.hardware.SensorManager");
            
            SensorManager.getDefaultSensor.implementation = function(type) {
                const originalSensor = this.getDefaultSensor(type);
                
                // Log the hook for debugging
                this.hookUtils.logHookExecution("SensorManager.getDefaultSensor", {
                    sensorType: type,
                    timestamp: Date.now()
                });
                
                // Record change in changelog
                this.hookUtils.writeToChangelog(
                    "SensorManager.getDefaultSensor",
                    "original_behavior",
                    "hooked_behavior",
                    `Sensor type ${type} intercepted`
                );
                
                return originalSensor;
            };
            
        } catch (error) {
            console.error(`[TrigDroid] Hook failed: ${error}`);
        }
    }
}
```

### Dependency Injection Usage

#### **Registering Services**
```python
# In configure_container()
from .my_service import MyService

# Singleton (same instance every time)
container.register_singleton(IMyService, MyService)

# Transient (new instance every time)  
container.register_transient(IMyService, MyService)

# Factory function
container.register_singleton(IMyService, lambda: MyService(config="custom"))

# Specific instance
container.register_instance(IMyService, my_service_instance)
```

#### **Resolving Dependencies**
```python
# Method 1: Through container
container = configure_container()
logger = container.resolve(ILogger)

# Method 2: Service Locator (global access)
ServiceLocator.set_container(container)
logger = ServiceLocator.get_service(ILogger)

# Method 3: Constructor injection
@inject(logger=ILogger, device=IAndroidDevice)
class MyTestRunner:
    def __init__(self, logger: ILogger, device: IAndroidDevice):
        self._logger = logger
        self._device = device
```

### Code Quality Standards

#### **Type Safety**
```python
# Use type hints everywhere
def process_config(config: TestConfiguration) -> TestResult:
    return TestResult.SUCCESS

# Use protocols for interfaces
class IMyService(Protocol):
    def do_something(self, value: str) -> bool: ...

# Use enums for constants
class TestPhase(Enum):
    SETUP = "setup"
    EXECUTION = "execution"
    TEARDOWN = "teardown"
```

#### **Error Handling**
```python
# Proper exception hierarchy
class TrigDroidException(Exception):
    """Base exception for TrigDroid."""
    pass

class DeviceConnectionError(TrigDroidException):
    """Device connection failed."""
    pass

# Use try/catch with specific exceptions
try:
    device.connect()
except DeviceConnectionError as e:
    logger.error(f"Failed to connect: {e}")
    return TestResult.FAILURE
```

#### **Logging Best Practices**
```python
# Use structured logging
logger.info("Test started", extra={
    "package": package_name,
    "phase": "setup",
    "timestamp": time.time()
})

# Use appropriate log levels
logger.debug("Detailed debugging info")      # Development only
logger.info("Important user information")    # Normal operation
logger.warning("Something might be wrong")   # Potential issues
logger.error("Something failed")             # Errors that don't stop execution
logger.critical("System cannot continue")    # Fatal errors
```

### Testing Framework

#### **Unit Tests**
```python
# tests/unit/test_sensor_runner.py
import pytest
from unittest.mock import Mock
from TrigDroid_Infrastructure.test_runners import SensorTestRunner
from TrigDroid_Infrastructure.interfaces import ILogger, ITestContext, TestResult

def test_sensor_runner_success():
    # Arrange
    mock_logger = Mock(spec=ILogger)
    mock_context = Mock(spec=ITestContext)
    runner = SensorTestRunner(mock_logger)
    
    # Act
    result = runner.execute(mock_context)
    
    # Assert
    assert result == TestResult.SUCCESS
    mock_logger.info.assert_called()
```

#### **Integration Tests**
```python
# tests/integration/test_full_workflow.py
@pytest.mark.integration
@pytest.mark.requires_device
def test_full_testing_workflow(test_device):
    """Test complete workflow with real device."""
    config = TestConfiguration(
        package="com.example.testapp",
        acceleration=3,
        timeout=60
    )
    
    with TrigDroidAPI() as api:
        api.configure(config)
        api.set_device(test_device.device_id)
        result = api.run_tests()
        
    assert result.success
    assert result.total_tests > 0
```

### Performance Optimization

#### **Fast Development Cycle**
```bash
# Skip TypeScript build during development
SKIP_HOOKS=1 pip install -e .

# Run only fast tests
make test-fast

# Use parallel testing
pytest -n auto tests/

# Quick format and lint check
make pre-commit
```

#### **Build Optimization**
```bash
# Build only what changed
make hooks-if-changed

# Use cached dependencies
pip install --cache-dir ~/.cache/pip -e .

# Parallel hook compilation
cd frida-hooks && npm run build:parallel
```

### Contributing Guidelines

#### **Code Standards**
- **Readable**: Code should read like well-written prose
- **Self-documenting**: Use clear variable and function names
- **Consistent**: Follow established patterns
- **Simple**: Prefer simple solutions over clever ones
- **DRY**: Extract common functionality
- **YAGNI**: Don't over-engineer

#### **Pull Request Process**
```bash
# 1. Development workflow
git checkout -b feature/new-feature
make dev-install
make pre-commit  # Format + lint + fast tests

# 2. Before committing
make test        # Full test suite
make build       # Ensure everything builds
make check       # Final quality check

# 3. Create pull request
git push origin feature/new-feature
# Open PR with detailed description
```

#### **Code Review Checklist**
- [ ] Follows SOLID principles
- [ ] Has proper type annotations
- [ ] Includes unit tests (>90% coverage)
- [ ] Updated documentation if needed
- [ ] No hardcoded values or magic numbers
- [ ] Proper error handling
- [ ] TypeScript hooks built successfully
- [ ] All quality checks pass

### Debugging and Troubleshooting

#### **Development Issues**
```bash
# TypeScript compilation fails
cd frida-hooks
rm -rf node_modules dist
npm install && npm run build

# Python import errors
pip uninstall trigdroid
pip install -e ".[full]"

# Dependency injection issues
# Check container registration in configure_container()
container.has_service(IMyService)  # Should return True

# Test runner not found
# Verify registration with correct name
container.resolve(ITestRunner, "my_runner")
```

#### **Runtime Debugging**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use dependency injection debug mode
container = configure_container()
if container.has_service(IMyService):
    service = container.resolve(IMyService)
    
# Check service registration
print(f"Registered services: {list(container._services.keys())}")
```

This development guide provides comprehensive information for contributing to and extending TrigDroid's modern architecture.

## Acknowledgments

- Built on the foundation of the [Evadroid](https://github.com/evadroid/evadroid) project
- Powered by [Frida](https://frida.re/) dynamic instrumentation toolkit
- Uses [Click](https://click.palletsprojects.com/) for command-line interface
- Enhanced with [Rich](https://rich.readthedocs.io/) for beautiful terminal output
