"""TrigDroid - Modern Android Security Testing Framework.

TrigDroid is a modern Android security testing framework designed to trigger
payloads in potentially malicious Android applications through sophisticated
environmental manipulation.

This package provides both a command-line interface and a Python API for
security researchers, malware analysts, and penetration testers.
"""

__version__ = "2.0.0"

# Export main API components
from .api.main import TrigDroidAPI
from .api.config import TestConfiguration
from .api.results import TestResult
from .api.devices import DeviceManager, AndroidDevice
from .api.quick_start import quick_test, validate_environment, setup_environment

# Export core types
from .core.enums import LogLevel, TestPhase, SensorType
from .exceptions import (
    TrigDroidError, 
    DeviceError, 
    ConfigurationError,
    TestExecutionError
)

__all__ = [
    # Main API
    "TrigDroidAPI",
    "TestConfiguration", 
    "TestResult",
    "DeviceManager",
    "AndroidDevice",
    
    # Convenience functions
    "quick_test",
    "validate_environment", 
    "setup_environment",
    
    # Enums
    "LogLevel",
    "TestPhase", 
    "SensorType",
    
    # Exceptions
    "TrigDroidError",
    "DeviceError",
    "ConfigurationError", 
    "TestExecutionError",
]