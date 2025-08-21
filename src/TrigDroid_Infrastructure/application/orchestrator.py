"""Application orchestrator following SOLID principles.

This module coordinates the entire TrigDroid testing flow with proper
separation of concerns and dependency inversion.
"""

from typing import List, Optional
from enum import Enum

from ..interfaces import (
    IApplicationOrchestrator, ILogger, IConfigurationProvider, 
    IAndroidDevice, ITestRunner, TestResult, IChangelogWriter
)
from ..test_runners import TestContext
from ..infrastructure.dependency_injection import Injectable


class TestPhase(Enum):
    """Test execution phases."""
    SETUP = "setup"
    EXECUTION = "execution" 
    TEARDOWN = "teardown"


class ApplicationOrchestrator(IApplicationOrchestrator, Injectable):
    """Main application orchestrator that coordinates the testing flow."""
    
    def __init__(self,
                 logger: ILogger,
                 config: IConfigurationProvider,
                 device: IAndroidDevice,
                 test_runners: List[ITestRunner],
                 changelog_writer: IChangelogWriter):
        super().__init__()
        self._logger = logger
        self._config = config
        self._device = device
        self._test_runners = test_runners
        self._changelog_writer = changelog_writer
        self._current_phase = TestPhase.SETUP
        self._test_context: Optional[TestContext] = None
    
    def setup(self) -> bool:
        """Setup phase: prepare device and test environment."""
        self._current_phase = TestPhase.SETUP
        self._logger.info("Starting device preparation for testing")
        
        try:
            # Initialize changelog
            if not self._initialize_changelog():
                return False
            
            # Prepare device
            if not self._prepare_device():
                return False
            
            # Setup test runners
            if not self._setup_test_runners():
                return False
            
            # Create test context
            package_name = self._config.get_value("package")
            if not package_name:
                self._logger.error("No package name configured")
                return False
                
            self._test_context = TestContext(
                device=self._device,
                config=self._config,
                logger=self._logger,
                package_name=str(package_name)
            )
            
            self._logger.info("Device preparation completed successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"Setup phase failed: {e}")
            return False
    
    def execute_tests(self) -> bool:
        """Execution phase: run the actual tests."""
        if not self._test_context:
            self._logger.error("Test context not initialized")
            return False
            
        self._current_phase = TestPhase.EXECUTION
        self._logger.info("Starting test execution")
        
        try:
            # Start the application
            if not self._start_application():
                return False
            
            # Execute test runners
            if not self._execute_test_runners():
                return False
            
            # Wait for minimum runtime
            self._wait_for_minimum_runtime()
            
            self._logger.info("Test execution completed successfully")
            return True
            
        except KeyboardInterrupt:
            self._logger.warning("Received keyboard interrupt during test execution")
            return False
        except Exception as e:
            self._logger.error(f"Test execution failed: {e}")
            return False
    
    def teardown(self) -> bool:
        """Teardown phase: cleanup resources."""
        self._current_phase = TestPhase.TEARDOWN
        self._logger.info("Starting teardown")
        
        try:
            # Stop application
            self._stop_application()
            
            # Teardown test runners
            self._teardown_test_runners()
            
            # Finalize changelog
            self._finalize_changelog()
            
            self._logger.info("Teardown completed successfully")
            return True
            
        except Exception as e:
            self._logger.error(f"Teardown failed: {e}")
            return False
    
    def _initialize_changelog(self) -> bool:
        """Initialize the changelog system."""
        try:
            disable_changelog = self._config.get_value("disable_changelog", False)
            if disable_changelog:
                self._logger.debug("Changelog disabled by configuration")
                return True
                
            changelog_file = self._config.get_value("changelog_file", "changelog.txt")
            # Initialize changelog with the specified file
            self._logger.debug(f"Initialized changelog: {changelog_file}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to initialize changelog: {e}")
            return False
    
    def _prepare_device(self) -> bool:
        """Prepare the Android device for testing."""
        try:
            # Unroot device by default for safety
            no_unroot = self._config.get_value("no_unroot", False)
            if not no_unroot:
                self._device.unroot()
            
            # Handle permissions
            if not self._handle_permissions():
                return False
            
            # Handle app installations/uninstallations
            if not self._handle_app_management():
                return False
            
            # Set device-specific configurations
            if not self._configure_device_settings():
                return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Device preparation failed: {e}")
            return False
    
    def _handle_permissions(self) -> bool:
        """Handle permission grants and revocations."""
        package_name = self._config.get_value("package")
        if not package_name:
            return True
            
        # Grant permissions
        grant_permissions = self._config.get_value("grant_permissions", [])
        if isinstance(grant_permissions, list):
            for permission in grant_permissions:
                if not self._device.grant_permission(str(package_name), permission):
                    self._logger.warning(f"Failed to grant permission {permission}")
        
        # Revoke permissions
        revoke_permissions = self._config.get_value("revoke_permissions", [])
        if isinstance(revoke_permissions, list):
            for permission in revoke_permissions:
                if not self._device.revoke_permission(str(package_name), permission):
                    self._logger.warning(f"Failed to revoke permission {permission}")
        
        return True
    
    def _handle_app_management(self) -> bool:
        """Handle app installations and uninstallations."""
        # Install dummy apps
        install_apps = self._config.get_value("install", [])
        if isinstance(install_apps, list):
            for app in install_apps:
                if not self._install_dummy_app(app):
                    self._logger.error(f"Failed to install dummy app {app}")
                    return False
        
        # Uninstall apps
        uninstall_apps = self._config.get_value("uninstall", [])
        if isinstance(uninstall_apps, list):
            for app in uninstall_apps:
                if not self._device.uninstall_app(app):
                    self._logger.warning(f"Failed to uninstall app {app}")
        
        return True
    
    def _configure_device_settings(self) -> bool:
        """Configure device-specific settings."""
        # Set accessibility service
        aas_enabled = self._config.get_value("android_accessability_service")
        if aas_enabled is not None:
            # Configure accessibility service
            pass
        
        # Set geolocation
        geolocation = self._config.get_value("geolocation")
        if geolocation:
            # Configure geolocation settings
            pass
        
        # Set language
        language = self._config.get_value("language")
        if language:
            # Configure system language
            pass
        
        return True
    
    def _setup_test_runners(self) -> bool:
        """Setup all test runners."""
        for runner in self._test_runners:
            if not runner.setup():
                self._logger.error(f"Failed to setup test runner {type(runner).__name__}")
                return False
        return True
    
    def _start_application(self) -> bool:
        """Start the target application."""
        if not self._test_context:
            return False
            
        package_name = self._test_context.package_name
        if package_name == "no_package":
            self._logger.info("Skipping app start - no_package specified")
            return True
        
        return self._device.start_app(package_name)
    
    def _execute_test_runners(self) -> bool:
        """Execute all applicable test runners."""
        if not self._test_context:
            return False
        
        success = True
        for runner in self._test_runners:
            try:
                result = runner.execute(self._test_context)
                if result == TestResult.FAILURE:
                    self._logger.error(f"Test runner {type(runner).__name__} failed")
                    success = False
                elif result == TestResult.SUCCESS:
                    self._logger.info(f"Test runner {type(runner).__name__} completed successfully")
                
            except Exception as e:
                self._logger.error(f"Test runner {type(runner).__name__} threw exception: {e}")
                success = False
        
        return success
    
    def _wait_for_minimum_runtime(self) -> None:
        """Wait for the configured minimum runtime."""
        min_runtime = self._config.get_value("min_runtime", 1)
        if isinstance(min_runtime, int) and min_runtime > 0:
            self._logger.info(f"Waiting {min_runtime} minutes for minimum runtime")
            import time
            time.sleep(min_runtime * 60)
            self._logger.debug("Minimum runtime wait completed")
    
    def _stop_application(self) -> None:
        """Stop the target application."""
        if not self._test_context:
            return
            
        package_name = self._test_context.package_name
        if package_name != "no_package":
            # Wait a moment before closing
            import time
            time.sleep(3)
            self._device.stop_app(package_name)
    
    def _teardown_test_runners(self) -> None:
        """Teardown all test runners."""
        for runner in self._test_runners:
            try:
                runner.teardown()
            except Exception as e:
                self._logger.warning(f"Error during teardown of {type(runner).__name__}: {e}")
    
    def _finalize_changelog(self) -> None:
        """Finalize the changelog."""
        try:
            disable_changelog = self._config.get_value("disable_changelog", False)
            if not disable_changelog:
                self._changelog_writer.flush()
                self._logger.debug("Changelog finalized")
        except Exception as e:
            self._logger.warning(f"Error finalizing changelog: {e}")
    
    def _install_dummy_app(self, app_name: str) -> bool:
        """Install a dummy app for testing."""
        # This would implement the dummy app installation logic
        # For now, just check if app is already installed
        if self._device.is_app_installed(app_name):
            self._logger.info(f"Skip installation of {app_name} - already installed")
            return True
        
        self._logger.info(f"Installing dummy app: {app_name}")
        # Actual installation logic would go here
        return True


class OrchestratorBuilder:
    """Builder for creating application orchestrator with dependencies."""
    
    def __init__(self):
        self._logger: Optional[ILogger] = None
        self._config: Optional[IConfigurationProvider] = None
        self._device: Optional[IAndroidDevice] = None
        self._test_runners: List[ITestRunner] = []
        self._changelog_writer: Optional[IChangelogWriter] = None
    
    def with_logger(self, logger: ILogger) -> 'OrchestratorBuilder':
        """Set the logger."""
        self._logger = logger
        return self
    
    def with_config(self, config: IConfigurationProvider) -> 'OrchestratorBuilder':
        """Set the configuration provider."""
        self._config = config
        return self
    
    def with_device(self, device: IAndroidDevice) -> 'OrchestratorBuilder':
        """Set the Android device."""
        self._device = device
        return self
    
    def add_test_runner(self, runner: ITestRunner) -> 'OrchestratorBuilder':
        """Add a test runner."""
        self._test_runners.append(runner)
        return self
    
    def with_changelog_writer(self, writer: IChangelogWriter) -> 'OrchestratorBuilder':
        """Set the changelog writer."""
        self._changelog_writer = writer
        return self
    
    def build(self) -> ApplicationOrchestrator:
        """Build the orchestrator."""
        if not all([self._logger, self._config, self._device, self._changelog_writer]):
            raise ValueError("Missing required dependencies for ApplicationOrchestrator")
        
        return ApplicationOrchestrator(
            logger=self._logger,
            config=self._config,
            device=self._device,
            test_runners=self._test_runners,
            changelog_writer=self._changelog_writer
        )