"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AndroidSensorHooks = void 0;
const types_1 = require("../types");
const utils_1 = require("../utils");
class AndroidSensorHooks {
    constructor(config) {
        this.config = config;
    }
    initialize() {
        this.hookSensorPower();
        this.hookSensorRange();
        this.hookSensorResolution();
        this.hookSensorManager();
    }
    hookSensorPower() {
        const sensorClass = utils_1.HookUtils.safeGetJavaClass('android.hardware.Sensor');
        if (!sensorClass)
            return;
        const originalGetPower = sensorClass.getPower;
        if (!originalGetPower)
            return;
        const config = this.config;
        sensorClass.getPower.implementation = function () {
            var _a, _b, _c, _d;
            const original = originalGetPower.call(this);
            const sensorType = this.getType();
            let fakeValue;
            let sensorName = 'unknown';
            switch (sensorType) {
                case types_1.SENSOR_TYPES.ACCELEROMETER:
                    fakeValue = (_a = config.accelerometer) === null || _a === void 0 ? void 0 : _a.power;
                    sensorName = 'accelerometer';
                    break;
                case types_1.SENSOR_TYPES.LIGHT:
                    fakeValue = (_b = config.light) === null || _b === void 0 ? void 0 : _b.power;
                    sensorName = 'light sensor';
                    break;
                case types_1.SENSOR_TYPES.MAGNETIC_FIELD:
                    fakeValue = (_c = config.magnetometer) === null || _c === void 0 ? void 0 : _c.power;
                    sensorName = 'magnetometer';
                    break;
                case types_1.SENSOR_TYPES.PRESSURE:
                    fakeValue = (_d = config.pressure) === null || _d === void 0 ? void 0 : _d.power;
                    sensorName = 'pressure sensor';
                    break;
            }
            if (fakeValue !== undefined) {
                utils_1.HookUtils.sendChangelog({
                    property: `${sensorName}_power`,
                    oldValue: original.toString(),
                    newValue: fakeValue.toString()
                });
                utils_1.HookUtils.sendInfo(`Hooked getPower() of android.hardware.Sensor and return ${fakeValue} instead of ${original} for ${sensorName}`);
                return fakeValue;
            }
            utils_1.HookUtils.sendDebug(`Hooked getPower() of android.hardware.Sensor and returned original value ${original}, sensorType=${sensorType} not configured`);
            return original;
        };
    }
    hookSensorRange() {
        const sensorClass = utils_1.HookUtils.safeGetJavaClass('android.hardware.Sensor');
        if (!sensorClass)
            return;
        const originalGetMaximumRange = sensorClass.getMaximumRange;
        if (!originalGetMaximumRange)
            return;
        const config = this.config;
        sensorClass.getMaximumRange.implementation = function () {
            var _a, _b;
            const original = originalGetMaximumRange.call(this);
            const sensorType = this.getType();
            let fakeValue;
            let sensorName = 'unknown';
            switch (sensorType) {
                case types_1.SENSOR_TYPES.ACCELEROMETER:
                    fakeValue = (_a = config.accelerometer) === null || _a === void 0 ? void 0 : _a.range;
                    sensorName = 'accelerometer';
                    break;
                case types_1.SENSOR_TYPES.MAGNETIC_FIELD:
                    fakeValue = (_b = config.magnetometer) === null || _b === void 0 ? void 0 : _b.range;
                    sensorName = 'magnetometer';
                    break;
            }
            if (fakeValue !== undefined) {
                utils_1.HookUtils.sendChangelog({
                    property: `${sensorName}_range`,
                    oldValue: original.toString(),
                    newValue: fakeValue.toString()
                });
                utils_1.HookUtils.sendInfo(`Hooked getMaximumRange() of android.hardware.Sensor and return ${fakeValue} instead of ${original} for ${sensorName}`);
                return fakeValue;
            }
            utils_1.HookUtils.sendDebug(`Hooked getMaximumRange() of android.hardware.Sensor and returned original value ${original}, sensorType=${sensorType} not configured`);
            return original;
        };
    }
    hookSensorResolution() {
        const sensorClass = utils_1.HookUtils.safeGetJavaClass('android.hardware.Sensor');
        if (!sensorClass)
            return;
        const originalGetResolution = sensorClass.getResolution;
        if (!originalGetResolution)
            return;
        const config = this.config;
        sensorClass.getResolution.implementation = function () {
            var _a, _b;
            const original = originalGetResolution.call(this);
            const sensorType = this.getType();
            let fakeValue;
            let sensorName = 'unknown';
            switch (sensorType) {
                case types_1.SENSOR_TYPES.ACCELEROMETER:
                    fakeValue = (_a = config.accelerometer) === null || _a === void 0 ? void 0 : _a.resolution;
                    sensorName = 'accelerometer';
                    break;
                case types_1.SENSOR_TYPES.PRESSURE:
                    fakeValue = (_b = config.pressure) === null || _b === void 0 ? void 0 : _b.resolution;
                    sensorName = 'pressure sensor';
                    break;
            }
            if (fakeValue !== undefined) {
                utils_1.HookUtils.sendChangelog({
                    property: `${sensorName}_resolution`,
                    oldValue: original.toString(),
                    newValue: fakeValue.toString()
                });
                utils_1.HookUtils.sendInfo(`Hooked getResolution() of android.hardware.Sensor and return ${fakeValue} instead of ${original} for ${sensorName}`);
                return fakeValue;
            }
            utils_1.HookUtils.sendDebug(`Hooked getResolution() of android.hardware.Sensor and returned original value ${original}, sensorType=${sensorType} not configured`);
            return original;
        };
    }
    hookSensorManager() {
        const sensorManagerClass = utils_1.HookUtils.safeGetJavaClass('android.hardware.SensorManager');
        if (!sensorManagerClass)
            return;
        const originalGetSensorList = sensorManagerClass.getSensorList;
        if (!originalGetSensorList)
            return;
        sensorManagerClass.getSensorList.implementation = function (type) {
            const original = originalGetSensorList.call(this, type);
            utils_1.HookUtils.sendDebug(`Hooked getSensorList(${type}) - returning original sensor list`);
            return original;
        };
    }
    getAccelerometerPowerValue() {
        var _a;
        return (_a = this.config.accelerometer) === null || _a === void 0 ? void 0 : _a.power;
    }
    getAccelerometerRangeValue() {
        var _a;
        return (_a = this.config.accelerometer) === null || _a === void 0 ? void 0 : _a.range;
    }
    getAccelerometerResolutionValue() {
        var _a;
        return (_a = this.config.accelerometer) === null || _a === void 0 ? void 0 : _a.resolution;
    }
    getLightPowerValue() {
        var _a;
        return (_a = this.config.light) === null || _a === void 0 ? void 0 : _a.power;
    }
    getMagnetometerPowerValue() {
        var _a;
        return (_a = this.config.magnetometer) === null || _a === void 0 ? void 0 : _a.power;
    }
    getMagnetometerRangeValue() {
        var _a;
        return (_a = this.config.magnetometer) === null || _a === void 0 ? void 0 : _a.range;
    }
    getPressurePowerValue() {
        var _a;
        return (_a = this.config.pressure) === null || _a === void 0 ? void 0 : _a.power;
    }
    getPressureResolutionValue() {
        var _a;
        return (_a = this.config.pressure) === null || _a === void 0 ? void 0 : _a.resolution;
    }
}
exports.AndroidSensorHooks = AndroidSensorHooks;
