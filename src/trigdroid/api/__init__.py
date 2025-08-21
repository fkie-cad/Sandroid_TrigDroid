"""TrigDroid API package.

This module provides the modern Python API for TrigDroid, including:
- TrigDroidAPI: Main API class with context manager support
- TestConfiguration: Type-safe configuration management 
- TestResult: Comprehensive test result handling
- Device management: Android device discovery and management
- Quick start functions: Convenience functions for simple usage
"""

from .main import TrigDroidAPI
from .config import TestConfiguration
from .results import TestResult
from .devices import DeviceManager, AndroidDevice
from .quick_start import quick_test, validate_environment, setup_environment

__all__ = [
    "TrigDroidAPI",
    "TestConfiguration",
    "TestResult", 
    "DeviceManager",
    "AndroidDevice",
    "quick_test",
    "validate_environment",
    "setup_environment",
]