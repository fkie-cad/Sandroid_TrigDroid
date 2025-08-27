===================
API Reference
===================

This section provides detailed API documentation for TrigDroid's Python modules.

TrigDroid Public API
====================

The main public API that users interact with.

.. toctree::
   :maxdepth: 2
   
   trigdroid

TrigDroid Infrastructure
=======================

Internal infrastructure components and interfaces.

.. toctree::
   :maxdepth: 2
   
   infrastructure

Quick API Examples
==================

Basic Usage
-----------

.. code-block:: python

   from trigdroid import TrigDroidAPI, TestConfiguration

   # Basic usage
   config = TestConfiguration(package="com.example.app")
   with TrigDroidAPI(config) as api:
       result = api.run_tests()
       print(f"Success: {result.success}")

Advanced Configuration
----------------------

.. code-block:: python

   from trigdroid import TrigDroidAPI, TestConfiguration

   # Advanced configuration
   config = TestConfiguration(
       package="com.suspicious.app",
       acceleration=8,
       sensors=["accelerometer", "gyroscope"], 
       network_states=["wifi", "data"],
       frida_hooks=True,
       timeout=600
   )

   with TrigDroidAPI(config) as api:
       result = api.run_tests()
       print(f"Success: {result.success}")
       print(f"Tests run: {result.total_tests}")

Device Management
-----------------

.. code-block:: python

   from trigdroid import DeviceManager, scan_devices

   # Scan for devices
   devices = scan_devices()

   # Connect to specific device
   manager = DeviceManager()
   device = manager.connect_to_device("emulator-5554")

Configuration Validation
-------------------------

.. code-block:: python

   from trigdroid import TestConfiguration

   config = TestConfiguration(package="com.example.app")
   if not config.is_valid():
       for error in config.validation_errors:
           print(f"Error: {error}")

Results Analysis
----------------

.. code-block:: python

   result = api.run_tests()
   print(f"Success: {result.success}")
   print(f"Phase: {result.phase}")
   print(f"Duration: {result.duration_seconds}s")
   print(f"App crashed: {result.app_crashed}")