/**
 * TypeScript type definitions for Frida hooks in TrigDroid.
 * This file provides type safety for Android API hooking operations.
 */

// Frida Java Bridge Types
declare global {
    interface Java {
        perform(callback: () => void): void;
        deoptimizeEverything(): void;
        use(className: string): JavaClass;
        choose<T>(className: string, callbacks: JavaChooseCallbacks<T>): void;
        array<T>(type: string, elements: T[]): T[];
    }

    interface JavaClass {
        $new(...args: any[]): JavaObject;
        $init: JavaMethod;
        [key: string]: any;
    }

    interface JavaObject {
        [key: string]: any;
    }

    interface JavaMethod {
        implementation: (...args: any[]) => any;
        overload(...types: string[]): JavaMethod;
    }

    interface JavaChooseCallbacks<T> {
        onMatch: (instance: T) => void;
        onComplete: () => void;
    }

    function send(message: string): void;
}

// Android API Types
export interface AndroidSensor {
    TYPE_ACCELEROMETER: { value: number };
    TYPE_LIGHT: { value: number };
    TYPE_MAGNETIC_FIELD: { value: number };
    TYPE_PRESSURE: { value: number };
    TYPE_GYROSCOPE: { value: number };
    getType(): number;
    getPower(): number;
    getMaximumRange(): number;
    getResolution(): number;
}

export interface AndroidBuild {
    BOARD: { value: string };
    BRAND: { value: string };
    CPU_ABI?: { value: string };
    CPU_ABI2?: { value: string };
    DEVICE: { value: string };
    FINGERPRINT: { value: string };
    HARDWARE?: { value: string };
    HOST: { value: string };
    ID: { value: string };
    MANUFACTURER?: { value: string };
    MODEL: { value: string };
    PRODUCT: { value: string };
    RADIO?: { value: string };
    SERIAL?: { value: string };
    TAGS: { value: string };
    USER: { value: string };
    SUPPORTED_ABIS?: { value: string[] };
    SUPPORTED_64_BIT_ABIS?: { value: string[] };
    getRadioVersion?(): string;
    getSerial?(): string;
}

export interface TelephonyManager {
    getSimCountryIso(): string;
    getNetworkCountryIso(): string;
    getLine1Number(): string;
    getNetworkType(): number;
    getNetworkOperator(): string;
    getNetworkOperatorName(): string;
    getImei?(): string;
    getMeid?(): string;
    getPhoneType(): number;
    getSimSerialNumber(): string;
    getSubscriberId(): string;
    getVoiceMailNumber(): string;
    getDataNetworkType?(): number;
}

export interface BluetoothAdapter {
    getAddress(): string;
    finalize(): void;
}

export interface BluetoothManager {
    getAdapter(): BluetoothAdapter | null;
}

// Hook Configuration Types
export interface HookConfig {
    [key: string]: string | number | boolean | HookConfig;
}

export interface ChangelogEntry {
    property: string;
    oldValue?: string;
    newValue?: string;
    description?: string;
}

export interface IPReplacement {
    pattern: string;
    old: Array<{min: string; max: string}>;
    new: Array<string | 'x'>;
}

// Hook Function Types
export type SensorHookFunction = (sensor: AndroidSensor, originalValue: number, sensorType: number) => number;
export type BuildHookFunction = (build: AndroidBuild, fieldName: string, originalValue: string) => string;
export type TelephonyHookFunction = (manager: TelephonyManager, methodName: string, originalValue: any) => any;

// Utility Types for Hook Templates
export interface HookTemplate {
    name: string;
    targetClass: string;
    targetMethod: string;
    replacement: string | number | boolean;
    condition?: (context: any) => boolean;
}

export interface HookSection {
    startTag: string;
    endTag: string;
    variables: Record<string, string>;
    nested?: HookSection[];
}

// Configuration Constants
export const SENSOR_TYPES = {
    ACCELEROMETER: 1,
    MAGNETIC_FIELD: 2,
    ORIENTATION: 3,
    GYROSCOPE: 4,
    LIGHT: 5,
    PRESSURE: 6,
    TEMPERATURE: 7,
    PROXIMITY: 8
} as const;

export const PHONE_TYPES = {
    NONE: 0,
    GSM: 1,
    CDMA: 2,
    SIP: 3
} as const;

export type SensorType = typeof SENSOR_TYPES[keyof typeof SENSOR_TYPES];
export type PhoneType = typeof PHONE_TYPES[keyof typeof PHONE_TYPES];