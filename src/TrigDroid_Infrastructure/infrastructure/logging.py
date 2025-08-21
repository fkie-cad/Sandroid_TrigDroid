"""Logging infrastructure following SOLID principles.

This module provides a clean logging abstraction that can be easily
extended and tested.
"""

import logging
import sys
from typing import Optional, Any
from enum import Enum

from ..interfaces import ILogger, LogLevel


class LogFormatter(logging.Formatter):
    """Custom formatter for TrigDroid logs."""
    
    def __init__(self, extended_format: bool = False):
        if extended_format:
            fmt = '[%(asctime)s] %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        else:
            fmt = '%(levelname)s - %(message)s'
        
        super().__init__(fmt, datefmt='%Y-%m-%d %H:%M:%S')


class StandardLogger(ILogger):
    """Standard logger implementation using Python's logging module."""
    
    def __init__(self, 
                 name: str = "TrigDroid",
                 level: LogLevel = LogLevel.INFO,
                 log_file: Optional[str] = None,
                 suppress_console: bool = False,
                 extended_format: bool = False):
        
        self._logger = logging.getLogger(name)
        self._logger.setLevel(self._convert_level(level))
        
        # Clear any existing handlers
        self._logger.handlers.clear()
        
        # Console handler
        if not suppress_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(LogFormatter(extended_format))
            self._logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(LogFormatter(True))  # Always use extended format for files
            self._logger.addHandler(file_handler)
    
    def debug(self, message: str, *args: Any) -> None:
        """Log debug message."""
        self._logger.debug(message, *args)
    
    def info(self, message: str, *args: Any) -> None:
        """Log info message."""
        self._logger.info(message, *args)
    
    def warning(self, message: str, *args: Any) -> None:
        """Log warning message."""
        self._logger.warning(message, *args)
    
    def error(self, message: str, *args: Any) -> None:
        """Log error message."""
        self._logger.error(message, *args)
    
    def critical(self, message: str, *args: Any) -> None:
        """Log critical message."""
        self._logger.critical(message, *args)
    
    def set_level(self, level: LogLevel) -> None:
        """Set the logging level."""
        self._logger.setLevel(self._convert_level(level))
    
    @staticmethod
    def _convert_level(level: LogLevel) -> int:
        """Convert LogLevel enum to logging module level."""
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }
        return level_map[level]


class FilteredLogger(ILogger):
    """Logger wrapper that applies include/exclude filters."""
    
    def __init__(self, 
                 base_logger: ILogger,
                 include_patterns: Optional[list[str]] = None,
                 exclude_patterns: Optional[list[str]] = None):
        
        self._base_logger = base_logger
        self._include_patterns = include_patterns or []
        self._exclude_patterns = exclude_patterns or []
    
    def debug(self, message: str, *args: Any) -> None:
        """Log debug message if it passes filters."""
        if self._should_log(message):
            self._base_logger.debug(message, *args)
    
    def info(self, message: str, *args: Any) -> None:
        """Log info message if it passes filters."""
        if self._should_log(message):
            self._base_logger.info(message, *args)
    
    def warning(self, message: str, *args: Any) -> None:
        """Log warning message if it passes filters."""
        if self._should_log(message):
            self._base_logger.warning(message, *args)
    
    def error(self, message: str, *args: Any) -> None:
        """Log error message if it passes filters."""
        if self._should_log(message):
            self._base_logger.error(message, *args)
    
    def critical(self, message: str, *args: Any) -> None:
        """Log critical message if it passes filters."""
        if self._should_log(message):
            self._base_logger.critical(message, *args)
    
    def _should_log(self, message: str) -> bool:
        """Check if message should be logged based on filters."""
        # If exclude patterns match, don't log
        for pattern in self._exclude_patterns:
            if pattern in message:
                return False
        
        # If include patterns are specified, message must match at least one
        if self._include_patterns:
            return any(pattern in message for pattern in self._include_patterns)
        
        # If no include patterns, log by default (unless excluded)
        return True


class NullLogger(ILogger):
    """Null object pattern logger for testing."""
    
    def debug(self, message: str, *args: Any) -> None:
        """No-op debug."""
        pass
    
    def info(self, message: str, *args: Any) -> None:
        """No-op info."""
        pass
    
    def warning(self, message: str, *args: Any) -> None:
        """No-op warning."""
        pass
    
    def error(self, message: str, *args: Any) -> None:
        """No-op error."""
        pass
    
    def critical(self, message: str, *args: Any) -> None:
        """No-op critical."""
        pass


class LoggerFactory:
    """Factory for creating different types of loggers."""
    
    @staticmethod
    def create_standard_logger(
        name: str = "TrigDroid",
        level: LogLevel = LogLevel.INFO,
        log_file: Optional[str] = None,
        suppress_console: bool = False,
        extended_format: bool = False
    ) -> ILogger:
        """Create a standard logger."""
        return StandardLogger(name, level, log_file, suppress_console, extended_format)
    
    @staticmethod
    def create_filtered_logger(
        base_logger: ILogger,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None
    ) -> ILogger:
        """Create a filtered logger."""
        return FilteredLogger(base_logger, include_patterns, exclude_patterns)
    
    @staticmethod
    def create_null_logger() -> ILogger:
        """Create a null logger for testing."""
        return NullLogger()
    
    @staticmethod
    def create_composite_logger(
        name: str = "TrigDroid",
        level: LogLevel = LogLevel.INFO,
        log_file: Optional[str] = None,
        suppress_console: bool = False,
        extended_format: bool = False,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None
    ) -> ILogger:
        """Create a logger with all features."""
        base_logger = StandardLogger(name, level, log_file, suppress_console, extended_format)
        
        if include_patterns or exclude_patterns:
            return FilteredLogger(base_logger, include_patterns, exclude_patterns)
        
        return base_logger