"""Test runner wrapper classes for TrigDroid API."""

from typing import Optional, Dict, Any
import logging

from .config import TestConfiguration
from .results import TestResult
from .devices import AndroidDevice
from ..core.enums import TestPhase
from ..exceptions import TestExecutionError


class TestRunner:
    """High-level test runner that wraps the infrastructure layer.
    
    This class provides a simplified interface for running TrigDroid tests
    while maintaining all the power of the underlying infrastructure.
    
    Examples:
        # Basic usage
        runner = TestRunner()
        result = runner.run_test(config, device)
        
        # With custom logger
        runner = TestRunner(logger=my_logger)
        result = runner.run_test(config, device)
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)
        
        # Import infrastructure components
        from ..TrigDroid.infrastructure.dependency_injection import ServiceContainer
        from ..TrigDroid.infrastructure.orchestration import ApplicationOrchestrator
        
        # Initialize service container
        self._container = ServiceContainer()
        self._container.register_singleton("ILogger", lambda: self._logger)
        
    def run_test(self, config: TestConfiguration, device: AndroidDevice) -> TestResult:
        """Run a complete TrigDroid test.
        
        Args:
            config: Test configuration
            device: Target Android device
            
        Returns:
            TestResult containing execution details
            
        Raises:
            TestExecutionError: If test execution fails
        """
        result = TestResult(success=False, phase=TestPhase.SETUP, config=config)
        
        try:
            # Setup phase
            self._logger.info(f"Starting test for package: {config.package}")
            result.device_info = device.get_device_info()
            
            # Get orchestrator from infrastructure
            from ..TrigDroid.infrastructure.orchestration import ApplicationOrchestrator
            orchestrator = ApplicationOrchestrator(self._logger)
            
            # Convert API config to infrastructure format
            infra_config = self._convert_config_to_infra(config)
            
            # Execution phase
            result.phase = TestPhase.EXECUTION
            
            # Run the actual test using infrastructure
            success = orchestrator.run_application_test(
                device._device,  # Use the underlying infrastructure device
                infra_config
            )
            
            result.success = success
            
            if success:
                self._logger.info("Test completed successfully")
                result.add_test_result("main_test", True)
            else:
                self._logger.error("Test failed")
                result.add_test_result("main_test", False, "Test execution failed")
            
        except Exception as e:
            self._logger.error(f"Test execution error: {e}")
            result.error = str(e)
            result.success = False
            raise TestExecutionError(f"Test execution failed: {e}") from e
        
        finally:
            # Teardown phase
            result.phase = TestPhase.TEARDOWN
            result.mark_completed()
            
        return result
    
    def _convert_config_to_infra(self, config: TestConfiguration) -> Dict[str, Any]:
        """Convert API configuration to infrastructure format.
        
        Args:
            config: API configuration
            
        Returns:
            Dictionary in infrastructure format
        """
        return {
            'package': config.package,
            'acceleration': config.acceleration,
            'sensors': config.sensors,
            'battery_rotation': config.battery_rotation,
            'network_states': config.network_states,
            'phone_type': config.phone_type,
            'network_type': config.network_type,
            'bluetooth_mac': config.bluetooth_mac,
            'nfc_available': config.nfc_available,
            'sensor_count': config.sensor_count,
            'logfile': config.logfile,
            'changelog': config.changelog,
            'image': config.image,
            'timeout': config.timeout,
            'verbose': config.verbose
        }
    
    def validate_config(self, config: TestConfiguration) -> bool:
        """Validate test configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not config.package:
            self._logger.error("Package name is required")
            return False
            
        if config.acceleration < 0 or config.acceleration > 10:
            self._logger.error("Acceleration must be between 0 and 10")
            return False
            
        return True
    
    def get_test_info(self, config: TestConfiguration) -> Dict[str, Any]:
        """Get information about what a test would do.
        
        Args:
            config: Test configuration
            
        Returns:
            Dictionary with test information
        """
        return {
            'package': config.package,
            'acceleration_level': config.acceleration,
            'sensor_tests': config.sensors,
            'network_tests': len(config.network_states) > 0,
            'battery_tests': config.battery_rotation > 0,
            'estimated_duration': self._estimate_duration(config),
            'hooks_to_load': self._get_hooks_list(config)
        }
    
    def _estimate_duration(self, config: TestConfiguration) -> int:
        """Estimate test duration in seconds.
        
        Args:
            config: Test configuration
            
        Returns:
            Estimated duration in seconds
        """
        base_time = 30  # Base time for setup/teardown
        
        # Add time based on acceleration level
        acceleration_time = config.acceleration * 10
        
        # Add time for sensor tests
        if config.sensors:
            acceleration_time += len(config.sensors) * 5
        
        # Add time for network state changes
        network_time = len(config.network_states) * 3
        
        # Add time for battery rotation
        battery_time = config.battery_rotation * 5
        
        return base_time + acceleration_time + network_time + battery_time
    
    def _get_hooks_list(self, config: TestConfiguration) -> list:
        """Get list of Frida hooks that would be loaded.
        
        Args:
            config: Test configuration
            
        Returns:
            List of hook names
        """
        hooks = ['main.js']  # Always load main hook
        
        if config.sensors:
            hooks.append('android-sensors.js')
        
        if config.network_states:
            hooks.append('android-network.js')
        
        if config.phone_type or config.network_type:
            hooks.append('android-telephony.js')
        
        return hooks