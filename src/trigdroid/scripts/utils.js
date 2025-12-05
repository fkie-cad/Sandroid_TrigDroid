"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HookUtils = void 0;
class HookUtils {
    static sendChangelog(entry) {
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
    static sendDebug(message) {
        send(`DEBUG: ${message}`);
    }
    static sendInfo(message) {
        send(`INFO: ${message}`);
    }
    static bytesToIPv6(bytes) {
        if (bytes.length !== 16) {
            throw new Error('The byte array must contain 16 elements.');
        }
        const hexArray = bytes.map(byte => byte.toString(16).padStart(2, '0'));
        const ipv6String = [];
        for (let i = 0; i < hexArray.length; i += 2) {
            ipv6String.push(hexArray[i] + hexArray[i + 1]);
        }
        const withoutLeadingZeros = ipv6String.map(group => parseInt(group, 16).toString(16));
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
            }
            else {
                currentSequence = 0;
            }
        }
        if (longestIndex !== -1) {
            if (longestSequence === withoutLeadingZeros.length) {
                withoutLeadingZeros.splice(0, withoutLeadingZeros.length, "", "", "");
            }
            else if (longestIndex - longestSequence + 1 === 0) {
                withoutLeadingZeros.splice(0, longestSequence, "", "");
            }
            else if (longestIndex + longestSequence === withoutLeadingZeros.length - 1) {
                withoutLeadingZeros.splice(longestIndex - longestSequence + 1, longestSequence, "", "");
            }
            else {
                withoutLeadingZeros.splice(longestIndex - longestSequence + 1, longestSequence, "");
            }
        }
        const result = withoutLeadingZeros.join(':');
        return result.length > 0 ? result : '::';
    }
    static intToIPv4(ipInt) {
        const bytes = [];
        bytes.push((ipInt >>> 24) & 0xFF);
        bytes.push((ipInt >>> 16) & 0xFF);
        bytes.push((ipInt >>> 8) & 0xFF);
        bytes.push(ipInt & 0xFF);
        return bytes.join('.');
    }
    static findIPReplacementIndex(replacements, originalBytes) {
        return replacements.findIndex(replacement => replacement.old.every((byteRange, index) => {
            const min = parseInt(byteRange.min, 10);
            const max = parseInt(byteRange.max, 10);
            return min <= originalBytes[index] && originalBytes[index] <= max;
        }));
    }
    static applyIPReplacement(replacement, originalBytes) {
        return replacement.new.map((newByte, index) => newByte === 'x' ? originalBytes[index] : parseInt(newByte, 10));
    }
    static updateSleepDelay(additionalDelay) {
        this.timeDelayOfSleep += additionalDelay;
    }
    static getSleepDelay() {
        return this.timeDelayOfSleep;
    }
    static safeGetJavaClass(className) {
        try {
            return Java.use(className);
        }
        catch (error) {
            this.sendDebug(`Failed to get Java class ${className}: ${error}`);
            return null;
        }
    }
    static hasMethod(javaObject, methodName) {
        try {
            return javaObject[methodName] !== undefined;
        }
        catch (_a) {
            return false;
        }
    }
    static getMethodSafely(javaObject, methodName, apiLevel) {
        if (!this.hasMethod(javaObject, methodName)) {
            this.sendDebug(`Method ${methodName} not available (API level ${apiLevel} required)`);
            return null;
        }
        return javaObject[methodName];
    }
    static validateConfigValue(key, value, expectedType) {
        const actualType = typeof value;
        if (actualType !== expectedType) {
            this.sendDebug(`Config validation failed for ${key}: expected ${expectedType}, got ${actualType}`);
            return false;
        }
        return true;
    }
    static formatPattern(oldPattern, newPattern) {
        return `${oldPattern} -> ${newPattern}`;
    }
}
exports.HookUtils = HookUtils;
HookUtils.timeDelayOfSleep = 0;
