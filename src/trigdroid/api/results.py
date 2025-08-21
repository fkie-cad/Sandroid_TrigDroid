"""Test result classes for TrigDroid API."""

from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, field

from ..core.enums import TestPhase, TestResult as TestResultEnum
from .config import TestConfiguration


@dataclass
class TestResult:
    """Result of a TrigDroid test execution.
    
    Contains all information about test execution including success status,
    timing information, configuration used, and any errors encountered.
    
    Examples:
        # Successful test
        result = TestResult(success=True, phase=TestPhase.EXECUTION)
        
        # Failed test
        result = TestResult(
            success=False,
            phase=TestPhase.SETUP,
            error="Device connection failed",
            config=config
        )
    """
    
    success: bool
    phase: TestPhase
    error: Optional[str] = None
    config: Optional[TestConfiguration] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Test execution details
    device_info: Dict[str, Any] = field(default_factory=dict)
    tests_run: List[str] = field(default_factory=list)
    tests_passed: List[str] = field(default_factory=list)
    tests_failed: List[str] = field(default_factory=list)
    tests_skipped: List[str] = field(default_factory=list)
    
    # Frida-specific results
    frida_hooks_loaded: int = 0
    frida_hooks_active: int = 0
    frida_errors: List[str] = field(default_factory=list)
    
    # Sensor test results
    sensor_tests_executed: Dict[str, bool] = field(default_factory=dict)
    sensor_values_changed: Dict[str, int] = field(default_factory=dict)
    
    # Network test results
    network_state_changes: Dict[str, bool] = field(default_factory=dict)
    
    # Application lifecycle results
    app_started: bool = False
    app_crashed: bool = False
    app_background_time: float = 0.0
    
    # Log files and outputs
    log_file_path: Optional[str] = None
    changelog_file_path: Optional[str] = None
    screenshot_paths: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate derived fields after initialization."""
        if self.end_time and self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def mark_completed(self, success: Optional[bool] = None) -> None:
        """Mark the test as completed.
        
        Args:
            success: Optional override for success status
        """
        self.end_time = datetime.now()
        if self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
        
        if success is not None:
            self.success = success
    
    def add_test_result(self, test_name: str, passed: bool, error: Optional[str] = None) -> None:
        """Add result for a specific test.
        
        Args:
            test_name: Name of the test
            passed: Whether the test passed
            error: Optional error message
        """
        self.tests_run.append(test_name)
        
        if passed:
            self.tests_passed.append(test_name)
        else:
            self.tests_failed.append(test_name)
            if error:
                if not self.error:
                    self.error = error
                else:
                    self.error += f"; {error}"
    
    def skip_test(self, test_name: str, reason: str) -> None:
        """Mark a test as skipped.
        
        Args:
            test_name: Name of the test
            reason: Reason for skipping
        """
        self.tests_skipped.append(test_name)
    
    @property
    def total_tests(self) -> int:
        """Total number of tests run."""
        return len(self.tests_run)
    
    @property
    def passed_tests(self) -> int:
        """Number of tests that passed."""
        return len(self.tests_passed)
    
    @property
    def failed_tests(self) -> int:
        """Number of tests that failed."""
        return len(self.tests_failed)
    
    @property
    def skipped_tests(self) -> int:
        """Number of tests that were skipped."""
        return len(self.tests_skipped)
    
    @property
    def success_rate(self) -> float:
        """Success rate as a percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    @property
    def result_enum(self) -> TestResultEnum:
        """Get the result as an enum value."""
        if self.success:
            return TestResultEnum.SUCCESS
        elif self.total_tests == 0:
            return TestResultEnum.SKIPPED
        else:
            return TestResultEnum.FAILURE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary.
        
        Returns:
            Dictionary representation of the result
        """
        return {
            'success': self.success,
            'phase': self.phase.value,
            'error': self.error,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'device_info': self.device_info,
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'skipped_tests': self.skipped_tests,
            'success_rate': self.success_rate,
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'tests_failed': self.tests_failed,
            'tests_skipped': self.tests_skipped,
            'frida_hooks_loaded': self.frida_hooks_loaded,
            'frida_hooks_active': self.frida_hooks_active,
            'frida_errors': self.frida_errors,
            'sensor_tests_executed': self.sensor_tests_executed,
            'sensor_values_changed': self.sensor_values_changed,
            'network_state_changes': self.network_state_changes,
            'app_started': self.app_started,
            'app_crashed': self.app_crashed,
            'app_background_time': self.app_background_time,
            'log_file_path': self.log_file_path,
            'changelog_file_path': self.changelog_file_path,
            'screenshot_paths': self.screenshot_paths,
        }
    
    def summary(self) -> str:
        """Get a human-readable summary of the results.
        
        Returns:
            Summary string
        """
        if self.success:
            status = "✓ PASSED"
        else:
            status = "✗ FAILED"
        
        duration_str = f"{self.duration_seconds:.1f}s" if self.duration_seconds else "unknown"
        
        summary_parts = [
            f"{status} in {duration_str}",
            f"Tests: {self.passed_tests} passed, {self.failed_tests} failed, {self.skipped_tests} skipped"
        ]
        
        if self.error:
            summary_parts.append(f"Error: {self.error}")
        
        if self.frida_hooks_active > 0:
            summary_parts.append(f"Frida: {self.frida_hooks_active} hooks active")
        
        if self.app_background_time > 0:
            summary_parts.append(f"Background time: {self.app_background_time:.1f}s")
        
        return " | ".join(summary_parts)