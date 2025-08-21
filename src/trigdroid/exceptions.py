"""Exception classes for TrigDroid."""


class TrigDroidError(Exception):
    """Base exception for TrigDroid errors."""
    pass


class ConfigurationError(TrigDroidError):
    """Configuration-related errors."""
    pass


class DeviceError(TrigDroidError):
    """Android device-related errors."""
    pass


class TestExecutionError(TrigDroidError):
    """Test execution errors."""
    pass


class FridaError(TrigDroidError):
    """Frida-related errors.""" 
    pass


class HookError(FridaError):
    """Hook compilation or injection errors."""
    pass


class NetworkError(TrigDroidError):
    """Network communication errors."""
    pass


class PermissionError(DeviceError):
    """Permission-related errors."""
    pass


class PackageError(DeviceError):
    """Package installation/management errors."""
    pass