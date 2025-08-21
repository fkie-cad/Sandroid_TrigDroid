"""Test helper utilities for TrigDroid tests."""

import os
import tempfile
import subprocess
import time
from typing import Dict, Any, List, Optional, Callable
from unittest.mock import Mock, MagicMock
from contextlib import contextmanager

from trigdroid.api.config import TestConfiguration
from trigdroid.core.enums import LogLevel, TestPhase
from TrigDroid_Infrastructure.interfaces import (
    ILogger, IAndroidDevice, ITestContext, 
    TestResult, DeviceConnectionState
)


class TestAPKBuilder:
    """Helper class for building test APK files."""
    
    @staticmethod
    def create_test_apk(package_name: str, version: str = "1.0") -> str:
        """Create a minimal test APK file for testing purposes.
        
        Args:
            package_name: Package name for the APK
            version: Version string
            
        Returns:
            Path to created APK file
        """
        # Create a temporary APK file (empty file for testing)
        with tempfile.NamedTemporaryFile(suffix='.apk', delete=False) as f:
            # Write minimal APK-like content (not a real APK, just for testing)
            f.write(b'PK\x03\x04')  # ZIP file header (APKs are ZIP files)
            f.write(f"package:{package_name}".encode())
            return f.name
    
    @staticmethod
    def cleanup_test_apk(apk_path: str) -> None:
        """Clean up test APK file."""
        try:
            os.unlink(apk_path)
        except OSError:
            pass


class MockDeviceBuilder:
    """Builder for creating mock Android devices with specific behaviors."""
    
    def __init__(self):
        self.device = Mock(spec=IAndroidDevice)
        self._installed_packages = set()
        self._running_apps = set()
        self._device_info = {
            'id': 'mock_device',
            'model': 'Mock Device',
            'android_version': '10',
            'status': 'device'
        }
    
    def with_device_id(self, device_id: str) -> 'MockDeviceBuilder':
        """Set device ID."""
        self._device_info['id'] = device_id
        return self
    
    def with_installed_packages(self, packages: List[str]) -> 'MockDeviceBuilder':
        """Set installed packages."""
        self._installed_packages.update(packages)
        return self
    
    def with_running_apps(self, apps: List[str]) -> 'MockDeviceBuilder':
        """Set running apps."""
        self._running_apps.update(apps)
        return self
    
    def with_device_info(self, **info) -> 'MockDeviceBuilder':
        """Update device info."""
        self._device_info.update(info)
        return self
    
    def build(self) -> Mock:
        """Build the mock device."""
        # Set up mock behaviors
        self.device.get_device_info.return_value = self._device_info
        self.device.is_app_installed.side_effect = lambda pkg: pkg in self._installed_packages
        
        # Command execution mock
        def mock_execute_command(command: str):
            result = Mock()
            result.success = True
            result.return_code = 0
            result.stderr = b''
            
            if 'pm list packages' in command:
                packages = '\n'.join([f'package:{pkg}' for pkg in self._installed_packages])
                result.stdout = packages.encode()
            else:
                result.stdout = b'Command output'
            
            return result
        
        self.device.execute_command.side_effect = mock_execute_command
        
        # App management mocks
        self.device.install_app.return_value = True
        self.device.uninstall_app.return_value = True
        self.device.start_app.return_value = True
        self.device.stop_app.return_value = True
        
        return self.device


class ConfigurationBuilder:
    """Builder for creating test configurations with fluent interface."""
    
    def __init__(self):
        self._config_data = {
            'package': 'com.example.test'
        }
    
    def with_package(self, package: str) -> 'ConfigurationBuilder':
        """Set package name."""
        self._config_data['package'] = package
        return self
    
    def with_device_id(self, device_id: str) -> 'ConfigurationBuilder':
        """Set device ID."""
        self._config_data['device_id'] = device_id
        return self
    
    def with_sensors(self, acceleration=0, gyroscope=0, light=0, pressure=0) -> 'ConfigurationBuilder':
        """Set sensor levels."""
        if acceleration > 0:
            self._config_data['acceleration'] = acceleration
        if gyroscope > 0:
            self._config_data['gyroscope'] = gyroscope
        if light > 0:
            self._config_data['light'] = light
        if pressure > 0:
            self._config_data['pressure'] = pressure
        return self
    
    def with_network_states(self, wifi=None, data=None, bluetooth=None) -> 'ConfigurationBuilder':
        """Set network states."""
        if wifi is not None:
            self._config_data['wifi'] = wifi
        if data is not None:
            self._config_data['data'] = data
        if bluetooth is not None:
            self._config_data['bluetooth'] = bluetooth
        return self
    
    def with_frida(self, enabled=True) -> 'ConfigurationBuilder':
        """Enable/disable Frida hooks."""
        self._config_data['frida_hooks'] = enabled
        return self
    
    def with_runtime(self, minutes=1) -> 'ConfigurationBuilder':
        """Set minimum runtime."""
        self._config_data['min_runtime'] = minutes
        return self
    
    def with_log_level(self, level: LogLevel) -> 'ConfigurationBuilder':
        """Set logging level."""
        self._config_data['log_level'] = level
        return self
    
    def build(self) -> TestConfiguration:
        """Build the configuration."""
        return TestConfiguration(**self._config_data)


class TestResultBuilder:
    """Builder for creating test results."""
    
    def __init__(self):
        self._result_data = {
            'success': True,
            'phase': TestPhase.EXECUTION,
            'total_tests': 1,
            'passed_tests': 1,
            'failed_tests': 0,
            'duration_seconds': 60.0,
            'app_started': True,
            'app_crashed': False
        }
    
    def with_success(self, success: bool) -> 'TestResultBuilder':
        """Set success status."""
        self._result_data['success'] = success
        if not success:
            self._result_data['failed_tests'] = 1
            self._result_data['passed_tests'] = 0
        return self
    
    def with_phase(self, phase: TestPhase) -> 'TestResultBuilder':
        """Set test phase."""
        self._result_data['phase'] = phase
        return self
    
    def with_error(self, error: str) -> 'TestResultBuilder':
        """Set error message."""
        self._result_data['error'] = error
        self._result_data['success'] = False
        return self
    
    def with_duration(self, seconds: float) -> 'TestResultBuilder':
        """Set test duration."""
        self._result_data['duration_seconds'] = seconds
        return self
    
    def with_app_crashed(self, crashed: bool = True) -> 'TestResultBuilder':
        """Set app crashed status."""
        self._result_data['app_crashed'] = crashed
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the test result dictionary."""
        return self._result_data.copy()


class ProcessHelper:
    """Helper for managing external processes in tests."""
    
    @staticmethod
    def run_command(command: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """Run command with timeout and proper error handling."""
        try:
            return subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
        except subprocess.TimeoutExpired as e:
            raise TimeoutError(f"Command timed out: {' '.join(command)}") from e
    
    @staticmethod
    def is_adb_available() -> bool:
        """Check if ADB is available in PATH."""
        try:
            result = subprocess.run(['adb', 'version'], capture_output=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    @staticmethod
    def get_connected_devices() -> List[str]:
        """Get list of connected Android devices."""
        if not ProcessHelper.is_adb_available():
            return []
        
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if result.returncode != 0:
                return []
            
            devices = []
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip() and '\t' in line:
                    device_id, status = line.strip().split('\t', 1)
                    if status == 'device':
                        devices.append(device_id)
            
            return devices
        except Exception:
            return []


class TimeHelper:
    """Helper for time-related test utilities."""
    
    @staticmethod
    @contextmanager
    def time_limit(seconds: float):
        """Context manager for enforcing time limits in tests."""
        start_time = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start_time
            if elapsed > seconds:
                raise TimeoutError(f"Operation took {elapsed:.2f}s, limit was {seconds}s")
    
    @staticmethod
    def wait_for_condition(condition: Callable[[], bool], timeout: float = 10.0, 
                          interval: float = 0.1) -> bool:
        """Wait for a condition to become true."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if condition():
                return True
            time.sleep(interval)
        return False


class LogCapture:
    """Helper for capturing and analyzing log output in tests."""
    
    def __init__(self):
        self.records = []
    
    def debug(self, message: str, *args) -> None:
        self.records.append(('DEBUG', message % args if args else message))
    
    def info(self, message: str, *args) -> None:
        self.records.append(('INFO', message % args if args else message))
    
    def warning(self, message: str, *args) -> None:
        self.records.append(('WARNING', message % args if args else message))
    
    def error(self, message: str, *args) -> None:
        self.records.append(('ERROR', message % args if args else message))
    
    def critical(self, message: str, *args) -> None:
        self.records.append(('CRITICAL', message % args if args else message))
    
    def clear(self) -> None:
        """Clear captured records."""
        self.records.clear()
    
    def has_message(self, level: str, message_part: str) -> bool:
        """Check if a message was logged at specified level."""
        return any(
            record[0] == level and message_part in record[1] 
            for record in self.records
        )
    
    def get_messages(self, level: Optional[str] = None) -> List[str]:
        """Get logged messages, optionally filtered by level."""
        if level:
            return [record[1] for record in self.records if record[0] == level]
        return [record[1] for record in self.records]
    
    def count_messages(self, level: Optional[str] = None) -> int:
        """Count logged messages, optionally filtered by level."""
        if level:
            return sum(1 for record in self.records if record[0] == level)
        return len(self.records)


class AssertionHelpers:
    """Collection of custom assertion helpers for TrigDroid tests."""
    
    @staticmethod
    def assert_configuration_valid(config: TestConfiguration) -> None:
        """Assert that configuration is valid."""
        assert config.is_valid(), f"Configuration should be valid. Errors: {config.validation_errors}"
    
    @staticmethod
    def assert_configuration_invalid(config: TestConfiguration, expected_error_count: int = None) -> None:
        """Assert that configuration is invalid."""
        assert not config.is_valid(), "Configuration should be invalid"
        if expected_error_count:
            assert len(config.validation_errors) == expected_error_count, \
                f"Expected {expected_error_count} errors, got {len(config.validation_errors)}"
    
    @staticmethod
    def assert_test_result_successful(result: Dict[str, Any]) -> None:
        """Assert that test result indicates success."""
        assert result['success'] is True, f"Test should be successful. Error: {result.get('error')}"
        assert result['passed_tests'] > 0, "Should have passed tests"
        assert result['failed_tests'] == 0, "Should have no failed tests"
    
    @staticmethod
    def assert_test_result_failed(result: Dict[str, Any]) -> None:
        """Assert that test result indicates failure."""
        assert result['success'] is False, "Test should have failed"
        assert result.get('error') is not None, "Should have error message"
    
    @staticmethod
    def assert_device_connected(device: IAndroidDevice) -> None:
        """Assert that device is connected."""
        info = device.get_device_info()
        assert info is not None, "Device should have info"
        assert 'id' in info, "Device info should have ID"
    
    @staticmethod
    def assert_package_installed(device: IAndroidDevice, package: str) -> None:
        """Assert that package is installed on device."""
        assert device.is_app_installed(package), f"Package {package} should be installed"
    
    @staticmethod
    def assert_log_contains(log_capture: LogCapture, level: str, message_part: str) -> None:
        """Assert that log contains specific message at level."""
        assert log_capture.has_message(level, message_part), \
            f"Log should contain '{message_part}' at level {level}. Messages: {log_capture.get_messages()}"


# Convenience functions for common test scenarios
def create_mock_logger() -> LogCapture:
    """Create a mock logger that captures output."""
    return LogCapture()


def create_basic_config(package: str = "com.example.test") -> TestConfiguration:
    """Create a basic test configuration."""
    return ConfigurationBuilder().with_package(package).build()


def create_advanced_config(package: str = "com.example.test") -> TestConfiguration:
    """Create an advanced test configuration with multiple features."""
    return (ConfigurationBuilder()
            .with_package(package)
            .with_sensors(acceleration=8, gyroscope=5)
            .with_network_states(wifi=True, data=True)
            .with_frida(True)
            .with_runtime(5)
            .build())


def create_mock_device(device_id: str = "test_device") -> Mock:
    """Create a basic mock device."""
    return (MockDeviceBuilder()
            .with_device_id(device_id)
            .with_installed_packages(['com.example.test', 'com.android.settings'])
            .build())


def create_successful_test_result() -> Dict[str, Any]:
    """Create a successful test result."""
    return TestResultBuilder().with_success(True).build()


def create_failed_test_result(error: str = "Test failed") -> Dict[str, Any]:
    """Create a failed test result."""
    return TestResultBuilder().with_success(False).with_error(error).build()


# Test data fixtures
SAMPLE_DEVICE_LIST = [
    {'id': 'emulator-5554', 'status': 'device'},
    {'id': 'emulator-5556', 'status': 'device'},
    {'id': 'physical-device', 'status': 'unauthorized'}
]

SAMPLE_PACKAGE_LIST = [
    'com.android.settings',
    'com.android.systemui',
    'com.example.test',
    'com.malicious.app'
]

SAMPLE_DEVICE_INFO = {
    'id': 'emulator-5554',
    'model': 'Android SDK built for x86',
    'android_version': '10',
    'api_level': '29',
    'arch': 'x86'
}