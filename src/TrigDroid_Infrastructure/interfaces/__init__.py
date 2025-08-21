"""Core interfaces for TrigDroid following SOLID principles.

This module defines the core abstractions that enable dependency inversion
and make the system more maintainable and testable.
"""

from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Generic, Any, Dict, List, Optional, Union
from enum import Enum

# Type definitions
T = TypeVar('T')
ConfigValue = Union[str, int, bool, List[str], None]


class LogLevel(Enum):
    """Logging levels for the application."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TestResult(Enum):
    """Result of test execution."""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    SKIPPED = "SKIPPED"


class DeviceConnectionState(Enum):
    """Android device connection states."""
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    UNAUTHORIZED = "UNAUTHORIZED"


# Core Interfaces

class ILogger(Protocol):
    """Logger interface for dependency inversion."""
    
    def debug(self, message: str, *args: Any) -> None: ...
    def info(self, message: str, *args: Any) -> None: ...
    def warning(self, message: str, *args: Any) -> None: ...
    def error(self, message: str, *args: Any) -> None: ...
    def critical(self, message: str, *args: Any) -> None: ...


class IConfigurationProvider(Protocol):
    """Configuration provider interface."""
    
    def get_value(self, key: str) -> ConfigValue: ...
    def set_value(self, key: str, value: ConfigValue) -> None: ...
    def has_key(self, key: str) -> bool: ...
    def validate(self) -> bool: ...


class IConfigurationValidator(Protocol):
    """Configuration validation interface."""
    
    def validate_config(self, config: Dict[str, ConfigValue]) -> List[str]: ...
    def is_valid(self, key: str, value: ConfigValue) -> bool: ...


class IAndroidDevice(Protocol):
    """Android device interface."""
    
    def execute_command(self, command: str) -> 'ICommandResult': ...
    def install_app(self, apk_path: str) -> bool: ...
    def uninstall_app(self, package_name: str) -> bool: ...
    def start_app(self, package_name: str) -> bool: ...
    def stop_app(self, package_name: str) -> bool: ...
    def is_app_installed(self, package_name: str) -> bool: ...
    def get_device_info(self) -> Dict[str, str]: ...


class ICommandResult(Protocol):
    """Command execution result interface."""
    
    @property
    def return_code(self) -> int: ...
    
    @property
    def stdout(self) -> bytes: ...
    
    @property
    def stderr(self) -> bytes: ...
    
    @property
    def success(self) -> bool: ...


class ITestRunner(Protocol):
    """Test runner interface for different test types."""
    
    def can_run(self, test_type: str) -> bool: ...
    def execute(self, context: 'ITestContext') -> TestResult: ...
    def setup(self) -> bool: ...
    def teardown(self) -> bool: ...


class ITestContext(Protocol):
    """Test execution context interface."""
    
    @property
    def device(self) -> IAndroidDevice: ...
    
    @property
    def config(self) -> IConfigurationProvider: ...
    
    @property
    def logger(self) -> ILogger: ...
    
    @property
    def package_name(self) -> str: ...


class IFridaHookProvider(Protocol):
    """Frida hook provider interface."""
    
    def get_hook_script(self) -> str: ...
    def get_hook_config(self) -> Dict[str, Any]: ...
    def supports_hook(self, hook_name: str) -> bool: ...


class IChangelogWriter(Protocol):
    """Changelog writer interface."""
    
    def write_entry(self, property_name: str, old_value: str, new_value: str, description: str = "") -> None: ...
    def flush(self) -> None: ...


class IApplicationOrchestrator(Protocol):
    """Main application orchestrator interface."""
    
    def setup(self) -> bool: ...
    def execute_tests(self) -> bool: ...
    def teardown(self) -> bool: ...


# Abstract Base Classes

class TestRunnerBase(ABC):
    """Base class for test runners implementing common functionality."""
    
    def __init__(self, logger: ILogger):
        self._logger = logger
        self._is_setup = False
    
    @abstractmethod
    def can_run(self, test_type: str) -> bool:
        """Check if this runner can handle the given test type."""
        pass
    
    @abstractmethod
    def _execute_internal(self, context: ITestContext) -> TestResult:
        """Internal execution logic to be implemented by subclasses."""
        pass
    
    def execute(self, context: ITestContext) -> TestResult:
        """Execute the test with proper error handling."""
        try:
            if not self._is_setup:
                if not self.setup():
                    return TestResult.FAILURE
                    
            return self._execute_internal(context)
            
        except Exception as e:
            self._logger.error(f"Test execution failed: {e}")
            return TestResult.FAILURE
    
    def setup(self) -> bool:
        """Setup the test runner."""
        self._is_setup = True
        return True
    
    def teardown(self) -> bool:
        """Cleanup after test execution."""
        self._is_setup = False
        return True


class ConfigurationProviderBase(ABC):
    """Base class for configuration providers."""
    
    def __init__(self, logger: ILogger):
        self._logger = logger
        self._config: Dict[str, ConfigValue] = {}
    
    @abstractmethod
    def _load_configuration(self) -> Dict[str, ConfigValue]:
        """Load configuration from the specific source."""
        pass
    
    def get_value(self, key: str) -> ConfigValue:
        """Get configuration value by key."""
        if not self._config:
            self._config = self._load_configuration()
        return self._config.get(key)
    
    def set_value(self, key: str, value: ConfigValue) -> None:
        """Set configuration value."""
        self._config[key] = value
    
    def has_key(self, key: str) -> bool:
        """Check if configuration key exists."""
        if not self._config:
            self._config = self._load_configuration()
        return key in self._config