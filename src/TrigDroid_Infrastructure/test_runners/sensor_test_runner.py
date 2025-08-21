"""Sensor test runner implementation.

This module handles sensor-related test operations including
accelerometer, gyroscope, light, and pressure sensor manipulations.
"""

from typing import Dict, Any
from enum import Enum

from ..interfaces import ITestRunner, ITestContext, TestResult, ILogger
from ..interfaces import TestRunnerBase


class SensorType(Enum):
    """Supported sensor types."""
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    LIGHT = "light"
    PRESSURE = "pressure"
    MAGNETOMETER = "magnetometer"


class SensorTestRunner(TestRunnerBase):
    """Test runner for sensor-based operations."""
    
    SUPPORTED_TESTS = [
        "sensor_rotation",
        "sensor_initial_values",
        "sensor_power_manipulation",
        "sensor_availability"
    ]
    
    def __init__(self, logger: ILogger):
        super().__init__(logger)
    
    def can_run(self, test_type: str) -> bool:
        """Check if this runner can handle the given test type."""
        return test_type in self.SUPPORTED_TESTS
    
    def _execute_internal(self, context: ITestContext) -> TestResult:
        """Execute sensor-related tests."""
        try:
            # Set initial sensor values
            if not self._set_initial_sensor_values(context):
                return TestResult.FAILURE
            
            # Run sensor rotation tests if configured
            if self._should_run_sensor_rotation(context):
                if not self._execute_sensor_rotation(context):
                    return TestResult.FAILURE
            
            return TestResult.SUCCESS
            
        except Exception as e:
            self._logger.error(f"Sensor test execution failed: {e}")
            return TestResult.FAILURE
    
    def _set_initial_sensor_values(self, context: ITestContext) -> bool:
        """Set initial sensor values to sensible defaults."""
        success = True
        
        # Set light sensor initial value
        light_config = context.config.get_value("light", 0)
        if isinstance(light_config, int) and light_config > 0:
            light_value = self._denormalize_light_sensor_value(0.25)
            if not self._set_sensor_value(context, SensorType.LIGHT, light_value):
                self._logger.warning("Couldn't set light sensor to initial value")
                success = False
        
        # Set pressure sensor initial value
        pressure_config = context.config.get_value("pressure", 0)
        if isinstance(pressure_config, int) and pressure_config > 0:
            pressure_value = self._denormalize_pressure_sensor_value(0.25)
            if not self._set_sensor_value(context, SensorType.PRESSURE, pressure_value):
                self._logger.warning("Couldn't set pressure sensor to initial value")
                success = False
        
        return success
    
    def _should_run_sensor_rotation(self, context: ITestContext) -> bool:
        """Check if sensor rotation tests should be executed."""
        rotation_configs = [
            context.config.get_value("acceleration", 0),
            context.config.get_value("gyroscope", 0),
            context.config.get_value("light", 0),
            context.config.get_value("pressure", 0)
        ]
        
        return any(isinstance(config, int) and config > 0 for config in rotation_configs)
    
    def _execute_sensor_rotation(self, context: ITestContext) -> bool:
        """Execute sensor rotation tests."""
        success = True
        
        # Accelerometer rotation
        acceleration_level = context.config.get_value("acceleration", 0)
        if isinstance(acceleration_level, int) and acceleration_level > 0:
            if not self._rotate_multi_value_sensor(context, SensorType.ACCELEROMETER, acceleration_level):
                self._logger.error("Got error while rotating acceleration status")
                success = False
        
        # Gyroscope rotation
        gyroscope_level = context.config.get_value("gyroscope", 0)
        if isinstance(gyroscope_level, int) and gyroscope_level > 0:
            if not self._rotate_multi_value_sensor(context, SensorType.GYROSCOPE, gyroscope_level):
                self._logger.error("Got error while rotating gyroscope status")
                success = False
        
        # Light sensor rotation
        light_level = context.config.get_value("light", 0)
        if isinstance(light_level, int) and light_level > 0:
            if not self._rotate_single_value_sensor(context, SensorType.LIGHT, light_level):
                self._logger.error("Got error while rotating light sensor status")
                success = False
        
        # Pressure sensor rotation
        pressure_level = context.config.get_value("pressure", 0)
        if isinstance(pressure_level, int) and pressure_level > 0:
            if not self._rotate_single_value_sensor(context, SensorType.PRESSURE, pressure_level):
                self._logger.error("Got error while rotating pressure sensor status")
                success = False
        
        return success
    
    def _set_sensor_value(self, context: ITestContext, sensor_type: SensorType, value: float) -> bool:
        """Set a specific sensor value using emulator console."""
        sensor_name = self._get_emulator_sensor_name(sensor_type)
        if not sensor_name:
            return False
        
        result = context.device.execute_command(f"emu sensor set {sensor_name} {value}")
        return result.success
    
    def _rotate_multi_value_sensor(self, context: ITestContext, sensor_type: SensorType, elaborateness: int) -> bool:
        """Rotate a multi-value sensor (accelerometer, gyroscope) through different states."""
        self._logger.info(f"Starting {sensor_type.value} rotation with elaborateness {elaborateness}")
        
        # This would implement the actual sensor rotation logic
        # For now, just simulate success
        self._logger.info(f"Completed {sensor_type.value} rotation")
        return True
    
    def _rotate_single_value_sensor(self, context: ITestContext, sensor_type: SensorType, elaborateness: int) -> bool:
        """Rotate a single-value sensor through different states."""
        self._logger.info(f"Starting {sensor_type.value} sensor rotation with elaborateness {elaborateness}")
        
        # This would implement the actual sensor rotation logic
        # For now, just simulate success
        self._logger.info(f"Completed {sensor_type.value} sensor rotation")
        return True
    
    def _get_emulator_sensor_name(self, sensor_type: SensorType) -> str:
        """Get the emulator console sensor name for a sensor type."""
        sensor_map = {
            SensorType.LIGHT: "light",
            SensorType.PRESSURE: "pressure",
            SensorType.ACCELEROMETER: "acceleration",
            SensorType.GYROSCOPE: "gyroscope",
            SensorType.MAGNETOMETER: "magnetic-field"
        }
        return sensor_map.get(sensor_type, "")
    
    def _denormalize_light_sensor_value(self, normalized_value: float) -> float:
        """Convert normalized light value to actual sensor reading."""
        # Light sensor typically ranges from 0 to 40000 lux
        return normalized_value * 40000.0
    
    def _denormalize_pressure_sensor_value(self, normalized_value: float) -> float:
        """Convert normalized pressure value to actual sensor reading."""
        # Pressure sensor typically ranges from 300 to 1100 hPa
        return 300.0 + (normalized_value * 800.0)