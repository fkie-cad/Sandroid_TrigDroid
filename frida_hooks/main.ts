/**
 * Main Frida hook entry point for TrigDroid.
 * This file will be compiled to JavaScript and loaded by Frida.
 */

import { AndroidSensorHooks } from './hooks/android-sensors';
import { AndroidBuildHooks } from './hooks/android-build';
import { HookUtils } from './utils';

// Bypass hook imports
import { SSLUnpinningHooks, SSLUnpinningConfig } from './hooks/ssl-unpinning';
import { RootDetectionHooks, RootDetectionConfig } from './hooks/root-detection';
import { EmulatorDetectionHooks, EmulatorDetectionConfig } from './hooks/emulator-detection';
import { FridaDetectionHooks, FridaDetectionConfig } from './hooks/frida-detection';
import { DebugDetectionHooks, DebugDetectionConfig } from './hooks/debug-detection';

/**
 * Main hook configuration interface.
 * This will be populated by the Python configuration system.
 */
interface TrigDroidHookConfig {
    // Sensor configuration
    sensors?: {
        accelerometer?: {
            power?: number;
            range?: number;
            resolution?: number;
        };
        light?: {
            power?: number;
        };
        magnetometer?: {
            power?: number;
            range?: number;
        };
        pressure?: {
            power?: number;
            resolution?: number;
        };
    };

    // Build properties configuration
    build?: {
        board?: string;
        brand?: string;
        cpu_abi?: string;
        cpu_abi2?: string;
        device?: string;
        fingerprint?: string;
        hardware?: string;
        host?: string;
        id?: string;
        manufacturer?: string;
        model?: string;
        product?: string;
        radio?: string;
        serial?: string;
        tags?: string;
        user?: string;
    };

    // Settings configuration
    settings?: {
        adb_enabled?: string;
    };

    // Time manipulation configuration
    time?: {
        uptime_add_minutes?: number;
        date_offset_seconds?: number;
    };

    // Thread manipulation configuration  
    thread?: {
        sleep_max_allowed_ms?: number;
        update_date_on_sleep?: boolean;
    };

    // Handler configuration
    handler?: {
        post_delayed_max_allowed_ms?: number;
    };

    // Input method configuration
    inputMethod?: {
        remove_regex?: string;
    };

    // Network configuration
    network?: {
        ipv4_replacements?: Array<{
            pattern: string;
            old: Array<{min: string; max: string}>;
            new: Array<string | 'x'>;
        }>;
        ipv6_replacements?: Array<{
            pattern: string;
            old: Array<{min: string; max: string}>;
            new: Array<string | 'x'>;
        }>;
    };

    // Parcel configuration
    parcel?: {
        strings_to_hide?: string[];
        fake_strings?: string[];
    };

    // Bluetooth configuration
    bluetooth?: {
        available?: boolean;
        mac_address?: string;
    };

    // NFC configuration
    nfc?: {
        available?: boolean;
    };

    // Telephony configuration
    telephony?: {
        sim_country_iso?: string;
        network_country_iso?: string;
        line1_number?: string;
        network_type?: number;
        network_operator?: string;
        network_operator_name?: string;
        device_id?: string;
        device_id2?: string;
        phone_type?: number;
        sim_serial_number?: string;
        subscriber_id?: string;
        voice_mail_number?: string;
        data_network_type?: number;
    };

    // Security bypass configuration
    // For authorized security testing and research purposes only
    bypass?: {
        ssl_unpinning?: SSLUnpinningConfig;
        root_detection?: RootDetectionConfig;
        emulator_detection?: EmulatorDetectionConfig;
        frida_detection?: FridaDetectionConfig;
        debug_detection?: DebugDetectionConfig;
    };
}

/**
 * Main hook initialization function.
 * This is called when the script is loaded by Frida.
 */
function initializeHooks(config: TrigDroidHookConfig): void {
    HookUtils.sendInfo('TrigDroid Frida hooks initializing...');

    try {
        // Initialize sensor hooks
        if (config.sensors) {
            const sensorHooks = new AndroidSensorHooks(config.sensors);
            sensorHooks.initialize();
        }

        // Initialize build property hooks
        if (config.build) {
            const buildHooks = new AndroidBuildHooks(config.build);
            buildHooks.initialize();
        }

        // Initialize security bypass hooks
        // These are for authorized security testing and research purposes only
        if (config.bypass) {
            const bypassConfig = config.bypass;

            // SSL/TLS Unpinning - bypass certificate pinning
            if (bypassConfig.ssl_unpinning?.enabled) {
                HookUtils.sendInfo('Loading SSL unpinning bypass hooks...');
                const sslHooks = new SSLUnpinningHooks(bypassConfig.ssl_unpinning);
                sslHooks.initialize();
            }

            // Root Detection Bypass - hide root indicators
            if (bypassConfig.root_detection?.enabled) {
                HookUtils.sendInfo('Loading root detection bypass hooks...');
                const rootHooks = new RootDetectionHooks(bypassConfig.root_detection);
                rootHooks.initialize();
            }

            // Emulator Detection Bypass - spoof device properties
            if (bypassConfig.emulator_detection?.enabled) {
                HookUtils.sendInfo('Loading emulator detection bypass hooks...');
                const emulatorHooks = new EmulatorDetectionHooks(bypassConfig.emulator_detection);
                emulatorHooks.initialize();
            }

            // Frida Detection Bypass - hide Frida presence
            // Note: Most effective in SPAWN mode as detection often occurs at startup
            if (bypassConfig.frida_detection?.enabled) {
                HookUtils.sendInfo('Loading Frida detection bypass hooks...');
                const fridaHooks = new FridaDetectionHooks(bypassConfig.frida_detection);
                fridaHooks.initialize();
            }

            // Debug Detection Bypass - hide debugger presence
            if (bypassConfig.debug_detection?.enabled) {
                HookUtils.sendInfo('Loading debug detection bypass hooks...');
                const debugHooks = new DebugDetectionHooks(bypassConfig.debug_detection);
                debugHooks.initialize();
            }
        }

        HookUtils.sendInfo('TrigDroid Frida hooks initialized successfully');
    } catch (error) {
        HookUtils.sendDebug(`Failed to initialize hooks: ${error}`);
    }
}

/**
 * Frida Java.perform wrapper with error handling.
 */
Java.perform(() => {
    try {
        Java.deoptimizeEverything();
        
        // Configuration will be injected by the Python system
        // For now, using placeholder configuration
        const config: TrigDroidHookConfig = {
            // This will be replaced by the actual configuration from Python
        };

        initializeHooks(config);
    } catch (error) {
        send(`Critical error in Frida hooks: ${error}`);
    }
});