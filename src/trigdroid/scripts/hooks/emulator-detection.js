"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EmulatorDetectionHooks = void 0;
const utils_1 = require("../utils");
const DEVICE_PROFILES = {
    pixel_4_xl: {
        MODEL: 'Pixel 4 XL',
        MANUFACTURER: 'Google',
        BRAND: 'google',
        DEVICE: 'coral',
        HARDWARE: 'coral',
        PRODUCT: 'coral',
        FINGERPRINT: 'google/coral/coral:12/SP1A.210812.016.C1/7676683:user/release-keys',
        BOARD: 'coral',
    },
    pixel_6_pro: {
        MODEL: 'Pixel 6 Pro',
        MANUFACTURER: 'Google',
        BRAND: 'google',
        DEVICE: 'raven',
        HARDWARE: 'raven',
        PRODUCT: 'raven',
        FINGERPRINT: 'google/raven/raven:13/TP1A.220624.021/8877034:user/release-keys',
        BOARD: 'raven',
    },
    samsung_s21: {
        MODEL: 'SM-G991B',
        MANUFACTURER: 'samsung',
        BRAND: 'samsung',
        DEVICE: 'o1s',
        HARDWARE: 'exynos2100',
        PRODUCT: 'o1sxeea',
        FINGERPRINT: 'samsung/o1sxeea/o1s:12/SP1A.210812.016/G991BXXU4BULF:user/release-keys',
        BOARD: 'exynos2100',
    },
    oneplus_9: {
        MODEL: 'LE2115',
        MANUFACTURER: 'OnePlus',
        BRAND: 'OnePlus',
        DEVICE: 'lemonade',
        HARDWARE: 'qcom',
        PRODUCT: 'OnePlus9',
        FINGERPRINT: 'OnePlus/OnePlus9/OnePlus9:12/SKQ1.211113.001/R.202205090123:user/release-keys',
        BOARD: 'lahaina',
    },
    generic: {
        MODEL: 'SM-G950F',
        MANUFACTURER: 'samsung',
        BRAND: 'samsung',
        DEVICE: 'dreamlte',
        HARDWARE: 'samsungexynos8895',
        PRODUCT: 'dreamltexx',
        FINGERPRINT: 'samsung/dreamltexx/dreamlte:9/PPR1.180610.011/G950FXXS9DSK1:user/release-keys',
        BOARD: 'exynos8895',
    },
};
const EMULATOR_INDICATORS = {
    models: ['sdk', 'google_sdk', 'Emulator', 'Android SDK', 'Genymotion', 'generic'],
    devices: ['generic', 'generic_x86', 'vbox86p', 'goldfish'],
    hardware: ['goldfish', 'ranchu', 'vbox86', 'nox'],
    products: ['sdk', 'google_sdk', 'sdk_x86', 'vbox86p', 'emulator'],
    manufacturers: ['Genymotion', 'unknown', 'Android'],
    fingerprints: ['generic', 'unknown', 'google/sdk_gphone', 'sdk_gphone_x86'],
};
class EmulatorDetectionHooks {
    constructor(config = {}) {
        this.config = Object.assign({ enabled: true, device_profile: 'pixel_4_xl', bypass_telephony: true, bypass_sensors: false }, config);
        this.profile = DEVICE_PROFILES[this.config.device_profile || 'generic'] || DEVICE_PROFILES.generic;
        if (this.config.custom_model)
            this.profile.MODEL = this.config.custom_model;
        if (this.config.custom_manufacturer)
            this.profile.MANUFACTURER = this.config.custom_manufacturer;
        if (this.config.custom_brand)
            this.profile.BRAND = this.config.custom_brand;
        if (this.config.custom_device)
            this.profile.DEVICE = this.config.custom_device;
        if (this.config.custom_hardware)
            this.profile.HARDWARE = this.config.custom_hardware;
        if (this.config.custom_fingerprint)
            this.profile.FINGERPRINT = this.config.custom_fingerprint;
        if (this.config.custom_product)
            this.profile.PRODUCT = this.config.custom_product;
    }
    initialize() {
        if (!this.config.enabled) {
            utils_1.HookUtils.sendInfo('Emulator detection bypass hooks disabled');
            return;
        }
        utils_1.HookUtils.sendInfo(`Initializing emulator detection bypass (profile: ${this.config.device_profile})...`);
        this.bypassBuildProperties();
        this.bypassSystemProperties();
        if (this.config.bypass_telephony) {
            this.bypassTelephonyChecks();
        }
        utils_1.HookUtils.sendInfo('Emulator detection bypass hooks initialized');
    }
    isEmulatorValue(value, type) {
        const indicators = EMULATOR_INDICATORS[type];
        const valueLower = value.toLowerCase();
        return indicators.some(ind => valueLower.includes(ind.toLowerCase()));
    }
    bypassBuildProperties() {
        const Build = utils_1.HookUtils.safeGetJavaClass('android.os.Build');
        if (!Build)
            return;
        const propsToSpoof = ['MODEL', 'MANUFACTURER', 'BRAND', 'DEVICE', 'HARDWARE', 'PRODUCT', 'FINGERPRINT', 'BOARD'];
        for (const prop of propsToSpoof) {
            try {
                const field = Build[prop];
                if (field && field.value) {
                    const originalValue = String(field.value);
                    const newValue = this.profile[prop];
                    if (newValue && originalValue !== newValue) {
                        field.value = newValue;
                        utils_1.HookUtils.sendChangelog({
                            property: `Build.${prop}`,
                            oldValue: originalValue,
                            newValue: newValue
                        });
                        utils_1.HookUtils.sendInfo(`Build.${prop} spoofed: ${originalValue} -> ${newValue}`);
                    }
                }
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`Failed to spoof Build.${prop}: ${e}`);
            }
        }
        try {
            Build.getSerial.implementation = function () {
                const fakeSerial = 'RF8M33XXXXX';
                utils_1.HookUtils.sendInfo(`Build.getSerial spoofed to ${fakeSerial}`);
                return fakeSerial;
            };
        }
        catch (e) {
        }
    }
    bypassSystemProperties() {
        const propertyGet = Module.findExportByName('libc.so', '__system_property_get');
        if (!propertyGet)
            return;
        const profile = this.profile;
        Interceptor.attach(propertyGet, {
            onEnter: function (args) {
                this.name = args[0].readCString();
                this.value = args[1];
            },
            onLeave: function (retval) {
                const name = this.name;
                const mappings = {
                    'ro.product.model': profile.MODEL,
                    'ro.product.manufacturer': profile.MANUFACTURER,
                    'ro.product.brand': profile.BRAND,
                    'ro.product.device': profile.DEVICE,
                    'ro.product.board': profile.BOARD,
                    'ro.hardware': profile.HARDWARE,
                    'ro.build.fingerprint': profile.FINGERPRINT,
                    'ro.build.product': profile.PRODUCT,
                    'ro.kernel.qemu': '0',
                    'ro.kernel.qemu.gles': '',
                    'ro.boot.qemu': '0',
                    'init.svc.qemud': '',
                    'init.svc.qemu-props': '',
                    'ro.bootloader': 'unknown',
                    'ro.bootmode': 'unknown',
                    'ro.secure': '1',
                    'ro.debuggable': '0',
                };
                if (name && mappings[name]) {
                    this.value.writeUtf8String(mappings[name]);
                    utils_1.HookUtils.sendInfo(`System property ${name} spoofed`);
                }
            }
        });
    }
    bypassTelephonyChecks() {
        const TelephonyManager = utils_1.HookUtils.safeGetJavaClass('android.telephony.TelephonyManager');
        if (!TelephonyManager)
            return;
        try {
            TelephonyManager.getDeviceId.overload().implementation = function () {
                const fakeId = '358240051111110';
                utils_1.HookUtils.sendInfo(`TelephonyManager.getDeviceId spoofed to ${fakeId}`);
                return fakeId;
            };
        }
        catch (e) { }
        try {
            TelephonyManager.getDeviceId.overload('int').implementation = function (slot) {
                const fakeId = '358240051111110';
                utils_1.HookUtils.sendInfo(`TelephonyManager.getDeviceId(${slot}) spoofed`);
                return fakeId;
            };
        }
        catch (e) { }
        try {
            TelephonyManager.getSubscriberId.implementation = function () {
                const fakeImsi = '310260000000000';
                utils_1.HookUtils.sendInfo(`TelephonyManager.getSubscriberId spoofed`);
                return fakeImsi;
            };
        }
        catch (e) { }
        try {
            TelephonyManager.getLine1Number.implementation = function () {
                const fakeNumber = '+15551234567';
                utils_1.HookUtils.sendInfo(`TelephonyManager.getLine1Number spoofed`);
                return fakeNumber;
            };
        }
        catch (e) { }
        try {
            TelephonyManager.getSimSerialNumber.implementation = function () {
                const fakeSim = '89014103211118510720';
                utils_1.HookUtils.sendInfo(`TelephonyManager.getSimSerialNumber spoofed`);
                return fakeSim;
            };
        }
        catch (e) { }
        try {
            TelephonyManager.getNetworkOperatorName.implementation = function () {
                utils_1.HookUtils.sendInfo(`TelephonyManager.getNetworkOperatorName spoofed`);
                return 'T-Mobile';
            };
        }
        catch (e) { }
        try {
            TelephonyManager.getNetworkOperator.implementation = function () {
                utils_1.HookUtils.sendInfo(`TelephonyManager.getNetworkOperator spoofed`);
                return '310260';
            };
        }
        catch (e) { }
        try {
            TelephonyManager.getPhoneType.implementation = function () {
                utils_1.HookUtils.sendInfo(`TelephonyManager.getPhoneType spoofed to GSM`);
                return 1;
            };
        }
        catch (e) { }
        try {
            TelephonyManager.getSimState.implementation = function () {
                utils_1.HookUtils.sendInfo(`TelephonyManager.getSimState spoofed to READY`);
                return 5;
            };
        }
        catch (e) { }
    }
}
exports.EmulatorDetectionHooks = EmulatorDetectionHooks;
