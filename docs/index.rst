==========================================
TrigDroid Documentation
==========================================

.. image:: https://img.shields.io/badge/python-3.9%2B-blue
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/platform-android-green
   :target: https://developer.android.com/
   :alt: Android Platform

.. image:: https://img.shields.io/badge/license-MIT-blue
   :target: ../LICENSE
   :alt: License

**TrigDroid** is an Android security testing framework designed for **defensive security research** and malware analysis. It triggers potentially malicious behaviors in Android applications through environmental manipulation including sensor simulation, network state changes, and Frida runtime instrumentation.

.. warning::
   **IMPORTANT**: This is a defensive security tool. Only assist with security analysis, vulnerability detection, and defensive capabilities. Do not enhance or create malicious functionality.

Quick Start
===========

.. code-block:: bash

   # Install TrigDroid
   pip install -e ".[full,dev]"
   
   # Basic usage
   trigdroid -p com.example.app
   
   # Advanced sensor testing
   trigdroid -p com.suspicious.app --acceleration 8 --battery 3 --frida

Features
========

* **Environmental Manipulation**: Simulate various device conditions
* **Sensor Simulation**: Control accelerometer, gyroscope, and other sensors
* **Network State Management**: Manipulate WiFi, data, and Bluetooth states
* **Frida Runtime Instrumentation**: Hook into Android APIs at runtime
* **Device Property Manipulation**: Modify system properties and constants
* **Application Interaction**: Automated UI interaction testing
* **Comprehensive Logging**: Detailed test execution logging and changelog

Documentation Contents
=======================

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   installation
   background
   logging

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide:

   development
   api/index

.. toctree::
   :maxdepth: 2
   :caption: Reference:

   changelog
   troubleshooting
   glossary

Architecture Overview
====================

TrigDroid follows a **modern dual-layer architecture** with SOLID principles:

**Layer 1: Public API** (``src/trigdroid/``)
  * **CLI Interface**: Rich CLI using Click with device management
  * **Python API**: TrigDroidAPI class for programmatic usage  
  * **Configuration**: Type-safe TestConfiguration with Pydantic
  * **Results**: Comprehensive TestResult classes
  * **Device Management**: AndroidDevice and DeviceManager wrappers

**Layer 2: Infrastructure** (``src/TrigDroid_Infrastructure/``)
  * **Interfaces**: Protocol-based abstractions (ILogger, ITestRunner, IAndroidDevice)
  * **Dependency Injection**: DI container with ServiceLocator
  * **Test Runners**: Pluggable test execution (SensorTestRunner, FridaTestRunner)
  * **Application Orchestrator**: Main workflow coordination

**TypeScript Frida Hooks** (``frida-hooks/``)
  * **Modern TypeScript hooks** replacing legacy JavaScript
  * **Modular design** with individual hook files in ``hooks/``
  * **Type safety** with ``@types/frida-gum``
  * **Built via npm** and integrated into Python package

Security Considerations
======================

* **Defensive purpose only**: Tool designed for security research and malware analysis
* **Authorized testing**: Only test applications you own or have permission to analyze
* **Isolated environments**: Run in controlled sandboxes
* **No malicious enhancement**: Do not create or improve malicious capabilities

Support
=======

* **Documentation**: Complete documentation with examples and tutorials
* **GitHub Issues**: Report bugs and request features
* **Developer Community**: Active development and contribution guidelines

License
=======

This project is licensed under the MIT License - see the ``LICENSE`` file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`