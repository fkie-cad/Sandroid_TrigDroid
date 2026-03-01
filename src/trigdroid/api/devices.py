"""Device management classes for TrigDroid API."""

from typing import List, Dict, Any, Optional
import subprocess
import logging

from ..core.enums import DeviceConnectionState
from ..exceptions import DeviceError


class CommandResult:
    """Result of an ADB command execution."""

    def __init__(self, return_code: int, stdout: bytes, stderr: bytes):
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr

    @property
    def success(self) -> bool:
        """Return True if the command completed successfully."""
        return self.return_code == 0


class AndroidDevice:
    """Represents an Android device for testing.

    Standalone implementation that communicates directly with ADB
    via subprocess calls. Does not depend on the infrastructure layer.
    """

    def __init__(self, device_id: str, logger: Optional[logging.Logger] = None):
        self.device_id = device_id
        self._logger = logger or logging.getLogger(__name__)

    def execute_command(self, command: str) -> CommandResult:
        """Execute an ADB command on this device.

        Args:
            command: The ADB command string (e.g. 'shell echo test').
                     Will be split and prepended with 'adb -s <device_id>'.

        Returns:
            CommandResult with return_code, stdout, stderr, and success.
        """
        cmd_list = ['adb', '-s', self.device_id] + command.split()
        try:
            result = subprocess.run(cmd_list, capture_output=True, timeout=30)
            return CommandResult(result.returncode, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return CommandResult(124, b"", b"Command timed out")

    def install_app(self, apk_path: str) -> bool:
        """Install an APK on the device.

        Args:
            apk_path: Path to the APK file.

        Returns:
            True if installation succeeded, False otherwise.
        """
        result = subprocess.run(
            ['adb', '-s', self.device_id, 'install', apk_path],
            capture_output=True,
            timeout=120,
        )
        return result.returncode == 0

    def uninstall_app(self, package_name: str) -> bool:
        """Uninstall an app from the device.

        Args:
            package_name: The package name to uninstall.

        Returns:
            True if uninstallation succeeded, False otherwise.
        """
        result = subprocess.run(
            ['adb', '-s', self.device_id, 'uninstall', package_name],
            capture_output=True,
            timeout=60,
        )
        return result.returncode == 0

    def start_app(self, package_name: str) -> bool:
        """Start an application on the device.

        Args:
            package_name: The package name to start.

        Returns:
            True if the start command succeeded, False otherwise.
        """
        result = subprocess.run(
            [
                'adb', '-s', self.device_id, 'shell', 'am', 'start',
                '-n', f'{package_name}/.MainActivity',
            ],
            capture_output=True,
            timeout=30,
        )
        return result.returncode == 0

    def stop_app(self, package_name: str) -> bool:
        """Stop an application on the device.

        Args:
            package_name: The package name to stop.

        Returns:
            True if the stop command succeeded, False otherwise.
        """
        result = subprocess.run(
            [
                'adb', '-s', self.device_id, 'shell', 'am', 'force-stop',
                package_name,
            ],
            capture_output=True,
            timeout=30,
        )
        return result.returncode == 0

    def is_app_installed(self, package_name: str) -> bool:
        """Check whether an app is installed on the device.

        Args:
            package_name: The package name to check.

        Returns:
            True if the package is found in the device's package list.
        """
        result = subprocess.run(
            ['adb', '-s', self.device_id, 'shell', 'pm', 'list', 'packages'],
            capture_output=True,
            timeout=30,
        )
        return package_name in result.stdout.decode('utf-8', errors='replace')

    def get_device_info(self) -> Dict[str, str]:
        """Retrieve device information via ADB getprop calls.

        Returns:
            Dictionary with keys: id, model, android_version, api_level, arch.
        """
        properties = [
            ('model', 'ro.product.model'),
            ('android_version', 'ro.build.version.release'),
            ('api_level', 'ro.build.version.sdk'),
            ('arch', 'ro.product.cpu.abi'),
        ]

        info: Dict[str, str] = {'id': self.device_id}

        for key, prop in properties:
            result = subprocess.run(
                ['adb', '-s', self.device_id, 'shell', 'getprop', prop],
                capture_output=True,
                timeout=30,
            )
            info[key] = result.stdout.decode('utf-8', errors='replace').strip()

        return info

    def is_connected(self) -> bool:
        """Check whether the device is reachable.

        Returns:
            True if a simple shell echo command succeeds.
        """
        result = self.execute_command('shell echo ping')
        return result.success

    def grant_permission(self, package_name: str, permission: str) -> bool:
        """Grant a runtime permission to an app.

        Args:
            package_name: The target package.
            permission: The Android permission string.

        Returns:
            True if the grant command succeeded, False otherwise.
        """
        result = subprocess.run(
            [
                'adb', '-s', self.device_id, 'shell', 'pm', 'grant',
                package_name, permission,
            ],
            capture_output=True,
            timeout=30,
        )
        return result.returncode == 0

    def revoke_permission(self, package_name: str, permission: str) -> bool:
        """Revoke a runtime permission from an app.

        Args:
            package_name: The target package.
            permission: The Android permission string.

        Returns:
            True if the revoke command succeeded, False otherwise.
        """
        result = subprocess.run(
            [
                'adb', '-s', self.device_id, 'shell', 'pm', 'revoke',
                package_name, permission,
            ],
            capture_output=True,
            timeout=30,
        )
        return result.returncode == 0


class DeviceManager:
    """Manages Android device connections and discovery."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)

    def list_devices(self) -> List[Dict[str, str]]:
        """List all connected Android devices.

        Returns:
            List of device information dictionaries.
        """
        try:
            result = subprocess.run(
                ['adb', 'devices', '-l'],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                raise DeviceError("Failed to list devices - is ADB installed?")

            devices = []
            all_lines = result.stdout.strip().split('\n')

            # Skip the ADB header line if present
            if all_lines and all_lines[0].startswith('List of devices'):
                lines = all_lines[1:]
            else:
                lines = all_lines

            for line in lines:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    status = parts[1]

                    device_info = {
                        'id': device_id,
                        'status': status,
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
        except DeviceError:
            raise
        except Exception as e:
            raise DeviceError(f"Error listing devices: {e}")

    def connect_to_device(self, device_id: Optional[str] = None) -> Optional[AndroidDevice]:
        """Connect to a specific device or auto-select if only one available.

        Args:
            device_id: Specific device ID to connect to, or None for auto-select.

        Returns:
            AndroidDevice instance or None if connection fails.
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
                    return AndroidDevice(device_id)

            self._logger.error(f"Device {device_id} not found or not connected")
            return None

        # Auto-select the first available device
        selected_id = connected_devices[0]['id']
        if len(connected_devices) > 1:
            self._logger.warning(
                f"Multiple devices connected ({len(connected_devices)}), "
                f"auto-selected first device: {selected_id}"
            )
        else:
            self._logger.info(f"Auto-selected device: {selected_id}")
        return AndroidDevice(selected_id)

    def get_device_info(self, device_id: str) -> Dict[str, Any]:
        """Get detailed information about a device.

        Args:
            device_id: Device ID to query.

        Returns:
            Dictionary containing device information.
        """
        device = AndroidDevice(device_id)
        return device.get_device_info()

    def wait_for_device(self, device_id: Optional[str] = None, timeout: int = 30) -> Optional[AndroidDevice]:
        """Wait for a device to become available.

        Args:
            device_id: Specific device to wait for, or None for any device.
            timeout: Timeout in seconds.

        Returns:
            AndroidDevice instance or None if timeout.
        """
        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            device = self.connect_to_device(device_id)
            if device:
                return device

            time.sleep(1)

        return None


def scan_devices() -> List[Dict[str, str]]:
    """Scan for connected Android devices.

    Convenience function that creates a DeviceManager and lists devices.

    Returns:
        List of device information dictionaries.
    """
    manager = DeviceManager()
    return manager.list_devices()
