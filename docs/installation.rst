============
Installation
============

This section covers the installation and setup requirements for TrigDroid.

.. note::
   TrigDroid is designed for **defensive security research** and malware analysis only. 
   Only test applications you own or have permission to analyze.

Requirements
============

System Requirements
------------------

* **Python 3.9+** - Required for running TrigDroid
* **Node.js 16+** - Required for building TypeScript Frida hooks
* **Android SDK with ADB** - For Android device communication
* **Android Device or Emulator** - With USB debugging enabled

Optional Dependencies
--------------------

* **Frida 16.0+** - For runtime instrumentation (recommended)
* **Android Studio** - For managing emulators and SDK components

Quick Installation
==================

Basic Installation
------------------

Install TrigDroid with basic functionality:

.. code-block:: bash

   pip install -e .

Development Installation
-----------------------

Install with all development tools and features:

.. code-block:: bash

   pip install -e ".[full,dev]"

Feature-Specific Installation
----------------------------

Install with specific features only:

.. code-block:: bash

   # Frida support only
   pip install -e ".[frida]"
   
   # Development tools only
   pip install -e ".[dev]"

Android SDK Setup
=================

Android Studio Installation
---------------------------

1. Download and install `Android Studio <https://developer.android.com/studio>`_
2. Launch Android Studio and complete the initial setup
3. Install the Android SDK and build tools through the SDK Manager

Setting up an Emulator
----------------------

1. Open Android Studio
2. Go to **Tools > AVD Manager**
3. Click **Create Virtual Device**
4. Select a device definition and system image
5. Configure the AVD settings and click **Finish**
6. Start the emulator from the AVD Manager

Adding ADB to PATH
------------------

Add the Android SDK platform-tools to your system PATH:

**Linux/macOS:**

.. code-block:: bash

   export PATH="$HOME/Android/Sdk/platform-tools:$PATH"
   # Add to your ~/.bashrc or ~/.zshrc for persistence

**Windows:**

.. code-block:: batch

   set PATH=%LOCALAPPDATA%\Android\Sdk\platform-tools;%PATH%

Device Configuration
====================

Physical Device Setup
---------------------

1. Enable **Developer Options** on your Android device:
   
   * Go to **Settings > About Phone**
   * Tap **Build Number** 7 times
   
2. Enable **USB Debugging**:
   
   * Go to **Settings > Developer Options**
   * Enable **USB Debugging**
   
3. Connect your device via USB and accept the debugging authorization

Emulator Setup
--------------

1. Start your Android emulator
2. Verify ADB connection:

.. code-block:: bash

   adb devices

You should see your device/emulator listed.

Verification
============

Test Your Installation
----------------------

Verify that TrigDroid is installed correctly:

.. code-block:: bash

   # Check TrigDroid installation
   python -c "import trigdroid; print('TrigDroid installed successfully')"
   
   # Test CLI access
   trigdroid --help
   
   # List connected devices
   trigdroid devices

Build TypeScript Hooks (Optional)
---------------------------------

If you plan to use Frida instrumentation:

.. code-block:: bash

   cd frida-hooks
   npm install
   npm run build

Quick Start Test
---------------

Run a basic test to verify everything works:

.. code-block:: bash

   # Test with a system app (replace with actual package)
   trigdroid -p com.android.settings

   # If you have a test app installed
   trigdroid -p com.example.testapp --timeout 30

Troubleshooting
===============

Common Issues
-------------

**ADB not found:**
   Ensure Android SDK platform-tools are in your PATH

**No devices found:**
   * Check USB debugging is enabled
   * Run ``adb devices`` to verify connection
   * Try ``adb kill-server && adb start-server``

**Permission denied:**
   * Check USB debugging authorization on device
   * Try different USB cable or port

**Frida installation issues:**
   * Install Frida server on your device/emulator
   * Ensure Frida version compatibility

**Import errors:**
   * Verify Python version (3.9+)
   * Try ``pip install -e ".[full]"`` for all dependencies

For more detailed troubleshooting, see the :doc:`troubleshooting` section.

Next Steps
==========

Now that TrigDroid is installed, you can:

* Read the :doc:`background` to understand TrigDroid's capabilities
* Check out the :doc:`api/index` for programmatic usage
* Explore the :doc:`development` guide if you want to contribute