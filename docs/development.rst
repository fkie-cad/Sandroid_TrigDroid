===========
Development
===========

This section provides comprehensive information for developers who want to contribute to or extend TrigDroid.

.. note::
   TrigDroid follows **SOLID principles** and modern software engineering practices. 
   All contributions must maintain the defensive security focus and high code quality standards.

Development Environment Setup
=============================

Prerequisites
-------------

Before setting up the development environment, ensure you have:

* **Python 3.9+** with pip and virtual environment support
* **Node.js 16+** and npm for TypeScript hooks
* **Git** for version control
* **Android SDK** with ADB for testing
* **IDE/Editor** with Python and TypeScript support (recommended: VS Code)

Initial Setup
-------------

1. **Clone the Repository**

.. code-block:: bash

   git clone <repository-url>
   cd Sandroid_TrigDroid

2. **Create Python Virtual Environment**

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install Development Dependencies**

.. code-block:: bash

   # Install in development mode with all features
   pip install -e ".[full,dev]"

4. **Set up TypeScript Hooks Development**

.. code-block:: bash

   cd frida-hooks
   npm install
   npm run build
   cd ..

5. **Verify Installation**

.. code-block:: bash

   # Run tests to verify setup
   pytest
   
   # Check code quality
   black src/ && isort src/ && mypy src/ && ruff check src/

Development Workflow
====================

Code Quality Standards
----------------------

TrigDroid maintains high code quality standards:

**Format and Style**

.. code-block:: bash

   # Format code
   black src/ tests/
   isort src/ tests/

**Type Checking**

.. code-block:: bash

   # Type checking
   mypy src/

**Linting**

.. code-block:: bash

   # Linting
   ruff check src/ tests/
   pylint src/trigdroid/

**All Quality Checks**

.. code-block:: bash

   # Run all quality checks
   black src/ && isort src/ && mypy src/ && ruff check src/

Testing Framework
-----------------

TrigDroid uses a comprehensive testing approach:

**Run All Tests**

.. code-block:: bash

   pytest

**Coverage Reports**

.. code-block:: bash

   # Run with coverage (target: 90%+ for critical paths)
   pytest --cov=src/trigdroid --cov=src/TrigDroid_Infrastructure --cov-report=html

**Test Categories**

.. code-block:: bash

   # Unit tests only (fast)
   pytest -m unit

   # Integration tests
   pytest -m integration

   # Skip slow tests
   pytest -m "not slow"

   # Device-dependent tests
   pytest -m requires_device

   # Frida-dependent tests
   pytest -m requires_frida

**Development Testing**

.. code-block:: bash

   # Stop on first failure
   pytest -x

   # Verbose output with local variables
   pytest -v -l

Architecture Guidelines
=======================

SOLID Principles Implementation
-------------------------------

**Single Responsibility Principle**
   Each class and function should have one reason to change

**Open/Closed Principle**
   Open for extension, closed for modification

**Liskov Substitution Principle**
   Derived classes must be substitutable for base classes

**Interface Segregation Principle**
   Many specific interfaces over general-purpose ones

**Dependency Inversion Principle**
   Depend on abstractions, not concretions

Layer Architecture
------------------

**Layer 1: Public API** (``src/trigdroid/``)

* **CLI Interface**: Rich command-line interface using Click
* **Python API**: TrigDroidAPI class for programmatic usage
* **Configuration**: Type-safe TestConfiguration with Pydantic
* **Results**: Comprehensive TestResult classes
* **Device Management**: AndroidDevice and DeviceManager wrappers

**Layer 2: Infrastructure** (``src/TrigDroid_Infrastructure/``)

* **Interfaces**: Protocol-based abstractions for extensibility
* **Dependency Injection**: Service container for loose coupling
* **Test Runners**: Pluggable execution engines
* **Application Orchestrator**: Main workflow coordination

**Layer 3: TypeScript Hooks** (``frida-hooks/``)

* **Modern TypeScript**: Type-safe Frida hook implementations
* **Modular Design**: Individual hook files for different components
* **Build Integration**: Automatic compilation and packaging

Adding New Features
===================

Creating New Test Runners
-------------------------

1. **Define the Interface**

.. code-block:: python

   # src/TrigDroid_Infrastructure/interfaces/__init__.py
   from typing import Protocol
   
   class ICustomTestRunner(Protocol):
       def can_run(self, test_type: str) -> bool: ...
       def execute(self, context: TestContext) -> TestResult: ...

2. **Implement the Test Runner**

.. code-block:: python

   # src/TrigDroid_Infrastructure/test_runners/custom_test_runner.py
   from ..interfaces import ITestRunner, TestRunnerBase, TestResult
   
   class CustomTestRunner(TestRunnerBase):
       def __init__(self, logger: ILogger):
           super().__init__(logger)
   
       def can_run(self, test_type: str) -> bool:
           return test_type == "custom"
       
       def _execute_internal(self, context: TestContext) -> TestResult:
           # Implementation here
           self.logger.info("Running custom test")
           return TestResult.SUCCESS

3. **Register in Dependency Container**

.. code-block:: python

   # src/TrigDroid_Infrastructure/infrastructure/dependency_injection.py
   container.register_transient(ITestRunner, CustomTestRunner, "custom")

Adding TypeScript Frida Hooks
-----------------------------

1. **Create Hook Module**

.. code-block:: typescript

   // frida-hooks/hooks/custom-hook.ts
   import { HookManager } from '../utils';
   
   export class CustomHook extends HookManager {
       public hookCustomAPI(): void {
           const SomeClass = Java.use("android.some.Class");
           SomeClass.someMethod.implementation = function(...args) {
               console.log("[TrigDroid] Custom hook triggered");
               this.logHookCall("SomeClass.someMethod", args);
               return this.someMethod.apply(this, args);
           };
       }
   }

2. **Register in Main Entry Point**

.. code-block:: typescript

   // frida-hooks/main.ts
   import { CustomHook } from './hooks/custom-hook';
   
   // Initialize and activate hooks
   const customHook = new CustomHook();
   customHook.hookCustomAPI();

3. **Build and Test**

.. code-block:: bash

   cd frida-hooks
   npm run build
   npm run test  # If tests are available

Extending Configuration
-----------------------

1. **Update Configuration Model**

.. code-block:: python

   # src/trigdroid/api/config.py
   from pydantic import BaseModel, Field
   
   class TestConfiguration(BaseModel):
       # Existing fields...
       custom_option: bool = Field(default=False, description="Enable custom testing")
       custom_parameters: Dict[str, Any] = Field(default_factory=dict)
   
       def is_valid(self) -> bool:
           # Add validation logic
           return super().is_valid() and self._validate_custom_options()

2. **Update CLI Interface**

.. code-block:: python

   # src/trigdroid/cli/main.py
   @click.option('--custom-option', is_flag=True, help='Enable custom testing')
   def main(custom_option: bool, ...):
       config = TestConfiguration(
           custom_option=custom_option,
           # ... other options
       )

Testing Guidelines
==================

Writing Unit Tests
------------------

**Test Structure**

.. code-block:: python

   # tests/unit/test_custom_runner.py
   import pytest
   from unittest.mock import Mock, patch
   from TrigDroid_Infrastructure.test_runners.custom_test_runner import CustomTestRunner
   from TrigDroid_Infrastructure.interfaces import ILogger, TestContext

   class TestCustomTestRunner:
       @pytest.fixture
       def mock_logger(self):
           return Mock(spec=ILogger)
       
       @pytest.fixture
       def runner(self, mock_logger):
           return CustomTestRunner(mock_logger)
       
       def test_can_run_returns_true_for_custom_type(self, runner):
           # Test specific functionality
           assert runner.can_run("custom") is True
           assert runner.can_run("other") is False
       
       def test_execute_calls_logger(self, runner, mock_logger):
           context = Mock(spec=TestContext)
           result = runner.execute(context)
           
           mock_logger.info.assert_called()
           assert result == TestResult.SUCCESS

**Test Categories and Markers**

.. code-block:: python

   import pytest
   
   @pytest.mark.unit
   def test_fast_unit_test():
       """Fast unit test with mocked dependencies."""
       pass
   
   @pytest.mark.integration  
   def test_component_integration():
       """Integration test with real components."""
       pass
   
   @pytest.mark.requires_device
   def test_device_functionality():
       """Test requiring Android device/emulator."""
       pass
   
   @pytest.mark.slow
   def test_long_running_operation():
       """Test that takes significant time.""" 
       pass

Writing Integration Tests
-------------------------

.. code-block:: python

   # tests/integration/test_full_workflow.py
   import pytest
   from trigdroid import TrigDroidAPI, TestConfiguration

   @pytest.mark.integration
   @pytest.mark.requires_device
   def test_full_workflow_success(test_device):
       """Test complete workflow with real device."""
       config = TestConfiguration(
           package="com.android.settings",  # System app
           timeout=60,
           sensors=["accelerometer"]
       )
       
       with TrigDroidAPI(config) as api:
           result = api.run_tests()
       
       assert result.success
       assert result.total_tests > 0
       assert result.phase == "completed"

Building and Packaging
======================

Building TypeScript Hooks
-------------------------

.. code-block:: bash

   cd frida-hooks
   
   # Development build with watching
   npm run watch
   
   # Production build
   npm run build
   
   # Clean and rebuild
   npm run clean && npm run build

Building Python Package
-----------------------

The build system automatically builds TypeScript hooks via ``hatch_build.py``:

.. code-block:: bash

   # Build package (auto-builds TypeScript hooks)
   python -m build
   
   # Clean build artifacts
   rm -rf dist/ build/ *.egg-info/
   cd frida-hooks && rm -rf dist/

Development Scripts
==================

Useful development commands and scripts:

**Complete Development Setup**

.. code-block:: bash

   #!/bin/bash
   # setup-dev.sh
   
   echo "Setting up TrigDroid development environment..."
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -e ".[full,dev]"
   
   # Setup TypeScript hooks
   cd frida-hooks
   npm install
   npm run build
   cd ..
   
   # Run initial tests
   pytest -m "unit and not slow"
   
   echo "Development environment ready!"

**Quality Check Script**

.. code-block:: bash

   #!/bin/bash
   # check-quality.sh
   
   echo "Running code quality checks..."
   
   # Format code
   black src/ tests/
   isort src/ tests/
   
   # Type checking
   mypy src/
   
   # Linting
   ruff check src/ tests/
   
   # Run tests
   pytest -m unit
   
   echo "Quality checks completed!"

Contributing Guidelines
=======================

Code Modification Protocol
--------------------------

**Before Making Changes:**

1. Analyze existing code structure and patterns
2. Understand the current architecture
3. Consider backward compatibility
4. Identify potential side effects

**When Adding Features:**

1. Follow existing patterns and conventions
2. Integrate smoothly with current architecture
3. Add comprehensive tests
4. Update documentation

**Security Requirements:**

1. Maintain defensive security focus
2. No malicious functionality enhancement
3. Validate all inputs
4. Follow security best practices

Pull Request Process
-------------------

1. **Create Feature Branch**

.. code-block:: bash

   git checkout -b feature/new-test-runner

2. **Make Changes**
   
   * Follow coding standards
   * Add tests for new functionality
   * Update documentation

3. **Run Quality Checks**

.. code-block:: bash

   # Run all quality checks
   ./check-quality.sh

4. **Commit Changes**

.. code-block:: bash

   git add .
   git commit -m "feat: add custom test runner for X functionality"

5. **Create Pull Request**
   
   * Provide clear description
   * Link related issues
   * Include test results

Documentation Updates
--------------------

When adding new features, always update:

* **API Documentation**: Docstrings and type hints
* **User Guide**: If user-facing functionality changes
* **Developer Guide**: For architecture or development process changes

For more information on the codebase structure and patterns, see the :doc:`api/index` documentation.