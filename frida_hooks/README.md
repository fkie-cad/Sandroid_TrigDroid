# TrigDroid Frida Hooks (TypeScript)

This directory contains the TypeScript implementation of Frida hooks for TrigDroid, providing type-safe Android runtime instrumentation.

## Overview

The hooks have been refactored from the original JavaScript implementation to TypeScript following SOLID principles:

- **Single Responsibility**: Each hook class handles one specific Android API area
- **Open/Closed**: Easy to extend with new hook types without modifying existing code  
- **Liskov Substitution**: All hooks implement common interfaces
- **Interface Segregation**: Focused interfaces for different hook categories
- **Dependency Inversion**: Hooks depend on abstractions, not concrete implementations

## Structure

```
frida-hooks/
├── types.ts              # TypeScript type definitions for Frida and Android APIs
├── utils.ts               # Utility functions for common hook operations
├── hooks/                 # Individual hook implementations
│   ├── android-sensors.ts # Sensor API hooks
│   ├── android-build.ts   # Build property hooks
│   └── ...               # Additional hook modules
├── main.ts               # Main entry point (compiled to JavaScript)
├── package.json          # Node.js package configuration
├── tsconfig.json         # TypeScript compiler configuration
└── README.md             # This file
```

## Building

1. Install dependencies:
```bash
npm install
```

2. Compile TypeScript to JavaScript:
```bash
npm run build
```

3. The compiled JavaScript will be output to `dist/main.js` - this is the file loaded by Frida.

## Development

- Use `npm run watch` for continuous compilation during development
- Use `npm run rebuild` to clean and rebuild everything

## Hook Configuration

Hooks are configured through the Python configuration system, which injects values into the TypeScript configuration interface. The main configuration object includes:

- **sensors**: Accelerometer, gyroscope, light, pressure sensor manipulation
- **build**: Android Build property spoofing  
- **telephony**: Phone and SIM information hooks
- **network**: IP address manipulation
- **bluetooth**: Bluetooth adapter hooks
- **time**: Date/time manipulation
- **thread**: Sleep and timing hooks

## Key Features

- **Type Safety**: Full TypeScript types for Frida and Android APIs
- **Error Handling**: Comprehensive error handling with proper logging
- **Configuration**: Template-based configuration injection from Python
- **Modularity**: Each Android API area has its own hook class
- **Logging**: Structured logging back to the host application
- **Changelog**: Automatic change tracking for all device modifications

## Integration

The compiled JavaScript is loaded by the `FridaTestRunner` in the Python codebase. The Python system:

1. Generates configuration based on command-line options
2. Injects configuration into the compiled hook script
3. Loads the script via Frida for runtime instrumentation

## Security Note

These hooks are designed for **defensive security research only**. They enable analysts to:

- Test malware behavior under different device conditions
- Analyze anti-analysis evasion techniques  
- Understand trigger mechanisms in malicious applications

**Do not use these hooks to enhance malicious capabilities.**