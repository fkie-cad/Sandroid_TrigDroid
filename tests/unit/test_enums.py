"""Unit tests for core enums."""

import pytest
from trigdroid.core.enums import LogLevel, TestPhase
from TrigDroid_Infrastructure.interfaces import TestResult, DeviceConnectionState


class TestLogLevel:
    """Test suite for LogLevel enum."""

    def test_all_log_levels_exist(self):
        """Test all expected log levels are defined."""
        # Act & Assert
        assert LogLevel.DEBUG.value == "DEBUG"
        assert LogLevel.INFO.value == "INFO"
        assert LogLevel.WARNING.value == "WARNING"
        assert LogLevel.ERROR.value == "ERROR"
        assert LogLevel.CRITICAL.value == "CRITICAL"

    def test_log_level_comparison(self):
        """Test log level comparison works as expected."""
        # Act & Assert
        assert LogLevel.DEBUG != LogLevel.INFO
        assert LogLevel.ERROR == LogLevel.ERROR
        assert LogLevel.CRITICAL != LogLevel.WARNING

    def test_log_level_string_conversion(self):
        """Test converting log levels to strings."""
        # Act & Assert
        assert str(LogLevel.DEBUG) == "LogLevel.DEBUG"
        assert str(LogLevel.INFO) == "LogLevel.INFO"
        assert str(LogLevel.ERROR) == "LogLevel.ERROR"

    def test_log_level_from_string(self):
        """Test creating log level from string value."""
        # Act & Assert
        assert LogLevel("DEBUG") == LogLevel.DEBUG
        assert LogLevel("INFO") == LogLevel.INFO
        assert LogLevel("ERROR") == LogLevel.ERROR

    def test_invalid_log_level_raises_error(self):
        """Test invalid log level raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError):
            LogLevel("INVALID")


class TestTestPhase:
    """Test suite for TestPhase enum."""

    def test_all_test_phases_exist(self):
        """Test all expected test phases are defined."""
        # Act & Assert
        assert TestPhase.SETUP.value == "SETUP"
        assert TestPhase.EXECUTION.value == "EXECUTION"
        assert TestPhase.TEARDOWN.value == "TEARDOWN"

    def test_test_phase_comparison(self):
        """Test test phase comparison works as expected."""
        # Act & Assert
        assert TestPhase.SETUP != TestPhase.EXECUTION
        assert TestPhase.EXECUTION == TestPhase.EXECUTION
        assert TestPhase.TEARDOWN != TestPhase.SETUP

    def test_test_phase_string_conversion(self):
        """Test converting test phases to strings."""
        # Act & Assert
        assert str(TestPhase.SETUP) == "TestPhase.SETUP"
        assert str(TestPhase.EXECUTION) == "TestPhase.EXECUTION"
        assert str(TestPhase.TEARDOWN) == "TestPhase.TEARDOWN"

    def test_test_phase_from_string(self):
        """Test creating test phase from string value."""
        # Act & Assert
        assert TestPhase("SETUP") == TestPhase.SETUP
        assert TestPhase("EXECUTION") == TestPhase.EXECUTION
        assert TestPhase("TEARDOWN") == TestPhase.TEARDOWN

    def test_invalid_test_phase_raises_error(self):
        """Test invalid test phase raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError):
            TestPhase("INVALID")


class TestTestResult:
    """Test suite for TestResult enum."""

    def test_all_test_results_exist(self):
        """Test all expected test results are defined."""
        # Act & Assert
        assert TestResult.SUCCESS.value == "SUCCESS"
        assert TestResult.FAILURE.value == "FAILURE"
        assert TestResult.SKIPPED.value == "SKIPPED"

    def test_test_result_comparison(self):
        """Test test result comparison works as expected."""
        # Act & Assert
        assert TestResult.SUCCESS != TestResult.FAILURE
        assert TestResult.SUCCESS == TestResult.SUCCESS
        assert TestResult.FAILURE != TestResult.SKIPPED

    def test_test_result_boolean_evaluation(self):
        """Test test result boolean evaluation."""
        # Note: This depends on implementation - adjust if needed
        # Act & Assert
        assert TestResult.SUCCESS  # Should be truthy
        assert TestResult.FAILURE  # Enums are truthy by default
        assert TestResult.SKIPPED  # Enums are truthy by default

    def test_test_result_from_string(self):
        """Test creating test result from string value."""
        # Act & Assert
        assert TestResult("SUCCESS") == TestResult.SUCCESS
        assert TestResult("FAILURE") == TestResult.FAILURE
        assert TestResult("SKIPPED") == TestResult.SKIPPED

    def test_invalid_test_result_raises_error(self):
        """Test invalid test result raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError):
            TestResult("INVALID")


class TestDeviceConnectionState:
    """Test suite for DeviceConnectionState enum."""

    def test_all_device_states_exist(self):
        """Test all expected device connection states are defined."""
        # Act & Assert
        assert DeviceConnectionState.CONNECTED.value == "CONNECTED"
        assert DeviceConnectionState.DISCONNECTED.value == "DISCONNECTED"
        assert DeviceConnectionState.UNAUTHORIZED.value == "UNAUTHORIZED"

    def test_device_state_comparison(self):
        """Test device state comparison works as expected."""
        # Act & Assert
        assert DeviceConnectionState.CONNECTED != DeviceConnectionState.DISCONNECTED
        assert DeviceConnectionState.CONNECTED == DeviceConnectionState.CONNECTED
        assert DeviceConnectionState.UNAUTHORIZED != DeviceConnectionState.CONNECTED

    def test_device_state_from_string(self):
        """Test creating device state from string value."""
        # Act & Assert
        assert DeviceConnectionState("CONNECTED") == DeviceConnectionState.CONNECTED
        assert DeviceConnectionState("DISCONNECTED") == DeviceConnectionState.DISCONNECTED
        assert DeviceConnectionState("UNAUTHORIZED") == DeviceConnectionState.UNAUTHORIZED

    def test_invalid_device_state_raises_error(self):
        """Test invalid device state raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError):
            DeviceConnectionState("INVALID")


class TestEnumInteractions:
    """Test interactions between different enums."""

    def test_enums_are_distinct_types(self):
        """Test that different enum types cannot be compared."""
        # Act & Assert
        assert LogLevel.DEBUG != TestPhase.SETUP
        assert TestResult.SUCCESS != DeviceConnectionState.CONNECTED
        
        # Type checking
        assert isinstance(LogLevel.INFO, LogLevel)
        assert isinstance(TestPhase.EXECUTION, TestPhase)
        assert isinstance(TestResult.SUCCESS, TestResult)
        assert isinstance(DeviceConnectionState.CONNECTED, DeviceConnectionState)

    def test_enum_membership_checks(self):
        """Test enum membership checks work correctly."""
        # Act & Assert
        assert LogLevel.DEBUG in LogLevel
        assert TestPhase.SETUP in TestPhase
        assert TestResult.SUCCESS in TestResult
        assert DeviceConnectionState.CONNECTED in DeviceConnectionState
        
        # Negative checks
        assert "DEBUG" not in LogLevel  # string is not a member
        assert "INVALID" not in LogLevel

    def test_enum_iteration(self):
        """Test enum iteration works correctly."""
        # Act
        log_levels = list(LogLevel)
        test_phases = list(TestPhase)
        test_results = list(TestResult)
        device_states = list(DeviceConnectionState)
        
        # Assert
        assert len(log_levels) == 5
        assert len(test_phases) == 3
        assert len(test_results) == 3
        assert len(device_states) == 3
        
        assert LogLevel.DEBUG in log_levels
        assert TestPhase.SETUP in test_phases
        assert TestResult.SUCCESS in test_results
        assert DeviceConnectionState.CONNECTED in device_states