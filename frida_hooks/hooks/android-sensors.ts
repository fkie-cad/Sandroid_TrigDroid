/**
 * Android sensor hooks for TrigDroid.
 * Provides runtime manipulation of sensor data to trigger malware behaviors.
 */

import { AndroidSensor, SENSOR_TYPES } from '../types';
import { HookUtils } from '../utils';

/**
 * Hook configuration for sensor manipulation.
 */
interface SensorHookConfig {
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
}

/**
 * Android sensor hooks class.
 */
export class AndroidSensorHooks {
    private config: SensorHookConfig;

    constructor(config: SensorHookConfig) {
        this.config = config;
    }

    /**
     * Initialize all sensor hooks.
     */
    public initialize(): void {
        this.hookSensorPower();
        this.hookSensorRange();
        this.hookSensorResolution();
        this.hookSensorManager();
    }

    /**
     * Hook sensor power consumption values.
     */
    private hookSensorPower(): void {
        const sensorClass = HookUtils.safeGetJavaClass('android.hardware.Sensor');
        if (!sensorClass) return;

        const originalGetPower = sensorClass.getPower;
        if (!originalGetPower) return;

        sensorClass.getPower.implementation = function(this: AndroidSensor) {
            const original = originalGetPower.call(this);
            const sensorType = this.getType();
            
            let fakeValue: number | undefined;
            let sensorName = 'unknown';

            switch (sensorType) {
                case SENSOR_TYPES.ACCELEROMETER:
                    fakeValue = this.getAccelerometerPowerValue();
                    sensorName = 'accelerometer';
                    break;
                case SENSOR_TYPES.LIGHT:
                    fakeValue = this.getLightPowerValue();
                    sensorName = 'light sensor';
                    break;
                case SENSOR_TYPES.MAGNETIC_FIELD:
                    fakeValue = this.getMagnetometerPowerValue();
                    sensorName = 'magnetometer';
                    break;
                case SENSOR_TYPES.PRESSURE:
                    fakeValue = this.getPressurePowerValue();
                    sensorName = 'pressure sensor';
                    break;
            }

            if (fakeValue !== undefined) {
                HookUtils.sendChangelog({
                    property: `${sensorName}_power`,
                    oldValue: original.toString(),
                    newValue: fakeValue.toString()
                });
                HookUtils.sendInfo(
                    `Hooked getPower() of android.hardware.Sensor and return ${fakeValue} instead of ${original} for ${sensorName}`
                );
                return fakeValue;
            }

            HookUtils.sendDebug(
                `Hooked getPower() of android.hardware.Sensor and returned original value ${original}, sensorType=${sensorType} not configured`
            );
            return original;
        }.bind(this);
    }

    /**
     * Hook sensor maximum range values.
     */
    private hookSensorRange(): void {
        const sensorClass = HookUtils.safeGetJavaClass('android.hardware.Sensor');
        if (!sensorClass) return;

        const originalGetMaximumRange = sensorClass.getMaximumRange;
        if (!originalGetMaximumRange) return;

        sensorClass.getMaximumRange.implementation = function(this: AndroidSensor) {
            const original = originalGetMaximumRange.call(this);
            const sensorType = this.getType();
            
            let fakeValue: number | undefined;
            let sensorName = 'unknown';

            switch (sensorType) {
                case SENSOR_TYPES.ACCELEROMETER:
                    fakeValue = this.getAccelerometerRangeValue();
                    sensorName = 'accelerometer';
                    break;
                case SENSOR_TYPES.MAGNETIC_FIELD:
                    fakeValue = this.getMagnetometerRangeValue();
                    sensorName = 'magnetometer';
                    break;
            }

            if (fakeValue !== undefined) {
                HookUtils.sendChangelog({
                    property: `${sensorName}_range`,
                    oldValue: original.toString(),
                    newValue: fakeValue.toString()
                });
                HookUtils.sendInfo(
                    `Hooked getMaximumRange() of android.hardware.Sensor and return ${fakeValue} instead of ${original} for ${sensorName}`
                );
                return fakeValue;
            }

            HookUtils.sendDebug(
                `Hooked getMaximumRange() of android.hardware.Sensor and returned original value ${original}, sensorType=${sensorType} not configured`
            );
            return original;
        }.bind(this);
    }

    /**
     * Hook sensor resolution values.
     */
    private hookSensorResolution(): void {
        const sensorClass = HookUtils.safeGetJavaClass('android.hardware.Sensor');
        if (!sensorClass) return;

        const originalGetResolution = sensorClass.getResolution;
        if (!originalGetResolution) return;

        sensorClass.getResolution.implementation = function(this: AndroidSensor) {
            const original = originalGetResolution.call(this);
            const sensorType = this.getType();
            
            let fakeValue: number | undefined;
            let sensorName = 'unknown';

            switch (sensorType) {
                case SENSOR_TYPES.ACCELEROMETER:
                    fakeValue = this.getAccelerometerResolutionValue();
                    sensorName = 'accelerometer';
                    break;
                case SENSOR_TYPES.PRESSURE:
                    fakeValue = this.getPressureResolutionValue();
                    sensorName = 'pressure sensor';
                    break;
            }

            if (fakeValue !== undefined) {
                HookUtils.sendChangelog({
                    property: `${sensorName}_resolution`,
                    oldValue: original.toString(),
                    newValue: fakeValue.toString()
                });
                HookUtils.sendInfo(
                    `Hooked getResolution() of android.hardware.Sensor and return ${fakeValue} instead of ${original} for ${sensorName}`
                );
                return fakeValue;
            }

            HookUtils.sendDebug(
                `Hooked getResolution() of android.hardware.Sensor and returned original value ${original}, sensorType=${sensorType} not configured`
            );
            return original;
        }.bind(this);
    }

    /**
     * Hook SensorManager to control available sensors.
     */
    private hookSensorManager(): void {
        const sensorManagerClass = HookUtils.safeGetJavaClass('android.hardware.SensorManager');
        if (!sensorManagerClass) return;

        const originalGetSensorList = sensorManagerClass.getSensorList;
        if (!originalGetSensorList) return;

        // This would need additional configuration for sensor count manipulation
        sensorManagerClass.getSensorList.implementation = function(type: number) {
            const original = originalGetSensorList.call(this, type);
            
            // For now, just return original - would need sensor count config
            HookUtils.sendDebug(`Hooked getSensorList(${type}) - returning original sensor list`);
            return original;
        };
    }

    // Helper methods for getting configured values
    private getAccelerometerPowerValue(): number | undefined {
        return this.config.accelerometer?.power;
    }

    private getAccelerometerRangeValue(): number | undefined {
        return this.config.accelerometer?.range;
    }

    private getAccelerometerResolutionValue(): number | undefined {
        return this.config.accelerometer?.resolution;
    }

    private getLightPowerValue(): number | undefined {
        return this.config.light?.power;
    }

    private getMagnetometerPowerValue(): number | undefined {
        return this.config.magnetometer?.power;
    }

    private getMagnetometerRangeValue(): number | undefined {
        return this.config.magnetometer?.range;
    }

    private getPressurePowerValue(): number | undefined {
        return this.config.pressure?.power;
    }

    private getPressureResolutionValue(): number | undefined {
        return this.config.pressure?.resolution;
    }
}