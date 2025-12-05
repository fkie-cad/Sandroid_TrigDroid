"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const utils_1 = require("./utils");
const ssl_unpinning_1 = require("./hooks/ssl-unpinning");
const root_detection_1 = require("./hooks/root-detection");
const frida_detection_1 = require("./hooks/frida-detection");
const emulator_detection_1 = require("./hooks/emulator-detection");
const debug_detection_1 = require("./hooks/debug-detection");
let sslHooks = null;
let rootHooks = null;
let fridaHooks = null;
let emulatorHooks = null;
let debugHooks = null;
const loadedAt = new Date().toISOString();
rpc.exports = {
    enableSSLUnpinning: function (config) {
        if (sslHooks !== null) {
            return { status: 'already_enabled', type: 'ssl_unpinning' };
        }
        try {
            Java.perform(() => {
                sslHooks = new ssl_unpinning_1.SSLUnpinningHooks(Object.assign({ enabled: true }, config));
                sslHooks.initialize();
            });
            return { status: 'enabled', type: 'ssl_unpinning' };
        }
        catch (e) {
            return { status: 'error', type: 'ssl_unpinning', message: String(e) };
        }
    },
    enableRootBypass: function (config) {
        if (rootHooks !== null) {
            return { status: 'already_enabled', type: 'root_detection' };
        }
        try {
            Java.perform(() => {
                rootHooks = new root_detection_1.RootDetectionHooks(Object.assign({ enabled: true }, config));
                rootHooks.initialize();
            });
            return { status: 'enabled', type: 'root_detection' };
        }
        catch (e) {
            return { status: 'error', type: 'root_detection', message: String(e) };
        }
    },
    enableFridaBypass: function (config) {
        if (fridaHooks !== null) {
            return { status: 'already_enabled', type: 'frida_detection' };
        }
        try {
            Java.perform(() => {
                fridaHooks = new frida_detection_1.FridaDetectionHooks(Object.assign({ enabled: true }, config));
                fridaHooks.initialize();
            });
            return { status: 'enabled', type: 'frida_detection' };
        }
        catch (e) {
            return { status: 'error', type: 'frida_detection', message: String(e) };
        }
    },
    enableEmulatorBypass: function (config) {
        if (emulatorHooks !== null) {
            return { status: 'already_enabled', type: 'emulator_detection' };
        }
        try {
            Java.perform(() => {
                emulatorHooks = new emulator_detection_1.EmulatorDetectionHooks(Object.assign({ enabled: true }, config));
                emulatorHooks.initialize();
            });
            return { status: 'enabled', type: 'emulator_detection' };
        }
        catch (e) {
            return { status: 'error', type: 'emulator_detection', message: String(e) };
        }
    },
    enableDebugBypass: function (config) {
        if (debugHooks !== null) {
            return { status: 'already_enabled', type: 'debug_detection' };
        }
        try {
            Java.perform(() => {
                debugHooks = new debug_detection_1.DebugDetectionHooks(Object.assign({ enabled: true }, config));
                debugHooks.initialize();
            });
            return { status: 'enabled', type: 'debug_detection' };
        }
        catch (e) {
            return { status: 'error', type: 'debug_detection', message: String(e) };
        }
    },
    enableBypasses: function (config) {
        const results = [];
        if (config.ssl) {
            const sslConfig = typeof config.ssl === 'boolean' ? {} : config.ssl;
            results.push(rpc.exports.enableSSLUnpinning(sslConfig));
        }
        if (config.root) {
            const rootConfig = typeof config.root === 'boolean' ? {} : config.root;
            results.push(rpc.exports.enableRootBypass(rootConfig));
        }
        if (config.frida) {
            const fridaConfig = typeof config.frida === 'boolean' ? {} : config.frida;
            results.push(rpc.exports.enableFridaBypass(fridaConfig));
        }
        if (config.emulator) {
            const emulatorConfig = typeof config.emulator === 'boolean' ? {} : config.emulator;
            results.push(rpc.exports.enableEmulatorBypass(emulatorConfig));
        }
        if (config.debug) {
            const debugConfig = typeof config.debug === 'boolean' ? {} : config.debug;
            results.push(rpc.exports.enableDebugBypass(debugConfig));
        }
        return results;
    },
    getStatus: function () {
        return {
            ssl_unpinning: sslHooks !== null,
            root_detection: rootHooks !== null,
            frida_detection: fridaHooks !== null,
            emulator_detection: emulatorHooks !== null,
            debug_detection: debugHooks !== null,
            loaded_at: loadedAt,
        };
    },
    getDeviceProfiles: function () {
        return ['pixel_4_xl', 'pixel_6_pro', 'samsung_s21', 'oneplus_9', 'generic'];
    },
    isSpawnMode: function () {
        try {
            const ActivityThread = Java.use('android.app.ActivityThread');
            const currentApp = ActivityThread.currentApplication();
            return currentApp === null;
        }
        catch (e) {
            return false;
        }
    },
    getVersion: function () {
        return {
            script: 'trigdroid_bypass_rpc',
            version: '1.0.0',
            loadedAt: loadedAt,
        };
    },
};
send('TrigDroid bypass script loaded (RPC mode) - awaiting configuration via RPC exports');
utils_1.HookUtils.sendInfo('Available RPC methods: enableSSLUnpinning, enableRootBypass, enableFridaBypass, enableEmulatorBypass, enableDebugBypass, enableBypasses, getStatus');
