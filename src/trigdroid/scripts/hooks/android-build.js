"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AndroidBuildHooks = void 0;
const utils_1 = require("../utils");
class AndroidBuildHooks {
    constructor(config) {
        this.config = config;
    }
    initialize() {
        this.hookBuildProperties();
    }
    hookBuildProperties() {
        const buildClass = utils_1.HookUtils.safeGetJavaClass('android.os.Build');
        if (!buildClass)
            return;
        try {
            buildClass.$new();
        }
        catch (error) {
            utils_1.HookUtils.sendDebug(`Could not create Build instance: ${error}`);
        }
        Java.choose('android.os.Build', {
            onMatch: (instance) => {
                utils_1.HookUtils.sendInfo('Hooked android.os.Build');
                this.hookBuildInstance(instance);
            },
            onComplete: () => {
                utils_1.HookUtils.sendInfo('Hooked all instances of android.os.Build');
            }
        });
    }
    hookBuildInstance(instance) {
        const fakeSupportedAbis = [];
        this.hookProperty(instance, 'BOARD', this.config.board);
        this.hookProperty(instance, 'BRAND', this.config.brand);
        this.hookOptionalProperty(instance, 'CPU_ABI', this.config.cpu_abi, 4, fakeSupportedAbis);
        this.hookOptionalProperty(instance, 'CPU_ABI2', this.config.cpu_abi2, 8, fakeSupportedAbis);
        this.hookProperty(instance, 'DEVICE', this.config.device);
        this.hookProperty(instance, 'FINGERPRINT', this.config.fingerprint);
        this.hookOptionalProperty(instance, 'HARDWARE', this.config.hardware, 8);
        this.hookProperty(instance, 'HOST', this.config.host);
        this.hookProperty(instance, 'ID', this.config.id);
        this.hookOptionalProperty(instance, 'MANUFACTURER', this.config.manufacturer, 4);
        this.hookProperty(instance, 'MODEL', this.config.model);
        this.hookProperty(instance, 'PRODUCT', this.config.product);
        this.hookRadioProperty(instance);
        this.hookSerialProperty(instance);
        this.hookProperty(instance, 'TAGS', this.config.tags);
        this.hookProperty(instance, 'USER', this.config.user);
        if (fakeSupportedAbis.length > 0) {
            this.hookSupportedAbis(instance, fakeSupportedAbis);
        }
    }
    hookProperty(instance, propertyName, fakeValue) {
        if (!fakeValue)
            return;
        const property = instance[propertyName];
        if (property && property.value !== undefined) {
            const originalValue = property.value;
            property.value = fakeValue;
            utils_1.HookUtils.sendChangelog({
                property: propertyName,
                oldValue: originalValue,
                newValue: fakeValue
            });
            utils_1.HookUtils.sendInfo(`Replace ${propertyName} ${originalValue} with ${fakeValue}`);
        }
    }
    hookOptionalProperty(instance, propertyName, fakeValue, apiLevel, supportedAbis) {
        if (!fakeValue)
            return;
        const property = instance[propertyName];
        if (property && property.value !== undefined) {
            const originalValue = property.value;
            property.value = fakeValue;
            if (supportedAbis && (propertyName === 'CPU_ABI' || propertyName === 'CPU_ABI2')) {
                supportedAbis.push(fakeValue);
            }
            utils_1.HookUtils.sendChangelog({
                property: propertyName,
                oldValue: originalValue,
                newValue: fakeValue
            });
            utils_1.HookUtils.sendInfo(`Replace ${propertyName} ${originalValue} with ${fakeValue}`);
        }
        else if (apiLevel) {
            utils_1.HookUtils.sendDebug(`Did not hook Build.${propertyName}, because it is undefined. It was introduced in API level ${apiLevel}, probably your test device has a lower API level.`);
        }
    }
    hookRadioProperty(instance) {
        if (!this.config.radio)
            return;
        this.hookOptionalProperty(instance, 'RADIO', this.config.radio, 8);
        const getRadioVersion = utils_1.HookUtils.getMethodSafely(instance, 'getRadioVersion', 14);
        if (getRadioVersion) {
            instance.getRadioVersion = () => {
                utils_1.HookUtils.sendChangelog({
                    property: 'RADIO',
                    newValue: this.config.radio,
                    description: 'getRadioVersion() method'
                });
                return this.config.radio;
            };
        }
    }
    hookSerialProperty(instance) {
        if (!this.config.serial)
            return;
        this.hookOptionalProperty(instance, 'SERIAL', this.config.serial, 9);
        const getSerial = utils_1.HookUtils.getMethodSafely(instance, 'getSerial', 26);
        if (getSerial) {
            instance.getSerial = () => {
                utils_1.HookUtils.sendChangelog({
                    property: 'SERIAL',
                    newValue: this.config.serial,
                    description: 'getSerial() method'
                });
                return this.config.serial;
            };
        }
    }
    hookSupportedAbis(instance, fakeSupportedAbis) {
        var _a;
        if (instance.SUPPORTED_ABIS && instance.SUPPORTED_ABIS.value) {
            const originalSupportedAbis = instance.SUPPORTED_ABIS.value;
            const originalSupported64BitAbis = (_a = instance.SUPPORTED_64_BIT_ABIS) === null || _a === void 0 ? void 0 : _a.value;
            instance.SUPPORTED_ABIS.value = fakeSupportedAbis;
            if (instance.SUPPORTED_64_BIT_ABIS) {
                instance.SUPPORTED_64_BIT_ABIS.value = fakeSupportedAbis;
            }
            utils_1.HookUtils.sendChangelog({
                property: 'SUPPORTED_ABIS',
                oldValue: originalSupportedAbis.toString(),
                newValue: fakeSupportedAbis.toString()
            });
            if (originalSupported64BitAbis) {
                utils_1.HookUtils.sendChangelog({
                    property: 'SUPPORTED_64_BIT_ABIS',
                    oldValue: originalSupported64BitAbis.toString(),
                    newValue: fakeSupportedAbis.toString()
                });
            }
            utils_1.HookUtils.sendInfo(`Replace SUPPORTED_ABIS ${originalSupportedAbis} with ${fakeSupportedAbis}`);
            if (originalSupported64BitAbis) {
                utils_1.HookUtils.sendInfo(`Replace SUPPORTED_64_BIT_ABIS ${originalSupported64BitAbis} with ${fakeSupportedAbis}`);
            }
        }
    }
}
exports.AndroidBuildHooks = AndroidBuildHooks;
