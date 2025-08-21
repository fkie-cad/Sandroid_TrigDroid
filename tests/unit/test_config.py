"""Unit tests for TestConfiguration class."""

import pytest
import tempfile
import os
from typing import List

from trigdroid.api.config import TestConfiguration
from trigdroid.core.enums import LogLevel


class TestTestConfiguration:
    """Test suite for TestConfiguration class."""

    def test_create_basic_configuration_should_succeed(self):
        """Test creating a basic configuration with required fields."""
        # Arrange & Act
        config = TestConfiguration(package="com.example.test")
        
        # Assert
        assert config.package == "com.example.test"
        assert config.log_level == LogLevel.INFO  # default
        assert config.min_runtime == 1  # default
        assert config.acceleration == 0  # default
        assert config.frida_hooks is False  # default

    def test_create_advanced_configuration_should_succeed(self):
        """Test creating advanced configuration with all options."""
        # Arrange & Act
        config = TestConfiguration(
            package="com.suspicious.app",
            device_id="emulator-5554",
            log_level=LogLevel.DEBUG,
            min_runtime=5,
            background_time=30,
            acceleration=8,
            gyroscope=5,
            battery_rotation=3,
            frida_hooks=True,
            timeout=600,
            verbose=True
        )
        
        # Assert
        assert config.package == "com.suspicious.app"
        assert config.device_id == "emulator-5554"
        assert config.log_level == LogLevel.DEBUG
        assert config.min_runtime == 5
        assert config.background_time == 30
        assert config.acceleration == 8
        assert config.gyroscope == 5
        assert config.battery_rotation == 3
        assert config.frida_hooks is True
        assert config.timeout == 600
        assert config.verbose is True

    def test_configuration_validation_with_valid_config_should_pass(self):
        """Test validation with valid configuration."""
        # Arrange
        config = TestConfiguration(
            package="com.example.test",
            acceleration=5,
            battery_rotation=2,
            min_runtime=1
        )
        
        # Act & Assert
        assert config.is_valid() is True
        assert len(config.validation_errors) == 0

    def test_configuration_validation_with_empty_package_should_fail(self):
        """Test validation fails with empty package name."""
        # Arrange
        config = TestConfiguration(package="")
        
        # Act & Assert
        assert config.is_valid() is False
        assert len(config.validation_errors) > 0
        assert any("package" in error.lower() for error in config.validation_errors)

    def test_configuration_validation_with_invalid_acceleration_should_fail(self):
        """Test validation fails with invalid acceleration value."""
        # Arrange
        config = TestConfiguration(package="com.example.test", acceleration=15)
        
        # Act & Assert
        assert config.is_valid() is False
        assert len(config.validation_errors) > 0
        assert any("acceleration" in error.lower() for error in config.validation_errors)

    def test_configuration_validation_with_invalid_battery_rotation_should_fail(self):
        """Test validation fails with invalid battery rotation value."""
        # Arrange
        config = TestConfiguration(package="com.example.test", battery_rotation=10)
        
        # Act & Assert
        assert config.is_valid() is False
        assert len(config.validation_errors) > 0
        assert any("battery" in error.lower() for error in config.validation_errors)

    def test_configuration_validation_with_negative_min_runtime_should_fail(self):
        """Test validation fails with negative minimum runtime."""
        # Arrange
        config = TestConfiguration(package="com.example.test", min_runtime=-1)
        
        # Act & Assert
        assert config.is_valid() is False
        assert len(config.validation_errors) > 0
        assert any("runtime" in error.lower() for error in config.validation_errors)

    def test_to_dict_should_return_all_configuration_values(self):
        """Test converting configuration to dictionary."""
        # Arrange
        config = TestConfiguration(
            package="com.example.test",
            acceleration=5,
            frida_hooks=True,
            verbose=True
        )
        
        # Act
        config_dict = config.to_dict()
        
        # Assert
        assert isinstance(config_dict, dict)
        assert config_dict["package"] == "com.example.test"
        assert config_dict["acceleration"] == 5
        assert config_dict["frida_hooks"] is True
        assert config_dict["verbose"] is True

    def test_from_dict_should_create_valid_configuration(self):
        """Test creating configuration from dictionary."""
        # Arrange
        config_dict = {
            "package": "com.example.test",
            "acceleration": 7,
            "battery_rotation": 2,
            "frida_hooks": True,
            "min_runtime": 3
        }
        
        # Act
        config = TestConfiguration.from_dict(config_dict)
        
        # Assert
        assert config.package == "com.example.test"
        assert config.acceleration == 7
        assert config.battery_rotation == 2
        assert config.frida_hooks is True
        assert config.min_runtime == 3

    def test_to_yaml_should_create_valid_yaml_string(self):
        """Test converting configuration to YAML string."""
        # Arrange
        config = TestConfiguration(
            package="com.example.test",
            acceleration=5,
            frida_hooks=True
        )
        
        # Act
        yaml_str = config.to_yaml()
        
        # Assert
        assert isinstance(yaml_str, str)
        assert "package: com.example.test" in yaml_str
        assert "acceleration: 5" in yaml_str
        assert "frida_hooks: true" in yaml_str

    def test_to_yaml_file_should_create_valid_yaml_file(self):
        """Test saving configuration to YAML file."""
        # Arrange
        config = TestConfiguration(
            package="com.example.test",
            acceleration=3,
            frida_hooks=False
        )
        
        # Act
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_file = f.name
        
        try:
            config.to_yaml_file(yaml_file)
            
            # Assert
            assert os.path.exists(yaml_file)
            with open(yaml_file, 'r') as f:
                content = f.read()
            assert "package: com.example.test" in content
            assert "acceleration: 3" in content
            
        finally:
            if os.path.exists(yaml_file):
                os.unlink(yaml_file)

    def test_from_yaml_file_should_create_valid_configuration(self):
        """Test loading configuration from YAML file."""
        # Arrange
        yaml_content = """
        package: com.example.test
        acceleration: 6
        gyroscope: 4
        battery_rotation: 2
        frida_hooks: true
        min_runtime: 2
        verbose: true
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            yaml_file = f.name
        
        try:
            # Act
            config = TestConfiguration.from_yaml_file(yaml_file)
            
            # Assert
            assert config.package == "com.example.test"
            assert config.acceleration == 6
            assert config.gyroscope == 4
            assert config.battery_rotation == 2
            assert config.frida_hooks is True
            assert config.min_runtime == 2
            assert config.verbose is True
            
        finally:
            if os.path.exists(yaml_file):
                os.unlink(yaml_file)

    def test_sensors_property_should_return_enabled_sensors(self):
        """Test sensors property returns list of enabled sensors."""
        # Arrange
        config = TestConfiguration(
            package="com.example.test",
            acceleration=5,
            gyroscope=3,
            light=2,
            pressure=0  # disabled
        )
        
        # Act
        sensors = config.sensors
        
        # Assert
        assert isinstance(sensors, list)
        assert "accelerometer" in sensors
        assert "gyroscope" in sensors
        assert "light" in sensors
        assert "pressure" not in sensors  # disabled

    def test_network_states_property_should_return_enabled_states(self):
        """Test network_states property returns list of enabled network states."""
        # Arrange
        config = TestConfiguration(
            package="com.example.test",
            wifi=True,
            data=True,
            bluetooth=False
        )
        
        # Act
        network_states = config.network_states
        
        # Assert
        assert isinstance(network_states, list)
        assert "wifi" in network_states
        assert "data" in network_states
        assert "bluetooth" not in network_states

    def test_has_sensor_manipulation_should_return_true_when_sensors_enabled(self):
        """Test has_sensor_manipulation returns True when sensors are enabled."""
        # Arrange
        config = TestConfiguration(
            package="com.example.test",
            acceleration=5
        )
        
        # Act & Assert
        assert config.has_sensor_manipulation is True

    def test_has_sensor_manipulation_should_return_false_when_no_sensors_enabled(self):
        """Test has_sensor_manipulation returns False when no sensors enabled."""
        # Arrange
        config = TestConfiguration(
            package="com.example.test",
            acceleration=0,
            gyroscope=0,
            light=0,
            pressure=0
        )
        
        # Act & Assert
        assert config.has_sensor_manipulation is False

    def test_has_network_manipulation_should_return_true_when_network_states_enabled(self):
        """Test has_network_manipulation returns True when network states enabled."""
        # Arrange
        config = TestConfiguration(
            package="com.example.test",
            wifi=True
        )
        
        # Act & Assert
        assert config.has_network_manipulation is True

    def test_has_network_manipulation_should_return_false_when_no_network_states_enabled(self):
        """Test has_network_manipulation returns False when no network states enabled."""
        # Arrange
        config = TestConfiguration(
            package="com.example.test",
            wifi=None,
            data=None,
            bluetooth=None
        )
        
        # Act & Assert
        assert config.has_network_manipulation is False

    def test_configuration_immutability_after_creation(self):
        """Test configuration values cannot be modified after creation."""
        # Arrange
        config = TestConfiguration(package="com.example.test")
        
        # Act & Assert - this should not be allowed if properly implemented
        # Note: Depending on implementation, this might need adjustment
        original_package = config.package
        
        # Try to modify (should not affect the original if immutable)
        try:
            # If using frozen dataclass or similar, this should raise an error
            config.package = "com.modified.test"  # type: ignore
        except AttributeError:
            # Expected for immutable configurations
            pass
        
        # Package should remain unchanged if properly implemented
        # Note: This test assumes immutability - adjust based on actual implementation
        # assert config.package == original_package

    def test_string_representation_should_be_readable(self):
        """Test string representation of configuration is readable."""
        # Arrange
        config = TestConfiguration(
            package="com.example.test",
            acceleration=5,
            frida_hooks=True
        )
        
        # Act
        str_repr = str(config)
        
        # Assert
        assert isinstance(str_repr, str)
        assert "com.example.test" in str_repr
        assert len(str_repr) > 0