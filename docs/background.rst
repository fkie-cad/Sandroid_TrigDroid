==================
Background & Usage
==================

This section provides comprehensive information about TrigDroid's architecture, features, and testing capabilities.

.. warning::
   **SECURITY NOTICE**: TrigDroid is designed exclusively for **defensive security research** 
   and malware analysis. Only use this tool to test applications you own or have explicit 
   permission to analyze in controlled environments.

What is TrigDroid?
==================

TrigDroid is a sophisticated Android security testing framework that triggers potentially malicious behaviors in Android applications through systematic environmental manipulation. By simulating various device conditions, sensor states, and runtime scenarios, TrigDroid helps security researchers identify conditional malware behaviors that might otherwise remain dormant.

Key Capabilities
================

Environmental Manipulation
--------------------------

TrigDroid can simulate a wide range of device conditions:

* **Device State Changes**: Battery levels, charging status, screen orientation
* **Network Conditions**: WiFi connectivity, mobile data, network availability
* **System Properties**: Device model, Android version, security patch level
* **Sensor Data**: Accelerometer, gyroscope, magnetometer readings
* **Temporal Conditions**: Time zones, system time, uptime simulation

Runtime Instrumentation
-----------------------

Through Frida integration, TrigDroid provides:

* **API Hooking**: Monitor and modify Android API calls in real-time
* **Method Interception**: Hook specific Java methods and native functions
* **Dynamic Analysis**: Observe application behavior changes
* **Memory Manipulation**: Modify runtime values and object states

Application Interaction
-----------------------

Automated interaction capabilities include:

* **UI Automation**: Simulate user touches, gestures, and input
* **Permission Management**: Grant or revoke permissions dynamically
* **Activity Lifecycle**: Control application states and transitions
* **Intent Broadcasting**: Send custom intents to trigger behaviors

Architecture Overview
=====================

TrigDroid follows a modern dual-layer architecture implementing SOLID design principles:

Public API Layer
----------------

The **trigdroid** package provides the main interface:

.. code-block:: python

   from trigdroid import TrigDroidAPI, TestConfiguration
   
   config = TestConfiguration(
       package="com.example.app",
       sensors=["accelerometer", "gyroscope"],
       network_states=["wifi", "disconnected"],
       frida_hooks=True
   )
   
   with TrigDroidAPI(config) as api:
       result = api.run_tests()

Infrastructure Layer  
--------------------

The **TrigDroid_Infrastructure** package contains:

* **Interfaces**: Protocol-based abstractions for extensibility
* **Dependency Injection**: Service container for loose coupling  
* **Test Runners**: Pluggable execution engines for different test types
* **Device Management**: Android device abstraction and control

TypeScript Frida Hooks
----------------------

Modern TypeScript-based hooks provide:

* **Type Safety**: Full TypeScript support with Frida type definitions
* **Modular Design**: Individual hook files for different Android components
* **Build Integration**: Automatic compilation and packaging

Testing Methodology
===================

TrigDroid employs a systematic approach to trigger malicious behaviors:

Phase-Based Testing
-------------------

1. **Setup Phase**
   
   * Device connection and validation
   * Application installation and preparation
   * Initial state configuration

2. **Execution Phase**
   
   * Environmental condition simulation
   * Sensor data manipulation
   * Network state changes
   * Runtime instrumentation

3. **Analysis Phase**
   
   * Behavior change detection
   * Log analysis and correlation
   * Result aggregation and reporting

4. **Teardown Phase**
   
   * Environment restoration
   * Cleanup and state reset

Configuration-Driven Testing
----------------------------

Tests are configured through YAML or programmatic configuration:

.. code-block:: yaml

   package: "com.suspicious.app"
   timeout: 600
   sensors:
     - accelerometer: high_movement
     - battery: low_battery
   network_states:
     - wifi: disconnected
     - mobile_data: enabled
   frida_hooks: true
   interaction:
     - touch_events: random
     - permission_changes: runtime

Common Testing Scenarios
========================

Conditional Malware Detection
-----------------------------

* **Time-based Activation**: Malware that activates after specific dates/times
* **Location-based Triggers**: Behavior changes based on GPS coordinates  
* **Sensor-based Evasion**: Detection of analysis environments through sensor data
* **Network-dependent Actions**: Malware requiring specific network conditions

Anti-Analysis Evasion
---------------------

* **Emulator Detection**: Identify apps that behave differently on emulators
* **Debugger Detection**: Find anti-debugging and tamper detection mechanisms
* **Dynamic Analysis Evasion**: Uncover Frida and instrumentation detection

Behavioral Analysis
-------------------

* **Permission Escalation**: Test how apps respond to permission changes
* **Data Exfiltration**: Monitor network activity under various conditions
* **UI Manipulation**: Detect overlay attacks and clickjacking attempts
* **Device Fingerprinting**: Identify unique device identification methods

Best Practices
==============

Security Considerations
-----------------------

* **Isolated Environment**: Always run tests in controlled, isolated environments
* **Authorized Testing**: Only test applications you own or have permission to analyze
* **Data Protection**: Ensure no sensitive data is exposed during testing
* **Result Storage**: Securely store and analyze test results

Effective Testing
-----------------

* **Comprehensive Coverage**: Test multiple environmental conditions
* **Iterative Refinement**: Adjust test parameters based on initial results
* **Baseline Comparison**: Compare behavior against known-good applications
* **Long-term Monitoring**: Some behaviors may require extended observation periods

Result Interpretation
---------------------

* **Behavior Correlation**: Link environmental changes to application responses
* **False Positive Filtering**: Distinguish malicious from legitimate behavior changes
* **Pattern Recognition**: Identify common evasion and triggering techniques
* **Documentation**: Maintain detailed records of test configurations and results

Integration Examples
====================

Basic Testing Workflow
-----------------------

.. code-block:: python

   from trigdroid import TrigDroidAPI, TestConfiguration, scan_devices
   
   # Scan for available devices
   devices = scan_devices()
   print(f"Found {len(devices)} devices")
   
   # Configure test parameters
   config = TestConfiguration(
       package="com.example.suspicious",
       acceleration=8,  # High movement simulation
       battery=15,      # Low battery simulation
       network_states=["disconnected", "wifi"],
       timeout=300
   )
   
   # Run comprehensive test
   with TrigDroidAPI(config) as api:
       result = api.run_tests()
       
       if result.success:
           print(f"Test completed successfully")
           print(f"Tests executed: {result.total_tests}")
           print(f"Behavioral changes detected: {result.behavior_changes}")
       else:
           print(f"Test failed in phase: {result.phase}")

Advanced Frida Integration
--------------------------

.. code-block:: python

   from trigdroid import TrigDroidAPI, TestConfiguration
   
   config = TestConfiguration(
       package="com.example.advanced",
       frida_hooks=True,
       custom_hooks=["crypto_hooks", "network_hooks"],
       sensor_simulation=True,
       deep_analysis=True
   )
   
   with TrigDroidAPI(config) as api:
       # Start monitoring
       api.start_monitoring()
       
       # Apply environmental changes
       api.set_battery_level(10)
       api.simulate_network_disconnect()
       api.inject_sensor_data("accelerometer", high_activity_data)
       
       # Analyze results
       behaviors = api.get_behavioral_changes()
       network_calls = api.get_network_activity()
       api_calls = api.get_hooked_api_calls()
       
       result = api.finalize_test()

For more detailed examples and advanced usage patterns, see the :doc:`api/index` documentation.