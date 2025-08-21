/**
 * Main Frida hook entry point for TrigDroid.
 * This file will be compiled to JavaScript and loaded by Frida.
 */

import { AndroidSensorHooks } from './hooks/android-sensors';
import { AndroidBuildHooks } from './hooks/android-build';
import { HookUtils } from './utils';

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

        // Initialize other hooks as needed
        // TODO: Add more hook modules here

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