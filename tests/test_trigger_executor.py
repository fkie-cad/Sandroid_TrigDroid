"""Tests for TriggerExecutor standalone trigger API."""

from unittest.mock import patch, MagicMock
import pytest
from trigdroid.api.trigger_executor import TriggerExecutor, TriggerResult


@pytest.fixture
def executor():
    return TriggerExecutor(device_id="emulator-5554")


class TestSensors:
    @patch("subprocess.run")
    def test_set_accelerometer(self, mock_run, executor):
        mock_run.return_value = MagicMock(stdout="OK", stderr="", returncode=0)
        result = executor.set_sensor("accelerometer", 5)
        assert result.success is True
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "sensor" in args and "set" in args and "acceleration" in args

    @patch("subprocess.run")
    def test_set_light(self, mock_run, executor):
        mock_run.return_value = MagicMock(stdout="OK", stderr="", returncode=0)
        result = executor.set_sensor("light", 3)
        assert result.success is True

    def test_unknown_sensor(self, executor):
        result = executor.set_sensor("unknown", 5)
        assert result.success is False

    @patch("subprocess.run")
    def test_reset_sensors(self, mock_run, executor):
        mock_run.return_value = MagicMock(stdout="OK", stderr="", returncode=0)
        result = executor.reset_sensors()
        assert result.success is True
        assert mock_run.call_count == 4


class TestNetwork:
    @patch("subprocess.run")
    def test_wifi_enable(self, mock_run, executor):
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        result = executor.toggle_wifi(True)
        assert result.success is True
        assert "enabled" in result.message

    @patch("subprocess.run")
    def test_wifi_disable(self, mock_run, executor):
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        result = executor.toggle_wifi(False)
        assert result.success is True
        assert "disabled" in result.message

    @patch("subprocess.run")
    def test_mobile_data(self, mock_run, executor):
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        result = executor.toggle_mobile_data(True)
        assert result.success is True

    @patch("subprocess.run")
    def test_bluetooth(self, mock_run, executor):
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        result = executor.toggle_bluetooth(False)
        assert result.success is True


class TestBattery:
    @patch("subprocess.run")
    def test_set_level(self, mock_run, executor):
        mock_run.return_value = MagicMock(stdout="OK", stderr="", returncode=0)
        result = executor.set_battery_level(50)
        assert result.success is True
        assert "50%" in result.message

    def test_invalid_level(self, executor):
        assert executor.set_battery_level(-1).success is False
        assert executor.set_battery_level(101).success is False

    @patch("subprocess.run")
    def test_battery_status(self, mock_run, executor):
        mock_run.return_value = MagicMock(stdout="OK", stderr="", returncode=0)
        result = executor.set_battery_status(True)
        assert result.success is True
        assert "charging" in result.message


class TestDeviceTargeting:
    @patch("subprocess.run")
    def test_device_id_in_command(self, mock_run):
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        ex = TriggerExecutor(device_id="emulator-5554")
        ex.toggle_wifi(True)
        args = mock_run.call_args[0][0]
        assert "-s" in args and "emulator-5554" in args

    @patch("subprocess.run")
    def test_no_device_id(self, mock_run):
        mock_run.return_value = MagicMock(stdout="", stderr="", returncode=0)
        ex = TriggerExecutor()
        ex.toggle_wifi(True)
        args = mock_run.call_args[0][0]
        assert "-s" not in args
