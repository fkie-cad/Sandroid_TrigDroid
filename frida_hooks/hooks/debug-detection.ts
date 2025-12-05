/**
 * Debug Detection Bypass hooks for TrigDroid.
 * Provides runtime bypass of common debugger detection techniques.
 *
 * For authorized security testing and research purposes only.
 */

import { HookUtils } from '../utils';

/**
 * Configuration for debug detection bypass hooks.
 */
export interface DebugDetectionConfig {
    enabled?: boolean;
    bypass_debug_class?: boolean;
    bypass_tracer_pid?: boolean;
    bypass_debuggable_flag?: boolean;
    bypass_timing_checks?: boolean;
}

/**
 * Debug Detection Bypass Hooks class.
 */
export class DebugDetectionHooks {
    private config: DebugDetectionConfig;

    constructor(config: DebugDetectionConfig = {}) {
        this.config = {
            enabled: true,
            bypass_debug_class: true,
            bypass_tracer_pid: true,
            bypass_debuggable_flag: true,
            bypass_timing_checks: false,  // Can affect app behavior
            ...config
        };
    }

    /**
     * Initialize all debug detection bypass hooks.
     */
    public initialize(): void {
        if (!this.config.enabled) {
            HookUtils.sendInfo('Debug detection bypass hooks disabled');
            return;
        }

        HookUtils.sendInfo('Initializing debug detection bypass hooks...');

        if (this.config.bypass_debug_class) {
            this.bypassDebugClass();
        }

        if (this.config.bypass_tracer_pid) {
            this.bypassTracerPid();
        }

        if (this.config.bypass_debuggable_flag) {
            this.bypassDebuggableFlag();
        }

        if (this.config.bypass_timing_checks) {
            this.bypassTimingChecks();
        }

        HookUtils.sendInfo('Debug detection bypass hooks initialized');
    }

    /**
     * Bypass android.os.Debug class checks.
     */
    private bypassDebugClass(): void {
        const Debug = HookUtils.safeGetJavaClass('android.os.Debug');
        if (!Debug) return;

        // isDebuggerConnected - most common check
        try {
            Debug.isDebuggerConnected.implementation = function() {
                HookUtils.sendInfo('Debug.isDebuggerConnected bypassed (returns false)');
                return false;
            };
        } catch (e) {
            HookUtils.sendDebug(`Debug.isDebuggerConnected hook failed: ${e}`);
        }

        // waitingForDebugger
        try {
            Debug.waitingForDebugger.implementation = function() {
                HookUtils.sendInfo('Debug.waitingForDebugger bypassed (returns false)');
                return false;
            };
        } catch (e) {
            HookUtils.sendDebug(`Debug.waitingForDebugger hook failed: ${e}`);
        }

        // getMemoryInfo - sometimes used for timing analysis
        // Leave this unhooked as it can affect app functionality
    }

    /**
     * Bypass TracerPid checks (reading /proc/self/status).
     */
    private bypassTracerPid(): void {
        // Hook BufferedReader.readLine to filter TracerPid
        const BufferedReader = HookUtils.safeGetJavaClass('java.io.BufferedReader');
        if (BufferedReader) {
            const originalReadLine = BufferedReader.readLine;
            BufferedReader.readLine.implementation = function() {
                const line = originalReadLine.call(this);

                if (line) {
                    const lineStr = String(line);
                    // Check for TracerPid line and return 0
                    if (lineStr.startsWith('TracerPid:')) {
                        HookUtils.sendInfo('TracerPid check bypassed (returns 0)');
                        return 'TracerPid:\t0';
                    }
                }
                return line;
            };
        }

        // Native hook for reading /proc/self/status
        const fopenPtr = Module.findExportByName('libc.so', 'fopen');
        if (fopenPtr) {
            Interceptor.attach(fopenPtr, {
                onEnter: function(args) {
                    const path = args[0].readCString();
                    if (path && (path.includes('/proc/self/status') || path.includes('/proc/') && path.includes('/status'))) {
                        HookUtils.sendInfo(`Detected /proc/*/status access: ${path}`);
                        this.isStatus = true;
                    }
                }
            });
        }

        // Hook ptrace to prevent debugger detection
        const ptrace = Module.findExportByName('libc.so', 'ptrace');
        if (ptrace) {
            Interceptor.attach(ptrace, {
                onEnter: function(args) {
                    const request = args[0].toInt32();
                    // PTRACE_TRACEME = 0, commonly used for anti-debug
                    if (request === 0) {
                        HookUtils.sendInfo('ptrace(PTRACE_TRACEME) detected - allowing');
                    }
                },
                onLeave: function(retval) {
                    // Some apps check if ptrace returns error (already being traced)
                    // Return 0 (success) to indicate no debugger
                    const ret = retval.toInt32();
                    if (ret === -1) {
                        HookUtils.sendInfo('ptrace returned -1, replacing with 0');
                        retval.replace(ptr(0));
                    }
                }
            });
        }
    }

    /**
     * Bypass ApplicationInfo.FLAG_DEBUGGABLE checks.
     */
    private bypassDebuggableFlag(): void {
        const ApplicationInfo = HookUtils.safeGetJavaClass('android.content.pm.ApplicationInfo');
        if (!ApplicationInfo) return;

        // Hook PackageManager.getApplicationInfo to clear debuggable flag
        const PackageManager = HookUtils.safeGetJavaClass('android.app.ApplicationPackageManager');
        if (PackageManager) {
            try {
                PackageManager.getApplicationInfo.overload(
                    'java.lang.String', 'int'
                ).implementation = function(packageName: any, flags: any) {
                    const appInfo = this.getApplicationInfo(packageName, flags);

                    // FLAG_DEBUGGABLE = 0x00000002
                    const FLAG_DEBUGGABLE = 0x00000002;
                    if ((appInfo.flags.value & FLAG_DEBUGGABLE) !== 0) {
                        HookUtils.sendInfo(`Cleared FLAG_DEBUGGABLE for ${packageName}`);
                        appInfo.flags.value &= ~FLAG_DEBUGGABLE;
                    }

                    return appInfo;
                };
            } catch (e) {
                HookUtils.sendDebug(`getApplicationInfo hook failed: ${e}`);
            }
        }

        // Also hook ApplicationInfo directly
        try {
            // Some apps access flags field directly
            Java.choose('android.content.pm.ApplicationInfo', {
                onMatch: function(instance: any) {
                    const FLAG_DEBUGGABLE = 0x00000002;
                    if ((instance.flags.value & FLAG_DEBUGGABLE) !== 0) {
                        instance.flags.value &= ~FLAG_DEBUGGABLE;
                        HookUtils.sendInfo('Cleared FLAG_DEBUGGABLE from ApplicationInfo instance');
                    }
                },
                onComplete: function() {}
            });
        } catch (e) {
            HookUtils.sendDebug(`ApplicationInfo Java.choose failed: ${e}`);
        }
    }

    /**
     * Bypass timing-based debug detection (optional, can affect app behavior).
     */
    private bypassTimingChecks(): void {
        // Some apps use timing to detect debuggers (stepping through code is slow)
        // This is aggressive and may cause issues

        const System = HookUtils.safeGetJavaClass('java.lang.System');
        if (System) {
            // Warn about this being enabled
            HookUtils.sendInfo('WARNING: Timing check bypass enabled - may affect app behavior');

            // We don't actually modify timing methods as it can break functionality
            // Instead, we just note when they're called
            try {
                const originalNanoTime = System.nanoTime;
                System.nanoTime.implementation = function() {
                    return originalNanoTime.call(this);
                };
            } catch (e) {
                // Leave timing alone
            }
        }

        // Native clock_gettime - leave alone but log
        const clockGettime = Module.findExportByName('libc.so', 'clock_gettime');
        if (clockGettime) {
            // Just monitor, don't modify
            Interceptor.attach(clockGettime, {
                onEnter: function(args) {
                    // CLOCK_MONOTONIC = 1 is often used for timing checks
                    const clockId = args[0].toInt32();
                    if (clockId === 1) {
                        // Log but don't modify
                    }
                }
            });
        }
    }
}
