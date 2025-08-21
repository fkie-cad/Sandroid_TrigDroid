"""Main TrigDroid API for programmatic usage."""

from typing import Optional, Dict, Any, List
import logging
from contextlib import contextmanager

from .config import TestConfiguration
from .results import TestResult
from .devices import AndroidDevice, DeviceManager
from ..exceptions import TrigDroidError, DeviceError, ConfigurationError
from ..core.enums import LogLevel, TestPhase

# Import the refactored core components
from ...TrigDroid_Infrastructure.infrastructure.dependency_injection import configure_container, ServiceLocator
from ...TrigDroid_Infrastructure.infrastructure.logging import LoggerFactory
from ...TrigDroid_Infrastructure.application.orchestrator import ApplicationOrchestrator


class TrigDroidAPI:
    """Main API class for TrigDroid library usage.
    
    This class provides a clean, context-manager-based interface for running
    TrigDroid tests programmatically.
    
    Examples:
        # Basic usage
        config = TestConfiguration(package='com.example.app')
        with TrigDroidAPI(config) as api:
            result = api.run_tests()
        
        # Advanced usage with custom device
        device_manager = DeviceManager()
        device = device_manager.connect_to_device('emulator-5554')
        
        config = TestConfiguration(
            package='com.example.app',
            acceleration=5,
            battery_rotation=3,
            min_runtime=2
        )
        
        with TrigDroidAPI(config, device=device) as api:
            result = api.run_tests()
            
        # Async usage
        async with TrigDroidAPI(config) as api:
            result = await api.run_tests_async()
    """
    
    def __init__(self, 
                 config: TestConfiguration,
                 device: Optional[AndroidDevice] = None,
                 logger: Optional[logging.Logger] = None):
        """Initialize TrigDroid API.
        
        Args:
            config: Test configuration
            device: Optional pre-configured Android device
            logger: Optional custom logger
        """
        self._config = config
        self._device = device
        self._logger = logger
        self._orchestrator: Optional[ApplicationOrchestrator] = None
        self._container = None
        self._initialized = False
        
        # Validate configuration
        if not self._config.is_valid():
            raise ConfigurationError(f"Invalid configuration: {self._config.validation_errors}")
    
    def __enter__(self) -> 'TrigDroidAPI':
        """Enter context manager."""
        self._initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager with cleanup."""
        self._cleanup()
        
    async def __aenter__(self) -> 'TrigDroidAPI':
        """Async context manager entry."""
        self._initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self._cleanup()
    
    def _initialize(self) -> None:
        """Initialize the API components."""
        if self._initialized:
            return
            
        try:
            # Setup dependency injection
            self._container = configure_container()
            ServiceLocator.set_container(self._container)
            
            # Setup logger
            if not self._logger:
                logger_factory = LoggerFactory()
                self._logger = logger_factory.create_standard_logger(
                    level=self._config.log_level,
                    log_file=self._config.log_file,
                    suppress_console=self._config.suppress_console_logs
                )
            
            # Setup device if not provided
            if not self._device:
                device_manager = DeviceManager(self._logger)
                self._device = device_manager.connect_to_device(self._config.device_id)
                if not self._device:
                    raise DeviceError("Failed to connect to Android device")
            
            # Create orchestrator
            self._orchestrator = self._container.resolve(ApplicationOrchestrator)
            
            self._initialized = True
            
        except Exception as e:
            raise TrigDroidError(f"Failed to initialize TrigDroid API: {e}")
    
    def run_tests(self) -> TestResult:
        """Run TrigDroid tests synchronously.
        
        Returns:
            TestResult object containing test results and metadata
            
        Raises:
            TrigDroidError: If tests fail to execute
            DeviceError: If device communication fails
        """
        if not self._initialized:
            raise TrigDroidError("API not initialized. Use within context manager.")
            
        try:
            self._logger.info("Starting TrigDroid test execution")
            
            # Setup phase
            if not self._orchestrator.setup():
                return TestResult(
                    success=False,
                    phase=TestPhase.SETUP,
                    error="Setup phase failed",
                    config=self._config
                )
            
            # Execution phase
            if not self._orchestrator.execute_tests():
                return TestResult(
                    success=False,
                    phase=TestPhase.EXECUTION,
                    error="Test execution failed",
                    config=self._config
                )
            
            self._logger.info("TrigDroid tests completed successfully")
            return TestResult(
                success=True,
                phase=TestPhase.EXECUTION,
                config=self._config
            )
            
        except Exception as e:
            self._logger.error(f"Test execution failed: {e}")
            return TestResult(
                success=False,
                phase=TestPhase.EXECUTION,
                error=str(e),
                config=self._config
            )
        finally:
            # Always run teardown
            if self._orchestrator:
                self._orchestrator.teardown()
    
    async def run_tests_async(self) -> TestResult:
        """Run TrigDroid tests asynchronously.
        
        Returns:
            TestResult object containing test results and metadata
        """
        # For now, run synchronously but can be made truly async later
        return self.run_tests()
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get information about the connected Android device.
        
        Returns:
            Dictionary containing device information
        """
        if not self._device:
            raise DeviceError("No device connected")
            
        return self._device.get_device_info()
    
    def list_installed_packages(self) -> List[str]:
        """Get list of installed packages on the device.
        
        Returns:
            List of package names
        """
        if not self._device:
            raise DeviceError("No device connected")
            
        result = self._device.execute_command("shell pm list packages")
        if not result.success:
            raise DeviceError("Failed to list packages")
            
        packages = []
        for line in result.stdout.decode().strip().split('\n'):
            if line.startswith('package:'):
                packages.append(line.replace('package:', ''))
                
        return packages
    
    def is_package_installed(self, package_name: str) -> bool:
        """Check if a package is installed on the device.
        
        Args:
            package_name: Package name to check
            
        Returns:
            True if package is installed, False otherwise
        """
        if not self._device:
            raise DeviceError("No device connected")
            
        return self._device.is_app_installed(package_name)
    
    def install_package(self, apk_path: str) -> bool:
        """Install an APK package on the device.
        
        Args:
            apk_path: Path to APK file
            
        Returns:
            True if installation successful, False otherwise
        """
        if not self._device:
            raise DeviceError("No device connected")
            
        return self._device.install_app(apk_path)
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self._orchestrator:
                self._orchestrator.teardown()
                
            if self._logger:
                self._logger.info("TrigDroid API cleanup completed")
                
        except Exception as e:
            if self._logger:
                self._logger.warning(f"Error during cleanup: {e}")
        finally:
            self._initialized = False


# Convenience function for simple use cases
def quick_test(package: str, 
               device_id: Optional[str] = None,
               **test_options) -> TestResult:
    """Quick test function for simple use cases.
    
    Args:
        package: Package name to test
        device_id: Optional device ID
        **test_options: Additional test configuration options
        
    Returns:
        TestResult object
        
    Example:
        result = quick_test('com.example.app', acceleration=5, battery_rotation=3)
    """
    config = TestConfiguration(
        package=package,
        device_id=device_id,
        **test_options
    )
    
    with TrigDroidAPI(config) as api:
        return api.run_tests()