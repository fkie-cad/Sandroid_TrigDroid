# TrigDroid Frida Hooks (TypeScript)

This directory contains the TypeScript implementation of Frida hooks for TrigDroid, providing type-safe Android runtime instrumentation.

## Overview

The hooks have been refactored from the original JavaScript implementation to TypeScript following SOLID principles:

- **Single Responsibility**: Each hook class handles one specific Android API area
- **Open/Closed**: Easy to extend with new hook types without modifying existing code
- **Liskov Substitution**: All hooks implement common interfaces
- **Interface Segregation**: Focused interfaces for different hook categories
- **Dependency Inversion**: Hooks depend on abstractions, not concrete implementations

## Directory Structure

```
frida_hooks/
├── types.ts                    # TypeScript type definitions for Frida and Android APIs
├── utils.ts                    # Utility functions (HookUtils class)
├── main.ts                     # Main entry point with configuration-based initialization
├── trigdroid_bypass_rpc.ts     # Unified bypass script with RPC exports
├── hooks/                      # Individual hook implementations
│   ├── ssl-unpinning.ts        # SSL/TLS certificate pinning bypass
│   ├── root-detection.ts       # Root/su detection bypass
│   ├── frida-detection.ts      # Frida detection bypass
│   ├── emulator-detection.ts   # Emulator detection bypass
│   ├── debug-detection.ts      # Debug detection bypass
│   ├── android-build.ts        # Android Build property manipulation
│   └── android-sensors.ts      # Android sensor data manipulation
├── package.json                # Node.js package configuration
├── tsconfig.json               # TypeScript compiler configuration (main)
├── tsconfig.bypass.json        # TypeScript compiler configuration (bypass)
└── README.md                   # This file
```

## Prerequisites

- **Node.js** >= 16.0.0
- **npm** (comes with Node.js)
- **frida-tools** (Python package for `frida-compile`)

```bash
# it is recommend that you are doing that from a venv (e.g. python3 -m venv env )
# Install frida-tools for frida-compile
pip install frida-tools
```

## Building

### Quick Build (Recommended)

```bash
# Install dependencies
npm install

# Build everything (main hooks + bypass script)
npm run build:all
```

### Build Commands

| Command | Description |
|---------|-------------|
| `npm run build` | Compile TypeScript and bundle main.js |
| `npm run build:bypass` | Compile and bundle bypass script |
| `npm run build:all` | Build both main and bypass scripts |
| `npm run watch` | Watch mode for development |
| `npm run clean` | Remove all compiled files |
| `npm run rebuild` | Clean and rebuild everything |

### Build Process Details

The build process involves multiple steps:

1. **TypeScript Compilation** (`tsc`): Compiles `.ts` files to `.js` in `dist/`
2. **Bundling** (`frida-compile`): Bundles scripts into self-contained files
3. **Copy to Package** (`copy-to-package`): Copies compiled scripts to Python package

#### Main Build (`npm run build`)
```bash
tsc                                              # Compile TypeScript
frida-compile dist/main.js -o dist/main_bundle.js  # Bundle main script
cp dist/*.js ../src/trigdroid/scripts/           # Copy to Python package
cp -r dist/hooks ../src/trigdroid/scripts/       # Copy hooks directory
```

#### Bypass Build (`npm run build:bypass`)
```bash
tsc -p tsconfig.bypass.json                      # Compile with bypass config
frida-compile dist/trigdroid_bypass_rpc.js \
  -o dist/trigdroid_bypass_bundle.js             # Bundle bypass script
cp dist/*.js ../src/trigdroid/scripts/           # Copy to Python package
cp -r dist/hooks ../src/trigdroid/scripts/       # Copy hooks directory
```

### Output Files

After building, the following files are created:

**In `dist/` directory:**
```
dist/
├── main.js                      # Compiled main script (unbundled)
├── main_bundle.js               # Bundled main script (self-contained, ~154KB)
├── trigdroid_bypass_rpc.js      # Compiled bypass script (unbundled)
├── trigdroid_bypass_bundle.js   # Bundled bypass script (self-contained, ~131KB)
├── types.js                     # Compiled types
├── utils.js                     # Compiled utilities
└── hooks/                       # Compiled individual hooks
    ├── ssl-unpinning.js
    ├── root-detection.js
    ├── frida-detection.js
    ├── emulator-detection.js
    ├── debug-detection.js
    ├── android-build.js
    └── android-sensors.js
```

**Copied to Python package (`src/trigdroid/scripts/`):**
- All `.js` files from `dist/`
- Complete `hooks/` directory

## Development

### Watch Mode

For continuous compilation during development:

```bash
npm run watch
```

Note: Watch mode only runs TypeScript compilation. You'll need to manually run bundling and copy steps after changes.

### Adding a New Hook

1. Create a new file in `hooks/`:
```typescript
// hooks/my-custom-hook.ts
import { HookUtils } from '../utils';

export class MyCustomHooks {
    private config: MyCustomConfig;

    constructor(config: MyCustomConfig) {
        this.config = config;
    }

    public initialize(): void {
        this.hookMyAPI();
    }

    private hookMyAPI(): void {
        const MyClass = HookUtils.safeGetJavaClass('com.example.MyClass');
        if (!MyClass) return;

        MyClass.myMethod.implementation = function() {
            HookUtils.sendInfo('Hooked myMethod');
            // Your hook logic here
            return this.myMethod();
        };
    }
}
```

2. Export from `main.ts` if needed for configuration-based initialization
3. Rebuild: `npm run build:all`

## Bypass Script (RPC Mode)

The bypass script (`trigdroid_bypass_rpc.ts`) provides runtime-controllable bypass functionality via Frida RPC exports.

### RPC Exports

| Export | Description |
|--------|-------------|
| `enableSSLUnpinning(config?)` | Enable SSL/TLS certificate pinning bypass |
| `enableRootBypass(config?)` | Enable root detection bypass |
| `enableEmulatorBypass(config?)` | Enable emulator detection bypass |
| `enableFridaBypass(config?)` | Enable Frida detection bypass |
| `enableDebugBypass(config?)` | Enable debug detection bypass |
| `enableBypasses(config)` | Batch enable multiple bypasses |
| `getStatus()` | Get current bypass status |
| `getDeviceProfiles()` | Get available device profiles for emulator bypass |

### Using from Python

```python
import frida

# Load the bypass script
with open(get_bypass_script_path()) as f:
    script_source = f.read()

script = session.create_script(script_source)
script.load()

# Enable bypasses via RPC
script.exports_sync.enableSSLUnpinning()
script.exports_sync.enableRootBypass()

# Or batch enable
script.exports_sync.enableBypasses({
    'ssl': True,
    'root': True,
    'emulator': {'device_profile': 'pixel_6_pro'}
})

# Check status
status = script.exports_sync.getStatus()
print(f"SSL unpinning active: {status['ssl_unpinning']}")
```

### Using with Objection

```bash
# Load bypass script with objection
objection -g com.example.app explore -s /path/to/trigdroid_bypass_bundle.js
```

## Hook Configuration

Hooks are configured through the Python configuration system, which injects values into the TypeScript configuration interface.

### Main Script Configuration

The main script (`main.ts`) accepts a configuration object:

```typescript
interface TrigDroidHookConfig {
    sensors?: {
        accelerometer?: { power?: number; range?: number; resolution?: number; };
        light?: { power?: number; };
        magnetometer?: { power?: number; range?: number; };
        pressure?: { power?: number; resolution?: number; };
    };
    build?: {
        board?: string;
        brand?: string;
        device?: string;
        fingerprint?: string;
        manufacturer?: string;
        model?: string;
        product?: string;
        // ... more Build properties
    };
    bypass?: {
        ssl_unpinning?: { enabled: boolean; /* config */ };
        root_detection?: { enabled: boolean; /* config */ };
        emulator_detection?: { enabled: boolean; device_profile?: string; };
        frida_detection?: { enabled: boolean; /* config */ };
        debug_detection?: { enabled: boolean; /* config */ };
    };
    // ... additional configuration sections
}
```

## Key Features

- **Type Safety**: Full TypeScript types for Frida and Android APIs
- **Error Handling**: Comprehensive error handling with proper logging
- **Configuration**: Template-based configuration injection from Python
- **Modularity**: Each Android API area has its own hook class
- **Logging**: Structured logging back to the host application via `HookUtils.sendInfo/sendDebug`
- **Changelog**: Automatic change tracking for all device modifications via `HookUtils.sendChangelog`

## Integration with Python

The compiled JavaScript is integrated with the Python package via the `trigdroid.scripts` module:

```python
from trigdroid.scripts import (
    get_bypass_script_path,    # Get bypass script path
    get_main_script_path,      # Get main script path (bundled by default)
    get_hook_script_path,      # Get individual hook script path
    list_available_scripts,    # List all available scripts
    list_available_hooks,      # List available hook names
    read_script,               # Read script contents as string
)

# Example: Load bypass script with Frida
bypass_path = get_bypass_script_path()
with open(bypass_path) as f:
    script = session.create_script(f.read())

# Example: Get individual hook
ssl_hook_path = get_hook_script_path("ssl-unpinning")
```

## Security Note

These hooks are designed for **defensive security research only**. They enable analysts to:

- Test malware behavior under different device conditions
- Analyze anti-analysis evasion techniques
- Understand trigger mechanisms in malicious applications

**Do not use these hooks to enhance malicious capabilities.**

## Troubleshooting

### TypeScript Compilation Errors

```bash
# Clear and rebuild
npm run rebuild

# Check TypeScript version
npx tsc --version  # Should be 5.x
```

### frida-compile Not Found

```bash
# Install frida-tools
pip install frida-tools

# Verify installation
which frida-compile
```

### Bundling Fails

```bash
# Check frida-compile version
frida-compile --version

# Try manual bundling
frida-compile dist/main.js -o dist/main_bundle.js
```

### Scripts Not Found in Python

```bash
# Rebuild and copy to package
npm run rebuild

# Verify scripts exist
ls -la ../src/trigdroid/scripts/
ls -la ../src/trigdroid/scripts/hooks/
```
