/**
 * Utility functions for Frida hooks in TrigDroid.
 * Provides reusable functionality for Android API manipulation.
 */

import { ChangelogEntry, IPReplacement } from './types';

/**
 * Utility class for common hook operations.
 */
export class HookUtils {
    private static timeDelayOfSleep: number = 0;

    /**
     * Send a changelog entry to the host application.
     */
    static sendChangelog(entry: ChangelogEntry): void {
        const { property, oldValue, newValue, description } = entry;
        let message = `#changelog ${property}`;
        
        if (oldValue !== undefined) {
            message += ` 0${oldValue}`;
        }
        
        if (newValue !== undefined) {
            message += ` 1${newValue}`;
        }
        
        if (description) {
            message += ` ${description}`;
        }
        
        send(message);
    }

    /**
     * Send a debug message to the host application.
     */
    static sendDebug(message: string): void {
        send(`DEBUG: ${message}`);
    }

    /**
     * Send an info message to the host application.
     */
    static sendInfo(message: string): void {
        send(`INFO: ${message}`);
    }

    /**
     * Convert IPv6 bytes array to string representation.
     */
    static bytesToIPv6(bytes: number[]): string {
        if (bytes.length !== 16) {
            throw new Error('The byte array must contain 16 elements.');
        }

        // Convert each byte to a hexadecimal digit
        const hexArray = bytes.map(byte => byte.toString(16).padStart(2, '0'));

        // Insert colons between the groups
        const ipv6String: string[] = [];
        for (let i = 0; i < hexArray.length; i += 2) {
            ipv6String.push(hexArray[i] + hexArray[i + 1]);
        }

        // Remove leading zeros in each group
        const withoutLeadingZeros = ipv6String.map(group => parseInt(group, 16).toString(16));

        // Find the longest sequence of consecutive zeros
        let currentSequence = 0;
        let longestSequence = 0;
        let longestIndex = -1;

        for (let i = 0; i < withoutLeadingZeros.length; i++) {
            if (withoutLeadingZeros[i] === "0") {
                currentSequence++;
                if (currentSequence > longestSequence) {
                    longestSequence = currentSequence;
                    longestIndex = i;
                }
            } else {
                currentSequence = 0;
            }
        }

        // Replace the longest sequence with an empty string
        if (longestIndex !== -1) {
            if (longestSequence === withoutLeadingZeros.length) {
                // The entire array is being replaced
                withoutLeadingZeros.splice(0, withoutLeadingZeros.length, "", "", "");
            } else if (longestIndex - longestSequence + 1 === 0) {
                // The beginning of the array is being replaced
                withoutLeadingZeros.splice(0, longestSequence, "", "");
            } else if (longestIndex + longestSequence === withoutLeadingZeros.length - 1) {
                // The end of the array is being replaced
                withoutLeadingZeros.splice(longestIndex - longestSequence + 1, longestSequence, "", "");
            } else {
                // A part in the middle of the array is being replaced
                withoutLeadingZeros.splice(longestIndex - longestSequence + 1, longestSequence, "");
            }
        }

        const result = withoutLeadingZeros.join(':');
        return result.length > 0 ? result : '::';
    }

    /**
     * Convert IPv4 integer to dotted decimal notation.
     */
    static intToIPv4(ipInt: number): string {
        const bytes: number[] = [];
        bytes.push((ipInt >>> 24) & 0xFF);
        bytes.push((ipInt >>> 16) & 0xFF);
        bytes.push((ipInt >>> 8) & 0xFF);
        bytes.push(ipInt & 0xFF);
        return bytes.join('.');
    }

    /**
     * Find the first matching IP replacement pattern.
     */
    static findIPReplacementIndex(replacements: IPReplacement[], originalBytes: number[]): number {
        return replacements.findIndex(replacement => 
            replacement.old.every((byteRange, index) => {
                const min = parseInt(byteRange.min, 10);
                const max = parseInt(byteRange.max, 10);
                return min <= originalBytes[index] && originalBytes[index] <= max;
            })
        );
    }

    /**
     * Apply IP replacement pattern to original bytes.
     */
    static applyIPReplacement(replacement: IPReplacement, originalBytes: number[]): number[] {
        return replacement.new.map((newByte, index) => 
            newByte === 'x' ? originalBytes[index] : parseInt(newByte as string, 10)
        );
    }

    /**
     * Update sleep delay for date manipulation.
     */
    static updateSleepDelay(additionalDelay: number): void {
        this.timeDelayOfSleep += additionalDelay;
    }

    /**
     * Get current sleep delay.
     */
    static getSleepDelay(): number {
        return this.timeDelayOfSleep;
    }

    /**
     * Safely get Java class, returning null if not found.
     */
    static safeGetJavaClass(className: string): any {
        try {
            return Java.use(className);
        } catch (error) {
            this.sendDebug(`Failed to get Java class ${className}: ${error}`);
            return null;
        }
    }

    /**
     * Check if a method exists on a Java object.
     */
    static hasMethod(javaObject: any, methodName: string): boolean {
        try {
            return javaObject[methodName] !== undefined;
        } catch {
            return false;
        }
    }

    /**
     * Get API level safe method with fallback.
     */
    static getMethodSafely<T>(javaObject: any, methodName: string, apiLevel: number): T | null {
        if (!this.hasMethod(javaObject, methodName)) {
            this.sendDebug(`Method ${methodName} not available (API level ${apiLevel} required)`);
            return null;
        }
        return javaObject[methodName];
    }

    /**
     * Validate configuration value type.
     */
    static validateConfigValue(key: string, value: any, expectedType: string): boolean {
        const actualType = typeof value;
        if (actualType !== expectedType) {
            this.sendDebug(`Config validation failed for ${key}: expected ${expectedType}, got ${actualType}`);
            return false;
        }
        return true;
    }

    /**
     * Format pattern string for logging.
     */
    static formatPattern(oldPattern: string, newPattern: string): string {
        return `${oldPattern} -> ${newPattern}`;
    }
}