"""Shared pytest configuration and fixtures for TrigDroid tests."""

import logging
import pytest
from typing import Dict, Any, Optional
from unittest.mock import Mock, MagicMock

# Import the modules we're testing
from trigdroid.api.config import TestConfiguration
from trigdroid.core.enums import LogLevel, TestPhase
from TrigDroid_Infrastructure.interfaces import (
    ILogger, IAndroidDevice, ITestContext, 
    IConfigurationProvider, TestResult
)


# Configure logging for tests
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')


@pytest.fixture
def mock_logger() -> Mock:
    """Create a mock logger for testing."""
    logger = Mock(spec=ILogger)
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture
def mock_android_device() -> Mock:
    """Create a mock Android device for testing."""
    device = Mock(spec=IAndroidDevice)
    
    # Set up default mock behaviors
    device.execute_command = Mock()
    device.install_app = Mock(return_value=True)
    device.uninstall_app = Mock(return_value=True)
    device.start_app = Mock(return_value=True)
    device.stop_app = Mock(return_value=True)
    device.is_app_installed = Mock(return_value=True)
    device.get_device_info = Mock(return_value={
        'id': 'test_device',
        'model': 'Test Device',
        'android_version': '10',
        'status': 'device'
    })
    
    return device


@pytest.fixture
def mock_command_result() -> Mock:
    """Create a mock command result for testing."""
    result = Mock()
    result.return_code = 0
    result.stdout = b'test output'
    result.stderr = b''
    result.success = True
    return result


@pytest.fixture
def mock_config_provider() -> Mock:
    """Create a mock configuration provider for testing."""
    config = Mock(spec=IConfigurationProvider)
    config.get_value = Mock(return_value=None)
    config.set_value = Mock()
    config.has_key = Mock(return_value=False)
    config.validate = Mock(return_value=True)
    return config


@pytest.fixture
def mock_test_context(mock_android_device, mock_config_provider, mock_logger) -> Mock:
    """Create a mock test context for testing."""
    context = Mock(spec=ITestContext)
    context.device = mock_android_device
    context.config = mock_config_provider
    context.logger = mock_logger
    context.package_name = "com.example.test"
    return context


@pytest.fixture
def basic_test_configuration() -> TestConfiguration:
    """Create a basic test configuration for testing."""
    return TestConfiguration(
        package="com.example.test",
        log_level=LogLevel.INFO,
        min_runtime=1,
        acceleration=0,
        battery_rotation=0,
        frida_hooks=False
    )


@pytest.fixture
def advanced_test_configuration() -> TestConfiguration:
    """Create an advanced test configuration for testing."""
    return TestConfiguration(
        package="com.suspicious.test",
        device_id="emulator-5554",
        log_level=LogLevel.DEBUG,
        min_runtime=5,
        background_time=30,
        acceleration=8,
        gyroscope=5,
        light=3,
        pressure=4,
        battery_rotation=3,
        wifi=True,
        data=True,
        bluetooth=True,
        frida_hooks=True,
        sensors=["accelerometer", "gyroscope", "light", "pressure"],
        network_states=["wifi", "data", "bluetooth"],
        install_dummy_apps=["com.dummy.app1", "com.dummy.app2"],
        grant_permissions=["android.permission.CAMERA", "android.permission.RECORD_AUDIO"],
        timeout=600,
        verbose=True
    )


@pytest.fixture
def test_device_info() -> Dict[str, Any]:
    """Provide test device information."""
    return {
        'id': 'emulator-5554',
        'status': 'device',
        'model': 'Android SDK built for x86',
        'android_version': '10',
        'api_level': '29',
        'arch': 'x86',
        'connected': True
    }


@pytest.fixture
def test_package_info() -> Dict[str, Any]:
    """Provide test package information."""
    return {
        'package': 'com.example.test',
        'version_name': '1.0.0',
        'version_code': '1',
        'target_sdk': '29',
        'min_sdk': '21',
        'permissions': [
            'android.permission.INTERNET',
            'android.permission.ACCESS_NETWORK_STATE'
        ],
        'activities': [
            'com.example.test.MainActivity'
        ],
        'services': [],
        'receivers': []
    }


@pytest.fixture
def sample_frida_hooks() -> Dict[str, str]:
    """Provide sample Frida hook scripts for testing."""
    return {
        'sensor_hook': '''
            Java.perform(function() {
                var SensorManager = Java.use("android.hardware.SensorManager");
                SensorManager.getDefaultSensor.implementation = function(type) {
                    console.log("[TrigDroid] Sensor requested: " + type);
                    return this.getDefaultSensor(type);
                };
            });
        ''',
        'network_hook': '''
            Java.perform(function() {
                var ConnectivityManager = Java.use("android.net.ConnectivityManager");
                ConnectivityManager.getActiveNetworkInfo.implementation = function() {
                    console.log("[TrigDroid] Network info requested");
                    return this.getActiveNetworkInfo();
                };
            });
        '''
    }


# Test markers for different test categories
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests (e.g., with real devices)")
    config.addinivalue_line("markers", "requires_device: Tests that require an Android device")
    config.addinivalue_line("markers", "requires_frida: Tests that require Frida")
    config.addinivalue_line("markers", "requires_root: Tests that require root access")


# Fixtures for integration testing (require actual Android environment)
@pytest.fixture(scope="session")
def real_android_device():
    """
    Fixture for integration tests requiring a real Android device.
    Skips test if no device is available.
    """
    pytest.importorskip("subprocess")
    import subprocess
    
    try:
        # Check if ADB is available and devices are connected
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        if result.returncode != 0:
            pytest.skip("ADB not available")
            
        devices = []
        for line in result.stdout.split('\n')[1:]:
            if line.strip() and 'device' in line:
                device_id = line.split('\t')[0]
                devices.append(device_id)
        
        if not devices:
            pytest.skip("No Android devices connected")
            
        return devices[0]  # Return first available device
        
    except FileNotFoundError:
        pytest.skip("ADB not found in PATH")


@pytest.fixture(scope="session")
def frida_available():
    """Check if Frida is available for testing."""
    try:
        import frida
        return True
    except ImportError:
        pytest.skip("Frida not available")


# Mock implementations for common scenarios
class MockCommandResult:
    """Mock implementation of command result."""
    
    def __init__(self, return_code: int = 0, stdout: bytes = b'', stderr: bytes = b''):
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
    
    @property
    def success(self) -> bool:
        return self.return_code == 0


class MockAndroidDevice:
    """Mock Android device implementation for testing."""
    
    def __init__(self, device_id: str = "test_device"):
        self.device_id = device_id
        self._installed_packages = set(['com.example.test'])
        self._running_apps = set()
        
    def execute_command(self, command: str) -> MockCommandResult:
        """Mock command execution."""
        if 'pm list packages' in command:
            packages = '\n'.join([f'package:{pkg}' for pkg in self._installed_packages])
            return MockCommandResult(0, packages.encode())
        elif 'dumpsys package' in command:
            return MockCommandResult(0, b'Package information...')
        else:
            return MockCommandResult(0, b'Command executed')
    
    def install_app(self, apk_path: str) -> bool:
        """Mock app installation."""
        # Extract package name from path for testing
        package = apk_path.split('/')[-1].replace('.apk', '')
        self._installed_packages.add(f'com.example.{package}')
        return True
    
    def uninstall_app(self, package_name: str) -> bool:
        """Mock app uninstallation."""
        if package_name in self._installed_packages:
            self._installed_packages.remove(package_name)
            return True
        return False
    
    def start_app(self, package_name: str) -> bool:
        """Mock app start."""
        if package_name in self._installed_packages:
            self._running_apps.add(package_name)
            return True
        return False
    
    def stop_app(self, package_name: str) -> bool:
        """Mock app stop."""
        if package_name in self._running_apps:
            self._running_apps.remove(package_name)
            return True
        return False
    
    def is_app_installed(self, package_name: str) -> bool:
        """Mock app installation check."""
        return package_name in self._installed_packages
    
    def get_device_info(self) -> Dict[str, str]:
        """Mock device info."""
        return {
            'id': self.device_id,
            'model': 'Mock Device',
            'android_version': '10',
            'status': 'device'
        }


# Helper functions for tests
def create_test_result(success: bool = True, phase: TestPhase = TestPhase.EXECUTION, 
                      error: Optional[str] = None) -> Dict[str, Any]:
    """Helper function to create test result dictionaries."""
    return {
        'success': success,
        'phase': phase,
        'error': error,
        'total_tests': 5 if success else 0,
        'passed_tests': 5 if success else 0,
        'failed_tests': 0 if success else 1,
        'duration_seconds': 120.5,
        'app_started': success,
        'app_crashed': not success,
        'frida_hooks_loaded': True if success else False,
        'sensor_tests_executed': ['accelerometer', 'gyroscope'] if success else [],
        'network_state_changes': ['wifi_on', 'wifi_off'] if success else []
    }


def assert_test_result_valid(result: Dict[str, Any]):
    """Helper function to validate test result structure."""
    required_fields = [
        'success', 'phase', 'total_tests', 'passed_tests', 
        'failed_tests', 'duration_seconds', 'app_started'
    ]
    
    for field in required_fields:
        assert field in result, f"Missing required field: {field}"
    
    # Validate types
    assert isinstance(result['success'], bool)
    assert isinstance(result['total_tests'], int)
    assert isinstance(result['passed_tests'], int)
    assert isinstance(result['failed_tests'], int)
    assert isinstance(result['duration_seconds'], (int, float))
    assert isinstance(result['app_started'], bool)


def create_mock_container():
    """Create a mock dependency injection container for testing."""
    container = Mock()
    container.resolve = Mock()
    container.register_singleton = Mock()
    container.register_transient = Mock()
    container.has_service = Mock(return_value=True)
    return container