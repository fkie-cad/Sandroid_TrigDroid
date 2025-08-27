===============
Troubleshooting
===============

This section covers common issues and their solutions when using TrigDroid.

Installation Issues
===================

Python Version Compatibility
-----------------------------

**Problem:** TrigDroid requires Python 3.9 or higher.

**Solution:** 

.. code-block:: bash

   # Check your Python version
   python --version
   
   # If using an older version, install Python 3.9+
   # On Ubuntu/Debian:
   sudo apt update
   sudo apt install python3.9 python3.9-pip python3.9-venv
   
   # On macOS with Homebrew:
   brew install python@3.9

Missing Dependencies
--------------------

**Problem:** Missing required system dependencies.

**Solution:**

.. code-block:: bash

   # Install all dependencies with full features
   pip install -e ".[full,dev]"
   
   # Or install specific features only
   pip install -e ".[frida]"    # Frida support only
   pip install -e ".[dev]"      # Development tools only

Android SDK Issues
------------------

**Problem:** ADB not found in PATH.

**Solution:**

1. Install Android Studio and Android SDK
2. Add SDK tools to PATH:

.. code-block:: bash

   # Add to ~/.bashrc or ~/.zshrc
   export ANDROID_HOME=$HOME/Android/Sdk
   export PATH=$PATH:$ANDROID_HOME/platform-tools
   export PATH=$PATH:$ANDROID_HOME/build-tools/<version>

3. Restart terminal and verify:

.. code-block:: bash

   adb version
   apksigner --help

Device Connection Issues
========================

Device Not Detected
--------------------

**Problem:** Android device/emulator not showing up.

**Solution:**

.. code-block:: bash

   # Check connected devices
   adb devices
   
   # If no devices shown:
   # 1. Enable USB debugging on device
   # 2. Trust the computer when prompted
   # 3. Try different USB cable/port
   # 4. Restart ADB server
   adb kill-server
   adb start-server

Emulator Issues
---------------

**Problem:** Emulator not starting or responding slowly.

**Solution:**

1. **Hardware Acceleration:**

   - Enable Intel HAXM or AMD-V in BIOS
   - Install Intel HAXM or AMD hypervisor

2. **Memory and Storage:**

   - Allocate sufficient RAM (4GB+)
   - Ensure sufficient disk space (8GB+)

3. **Emulator Settings:**

   .. code-block:: bash
   
      # Start emulator with more memory
      emulator -avd <avd_name> -memory 4096
      
      # Enable hardware acceleration
      emulator -avd <avd_name> -accel-check

Permission Issues
=================

USB Debugging Not Authorized
-----------------------------

**Problem:** Device shows as unauthorized.

**Solution:**

1. Enable "USB Debugging" in Developer Options
2. When prompted on device, select "Always allow from this computer"
3. If still issues, revoke and re-authorize:

.. code-block:: bash

   adb kill-server
   adb start-server
   # Accept authorization on device

Root Access Required
--------------------

**Problem:** Some features require root access.

**Solution:**

1. **For Emulators:** Usually rooted by default
2. **For Physical Devices:** 

   - Use rooted device or custom ROM
   - Some features work without root (check documentation)

Frida Issues
============

Frida Server Not Running
-------------------------

**Problem:** Frida instrumentation fails.

**Solution:**

.. code-block:: bash

   # Check if frida-server is running on device
   adb shell ps | grep frida-server
   
   # If not running, start frida-server
   adb push frida-server /data/local/tmp/
   adb shell chmod 755 /data/local/tmp/frida-server
   adb shell /data/local/tmp/frida-server &

Architecture Mismatch
----------------------

**Problem:** Frida version mismatch or wrong architecture.

**Solution:**

1. Download correct frida-server for your device architecture:

   .. code-block:: bash
   
      # Check device architecture
      adb shell getprop ro.product.cpu.abi
      
      # Download matching frida-server from:
      # https://github.com/frida/frida/releases

2. Ensure Frida Python client version matches:

   .. code-block:: bash
   
      pip install frida-tools==<version>

TypeScript Build Issues
=======================

Node.js/NPM Issues
------------------

**Problem:** TypeScript hooks fail to build.

**Solution:**

.. code-block:: bash

   # Install Node.js 16+ and npm
   # On Ubuntu/Debian:
   curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
   sudo apt-get install -y nodejs
   
   # On macOS:
   brew install node@16
   
   # Verify installation
   node --version
   npm --version

Build Failures
---------------

**Problem:** Frida hooks compilation fails.

**Solution:**

.. code-block:: bash

   # Navigate to frida-hooks directory
   cd frida-hooks
   
   # Clean and rebuild
   npm run clean
   npm install
   npm run build
   
   # For development with watch mode
   npm run watch

Testing Issues
==============

Tests Failing
-------------

**Problem:** Test suite shows failures.

**Solution:**

1. **Check Requirements:**

   .. code-block:: bash
   
      # Ensure all dev dependencies installed
      pip install -e ".[dev]"

2. **Run Specific Test Categories:**

   .. code-block:: bash
   
      # Run only unit tests (fast)
      pytest -m unit
      
      # Skip slow integration tests
      pytest -m "not slow"
      
      # Run with verbose output
      pytest -v -l

3. **Device-Dependent Tests:**

   .. code-block:: bash
   
      # Skip tests requiring devices
      pytest -m "not requires_device"
      
      # Skip Frida tests
      pytest -m "not requires_frida"

Test Coverage Issues
--------------------

**Problem:** Low test coverage or coverage report failures.

**Solution:**

.. code-block:: bash

   # Install coverage tools
   pip install pytest-cov
   
   # Run with coverage
   pytest --cov=src/trigdroid --cov=src/TrigDroid_Infrastructure --cov-report=html
   
   # View coverage report
   open htmlcov/index.html

Application Testing Issues
==========================

App Crashes
-----------

**Problem:** Target application crashes during testing.

**Solution:**

1. **Check Application Logs:**

   .. code-block:: bash
   
      # Monitor logcat during testing
      adb logcat | grep <package_name>

2. **Reduce Test Intensity:**

   - Lower sensor manipulation frequency
   - Reduce interaction complexity
   - Increase timeouts

3. **Application Compatibility:**

   - Check Android API level compatibility
   - Verify application permissions
   - Test with different Android versions

Performance Issues
==================

Slow Test Execution
--------------------

**Problem:** Tests run very slowly.

**Solution:**

1. **Hardware Optimization:**

   - Use physical device instead of emulator
   - Increase emulator RAM and CPU cores
   - Enable hardware acceleration

2. **Configuration Optimization:**

   .. code-block:: bash
   
      # Disable changelog for faster execution
      trigdroid -p com.example.app --disable-changelog
      
      # Enable changelog caching
      trigdroid -p com.example.app --changelog-cache

3. **Selective Testing:**

   - Disable unnecessary features
   - Use targeted test configurations
   - Run parallel tests when possible

Memory Issues
-------------

**Problem:** High memory usage or out-of-memory errors.

**Solution:**

1. **Monitor Memory:**

   .. code-block:: bash
   
      # Monitor system resources
      top
      htop
      
      # Monitor Android device memory
      adb shell cat /proc/meminfo

2. **Optimize Configuration:**

   - Reduce concurrent operations
   - Clear cache between tests
   - Limit log file sizes

Configuration Issues
====================

Invalid Configuration
----------------------

**Problem:** Configuration validation errors.

**Solution:**

.. code-block:: python

   from trigdroid import TestConfiguration
   
   config = TestConfiguration(package="com.example.app")
   if not config.is_valid():
       for error in config.validation_errors:
           print(f"Configuration Error: {error}")

YAML Configuration Issues
-------------------------

**Problem:** YAML configuration file parsing errors.

**Solution:**

1. **Validate YAML Syntax:**

   .. code-block:: bash
   
      # Use online YAML validator or:
      python -c "import yaml; yaml.safe_load(open('config.yaml'))"

2. **Check Configuration Schema:**

   .. code-block:: yaml
   
      # Example valid configuration
      package: "com.example.app"
      acceleration: 8
      battery: 3
      frida_hooks: true
      timeout: 600
      sensors:
        - "accelerometer"
        - "gyroscope"

Getting Help
============

Log Analysis
------------

When reporting issues, include relevant logs:

.. code-block:: bash

   # Enable debug logging
   trigdroid -p com.example.app --log-level DEBUG --log-file debug.log
   
   # Enable extended log format
   trigdroid -p com.example.app --extended-log-format

Community Support
-----------------

1. **Check Documentation:** Review all sections of this documentation
2. **Search Issues:** Look through existing GitHub issues
3. **Create Issue:** Report bugs with full logs and reproduction steps
4. **Development Chat:** Join the development community discussions

Issue Reporting Template
------------------------

When reporting issues, please include:

1. **Environment Information:**

   - Operating system and version
   - Python version
   - TrigDroid version
   - Android device/emulator details

2. **Reproduction Steps:**

   - Exact commands used
   - Configuration files
   - Expected vs actual behavior

3. **Logs and Error Messages:**

   - Full error messages
   - Debug logs
   - Stack traces

4. **Additional Context:**

   - Related issues or workarounds tried
   - Screenshots if applicable