/**
 * TrigDroid Unified Bypass Script with RPC Controls.
 *
 * This script provides a single entry point for all bypass hooks with runtime
 * RPC controls. Instead of loading multiple pre-compiled variants, this script
 * exposes RPC exports to enable/disable individual bypass categories at runtime.
 *
 * For authorized security testing and research purposes only.
 *
 * Usage:
 *   Load this script once, then use RPC calls to enable bypasses:
 *   - script.exports.enableSSLUnpinning({})
 *   - script.exports.enableRootBypass({})
 *   - script.exports.enableEmulatorBypass({ device_profile: 'pixel_6_pro' })
 *   - script.exports.enableFridaBypass({})
 *   - script.exports.enableDebugBypass({})
 *   - script.exports.enableBypasses({ ssl: true, root: true, emulator: { profile: 'pixel_4_xl' } })
 */

import { HookUtils } from './utils';
import { SSLUnpinningHooks, SSLUnpinningConfig } from './hooks/ssl-unpinning';
import { RootDetectionHooks, RootDetectionConfig } from './hooks/root-detection';
import { FridaDetectionHooks, FridaDetectionConfig } from './hooks/frida-detection';
import { EmulatorDetectionHooks, EmulatorDetectionConfig } from './hooks/emulator-detection';
import { DebugDetectionHooks, DebugDetectionConfig } from './hooks/debug-detection';

// Singleton instances - lazy initialized
let sslHooks: SSLUnpinningHooks | null = null;
let rootHooks: RootDetectionHooks | null = null;
let fridaHooks: FridaDetectionHooks | null = null;
let emulatorHooks: EmulatorDetectionHooks | null = null;
let debugHooks: DebugDetectionHooks | null = null;

/**
 * Result interface for bypass operations.
 */
interface BypassResult {
    status: 'enabled' | 'already_enabled' | 'error';
    type: string;
    message?: string;
}

/**
 * Configuration for batch bypass enabling.
 */
interface BatchBypassConfig {
    ssl?: boolean | SSLUnpinningConfig;
    root?: boolean | RootDetectionConfig;
    frida?: boolean | FridaDetectionConfig;
    emulator?: boolean | EmulatorDetectionConfig;
    debug?: boolean | DebugDetectionConfig;
}

/**
 * Status of all bypass hooks.
 */
interface BypassStatus {
    ssl_unpinning: boolean;
    root_detection: boolean;
    frida_detection: boolean;
    emulator_detection: boolean;
    debug_detection: boolean;
    loaded_at?: string;
}

// Track when script was loaded
const loadedAt = new Date().toISOString();

// RPC Exports
rpc.exports = {
    /**
     * Enable SSL unpinning bypass hooks.
     * @param config Optional SSL unpinning configuration
     */
    enableSSLUnpinning: function(config?: SSLUnpinningConfig): BypassResult {
        if (sslHooks !== null) {
            return { status: 'already_enabled', type: 'ssl_unpinning' };
        }

        try {
            Java.perform(() => {
                sslHooks = new SSLUnpinningHooks({ enabled: true, ...config });
                sslHooks.initialize();
            });
            return { status: 'enabled', type: 'ssl_unpinning' };
        } catch (e) {
            return { status: 'error', type: 'ssl_unpinning', message: String(e) };
        }
    },

    /**
     * Enable root detection bypass hooks.
     * @param config Optional root detection bypass configuration
     */
    enableRootBypass: function(config?: RootDetectionConfig): BypassResult {
        if (rootHooks !== null) {
            return { status: 'already_enabled', type: 'root_detection' };
        }

        try {
            Java.perform(() => {
                rootHooks = new RootDetectionHooks({ enabled: true, ...config });
                rootHooks.initialize();
            });
            return { status: 'enabled', type: 'root_detection' };
        } catch (e) {
            return { status: 'error', type: 'root_detection', message: String(e) };
        }
    },

    /**
     * Enable Frida detection bypass hooks.
     * NOTE: For best results, this should be enabled in SPAWN mode.
     * @param config Optional Frida detection bypass configuration
     */
    enableFridaBypass: function(config?: FridaDetectionConfig): BypassResult {
        if (fridaHooks !== null) {
            return { status: 'already_enabled', type: 'frida_detection' };
        }

        try {
            Java.perform(() => {
                fridaHooks = new FridaDetectionHooks({ enabled: true, ...config });
                fridaHooks.initialize();
            });
            return { status: 'enabled', type: 'frida_detection' };
        } catch (e) {
            return { status: 'error', type: 'frida_detection', message: String(e) };
        }
    },

    /**
     * Enable emulator detection bypass hooks.
     * @param config Optional emulator detection bypass configuration with device profile
     */
    enableEmulatorBypass: function(config?: EmulatorDetectionConfig): BypassResult {
        if (emulatorHooks !== null) {
            return { status: 'already_enabled', type: 'emulator_detection' };
        }

        try {
            Java.perform(() => {
                emulatorHooks = new EmulatorDetectionHooks({ enabled: true, ...config });
                emulatorHooks.initialize();
            });
            return { status: 'enabled', type: 'emulator_detection' };
        } catch (e) {
            return { status: 'error', type: 'emulator_detection', message: String(e) };
        }
    },

    /**
     * Enable debug detection bypass hooks.
     * @param config Optional debug detection bypass configuration
     */
    enableDebugBypass: function(config?: DebugDetectionConfig): BypassResult {
        if (debugHooks !== null) {
            return { status: 'already_enabled', type: 'debug_detection' };
        }

        try {
            Java.perform(() => {
                debugHooks = new DebugDetectionHooks({ enabled: true, ...config });
                debugHooks.initialize();
            });
            return { status: 'enabled', type: 'debug_detection' };
        } catch (e) {
            return { status: 'error', type: 'debug_detection', message: String(e) };
        }
    },

    /**
     * Enable multiple bypasses at once.
     * @param config Object specifying which bypasses to enable
     */
    enableBypasses: function(config: BatchBypassConfig): BypassResult[] {
        const results: BypassResult[] = [];

        if (config.ssl) {
            const sslConfig = typeof config.ssl === 'boolean' ? {} : config.ssl;
            results.push(rpc.exports.enableSSLUnpinning(sslConfig) as BypassResult);
        }

        if (config.root) {
            const rootConfig = typeof config.root === 'boolean' ? {} : config.root;
            results.push(rpc.exports.enableRootBypass(rootConfig) as BypassResult);
        }

        if (config.frida) {
            const fridaConfig = typeof config.frida === 'boolean' ? {} : config.frida;
            results.push(rpc.exports.enableFridaBypass(fridaConfig) as BypassResult);
        }

        if (config.emulator) {
            const emulatorConfig = typeof config.emulator === 'boolean' ? {} : config.emulator;
            results.push(rpc.exports.enableEmulatorBypass(emulatorConfig) as BypassResult);
        }

        if (config.debug) {
            const debugConfig = typeof config.debug === 'boolean' ? {} : config.debug;
            results.push(rpc.exports.enableDebugBypass(debugConfig) as BypassResult);
        }

        return results;
    },

    /**
     * Get status of all bypass hooks.
     */
    getStatus: function(): BypassStatus {
        return {
            ssl_unpinning: sslHooks !== null,
            root_detection: rootHooks !== null,
            frida_detection: fridaHooks !== null,
            emulator_detection: emulatorHooks !== null,
            debug_detection: debugHooks !== null,
            loaded_at: loadedAt,
        };
    },

    /**
     * Get list of available device profiles for emulator bypass.
     */
    getDeviceProfiles: function(): string[] {
        return ['pixel_4_xl', 'pixel_6_pro', 'samsung_s21', 'oneplus_9', 'generic'];
    },

    /**
     * Check if running in spawn mode (recommended for some bypasses).
     */
    isSpawnMode: function(): boolean {
        // Heuristic: in spawn mode, the app hasn't fully initialized yet
        try {
            const ActivityThread = Java.use('android.app.ActivityThread');
            const currentApp = ActivityThread.currentApplication();
            return currentApp === null;
        } catch (e) {
            return false;
        }
    },

    /**
     * Get version information.
     */
    getVersion: function(): object {
        return {
            script: 'trigdroid_bypass_rpc',
            version: '1.0.0',
            loadedAt: loadedAt,
        };
    },
};

// Notify that the script is loaded and ready for RPC calls
send('TrigDroid bypass script loaded (RPC mode) - awaiting configuration via RPC exports');
HookUtils.sendInfo('Available RPC methods: enableSSLUnpinning, enableRootBypass, enableFridaBypass, enableEmulatorBypass, enableDebugBypass, enableBypasses, getStatus');
