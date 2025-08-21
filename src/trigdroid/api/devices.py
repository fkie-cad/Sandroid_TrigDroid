"""Device management classes for TrigDroid API."""

from typing import List, Dict, Any, Optional
import subprocess
import logging

from ..core.enums import DeviceConnectionState
from ..exceptions import DeviceError


class AndroidDevice:
    """Represents an Android device for testing.
    
    This class provides a simplified interface over the more complex
    infrastructure AndroidDevice class.
    """
    
    def __init__(self, device_id: str, logger: Optional[logging.Logger] = None):
        self.device_id = device_id
        self._logger = logger or logging.getLogger(__name__)
        
        # Import the infrastructure device class
        from ..TrigDroid.infrastructure.android import AndroidDevice as InfraDevice
        self._device = InfraDevice(self._logger, device_id)
    
    def execute_command(self, command: str):
        """Execute ADB command on device."""
        return self._device.execute_command(command)
    
    def install_app(self, apk_path: str) -> bool:
        """Install APK on device."""
        return self._device.install_app(apk_path)
    
    def uninstall_app(self, package_name: str) -> bool:
        """Uninstall app from device."""
        return self._device.uninstall_app(package_name)
    
    def is_app_installed(self, package_name: str) -> bool:
        """Check if app is installed."""
        return self._device.is_app_installed(package_name)
    
    def start_app(self, package_name: str) -> bool:
        """Start an application."""
        return self._device.start_app(package_name)
    
    def stop_app(self, package_name: str) -> bool:
        """Stop an application."""
        return self._device.stop_app(package_name)
    
    def get_device_info(self) -> Dict[str, str]:
        """Get device information."""
        return self._device.get_device_info()
    
    def grant_permission(self, package_name: str, permission: str) -> bool:
        """Grant permission to app."""
        return self._device.grant_permission(package_name, permission)
    
    def revoke_permission(self, package_name: str, permission: str) -> bool:
        """Revoke permission from app."""
        return self._device.revoke_permission(package_name, permission)


class DeviceManager:
    """Manages Android device connections and discovery."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)
    
    def list_devices(self) -> List[Dict[str, str]]:
        """List all connected Android devices.
        
        Returns:
            List of device information dictionaries
        """
        try:
            result = subprocess.run(
                ['adb', 'devices', '-l'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise DeviceError("Failed to list devices - is ADB installed?")
            
            devices = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    status = parts[1]
                    
                    device_info = {
                        'id': device_id,
                        'status': status
                    }
                    
                    # Parse additional info if available
                    for part in parts[2:]:
                        if ':' in part:
                            key, value = part.split(':', 1)
                            device_info[key] = value
                    
                    devices.append(device_info)
            
            return devices
            
        except subprocess.TimeoutExpired:
            raise DeviceError("Timeout while listing devices")
        except subprocess.CalledProcessError as e:
            raise DeviceError(f"ADB command failed: {e}")
        except Exception as e:
            raise DeviceError(f"Error listing devices: {e}")
    
    def connect_to_device(self, device_id: Optional[str] = None) -> Optional[AndroidDevice]:
        """Connect to a specific device or auto-select if only one available.
        
        Args:
            device_id: Specific device ID to connect to, or None for auto-select
            
        Returns:
            AndroidDevice instance or None if connection fails
        """
        devices = self.list_devices()
        
        # Filter to only connected devices
        connected_devices = [d for d in devices if d['status'] == 'device']
        
        if not connected_devices:
            self._logger.error("No connected Android devices found")
            return None
        
        if device_id:
            # Find specific device
            for device in connected_devices:
                if device['id'] == device_id:
                    self._logger.info(f"Connected to device: {device_id}")
                    return AndroidDevice(device_id, self._logger)
            
            self._logger.error(f"Device {device_id} not found or not connected")
            return None
        else:
            # Auto-select device
            if len(connected_devices) > 1:
                self._logger.error(f"Multiple devices connected ({len(connected_devices)}), please specify device ID")
                return None
            
            device_id = connected_devices[0]['id']
            self._logger.info(f"Auto-selected device: {device_id}")
            return AndroidDevice(device_id, self._logger)
    
    def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """Get detailed information about a device.
        
        Args:
            device_id: Device ID to query
            
        Returns:
            Dictionary containing device information
        """
        device = AndroidDevice(device_id, self._logger)
        return device.get_device_info()
    
    def wait_for_device(self, device_id: Optional[str] = None, timeout: int = 30) -> Optional[AndroidDevice]:
        """Wait for a device to become available.
        
        Args:
            device_id: Specific device to wait for, or None for any device
            timeout: Timeout in seconds
            
        Returns:
            AndroidDevice instance or None if timeout
        """
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            device = self.connect_to_device(device_id)
            if device:
                return device
            
            time.sleep(1)
        
        return None