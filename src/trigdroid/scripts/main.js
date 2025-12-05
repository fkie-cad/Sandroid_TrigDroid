"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const android_sensors_1 = require("./hooks/android-sensors");
const android_build_1 = require("./hooks/android-build");
const utils_1 = require("./utils");
const ssl_unpinning_1 = require("./hooks/ssl-unpinning");
const root_detection_1 = require("./hooks/root-detection");
const emulator_detection_1 = require("./hooks/emulator-detection");
const frida_detection_1 = require("./hooks/frida-detection");
const debug_detection_1 = require("./hooks/debug-detection");
function initializeHooks(config) {
    var _a, _b, _c, _d, _e;
    utils_1.HookUtils.sendInfo('TrigDroid Frida hooks initializing...');
    try {
        if (config.sensors) {
            const sensorHooks = new android_sensors_1.AndroidSensorHooks(config.sensors);
            sensorHooks.initialize();
        }
        if (config.build) {
            const buildHooks = new android_build_1.AndroidBuildHooks(config.build);
            buildHooks.initialize();
        }
        if (config.bypass) {
            const bypassConfig = config.bypass;
            if ((_a = bypassConfig.ssl_unpinning) === null || _a === void 0 ? void 0 : _a.enabled) {
                utils_1.HookUtils.sendInfo('Loading SSL unpinning bypass hooks...');
                const sslHooks = new ssl_unpinning_1.SSLUnpinningHooks(bypassConfig.ssl_unpinning);
                sslHooks.initialize();
            }
            if ((_b = bypassConfig.root_detection) === null || _b === void 0 ? void 0 : _b.enabled) {
                utils_1.HookUtils.sendInfo('Loading root detection bypass hooks...');
                const rootHooks = new root_detection_1.RootDetectionHooks(bypassConfig.root_detection);
                rootHooks.initialize();
            }
            if ((_c = bypassConfig.emulator_detection) === null || _c === void 0 ? void 0 : _c.enabled) {
                utils_1.HookUtils.sendInfo('Loading emulator detection bypass hooks...');
                const emulatorHooks = new emulator_detection_1.EmulatorDetectionHooks(bypassConfig.emulator_detection);
                emulatorHooks.initialize();
            }
            if ((_d = bypassConfig.frida_detection) === null || _d === void 0 ? void 0 : _d.enabled) {
                utils_1.HookUtils.sendInfo('Loading Frida detection bypass hooks...');
                const fridaHooks = new frida_detection_1.FridaDetectionHooks(bypassConfig.frida_detection);
                fridaHooks.initialize();
            }
            if ((_e = bypassConfig.debug_detection) === null || _e === void 0 ? void 0 : _e.enabled) {
                utils_1.HookUtils.sendInfo('Loading debug detection bypass hooks...');
                const debugHooks = new debug_detection_1.DebugDetectionHooks(bypassConfig.debug_detection);
                debugHooks.initialize();
            }
        }
        utils_1.HookUtils.sendInfo('TrigDroid Frida hooks initialized successfully');
    }
    catch (error) {
        utils_1.HookUtils.sendDebug(`Failed to initialize hooks: ${error}`);
    }
}
Java.perform(() => {
    try {
        Java.deoptimizeEverything();
        const config = {};
        initializeHooks(config);
    }
    catch (error) {
        send(`Critical error in Frida hooks: ${error}`);
    }
});
