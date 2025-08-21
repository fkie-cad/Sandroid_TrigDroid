/**
 * Android Build information hooks for TrigDroid.
 * Provides runtime manipulation of device build properties.
 */

import { AndroidBuild } from '../types';
import { HookUtils } from '../utils';

/**
 * Hook configuration for Android Build properties.
 */
interface BuildHookConfig {
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
}

/**
 * Android Build hooks class.
 */
export class AndroidBuildHooks {
    private config: BuildHookConfig;

    constructor(config: BuildHookConfig) {
        this.config = config;
    }

    /**
     * Initialize all Build hooks.
     */
    public initialize(): void {
        this.hookBuildProperties();
    }

    /**
     * Hook Android Build properties using Java.choose.
     */
    private hookBuildProperties(): void {
        const buildClass = HookUtils.safeGetJavaClass('android.os.Build');
        if (!buildClass) return;

        // Create an instance first to ensure the class is loaded
        try {
            buildClass.$new();
        } catch (error) {
            HookUtils.sendDebug(`Could not create Build instance: ${error}`);
        }

        Java.choose('android.os.Build', {
            onMatch: (instance: AndroidBuild) => {
                HookUtils.sendInfo('Hooked android.os.Build');
                this.hookBuildInstance(instance);
            },
            onComplete: () => {
                HookUtils.sendInfo('Hooked all instances of android.os.Build');
            }
        });
    }

    /**
     * Hook individual Build instance properties.
     */
    private hookBuildInstance(instance: AndroidBuild): void {
        // Prepare supported ABIs array
        const fakeSupportedAbis: string[] = [];
        
        // Hook individual properties
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
        
        // Hook supported ABIs if we have any
        if (fakeSupportedAbis.length > 0) {
            this.hookSupportedAbis(instance, fakeSupportedAbis);
        }
    }

    /**
     * Hook a required Build property.
     */
    private hookProperty(instance: AndroidBuild, propertyName: string, fakeValue?: string): void {
        if (!fakeValue) return;

        const property = (instance as any)[propertyName];
        if (property && property.value !== undefined) {
            const originalValue = property.value;
            property.value = fakeValue;
            
            HookUtils.sendChangelog({
                property: propertyName,
                oldValue: originalValue,
                newValue: fakeValue
            });
            HookUtils.sendInfo(`Replace ${propertyName} ${originalValue} with ${fakeValue}`);
        }
    }

    /**
     * Hook an optional Build property (API level dependent).
     */
    private hookOptionalProperty(
        instance: AndroidBuild, 
        propertyName: string, 
        fakeValue?: string, 
        apiLevel?: number,
        supportedAbis?: string[]
    ): void {
        if (!fakeValue) return;

        const property = (instance as any)[propertyName];
        if (property && property.value !== undefined) {
            const originalValue = property.value;
            property.value = fakeValue;
            
            if (supportedAbis && (propertyName === 'CPU_ABI' || propertyName === 'CPU_ABI2')) {
                supportedAbis.push(fakeValue);
            }
            
            HookUtils.sendChangelog({
                property: propertyName,
                oldValue: originalValue,
                newValue: fakeValue
            });
            HookUtils.sendInfo(`Replace ${propertyName} ${originalValue} with ${fakeValue}`);
        } else if (apiLevel) {
            HookUtils.sendDebug(
                `Did not hook Build.${propertyName}, because it is undefined. It was introduced in API level ${apiLevel}, probably your test device has a lower API level.`
            );
        }
    }

    /**
     * Hook RADIO property and getRadioVersion method.
     */
    private hookRadioProperty(instance: AndroidBuild): void {
        if (!this.config.radio) return;

        // Hook RADIO field (deprecated)
        this.hookOptionalProperty(instance, 'RADIO', this.config.radio, 8);
        
        // Hook getRadioVersion method (replacement for RADIO field)
        const getRadioVersion = HookUtils.getMethodSafely(instance, 'getRadioVersion', 14);
        if (getRadioVersion) {
            instance.getRadioVersion = () => {
                HookUtils.sendChangelog({
                    property: 'RADIO',
                    newValue: this.config.radio!,
                    description: 'getRadioVersion() method'
                });
                return this.config.radio!;
            };
        }
    }

    /**
     * Hook SERIAL property and getSerial method.
     */
    private hookSerialProperty(instance: AndroidBuild): void {
        if (!this.config.serial) return;

        // Hook SERIAL field (deprecated)
        this.hookOptionalProperty(instance, 'SERIAL', this.config.serial, 9);
        
        // Hook getSerial method (replacement for SERIAL field)
        const getSerial = HookUtils.getMethodSafely(instance, 'getSerial', 26);
        if (getSerial) {
            instance.getSerial = () => {
                HookUtils.sendChangelog({
                    property: 'SERIAL',
                    newValue: this.config.serial!,
                    description: 'getSerial() method'
                });
                return this.config.serial!;
            };
        }
    }

    /**
     * Hook SUPPORTED_ABIS arrays.
     */
    private hookSupportedAbis(instance: AndroidBuild, fakeSupportedAbis: string[]): void {
        if (instance.SUPPORTED_ABIS && instance.SUPPORTED_ABIS.value) {
            const originalSupportedAbis = instance.SUPPORTED_ABIS.value;
            const originalSupported64BitAbis = instance.SUPPORTED_64_BIT_ABIS?.value;
            
            instance.SUPPORTED_ABIS.value = fakeSupportedAbis;
            if (instance.SUPPORTED_64_BIT_ABIS) {
                instance.SUPPORTED_64_BIT_ABIS.value = fakeSupportedAbis;
            }
            
            HookUtils.sendChangelog({
                property: 'SUPPORTED_ABIS',
                oldValue: originalSupportedAbis.toString(),
                newValue: fakeSupportedAbis.toString()
            });
            
            if (originalSupported64BitAbis) {
                HookUtils.sendChangelog({
                    property: 'SUPPORTED_64_BIT_ABIS',
                    oldValue: originalSupported64BitAbis.toString(),
                    newValue: fakeSupportedAbis.toString()
                });
            }
            
            HookUtils.sendInfo(`Replace SUPPORTED_ABIS ${originalSupportedAbis} with ${fakeSupportedAbis}`);
            if (originalSupported64BitAbis) {
                HookUtils.sendInfo(`Replace SUPPORTED_64_BIT_ABIS ${originalSupported64BitAbis} with ${fakeSupportedAbis}`);
            }
        }
    }
}