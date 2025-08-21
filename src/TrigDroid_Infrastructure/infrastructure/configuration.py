"""Configuration system refactored to follow SOLID principles.

This module provides a clean separation between configuration sources,
validation, and consumption following the Single Responsibility Principle.
"""

import argparse
import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import yaml

from ..interfaces import IConfigurationProvider, IConfigurationValidator, ILogger, ConfigValue
from ..infrastructure.dependency_injection import Injectable


class ConfigurationError(Exception):
    """Configuration-related errors."""
    pass


class CommandLineConfigProvider(IConfigurationProvider):
    """Configuration provider for command line arguments."""
    
    def __init__(self, parser: Optional[argparse.ArgumentParser] = None):
        self._parser = parser or self._create_default_parser()
        self._config: Dict[str, ConfigValue] = {}
        self._loaded = False
    
    def get_value(self, key: str) -> ConfigValue:
        """Get configuration value by key."""
        if not self._loaded:
            self._load_configuration()
        return self._config.get(key)
    
    def set_value(self, key: str, value: ConfigValue) -> None:
        """Set configuration value."""
        self._config[key] = value
    
    def has_key(self, key: str) -> bool:
        """Check if configuration key exists."""
        if not self._loaded:
            self._load_configuration()
        return key in self._config
    
    def validate(self) -> bool:
        """Validate the configuration."""
        # Command line validation is handled by argparse
        return True
    
    def _load_configuration(self) -> None:
        """Load configuration from command line arguments."""
        try:
            args = self._parser.parse_args()
            self._config = vars(args)
            self._loaded = True
        except SystemExit:
            raise ConfigurationError("Invalid command line arguments")
    
    def _create_default_parser(self) -> argparse.ArgumentParser:
        """Create a default argument parser."""
        parser = argparse.ArgumentParser(
            prog='TrigDroid',
            description='Android Sandbox Payload Trigger Framework'
        )
        
        # Add basic arguments - this would be expanded with full option set
        parser.add_argument('-p', '--package', required=True, help='Package name to test')
        parser.add_argument('-d', '--device', help='Device to use')
        parser.add_argument('-c', '--config', help='Configuration file path')
        parser.add_argument('--log-level', default='INFO', help='Logging level')
        
        return parser


class YamlConfigProvider(IConfigurationProvider):
    """Configuration provider for YAML files."""
    
    def __init__(self, config_path: Optional[str] = None):
        self._config_path = config_path
        self._config: Dict[str, ConfigValue] = {}
        self._loaded = False
    
    def get_value(self, key: str) -> ConfigValue:
        """Get configuration value by key."""
        if not self._loaded:
            self._load_configuration()
        return self._config.get(key)
    
    def set_value(self, key: str, value: ConfigValue) -> None:
        """Set configuration value."""
        self._config[key] = value
    
    def has_key(self, key: str) -> bool:
        """Check if configuration key exists."""
        if not self._loaded:
            self._load_configuration()
        return key in self._config
    
    def validate(self) -> bool:
        """Validate the YAML structure."""
        try:
            if self._config_path and Path(self._config_path).exists():
                self._load_configuration()
                return True
            return True  # No file is valid
        except Exception:
            return False
    
    def set_config_path(self, path: str) -> None:
        """Set the configuration file path."""
        self._config_path = path
        self._loaded = False
    
    def _load_configuration(self) -> None:
        """Load configuration from YAML file."""
        if not self._config_path or not Path(self._config_path).exists():
            self._loaded = True
            return
        
        try:
            with open(self._config_path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file) or {}
            self._loaded = True
        except Exception as e:
            raise ConfigurationError(f"Failed to load YAML config: {e}")


class CompositeConfigurationProvider(IConfigurationProvider):
    """Configuration provider that merges multiple sources."""
    
    def __init__(self, providers: List[IConfigurationProvider]):
        self._providers = providers
    
    def get_value(self, key: str) -> ConfigValue:
        """Get configuration value, checking providers in order."""
        for provider in self._providers:
            if provider.has_key(key):
                value = provider.get_value(key)
                if value is not None:
                    return value
        return None
    
    def set_value(self, key: str, value: ConfigValue) -> None:
        """Set value in the first provider."""
        if self._providers:
            self._providers[0].set_value(key, value)
    
    def has_key(self, key: str) -> bool:
        """Check if any provider has the key."""
        return any(provider.has_key(key) for provider in self._providers)
    
    def validate(self) -> bool:
        """Validate all providers."""
        return all(provider.validate() for provider in self._providers)


class ConfigurationValidator(IConfigurationValidator, Injectable):
    """Validates configuration values according to rules."""
    
    def __init__(self, logger: ILogger):
        super().__init__()
        self._logger = logger
        self._validation_rules: Dict[str, Dict[str, Any]] = {
            'package': {
                'type': str,
                'regex': r'^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)*$|^no_package$',
                'required': True
            },
            'device': {
                'type': str,
                'regex': r'^[\w\-:.]+$'
            },
            'log_level': {
                'type': str,
                'choices': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            },
            'min_runtime': {
                'type': int,
                'min': 0,
                'max': 1440  # 24 hours
            },
            'background_time': {
                'type': int,
                'min': 0,
                'max': 300  # 5 minutes
            },
            'battery': {
                'type': int,
                'min': 0,
                'max': 4
            },
            'acceleration': {
                'type': int,
                'min': 0,
                'max': 10
            },
            'gyroscope': {
                'type': int,
                'min': 0,
                'max': 10
            },
            'light': {
                'type': int,
                'min': 0,
                'max': 10
            },
            'pressure': {
                'type': int,
                'min': 0,
                'max': 10
            }
        }
    
    def validate_config(self, config: Dict[str, ConfigValue]) -> List[str]:
        """Validate entire configuration and return list of errors."""
        errors = []
        
        for key, value in config.items():
            if key in self._validation_rules:
                error = self._validate_single_value(key, value)
                if error:
                    errors.append(error)
        
        # Check required fields
        for key, rules in self._validation_rules.items():
            if rules.get('required', False) and key not in config:
                errors.append(f"Required field '{key}' is missing")
        
        return errors
    
    def is_valid(self, key: str, value: ConfigValue) -> bool:
        """Check if a single value is valid."""
        return self._validate_single_value(key, value) is None
    
    def _validate_single_value(self, key: str, value: ConfigValue) -> Optional[str]:
        """Validate a single configuration value."""
        if key not in self._validation_rules:
            return None  # Unknown keys are allowed
        
        rules = self._validation_rules[key]
        
        # Type checking
        expected_type = rules.get('type')
        if expected_type and value is not None:
            if not isinstance(value, expected_type):
                return f"'{key}' must be of type {expected_type.__name__}, got {type(value).__name__}"
        
        # Choice validation
        choices = rules.get('choices')
        if choices and value not in choices:
            return f"'{key}' must be one of {choices}, got '{value}'"
        
        # Regex validation
        regex = rules.get('regex')
        if regex and isinstance(value, str):
            if not re.match(regex, value):
                return f"'{key}' does not match required pattern"
        
        # Range validation for numbers
        if isinstance(value, (int, float)):
            min_val = rules.get('min')
            max_val = rules.get('max')
            
            if min_val is not None and value < min_val:
                return f"'{key}' must be >= {min_val}, got {value}"
            
            if max_val is not None and value > max_val:
                return f"'{key}' must be <= {max_val}, got {value}"
        
        return None


class ConfigurationManager(Injectable):
    """High-level configuration manager that coordinates providers and validation."""
    
    def __init__(self, 
                 config_provider: IConfigurationProvider,
                 validator: IConfigurationValidator,
                 logger: ILogger):
        super().__init__()
        self._config_provider = config_provider
        self._validator = validator
        self._logger = logger
        self._validated = False
    
    def get_value(self, key: str, default: ConfigValue = None) -> ConfigValue:
        """Get a configuration value with optional default."""
        value = self._config_provider.get_value(key)
        return value if value is not None else default
    
    def get_required_value(self, key: str) -> ConfigValue:
        """Get a required configuration value, raising error if missing."""
        value = self._config_provider.get_value(key)
        if value is None:
            raise ConfigurationError(f"Required configuration '{key}' is missing")
        return value
    
    def validate_configuration(self) -> bool:
        """Validate the entire configuration."""
        if self._validated:
            return True
        
        # Get all configuration values
        config_dict = self._get_all_config_values()
        
        # Validate
        errors = self._validator.validate_config(config_dict)
        
        if errors:
            for error in errors:
                self._logger.error(f"Configuration error: {error}")
            return False
        
        self._validated = True
        return True
    
    def _get_all_config_values(self) -> Dict[str, ConfigValue]:
        """Get all configuration values from the provider."""
        # This is a simplified version - would need to be implemented based on provider capabilities
        return {}


class ConfigurationBuilder:
    """Builder pattern for creating configuration managers."""
    
    def __init__(self):
        self._providers: List[IConfigurationProvider] = []
        self._validator: Optional[IConfigurationValidator] = None
        self._logger: Optional[ILogger] = None
    
    def add_command_line_provider(self, parser: Optional[argparse.ArgumentParser] = None) -> 'ConfigurationBuilder':
        """Add command line configuration provider."""
        self._providers.append(CommandLineConfigProvider(parser))
        return self
    
    def add_yaml_provider(self, config_path: Optional[str] = None) -> 'ConfigurationBuilder':
        """Add YAML configuration provider."""
        self._providers.append(YamlConfigProvider(config_path))
        return self
    
    def set_validator(self, validator: IConfigurationValidator) -> 'ConfigurationBuilder':
        """Set the configuration validator."""
        self._validator = validator
        return self
    
    def set_logger(self, logger: ILogger) -> 'ConfigurationBuilder':
        """Set the logger."""
        self._logger = logger
        return self
    
    def build(self) -> ConfigurationManager:
        """Build the configuration manager."""
        if not self._providers:
            raise ConfigurationError("At least one configuration provider is required")
        
        if not self._validator:
            raise ConfigurationError("Configuration validator is required")
        
        if not self._logger:
            raise ConfigurationError("Logger is required")
        
        composite_provider = CompositeConfigurationProvider(self._providers)
        return ConfigurationManager(composite_provider, self._validator, self._logger)