"""Test context implementation for TrigDroid.

This module provides the test execution context that contains all
necessary dependencies for test runners.
"""

from ..interfaces import ITestContext, IAndroidDevice, IConfigurationProvider, ILogger


class TestContext(ITestContext):
    """Implementation of test execution context."""
    
    def __init__(self, 
                 device: IAndroidDevice,
                 config: IConfigurationProvider,
                 logger: ILogger,
                 package_name: str):
        self._device = device
        self._config = config
        self._logger = logger
        self._package_name = package_name
    
    @property
    def device(self) -> IAndroidDevice:
        """Get the Android device instance."""
        return self._device
    
    @property
    def config(self) -> IConfigurationProvider:
        """Get the configuration provider."""
        return self._config
    
    @property
    def logger(self) -> ILogger:
        """Get the logger instance."""
        return self._logger
    
    @property
    def package_name(self) -> str:
        """Get the package name being tested."""
        return self._package_name