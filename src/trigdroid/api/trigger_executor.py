"""Standalone trigger executor for individual trigger execution.

Allows executing individual triggers (sensors, network, battery) without
a full TrigDroid test run. Uses ADB commands directly via subprocess.
"""

import subprocess
from dataclasses import dataclass
from logging import getLogger

logger = getLogger(__name__)

# Sensor name mapping: user-friendly name -> emulator sensor name
SENSOR_NAME_MAP = {
    "accelerometer": "acceleration",
    "gyroscope": "gyroscope",
    "light": "light",
    "pressure": "pressure",
    "magnetometer": "magnetic-field",
}


@dataclass
class TriggerResult:
    """Result of a trigger execution.

    Attributes:
        success: Whether the trigger executed successfully
        message: Human-readable result message
        error: Error details if failed
    """

    success: bool
    message: str = ""
    error: str | None = None


class TriggerExecutor:
    """Execute individual triggers without a full test run.

    Provides methods for sensor manipulation, network toggling,
    and battery level control via ADB commands.

    Args:
        device_id: Optional device serial (e.g., "emulator-5554").
            If provided, commands target that specific device.
    """

    def __init__(self, device_id: str | None = None) -> None:
        """Initialize the TriggerExecutor.

        Args:
            device_id: Optional ADB device serial number
        """
        self._device_id = device_id

    def _run_adb(self, *args: str) -> tuple[str, str, int]:
        """Run an ADB command and return stdout, stderr, returncode.

        Args:
            *args: ADB command arguments (without 'adb' prefix)

        Returns:
            Tuple of (stdout, stderr, returncode)
        """
        cmd = ["adb"]
        if self._device_id:
            cmd.extend(["-s", self._device_id])
        cmd.extend(args)

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15, check=False
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            logger.error(f"ADB command timed out: {cmd}")
            return "", "Command timed out", 1
        except Exception as e:
            logger.error(f"ADB command failed: {e}")
            return "", str(e), 1

    # ── Sensors ─────────────────────────────────────────────────────

    def set_sensor(self, sensor_type: str, level: int) -> TriggerResult:
        """Set a sensor value on the emulator.

        Args:
            sensor_type: Sensor type (accelerometer, gyroscope, light, pressure)
            level: Sensor level value

        Returns:
            TriggerResult with success/failure status
        """
        sensor_name = SENSOR_NAME_MAP.get(sensor_type)
        if not sensor_name:
            return TriggerResult(
                success=False,
                message=f"Unknown sensor: {sensor_type}",
                error=f"Supported: {', '.join(SENSOR_NAME_MAP.keys())}",
            )

        # Multi-axis sensors get 3D values, single-value sensors get scalar
        if sensor_name in ("acceleration", "gyroscope"):
            values = f"{level}:{level}:{level}"
        else:
            values = str(level)

        stdout, stderr, rc = self._run_adb("emu", "sensor", "set", sensor_name, values)
        if rc != 0:
            return TriggerResult(
                success=False,
                message=f"Failed to set {sensor_type}",
                error=stderr,
            )
        return TriggerResult(success=True, message=f"{sensor_type} set to {level}")

    def reset_sensors(self) -> TriggerResult:
        """Reset all sensors to default values.

        Returns:
            TriggerResult with success/failure status
        """
        defaults = {
            "acceleration": "0:9.77622:0.813417",
            "gyroscope": "0:0:0",
            "light": "0",
            "pressure": "0",
        }
        for sensor_name, default_val in defaults.items():
            stdout, stderr, rc = self._run_adb(
                "emu", "sensor", "set", sensor_name, default_val
            )
            if rc != 0:
                return TriggerResult(
                    success=False,
                    message=f"Failed to reset {sensor_name}",
                    error=stderr,
                )
        return TriggerResult(success=True, message="Sensors reset to defaults")

    # ── Network ─────────────────────────────────────────────────────

    def _toggle_svc(self, service: str, label: str, enabled: bool) -> TriggerResult:
        """Toggle an Android system service via ``adb shell svc``.

        Args:
            service: The svc name ("wifi", "data", "bluetooth")
            label: Human-readable label ("WiFi", "Mobile data", "Bluetooth")
            enabled: True to enable, False to disable

        Returns:
            TriggerResult with success/failure status
        """
        action = "enable" if enabled else "disable"
        _stdout, stderr, rc = self._run_adb("shell", "svc", service, action)
        if rc != 0:
            return TriggerResult(
                success=False, message=f"Failed to {action} {label}", error=stderr
            )
        state = "enabled" if enabled else "disabled"
        return TriggerResult(success=True, message=f"{label} {state}")

    def toggle_wifi(self, enabled: bool) -> TriggerResult:
        """Toggle WiFi on/off.

        Args:
            enabled: True to enable, False to disable

        Returns:
            TriggerResult with success/failure status
        """
        return self._toggle_svc("wifi", "WiFi", enabled)

    def toggle_mobile_data(self, enabled: bool) -> TriggerResult:
        """Toggle mobile data on/off.

        Args:
            enabled: True to enable, False to disable

        Returns:
            TriggerResult with success/failure status
        """
        return self._toggle_svc("data", "Mobile data", enabled)

    def toggle_bluetooth(self, enabled: bool) -> TriggerResult:
        """Toggle Bluetooth on/off.

        Args:
            enabled: True to enable, False to disable

        Returns:
            TriggerResult with success/failure status
        """
        return self._toggle_svc("bluetooth", "Bluetooth", enabled)

    # ── Battery ─────────────────────────────────────────────────────

    def set_battery_level(self, level: int) -> TriggerResult:
        """Set battery level on the emulator.

        Args:
            level: Battery level (0-100)

        Returns:
            TriggerResult with success/failure status
        """
        if not 0 <= level <= 100:
            return TriggerResult(
                success=False,
                message="Battery level must be 0-100",
                error=f"Invalid level: {level}",
            )
        stdout, stderr, rc = self._run_adb("emu", "power", "capacity", str(level))
        if rc != 0:
            return TriggerResult(
                success=False,
                message="Failed to set battery level",
                error=stderr,
            )
        return TriggerResult(success=True, message=f"Battery set to {level}%")

    def set_battery_status(self, charging: bool) -> TriggerResult:
        """Set battery charging status.

        Args:
            charging: True for charging, False for discharging

        Returns:
            TriggerResult with success/failure status
        """
        status = "charging" if charging else "discharging"
        stdout, stderr, rc = self._run_adb("emu", "power", "status", status)
        if rc != 0:
            return TriggerResult(
                success=False,
                message=f"Failed to set battery status to {status}",
                error=stderr,
            )
        return TriggerResult(success=True, message=f"Battery status: {status}")
