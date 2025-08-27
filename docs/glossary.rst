========
Glossary
========

This glossary defines key terms and concepts used throughout TrigDroid documentation.

.. glossary::

   ADB
      Android Debug Bridge. A versatile command-line tool that lets you communicate with a device.

   Android Virtual Device (AVD)
      An emulator configuration that represents a specific Android device.

   API Level
      An integer value that uniquely identifies the framework API revision offered by a version of the Android platform.

   APK
      Android Application Package. The file format used by Android for distribution and installation of mobile apps.

   Defensive Security
      Security practices focused on protecting systems and detecting threats rather than attacking them.

   Dependency Injection (DI)
      A design pattern where objects receive their dependencies from external sources rather than creating them internally.

   Device Under Test (DUT)
      The Android device or emulator being tested with TrigDroid.

   Frida
      A dynamic instrumentation toolkit for developers, reverse-engineers, and security researchers.

   Hook
      In the context of Frida, code that intercepts and potentially modifies the behavior of existing functions.

   Instrumentation
      The process of modifying code to monitor or alter its behavior during execution.

   Malware Analysis
      The process of analyzing malicious software to understand its functionality and behavior.

   Mocking
      Creating fake versions of real objects to simulate their behavior in a controlled way.

   Orchestrator
      The main component that coordinates the execution of tests and manages the overall workflow.

   Package Name
      A unique identifier for Android applications, typically in reverse domain notation (e.g., com.example.app).

   Payload
      In security testing, the malicious functionality that an application might execute under certain conditions.

   Protocol
      In Python typing, an interface definition that specifies the methods and attributes a class must implement.

   Pydantic
      A Python library that provides data validation and settings management using Python type hints.

   Service Locator
      A design pattern that provides a centralized registry for obtaining service instances.

   SOLID Principles
      Five design principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion) that make software designs more understandable, flexible, and maintainable.

   Test Runner
      A component responsible for executing specific types of tests within the TrigDroid framework.

   Trigger
      An environmental condition or stimulus designed to activate potentially malicious behavior in an application.

   TypeScript
      A programming language developed by Microsoft that builds on JavaScript by adding static type definitions.

   USB Debugging
      A feature on Android devices that allows debugging via USB connection.

Architectural Terms
===================

.. glossary::

   Application Layer
      The top layer of TrigDroid's architecture containing the main orchestrator and workflow logic.

   Infrastructure Layer
      The lower layer containing core services like dependency injection, logging, and configuration management.

   Interface Segregation
      The principle that clients should not be forced to depend on interfaces they do not use.

   Inversion of Control (IoC)
      A design principle where the control of object creation and management is transferred to an external container.

   Public API Layer
      The external interface layer that users interact with, including CLI and Python API.

   Service Container
      A container that manages the creation and lifecycle of service instances.

Testing Terms
=============

.. glossary::

   Code Coverage
      A measure of how much of the source code is executed during testing.

   Integration Test
      Tests that verify the interaction between multiple components or systems.

   Mock Object
      A simulated object that mimics the behavior of real objects in controlled ways.

   Test Context
      The environment and data required for executing a specific test.

   Test Fixture
      A fixed state of a set of objects used as a baseline for running tests.

   Unit Test
      Tests that verify the functionality of individual components in isolation.

Security Terms
==============

.. glossary::

   Dynamic Analysis
      Security analysis performed while the program is executing.

   Evasion Technique
      Methods used by malware to avoid detection by security systems.

   Runtime Analysis
      Analysis of software behavior during execution.

   Sandbox
      An isolated environment where potentially malicious code can be executed safely.

   Static Analysis
      Security analysis performed without executing the program.

   Threat Detection
      The process of identifying potential security threats or malicious activities.

   Vulnerability Assessment
      The process of identifying, quantifying, and prioritizing vulnerabilities in a system.

Android-Specific Terms
======================

.. glossary::

   Activity
      A single screen with a user interface in an Android application.

   Android Manifest
      An XML file that contains essential information about the application.

   Broadcast Receiver
      An Android component that responds to system-wide broadcast announcements.

   Content Provider
      An Android component that manages access to a structured set of app data.

   Intent
      A messaging object used to request an action from another app component.

   Logcat
      Android's logging system that provides a mechanism for collecting and viewing system debug output.

   Sensor Manager
      Android system service that provides access to device sensors.

   Service
      An Android component that performs long-running operations in the background.

   System Properties
      Key-value pairs that store system configuration and runtime information.

Development Terms
=================

.. glossary::

   Black
      A Python code formatter that automatically formats code according to PEP 8.

   Click
      A Python package for creating command-line interfaces.

   Continuous Integration (CI)
      The practice of automatically testing code changes.

   isort
      A Python utility for sorting imports alphabetically.

   Makefile
      A file containing a set of directives for building and managing projects.

   MyPy
      A static type checker for Python.

   pytest
      A Python testing framework.

   Read the Docs (RTD)
      A documentation hosting platform that builds and hosts documentation.

   Ruff
      A fast Python linter.

   Sphinx
      A documentation generation tool for Python projects.

   tox
      A tool for testing Python packages across multiple environments.

File Formats and Extensions
===========================

.. glossary::

   .apk
      Android Application Package file format.

   .md
      Markdown file extension for documentation.

   .rst
      reStructuredText file extension for Sphinx documentation.

   .toml
      Tom's Obvious, Minimal Language configuration file format.

   .ts
      TypeScript file extension.

   .yaml/.yml
      YAML Ain't Markup Language configuration file format.

Environment Variables
====================

.. glossary::

   ANDROID_HOME
      Environment variable pointing to the Android SDK installation directory.

   PATH
      System environment variable containing directories to search for executable files.

   PYTHONPATH
      Environment variable that augments the default search path for Python module files.