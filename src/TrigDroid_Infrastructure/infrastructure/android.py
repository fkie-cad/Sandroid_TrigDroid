"""Android device abstraction following SOLID principles.

This module provides a clean abstraction over ADB operations
that can be easily tested and extended.
"""

import subprocess
import json
from typing import Dict, List, Optional, Union
from enum import Enum

from ..interfaces import IAndroidDevice, ICommandResult, ILogger, DeviceConnectionState
from ..infrastructure.dependency_injection import Injectable


class CommandResult(ICommandResult):
    """Implementation of command result interface."""
    
    def __init__(self, return_code: int, stdout: bytes, stderr: bytes):
        self._return_code = return_code
        self._stdout = stdout
        self._stderr = stderr
    
    @property
    def return_code(self) -> int:
        """Return code of the command."""
        return self._return_code
    
    @property
    def stdout(self) -> bytes:
        """Standard output."""
        return self._stdout
    
    @property
    def stderr(self) -> bytes:
        """Standard error output."""
        return self._stderr
    
    @property
    def success(self) -> bool:
        """Whether the command was successful."""
        return self._return_code == 0


class AndroidDevice(IAndroidDevice, Injectable):
    """Android device implementation using ADB."""
    
    def __init__(self, logger: ILogger, device_id: Optional[str] = None):
        super().__init__()
        self._logger = logger
        self._device_id = device_id
        self._current_package: Optional[str] = None
    
    def execute_command(self, command: str) -> ICommandResult:
        """Execute an ADB command."""
        full_command = self._build_adb_command(command)
        
        try:
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                timeout=30
            )
            
            cmd_result = CommandResult(result.returncode, result.stdout, result.stderr)
            
            if not cmd_result.success:
                self._logger.debug(f"Command failed: {full_command}")
                self._logger.debug(f"Error: {cmd_result.stderr.decode()}")
            
            return cmd_result
            
        except subprocess.TimeoutExpired:
            self._logger.error(f"Command timed out: {full_command}")
            return CommandResult(124, b"", b"Command timed out")
        except Exception as e:
            self._logger.error(f"Command execution failed: {e}")
            return CommandResult(1, b"", str(e).encode())
    
    def install_app(self, apk_path: str) -> bool:
        """Install an APK file."""
        result = self.execute_command(f"install {apk_path}")
        if result.success:
            self._logger.info(f"Successfully installed {apk_path}")
            return True
        else:
            self._logger.error(f"Failed to install {apk_path}: {result.stderr.decode()}")
            return False
    
    def uninstall_app(self, package_name: str) -> bool:
        """Uninstall an application."""
        result = self.execute_command(f"uninstall {package_name}")
        if result.success:
            self._logger.info(f"Successfully uninstalled {package_name}")
            return True
        else:
            self._logger.error(f"Failed to uninstall {package_name}: {result.stderr.decode()}")
            return False
    
    def start_app(self, package_name: Optional[str] = None) -> bool:
        """Start an application."""
        pkg = package_name or self._current_package
        if not pkg:
            self._logger.error("No package name provided for app start")
            return False
        
        # Get main activity
        main_activity = self._get_main_activity(pkg)
        if not main_activity:
            return False
        
        result = self.execute_command(f"shell am start -n {pkg}/{main_activity}")
        if result.success:
            self._logger.info(f"Successfully started {pkg}")
            return True
        else:
            self._logger.error(f"Failed to start {pkg}: {result.stderr.decode()}")
            return False
    
    def stop_app(self, package_name: Optional[str] = None) -> bool:
        """Stop an application."""
        pkg = package_name or self._current_package
        if not pkg:
            self._logger.error("No package name provided for app stop")
            return False
        
        result = self.execute_command(f"shell am force-stop {pkg}")
        if result.success:
            self._logger.info(f"Successfully stopped {pkg}")
            return True
        else:
            self._logger.error(f"Failed to stop {pkg}: {result.stderr.decode()}")
            return False
    
    def is_app_installed(self, package_name: str) -> bool:
        """Check if an application is installed."""
        result = self.execute_command(f"shell pm list packages {package_name}")
        return result.success and package_name in result.stdout.decode()
    
    def get_device_info(self) -> Dict[str, str]:
        """Get device information."""
        info = {}
        
        # Get device properties
        properties_to_get = [
            'ro.product.model',
            'ro.product.brand',
            'ro.product.manufacturer',
            'ro.build.version.release',
            'ro.build.version.sdk',
            'ro.product.board',
            'ro.product.device'
        ]
        
        for prop in properties_to_get:
            result = self.execute_command(f"shell getprop {prop}")
            if result.success:
                info[prop] = result.stdout.decode().strip()
        
        return info
    
    def set_current_package(self, package_name: str) -> None:
        """Set the current test package."""
        self._current_package = package_name
    
    def get_connection_state(self) -> DeviceConnectionState:
        """Get the device connection state."""
        if not self._device_id:
            return DeviceConnectionState.DISCONNECTED
        
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        if result.returncode != 0:
            return DeviceConnectionState.DISCONNECTED
        
        for line in result.stdout.split('\n')[1:]:
            if line.strip() and self._device_id in line:
                if 'device' in line:
                    return DeviceConnectionState.CONNECTED
                elif 'unauthorized' in line:
                    return DeviceConnectionState.UNAUTHORIZED
        
        return DeviceConnectionState.DISCONNECTED
    
    def grant_permission(self, package_name: str, permission: str) -> bool:
        """Grant a permission to an app."""
        result = self.execute_command(f"shell pm grant {package_name} {permission}")
        if result.success:
            self._logger.info(f"Granted permission {permission} to {package_name}")
            return True
        else:
            self._logger.warning(f"Failed to grant permission {permission} to {package_name}")
            return False
    
    def revoke_permission(self, package_name: str, permission: str) -> bool:
        """Revoke a permission from an app."""
        result = self.execute_command(f"shell pm revoke {package_name} {permission}")
        if result.success:
            self._logger.info(f"Revoked permission {permission} from {package_name}")
            return True
        else:
            self._logger.warning(f"Failed to revoke permission {permission} from {package_name}")
            return False
    
    def push_file(self, local_path: str, remote_path: str) -> bool:
        """Push a file to the device."""
        result = self.execute_command(f"push {local_path} {remote_path}")
        return result.success
    
    def pull_file(self, remote_path: str, local_path: str) -> bool:
        """Pull a file from the device."""
        result = self.execute_command(f"pull {remote_path} {local_path}")
        return result.success
    
    def root(self) -> bool:
        """Root the ADB connection."""
        result = self.execute_command("root")
        if result.success:
            self._logger.info("Successfully rooted ADB connection")
            return True
        else:
            self._logger.warning("Failed to root ADB connection")
            return False
    
    def unroot(self) -> bool:
        """Unroot the ADB connection."""
        result = self.execute_command("unroot")
        if result.success:
            self._logger.info("Successfully unrooted ADB connection")
            return True
        else:
            self._logger.warning("Failed to unroot ADB connection")
            return False
    
    def _build_adb_command(self, command: str) -> str:
        """Build the full ADB command."""
        base_cmd = "adb"
        if self._device_id:
            base_cmd += f" -s {self._device_id}"
        return f"{base_cmd} {command}"
    
    def _get_main_activity(self, package_name: str) -> Optional[str]:
        """Get the main activity of a package."""
        result = self.execute_command(f"shell pm dump {package_name} | grep -A 1 'android.intent.action.MAIN'")
        
        if not result.success:
            self._logger.warning(f"Could not get main activity for {package_name}")
            return None
        
        output = result.stdout.decode()
        # Parse the output to extract the main activity
        # This is a simplified version - the actual implementation would be more robust
        for line in output.split('\n'):
            if 'Activity' in line and package_name in line:
                # Extract activity name
                start = line.find(package_name)
                if start != -1:
                    activity = line[start:].split()[0]
                    return activity.replace(f"{package_name}/", "").replace(f"{package_name}", "")
        
        return None


class DeviceManager:
    """Manager for discovering and connecting to Android devices."""
    
    def __init__(self, logger: ILogger):
        self._logger = logger
    
    def list_devices(self) -> List[str]:
        """List all connected devices."""
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if result.returncode != 0:
                self._logger.error("Failed to list devices")
                return []
            
            devices = []
            for line in result.stdout.split('\n')[1:]:
                if line.strip() and '\t' in line:
                    device_id = line.split('\t')[0]
                    devices.append(device_id)
            
            return devices
            
        except Exception as e:
            self._logger.error(f"Error listing devices: {e}")
            return []
    
    def connect_to_device(self, device_id: Optional[str] = None) -> Optional[AndroidDevice]:
        """Connect to a specific device or auto-select if only one available."""
        available_devices = self.list_devices()
        
        if not available_devices:
            self._logger.error("No devices connected")
            return None
        
        if device_id:
            if device_id not in available_devices:
                self._logger.error(f"Device {device_id} not found")
                return None
            selected_device = device_id
        else:
            if len(available_devices) > 1:
                self._logger.error("Multiple devices connected, please specify device ID")
                return None
            selected_device = available_devices[0]
        
        self._logger.info(f"Connected to device: {selected_device}")
        return AndroidDevice(self._logger, selected_device)