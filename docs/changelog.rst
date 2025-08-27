=========
Changelog
=========

This page documents the version history and changes made to TrigDroid.

Version 1.0.0 (Current)
========================

**New Features:**

* Modern dual-layer architecture with SOLID principles
* TypeScript Frida hooks with type safety
* Comprehensive CLI interface using Click
* Python API for programmatic usage
* Type-safe configuration with Pydantic
* Device management with AndroidDevice and DeviceManager
* Pluggable test runners architecture
* Dependency injection container with ServiceLocator
* Extensive sensor manipulation capabilities
* Network state control (WiFi, data, Bluetooth)
* Frida runtime instrumentation support
* Device property manipulation
* Automated UI interaction testing
* Comprehensive logging and changelog system

**Architecture Improvements:**

* **Layer 1: Public API** (``src/trigdroid/``)

  - CLI Interface with rich device management
  - Python API with TrigDroidAPI class
  - Type-safe TestConfiguration
  - Comprehensive TestResult classes
  - AndroidDevice and DeviceManager wrappers

* **Layer 2: Infrastructure** (``src/TrigDroid_Infrastructure/``)

  - Protocol-based abstractions (ILogger, ITestRunner, IAndroidDevice)
  - DI container with ServiceLocator
  - Pluggable test execution (SensorTestRunner, FridaTestRunner)
  - Application orchestrator for workflow coordination

* **TypeScript Frida Hooks** (``frida-hooks/``)

  - Modern TypeScript implementation
  - Modular design with individual hook files
  - Type safety with ``@types/frida-gum``
  - NPM build integration

**Security Focus:**

* Designed specifically for defensive security research
* Malware analysis capabilities
* Authorized testing workflows
* Isolated environment recommendations

**Testing & Quality:**

* Comprehensive test suite with pytest
* Unit tests with mocked dependencies
* Integration tests for component interaction
* Device tests requiring Android device/emulator
* Frida tests for instrumentation features
* Test coverage reporting
* Code quality tools (black, isort, mypy, ruff, pylint)

**Documentation:**

* Complete Sphinx documentation with Read the Docs theme
* API reference documentation
* User guides and tutorials
* Development guidelines
* Installation instructions
* Troubleshooting guides

**Development Tools:**

* Development environment setup with pip install -e ".[full,dev]"
* Code formatting with black and isort
* Type checking with mypy
* Linting with ruff and pylint
* Automated testing with pytest
* Build system with hatch

Legacy Versions
===============

Previous versions of TrigDroid used different architectures and implementation approaches. The 1.0.0 release represents a complete modernization of the framework with improved maintainability, testability, and extensibility.

**Key Changes from Legacy:**

* Migration from monolithic to modular architecture
* Introduction of dependency injection and service locator patterns
* Type safety improvements with Pydantic and TypeScript
* Modern Python packaging with pyproject.toml
* Comprehensive testing infrastructure
* Professional documentation system

Migration Guide
===============

If you're migrating from a legacy version of TrigDroid, please note the following breaking changes:

**Command Line Interface:**

* New CLI structure using Click framework
* Updated command arguments and options
* New device management commands

**Python API:**

* New TrigDroidAPI class replaces legacy interfaces
* TestConfiguration replaces old configuration methods
* Updated result handling with TestResult classes

**Configuration:**

* YAML configuration support
* Type-safe configuration validation
* New configuration file format

**Testing:**

* New test runner architecture
* Updated Frida hook implementation
* Improved error handling and logging

For detailed migration instructions, please refer to the development guide or contact the development team.