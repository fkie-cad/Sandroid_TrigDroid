"""Configuration classes for TrigDroid API."""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import yaml

from ..core.enums import LogLevel
from ..exceptions import ConfigurationError


@dataclass
class TestConfiguration:
    """Test configuration for TrigDroid API.
    
    This class provides a clean, type-safe interface for configuring TrigDroid tests
    programmatically. All parameters have sensible defaults for quick setup.
    
    Examples:
        # Minimal configuration
        config = TestConfiguration(package='com.example.app')
        
        # Full configuration
        config = TestConfiguration(
            package='com.example.app',
            device_id='emulator-5554',
            acceleration=5,
            gyroscope=3,
            battery_rotation=4,
            min_runtime=5,
            log_level=LogLevel.DEBUG,
            frida_hooks=True,
            install_dummy_apps=['com.dummy.app1', 'com.dummy.app2']
        )
        
        # Load from file
        config = TestConfiguration.from_yaml_file('config.yaml')
        
        # Convert to dictionary
        config_dict = config.to_dict()
    """
    
    # Required parameters
    package: str = ""
    
    # Device configuration
    device_id: Optional[str] = None
    
    # Test duration
    min_runtime: int = 1  # minutes
    background_time: int = 0  # seconds
    
    # Sensor configuration
    acceleration: int = 0  # 0-10 elaborateness level
    gyroscope: int = 0  # 0-10 elaborateness level
    light: int = 0  # 0-10 elaborateness level
    pressure: int = 0  # 0-10 elaborateness level
    
    # Battery configuration
    battery_rotation: int = 0  # 0-4 elaborateness level
    
    # Network configuration
    wifi: Optional[bool] = None
    data: Optional[bool] = None
    bluetooth: Optional[bool] = None
    bluetooth_mac: Optional[str] = None
    
    # Application management
    install_dummy_apps: List[str] = field(default_factory=list)
    uninstall_apps: List[str] = field(default_factory=list)
    grant_permissions: List[str] = field(default_factory=list)
    revoke_permissions: List[str] = field(default_factory=list)
    
    # Frida configuration
    frida_hooks: bool = False
    frida_constants: Optional[str] = None
    adb_enabled: Optional[bool] = None
    uptime_offset: int = 0  # minutes to add to uptime
    
    # Geolocation and language
    geolocation: Optional[str] = None
    language: Optional[str] = None
    
    # System properties
    baseband: Optional[str] = None
    build_properties: Dict[str, str] = field(default_factory=dict)
    
    # Logging configuration
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[str] = None
    suppress_console_logs: bool = False
    extended_log_format: bool = False
    log_filter_include: List[str] = field(default_factory=list)
    log_filter_exclude: List[str] = field(default_factory=list)
    
    # Changelog configuration
    disable_changelog: bool = False
    changelog_file: str = "changelog.txt"
    
    # Advanced options
    interaction: bool = False  # Enable UI interaction simulation
    no_unroot: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Validate configuration values."""
        errors = []
        
        # Package name validation
        if not self.package:
            errors.append("Package name is required")
        elif self.package != "no_package":
            # Basic package name validation
            if not self.package.replace('.', '').replace('_', '').isalnum():
                errors.append(f"Invalid package name format: {self.package}")
        
        # Range validations
        if not (0 <= self.min_runtime <= 1440):  # Max 24 hours
            errors.append("min_runtime must be between 0 and 1440 minutes")
            
        if not (0 <= self.background_time <= 300):  # Max 5 minutes
            errors.append("background_time must be between 0 and 300 seconds")
            
        # Sensor level validations
        for sensor in ['acceleration', 'gyroscope', 'light', 'pressure']:
            value = getattr(self, sensor)
            if not (0 <= value <= 10):
                errors.append(f"{sensor} must be between 0 and 10")
        
        # Battery rotation validation
        if not (0 <= self.battery_rotation <= 4):
            errors.append("battery_rotation must be between 0 and 4")
        
        # File path validations
        if self.log_file and not Path(self.log_file).parent.exists():
            errors.append(f"Log file directory does not exist: {Path(self.log_file).parent}")
            
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def is_valid(self) -> bool:
        """Check if configuration is valid.
        
        Returns:
            True if valid, False otherwise
        """
        try:
            self._validate()
            return True
        except ConfigurationError:
            return False
    
    @property
    def validation_errors(self) -> List[str]:
        """Get list of validation errors.
        
        Returns:
            List of validation error messages
        """
        try:
            self._validate()
            return []
        except ConfigurationError as e:
            return str(e).split(': ', 1)[1].split('; ')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        result = {}
        for field_name, field_def in self.__dataclass_fields__.items():
            value = getattr(self, field_name)
            
            # Convert enums to their values
            if hasattr(value, 'value'):
                value = value.value
            
            # Skip default values for cleaner output
            if value != field_def.default and value != field_def.default_factory():
                result[field_name] = value
        
        return result
    
    def to_yaml(self, file_path: Optional[str] = None) -> str:
        """Convert configuration to YAML format.
        
        Args:
            file_path: Optional path to save YAML file
            
        Returns:
            YAML string representation
        """
        yaml_str = yaml.safe_dump(self.to_dict(), default_flow_style=False, sort_keys=True)
        
        if file_path:
            Path(file_path).write_text(yaml_str)
            
        return yaml_str
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestConfiguration':
        """Create configuration from dictionary.
        
        Args:
            data: Dictionary containing configuration values
            
        Returns:
            TestConfiguration instance
        """
        # Convert string log levels to enum
        if 'log_level' in data and isinstance(data['log_level'], str):
            data['log_level'] = LogLevel(data['log_level'])
        
        # Handle missing fields with defaults
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    @classmethod
    def from_yaml_file(cls, file_path: str) -> 'TestConfiguration':
        """Load configuration from YAML file.
        
        Args:
            file_path: Path to YAML configuration file
            
        Returns:
            TestConfiguration instance
            
        Raises:
            ConfigurationError: If file cannot be loaded or parsed
        """
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise ConfigurationError(f"Configuration file not found: {file_path}")
                
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if not isinstance(data, dict):
                raise ConfigurationError(f"Invalid YAML format in {file_path}")
                
            return cls.from_dict(data)
            
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML file {file_path}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration from {file_path}: {e}")
    
    @classmethod
    def from_command_line(cls, args: List[str]) -> 'TestConfiguration':
        """Create configuration from command line arguments.
        
        Args:
            args: List of command line arguments
            
        Returns:
            TestConfiguration instance
        """
        # This would integrate with the existing command line parser
        # For now, return a basic configuration
        # TODO: Implement full command line parsing
        return cls(package=args[0] if args else "")
    
    def merge_with(self, other: 'TestConfiguration') -> 'TestConfiguration':
        """Merge this configuration with another, with other taking precedence.
        
        Args:
            other: Configuration to merge with
            
        Returns:
            New TestConfiguration instance with merged values
        """
        merged_data = self.to_dict()
        other_data = other.to_dict()
        merged_data.update(other_data)
        return self.from_dict(merged_data)
    
    def copy(self) -> 'TestConfiguration':
        """Create a copy of this configuration.
        
        Returns:
            New TestConfiguration instance
        """
        return self.from_dict(self.to_dict())