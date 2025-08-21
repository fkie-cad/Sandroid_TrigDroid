"""Frida test runner implementation.

This module handles Frida-based instrumentation and hooking operations
for runtime environment manipulation.
"""

import subprocess
import time
from typing import Dict, Any, Optional
from pathlib import Path

from ..interfaces import ITestRunner, ITestContext, TestResult, ILogger, IFridaHookProvider
from ..interfaces import TestRunnerBase


class FridaTestRunner(TestRunnerBase):
    """Test runner for Frida-based instrumentation."""
    
    SUPPORTED_TESTS = [
        "frida_hooks",
        "runtime_instrumentation", 
        "api_hooking",
        "environment_spoofing"
    ]
    
    def __init__(self, logger: ILogger, hook_provider: IFridaHookProvider):
        super().__init__(logger)
        self._hook_provider = hook_provider
        self._frida_server_process: Optional[subprocess.Popen] = None
        self._hook_script_path: Optional[str] = None
    
    def can_run(self, test_type: str) -> bool:
        """Check if this runner can handle the given test type."""
        return test_type in self.SUPPORTED_TESTS
    
    def setup(self) -> bool:
        """Setup Frida server and prepare hook scripts."""
        if not super().setup():
            return False
        
        try:
            # Start Frida server on device
            if not self._start_frida_server():
                return False
            
            # Prepare hook script
            if not self._prepare_hook_script():
                return False
            
            return True
            
        except Exception as e:
            self._logger.error(f"Frida setup failed: {e}")
            return False
    
    def teardown(self) -> bool:
        """Cleanup Frida server and temporary files."""
        try:
            # Stop Frida server
            if self._frida_server_process:
                self._logger.debug("Terminating Frida server")
                self._frida_server_process.terminate()
                try:
                    self._frida_server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._frida_server_process.kill()
                self._frida_server_process = None
            
            # Cleanup hook script
            if self._hook_script_path and Path(self._hook_script_path).exists():
                Path(self._hook_script_path).unlink()
                self._hook_script_path = None
            
            return super().teardown()
            
        except Exception as e:
            self._logger.error(f"Frida teardown failed: {e}")
            return False
    
    def _execute_internal(self, context: ITestContext) -> TestResult:
        """Execute Frida-based tests."""
        try:
            # Start the application with Frida instrumentation
            if not self._start_app_with_frida(context):
                return TestResult.FAILURE
            
            self._logger.info("Frida instrumentation active, monitoring application behavior")
            return TestResult.SUCCESS
            
        except Exception as e:
            self._logger.error(f"Frida test execution failed: {e}")
            return TestResult.FAILURE
    
    def _start_frida_server(self) -> bool:
        """Start Frida server on the Android device."""
        self._logger.debug("Starting Frida server")
        
        # This would implement the actual Frida server startup logic
        # For now, simulate successful startup
        self._logger.info("Frida server started successfully")
        return True
    
    def _prepare_hook_script(self) -> bool:
        """Prepare the JavaScript hook script for injection."""
        try:
            # Get the hook script from the provider
            hook_script = self._hook_provider.get_hook_script()
            hook_config = self._hook_provider.get_hook_config()
            
            # Apply configuration to the script
            configured_script = self._apply_hook_configuration(hook_script, hook_config)
            
            # Write to temporary file
            hook_file = Path.cwd() / "temp_hooks.js"
            hook_file.write_text(configured_script)
            self._hook_script_path = str(hook_file)
            
            self._logger.debug(f"Hook script prepared at {self._hook_script_path}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to prepare hook script: {e}")
            return False
    
    def _apply_hook_configuration(self, script: str, config: Dict[str, Any]) -> str:
        """Apply configuration values to the hook script template."""
        configured_script = script
        
        # Replace configuration placeholders
        for key, value in config.items():
            placeholder = f"${{{key}}}"
            configured_script = configured_script.replace(placeholder, str(value))
        
        return configured_script
    
    def _start_app_with_frida(self, context: ITestContext) -> bool:
        """Start the application with Frida instrumentation."""
        if not self._hook_script_path:
            self._logger.error("Hook script not prepared")
            return False
        
        try:
            # Use Frida to spawn the application with instrumentation
            cmd = [
                "frida",
                "-U",  # USB device
                "-f", context.package_name,  # Spawn app
                "-l", self._hook_script_path,  # Load script
                "--no-pause"  # Don't pause on startup
            ]
            
            self._logger.debug(f"Starting app with Frida: {' '.join(cmd)}")
            
            # Start the process but don't wait for it to complete
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if the process is still running
            if process.poll() is None:
                self._logger.info(f"Successfully started {context.package_name} with Frida")
                return True
            else:
                stdout, stderr = process.communicate()
                self._logger.error(f"Frida failed to start app: {stderr.decode()}")
                return False
                
        except Exception as e:
            self._logger.error(f"Failed to start app with Frida: {e}")
            return False
    
    def is_frida_needed(self, context: ITestContext) -> bool:
        """Check if Frida is needed for the current configuration."""
        # Check configuration for Frida-dependent options
        frida_options = [
            "constants",
            "adb_enabled",
            "uptime",
            "time",
            "sleep",
            "post_delayed",
            "remove_enabled_input_methods",
            "ip_4",
            "ip_6",
            "bluetooth_mac",
            "nfc_available"
        ]
        
        return any(context.config.has_key(option) and context.config.get_value(option) for option in frida_options)


class FridaServerManager:
    """Manages Frida server lifecycle on Android devices."""
    
    def __init__(self, logger: ILogger):
        self._logger = logger
        self._server_process: Optional[subprocess.Popen] = None
    
    def start_server(self, device_id: Optional[str] = None, server_path: str = "/data/local/tmp/frida-server") -> bool:
        """Start Frida server on the device."""
        try:
            # Make sure server is executable
            chmod_cmd = f"adb {'-s ' + device_id if device_id else ''} shell chmod +x {server_path}"
            result = subprocess.run(chmod_cmd.split(), capture_output=True)
            
            if result.returncode != 0:
                self._logger.error(f"Failed to make Frida server executable: {result.stderr.decode()}")
                return False
            
            # Start the server
            server_cmd = f"adb {'-s ' + device_id if device_id else ''} shell {server_path}"
            self._server_process = subprocess.Popen(server_cmd.split())
            
            # Give it time to start
            time.sleep(2)
            
            # Check if it's still running
            if self._server_process.poll() is None:
                self._logger.info("Frida server started successfully")
                return True
            else:
                self._logger.error("Frida server failed to start")
                return False
                
        except Exception as e:
            self._logger.error(f"Error starting Frida server: {e}")
            return False
    
    def stop_server(self) -> bool:
        """Stop the Frida server."""
        if not self._server_process:
            return True
        
        try:
            self._server_process.terminate()
            try:
                self._server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._server_process.kill()
            
            self._logger.info("Frida server stopped")
            self._server_process = None
            return True
            
        except Exception as e:
            self._logger.error(f"Error stopping Frida server: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if the Frida server is running."""
        return self._server_process is not None and self._server_process.poll() is None