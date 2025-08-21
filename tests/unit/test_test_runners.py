"""Unit tests for test runners."""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from TrigDroid_Infrastructure.interfaces import (
    ILogger, ITestContext, TestResult, TestRunnerBase
)
from TrigDroid_Infrastructure.test_runners.sensor_test_runner import SensorTestRunner
from TrigDroid_Infrastructure.test_runners.frida_test_runner import FridaTestRunner


class MockTestRunner(TestRunnerBase):
    """Mock test runner implementation for testing base class."""
    
    def __init__(self, logger: ILogger, can_run_result: bool = True, 
                 execute_result: TestResult = TestResult.SUCCESS):
        super().__init__(logger)
        self._can_run_result = can_run_result
        self._execute_result = execute_result
        
    def can_run(self, test_type: str) -> bool:
        return self._can_run_result
    
    def _execute_internal(self, context: ITestContext) -> TestResult:
        return self._execute_result


class TestTestRunnerBase:
    """Test suite for TestRunnerBase abstract class."""
    
    def test_runner_initialization_should_succeed(self, mock_logger):
        """Test runner initialization with logger."""
        # Act
        runner = MockTestRunner(mock_logger)
        
        # Assert
        assert runner._logger is mock_logger
        assert runner._is_setup is False
    
    def test_setup_should_mark_runner_as_setup(self, mock_logger):
        """Test setup marks runner as initialized."""
        # Arrange
        runner = MockTestRunner(mock_logger)
        
        # Act
        result = runner.setup()
        
        # Assert
        assert result is True
        assert runner._is_setup is True
    
    def test_teardown_should_mark_runner_as_not_setup(self, mock_logger):
        """Test teardown marks runner as not initialized."""
        # Arrange
        runner = MockTestRunner(mock_logger)
        runner._is_setup = True
        
        # Act
        result = runner.teardown()
        
        # Assert
        assert result is True
        assert runner._is_setup is False
    
    def test_execute_should_call_setup_when_not_setup(self, mock_logger, mock_test_context):
        """Test execute calls setup when runner is not setup."""
        # Arrange
        runner = MockTestRunner(mock_logger)
        assert runner._is_setup is False
        
        # Act
        result = runner.execute(mock_test_context)
        
        # Assert
        assert result == TestResult.SUCCESS
        assert runner._is_setup is True
    
    def test_execute_should_not_call_setup_when_already_setup(self, mock_logger, mock_test_context):
        """Test execute doesn't call setup when already setup."""
        # Arrange
        runner = MockTestRunner(mock_logger)
        runner._is_setup = True
        
        # Act
        result = runner.execute(mock_test_context)
        
        # Assert
        assert result == TestResult.SUCCESS
        assert runner._is_setup is True
    
    def test_execute_should_return_failure_when_setup_fails(self, mock_logger, mock_test_context):
        """Test execute returns failure when setup fails."""
        # Arrange
        runner = MockTestRunner(mock_logger)
        
        with patch.object(runner, 'setup', return_value=False):
            # Act
            result = runner.execute(mock_test_context)
            
            # Assert
            assert result == TestResult.FAILURE
    
    def test_execute_should_handle_exceptions_and_return_failure(self, mock_logger, mock_test_context):
        """Test execute handles exceptions and returns failure."""
        # Arrange
        runner = MockTestRunner(mock_logger)
        
        with patch.object(runner, '_execute_internal', side_effect=Exception("Test error")):
            # Act
            result = runner.execute(mock_test_context)
            
            # Assert
            assert result == TestResult.FAILURE
            mock_logger.error.assert_called()
    
    def test_execute_should_return_internal_result_on_success(self, mock_logger, mock_test_context):
        """Test execute returns internal execution result on success."""
        # Arrange
        runner = MockTestRunner(mock_logger, execute_result=TestResult.SKIPPED)
        
        # Act
        result = runner.execute(mock_test_context)
        
        # Assert
        assert result == TestResult.SKIPPED


class TestSensorTestRunner:
    """Test suite for SensorTestRunner class."""
    
    def test_sensor_runner_initialization_should_succeed(self, mock_logger):
        """Test sensor runner initialization."""
        # Act
        runner = SensorTestRunner(mock_logger)
        
        # Assert
        assert runner._logger is mock_logger
        assert isinstance(runner, TestRunnerBase)
    
    def test_can_run_should_return_true_for_sensor_test_type(self, mock_logger):
        """Test can_run returns True for sensor test type."""
        # Arrange
        runner = SensorTestRunner(mock_logger)
        
        # Act & Assert
        assert runner.can_run("sensor") is True
        assert runner.can_run("sensors") is True
        assert runner.can_run("accelerometer") is True
    
    def test_can_run_should_return_false_for_non_sensor_test_type(self, mock_logger):
        """Test can_run returns False for non-sensor test types."""
        # Arrange
        runner = SensorTestRunner(mock_logger)
        
        # Act & Assert
        assert runner.can_run("frida") is False
        assert runner.can_run("network") is False
        assert runner.can_run("unknown") is False
    
    @patch('TrigDroid_Infrastructure.test_runners.sensor_test_runner.SensorTestRunner._simulate_sensor_changes')
    def test_execute_internal_should_simulate_sensor_changes(self, mock_simulate, mock_logger, mock_test_context):
        """Test _execute_internal calls sensor simulation methods."""
        # Arrange
        runner = SensorTestRunner(mock_logger)
        mock_simulate.return_value = True
        
        # Act
        result = runner._execute_internal(mock_test_context)
        
        # Assert
        assert result == TestResult.SUCCESS
        mock_simulate.assert_called_once_with(mock_test_context)
    
    @patch('TrigDroid_Infrastructure.test_runners.sensor_test_runner.SensorTestRunner._simulate_sensor_changes')
    def test_execute_internal_should_return_failure_when_simulation_fails(self, mock_simulate, mock_logger, mock_test_context):
        """Test _execute_internal returns failure when sensor simulation fails."""
        # Arrange
        runner = SensorTestRunner(mock_logger)
        mock_simulate.return_value = False
        
        # Act
        result = runner._execute_internal(mock_test_context)
        
        # Assert
        assert result == TestResult.FAILURE
    
    def test_simulate_sensor_changes_should_log_sensor_activity(self, mock_logger, mock_test_context):
        """Test sensor simulation logs appropriate activity."""
        # Arrange
        runner = SensorTestRunner(mock_logger)
        mock_test_context.config.get_value = Mock(return_value=5)  # acceleration level
        mock_test_context.device.execute_command = Mock()
        mock_test_context.device.execute_command.return_value.success = True
        
        # Act
        result = runner._simulate_sensor_changes(mock_test_context)
        
        # Assert
        assert result is True
        mock_logger.info.assert_called()
    
    def test_get_sensor_commands_should_return_appropriate_commands(self, mock_logger):
        """Test sensor command generation for different sensor types."""
        # Arrange
        runner = SensorTestRunner(mock_logger)
        
        # Act
        accel_commands = runner._get_sensor_commands("accelerometer", 5)
        gyro_commands = runner._get_sensor_commands("gyroscope", 3)
        
        # Assert
        assert isinstance(accel_commands, list)
        assert isinstance(gyro_commands, list)
        assert len(accel_commands) > 0
        assert len(gyro_commands) > 0
        
        # Commands should be different for different sensors
        assert accel_commands != gyro_commands


class TestFridaTestRunner:
    """Test suite for FridaTestRunner class."""
    
    def test_frida_runner_initialization_should_succeed(self, mock_logger):
        """Test Frida runner initialization."""
        # Act
        runner = FridaTestRunner(mock_logger)
        
        # Assert
        assert runner._logger is mock_logger
        assert isinstance(runner, TestRunnerBase)
    
    def test_can_run_should_return_true_for_frida_test_type(self, mock_logger):
        """Test can_run returns True for Frida test type."""
        # Arrange
        runner = FridaTestRunner(mock_logger)
        
        # Act & Assert
        assert runner.can_run("frida") is True
        assert runner.can_run("hook") is True
        assert runner.can_run("instrumentation") is True
    
    def test_can_run_should_return_false_for_non_frida_test_type(self, mock_logger):
        """Test can_run returns False for non-Frida test types."""
        # Arrange
        runner = FridaTestRunner(mock_logger)
        
        # Act & Assert
        assert runner.can_run("sensor") is False
        assert runner.can_run("network") is False
        assert runner.can_run("unknown") is False
    
    @patch('TrigDroid_Infrastructure.test_runners.frida_test_runner.frida')
    def test_execute_internal_should_load_and_run_frida_hooks(self, mock_frida, mock_logger, mock_test_context):
        """Test _execute_internal loads and runs Frida hooks."""
        # Arrange
        runner = FridaTestRunner(mock_logger)
        mock_device = Mock()
        mock_session = Mock()
        mock_script = Mock()
        
        mock_frida.get_usb_device.return_value = mock_device
        mock_device.attach.return_value = mock_session
        mock_session.create_script.return_value = mock_script
        
        # Act
        result = runner._execute_internal(mock_test_context)
        
        # Assert
        assert result == TestResult.SUCCESS
        mock_frida.get_usb_device.assert_called()
        mock_session.create_script.assert_called()
        mock_script.load.assert_called()
    
    @patch('TrigDroid_Infrastructure.test_runners.frida_test_runner.frida')
    def test_execute_internal_should_handle_frida_errors(self, mock_frida, mock_logger, mock_test_context):
        """Test _execute_internal handles Frida errors gracefully."""
        # Arrange
        runner = FridaTestRunner(mock_logger)
        mock_frida.get_usb_device.side_effect = Exception("Frida error")
        
        # Act
        result = runner._execute_internal(mock_test_context)
        
        # Assert
        assert result == TestResult.FAILURE
        mock_logger.error.assert_called()
    
    def test_load_hook_script_should_return_hook_content(self, mock_logger):
        """Test hook script loading returns appropriate content."""
        # Arrange
        runner = FridaTestRunner(mock_logger)
        
        # Act
        script = runner._load_hook_script("sensor")
        
        # Assert
        assert isinstance(script, str)
        assert len(script) > 0
        # Should contain JavaScript/Frida code
        assert "Java.perform" in script or "function" in script
    
    def test_get_target_package_should_extract_package_from_context(self, mock_logger, mock_test_context):
        """Test target package extraction from context."""
        # Arrange
        runner = FridaTestRunner(mock_logger)
        mock_test_context.package_name = "com.example.target"
        
        # Act
        package = runner._get_target_package(mock_test_context)
        
        # Assert
        assert package == "com.example.target"
    
    @patch('TrigDroid_Infrastructure.test_runners.frida_test_runner.time.sleep')
    def test_wait_for_hooks_should_wait_appropriate_time(self, mock_sleep, mock_logger):
        """Test hook waiting mechanism."""
        # Arrange
        runner = FridaTestRunner(mock_logger)
        
        # Act
        runner._wait_for_hooks(5)  # 5 seconds
        
        # Assert
        mock_sleep.assert_called_with(5)


class TestTestRunnerFactory:
    """Test suite for test runner factory functionality."""
    
    def test_create_appropriate_runner_based_on_test_type(self, mock_logger):
        """Test creating appropriate runners based on test type."""
        # This would test a factory pattern if implemented
        # For now, we test direct instantiation
        
        # Act
        sensor_runner = SensorTestRunner(mock_logger)
        frida_runner = FridaTestRunner(mock_logger)
        
        # Assert
        assert sensor_runner.can_run("sensor")
        assert not sensor_runner.can_run("frida")
        
        assert frida_runner.can_run("frida")
        assert not frida_runner.can_run("sensor")
    
    def test_multiple_runners_can_coexist(self, mock_logger):
        """Test multiple test runners can coexist."""
        # Arrange & Act
        sensor_runner = SensorTestRunner(mock_logger)
        frida_runner = FridaTestRunner(mock_logger)
        
        # Assert
        assert sensor_runner is not frida_runner
        assert sensor_runner._logger is frida_runner._logger  # Same logger
        assert not sensor_runner._is_setup
        assert not frida_runner._is_setup
    
    def test_runners_maintain_independent_state(self, mock_logger):
        """Test runners maintain independent state."""
        # Arrange
        runner1 = SensorTestRunner(mock_logger)
        runner2 = SensorTestRunner(mock_logger)
        
        # Act
        runner1.setup()
        
        # Assert
        assert runner1._is_setup is True
        assert runner2._is_setup is False  # Independent state