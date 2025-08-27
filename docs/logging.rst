=====================
Logging & Monitoring
=====================

This section covers TrigDroid's comprehensive logging capabilities and monitoring features for security testing and analysis.

.. important::
   Proper logging is crucial for security research. TrigDroid provides detailed logging 
   to help you understand application behavior changes and detect potential threats.

Logging Architecture
====================

TrigDroid implements a layered logging architecture that captures different aspects of the testing process:

Logging Levels
--------------

TrigDroid uses standard Python logging levels with security-focused categorization:

* **DEBUG**: Detailed execution information, API call traces, internal state changes
* **INFO**: General test execution flow, configuration details, phase transitions
* **WARNING**: Unexpected behaviors, potential issues, configuration warnings
* **ERROR**: Test failures, device connection issues, critical errors
* **CRITICAL**: Security-relevant events, malicious behavior detection

Logging Categories
==================

System Logging
--------------

Core system operations and infrastructure events:

.. code-block:: python

   import logging
   from trigdroid import TrigDroidAPI, TestConfiguration
   
   # Configure logging level
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger('trigdroid')
   
   config = TestConfiguration(
       package="com.example.app",
       log_level="DEBUG"  # Detailed logging
   )
   
   with TrigDroidAPI(config) as api:
       # System logs automatically captured
       result = api.run_tests()

Device Interaction Logging
--------------------------

ADB commands, device state changes, and hardware interactions:

.. code-block:: python

   config = TestConfiguration(
       package="com.test.app",
       log_device_interactions=True,  # Enable device logging
       log_adb_commands=True          # Log ADB command execution
   )

Application Behavior Logging
----------------------------

Application-specific events and behavioral changes:

.. code-block:: python

   config = TestConfiguration(
       package="com.suspicious.app",
       log_app_lifecycle=True,        # Activity lifecycle events
       log_permission_changes=True,   # Permission grant/revoke events
       log_network_activity=True      # Network connections and data transfer
   )

Frida Instrumentation Logging
-----------------------------

Runtime hooking and dynamic analysis events:

.. code-block:: python

   config = TestConfiguration(
       package="com.analysis.target",
       frida_hooks=True,
       log_frida_hooks=True,          # Hook invocation logging
       log_api_calls=True,            # Android API call logging
       log_method_arguments=True      # Method argument capture
   )

Security Event Logging
----------------------

High-priority security-relevant events:

.. code-block:: python

   config = TestConfiguration(
       package="com.malware.sample",
       log_security_events=True,      # Malicious behavior indicators
       log_anti_analysis=True,        # Anti-analysis technique detection
       log_evasion_attempts=True      # Evasion behavior logging
   )

Log Configuration
=================

Configuration File
------------------

Create a logging configuration file for detailed control:

.. code-block:: yaml

   # logging_config.yaml
   version: 1
   formatters:
     detailed:
       format: '[{asctime}] {levelname:8} {name}: {message}'
       style: '{'
     security:
       format: '[{asctime}] SECURITY-{levelname}: {name}: {message}'
       style: '{'
   
   handlers:
     console:
       class: logging.StreamHandler
       level: INFO
       formatter: detailed
       stream: ext://sys.stdout
     
     file:
       class: logging.handlers.RotatingFileHandler
       level: DEBUG
       formatter: detailed
       filename: trigdroid.log
       maxBytes: 10485760  # 10MB
       backupCount: 5
     
     security_file:
       class: logging.FileHandler
       level: WARNING
       formatter: security
       filename: security_events.log
   
   loggers:
     trigdroid:
       level: DEBUG
       handlers: [console, file]
       propagate: false
     
     trigdroid.security:
       level: WARNING
       handlers: [security_file]
       propagate: false
   
   root:
     level: WARNING
     handlers: [console]

Programmatic Configuration
-------------------------

Configure logging programmatically:

.. code-block:: python

   import logging
   import logging.config
   from trigdroid import TrigDroidAPI, TestConfiguration
   
   # Load logging configuration
   with open('logging_config.yaml', 'r') as f:
       logging.config.dictConfig(yaml.safe_load(f))
   
   # Create logger
   logger = logging.getLogger('trigdroid')
   
   # Configure TrigDroid with custom logging
   config = TestConfiguration(
       package="com.example.app",
       logger=logger,
       log_level="DEBUG",
       log_format="[{timestamp}] {level}: {module}: {message}"
   )

Log Output Examples
===================

System Execution Logs
---------------------

.. code-block:: text

   [2024-01-15 10:30:15] INFO     trigdroid.api: Starting TrigDroid test session
   [2024-01-15 10:30:15] INFO     trigdroid.device: Connected to device emulator-5554
   [2024-01-15 10:30:16] INFO     trigdroid.config: Loaded configuration for com.example.app
   [2024-01-15 10:30:16] DEBUG    trigdroid.setup: Installing application package
   [2024-01-15 10:30:18] INFO     trigdroid.runner: Starting sensor test runner
   [2024-01-15 10:30:18] DEBUG    trigdroid.sensors: Setting accelerometer to high activity
   [2024-01-15 10:30:19] INFO     trigdroid.app: Application launched successfully

Device Interaction Logs
-----------------------

.. code-block:: text

   [2024-01-15 10:30:20] DEBUG    trigdroid.adb: adb shell am start -n com.example.app/.MainActivity
   [2024-01-15 10:30:21] DEBUG    trigdroid.device: Battery level changed: 100% -> 15%
   [2024-01-15 10:30:22] DEBUG    trigdroid.network: WiFi state changed: connected -> disconnected
   [2024-01-15 10:30:23] DEBUG    trigdroid.sensors: Gyroscope data injected: x=1.2, y=2.1, z=0.8

Frida Hook Logs
---------------

.. code-block:: text

   [2024-01-15 10:30:25] DEBUG    trigdroid.frida: Hook attached to android.telephony.TelephonyManager.getDeviceId
   [2024-01-15 10:30:26] INFO     trigdroid.hooks: API call intercepted: TelephonyManager.getDeviceId()
   [2024-01-15 10:30:26] DEBUG    trigdroid.hooks: Return value modified: 'real_imei' -> 'fake_imei_123'
   [2024-01-15 10:30:27] WARNING  trigdroid.hooks: Suspicious call detected: Runtime.exec("su")

Security Event Logs
-------------------

.. code-block:: text

   [2024-01-15 10:30:30] WARNING  trigdroid.security: Anti-emulator check detected in com.example.app
   [2024-01-15 10:30:31] ERROR    trigdroid.security: Potential malicious behavior: Attempting to access /system/bin/su
   [2024-01-15 10:30:32] CRITICAL trigdroid.security: Data exfiltration detected: Unauthorized network connection to 192.168.1.100:8080
   [2024-01-15 10:30:33] ERROR    trigdroid.security: Root detection bypass attempted

Log Analysis and Monitoring
===========================

Real-time Monitoring
--------------------

Monitor logs in real-time during test execution:

.. code-block:: python

   import logging
   from trigdroid import TrigDroidAPI, TestConfiguration
   
   class SecurityEventHandler(logging.Handler):
       def emit(self, record):
           if record.levelno >= logging.WARNING:
               if 'malicious' in record.getMessage().lower():
                   # Alert on potential malicious behavior
                   self.send_security_alert(record.getMessage())
   
   # Add custom handler
   security_handler = SecurityEventHandler()
   security_logger = logging.getLogger('trigdroid.security')
   security_logger.addHandler(security_handler)

Log Aggregation
---------------

Collect and aggregate logs from multiple test sessions:

.. code-block:: python

   import json
   import logging.handlers
   from trigdroid import TrigDroidAPI, TestConfiguration
   
   # JSON formatter for structured logs
   class JSONFormatter(logging.Formatter):
       def format(self, record):
           log_data = {
               'timestamp': self.formatTime(record),
               'level': record.levelname,
               'logger': record.name,
               'message': record.getMessage(),
               'module': record.module,
               'function': record.funcName,
               'line': record.lineno
           }
           return json.dumps(log_data)
   
   # Configure JSON logging
   json_handler = logging.handlers.RotatingFileHandler(
       'trigdroid_structured.log', maxBytes=50*1024*1024, backupCount=10
   )
   json_handler.setFormatter(JSONFormatter())
   
   logger = logging.getLogger('trigdroid')
   logger.addHandler(json_handler)

Log Analysis Tools
==================

Built-in Analysis
-----------------

TrigDroid provides built-in log analysis capabilities:

.. code-block:: python

   from trigdroid.analysis import LogAnalyzer
   
   # Analyze test logs
   analyzer = LogAnalyzer('trigdroid.log')
   
   # Extract security events
   security_events = analyzer.extract_security_events()
   
   # Identify behavioral patterns
   patterns = analyzer.identify_patterns()
   
   # Generate summary report
   report = analyzer.generate_report()
   print(report)

Custom Analysis Scripts
----------------------

Create custom analysis scripts for specific use cases:

.. code-block:: python

   import re
   import json
   from collections import defaultdict
   
   def analyze_api_calls(log_file):
       """Analyze API call patterns from Frida hook logs."""
       api_calls = defaultdict(int)
       suspicious_calls = []
       
       with open(log_file, 'r') as f:
           for line in f:
               if 'API call intercepted' in line:
                   # Extract API call name
                   match = re.search(r'API call intercepted: (.+)\(', line)
                   if match:
                       api_name = match.group(1)
                       api_calls[api_name] += 1
                       
                       # Flag suspicious APIs
                       if any(sus in api_name.lower() for sus in ['exec', 'root', 'su', 'system']):
                           suspicious_calls.append((line.strip(), api_name))
       
       return api_calls, suspicious_calls
   
   # Usage
   calls, suspicious = analyze_api_calls('trigdroid.log')
   print(f"Total API calls: {len(calls)}")
   print(f"Suspicious calls: {len(suspicious)}")

Performance Monitoring
=====================

Execution Time Tracking
-----------------------

Monitor test execution performance:

.. code-block:: python

   import time
   import logging
   from functools import wraps
   
   def timed_operation(operation_name):
       def decorator(func):
           @wraps(func)
           def wrapper(*args, **kwargs):
               logger = logging.getLogger('trigdroid.performance')
               start_time = time.time()
               logger.info(f"Starting {operation_name}")
               
               try:
                   result = func(*args, **kwargs)
                   duration = time.time() - start_time
                   logger.info(f"{operation_name} completed in {duration:.2f}s")
                   return result
               except Exception as e:
                   duration = time.time() - start_time
                   logger.error(f"{operation_name} failed after {duration:.2f}s: {e}")
                   raise
           return wrapper
       return decorator

Resource Usage Monitoring
-------------------------

Track system resource usage during testing:

.. code-block:: python

   import psutil
   import logging
   import threading
   import time
   
   class ResourceMonitor:
       def __init__(self, interval=5):
           self.interval = interval
           self.monitoring = False
           self.logger = logging.getLogger('trigdroid.resources')
       
       def start_monitoring(self):
           self.monitoring = True
           threading.Thread(target=self._monitor, daemon=True).start()
       
       def stop_monitoring(self):
           self.monitoring = False
       
       def _monitor(self):
           while self.monitoring:
               cpu_percent = psutil.cpu_percent()
               memory = psutil.virtual_memory()
               
               self.logger.info(
                   f"Resource usage - CPU: {cpu_percent}%, "
                   f"Memory: {memory.percent}% ({memory.used/1024/1024:.1f}MB)"
               )
               time.sleep(self.interval)

Best Practices
==============

Logging Security Guidelines
---------------------------

* **Sensitive Data**: Never log passwords, tokens, or personally identifiable information
* **Data Classification**: Classify logs based on sensitivity (public, internal, confidential)
* **Retention Policy**: Implement appropriate log retention policies
* **Access Control**: Restrict access to security-relevant logs

Log Management
--------------

* **Rotation**: Use log rotation to prevent disk space issues
* **Compression**: Compress old log files to save space
* **Centralization**: Consider centralized logging for multiple test environments
* **Backup**: Regularly backup important log files

Analysis Efficiency
-------------------

* **Structured Logging**: Use structured formats (JSON) for easier parsing
* **Indexing**: Index logs for faster searching and analysis
* **Filtering**: Implement log filtering to reduce noise
* **Alerting**: Set up automated alerting for critical security events

Integration Examples
===================

ELK Stack Integration
--------------------

Integrate with Elasticsearch, Logstash, and Kibana:

.. code-block:: python

   import logging
   from pythonjsonlogger import jsonlogger
   
   # Configure JSON logging for ELK
   logHandler = logging.StreamHandler()
   formatter = jsonlogger.JsonFormatter()
   logHandler.setFormatter(formatter)
   logger = logging.getLogger('trigdroid')
   logger.addHandler(logHandler)
   logger.setLevel(logging.INFO)

SIEM Integration
---------------

Send security events to Security Information and Event Management systems:

.. code-block:: python

   import logging
   import requests
   
   class SIEMHandler(logging.Handler):
       def __init__(self, siem_url, api_key):
           super().__init__()
           self.siem_url = siem_url
           self.api_key = api_key
       
       def emit(self, record):
           if record.levelno >= logging.WARNING:
               event_data = {
                   'timestamp': self.formatTime(record),
                   'severity': record.levelname,
                   'source': 'TrigDroid',
                   'message': record.getMessage(),
                   'category': 'mobile_security_testing'
               }
               
               try:
                   requests.post(
                       self.siem_url,
                       json=event_data,
                       headers={'Authorization': f'Bearer {self.api_key}'},
                       timeout=5
                   )
               except Exception:
                   # Don't fail the main operation if SIEM is unavailable
                   pass

For more advanced logging configurations and analysis techniques, see the :doc:`development` guide.