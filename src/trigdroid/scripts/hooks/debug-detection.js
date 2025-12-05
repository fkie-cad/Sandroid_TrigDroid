"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DebugDetectionHooks = void 0;
const utils_1 = require("../utils");
class DebugDetectionHooks {
    constructor(config = {}) {
        this.config = Object.assign({ enabled: true, bypass_debug_class: true, bypass_tracer_pid: true, bypass_debuggable_flag: true, bypass_timing_checks: false }, config);
    }
    initialize() {
        if (!this.config.enabled) {
            utils_1.HookUtils.sendInfo('Debug detection bypass hooks disabled');
            return;
        }
        utils_1.HookUtils.sendInfo('Initializing debug detection bypass hooks...');
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
        utils_1.HookUtils.sendInfo('Debug detection bypass hooks initialized');
    }
    bypassDebugClass() {
        const Debug = utils_1.HookUtils.safeGetJavaClass('android.os.Debug');
        if (!Debug)
            return;
        try {
            Debug.isDebuggerConnected.implementation = function () {
                utils_1.HookUtils.sendInfo('Debug.isDebuggerConnected bypassed (returns false)');
                return false;
            };
        }
        catch (e) {
            utils_1.HookUtils.sendDebug(`Debug.isDebuggerConnected hook failed: ${e}`);
        }
        try {
            Debug.waitingForDebugger.implementation = function () {
                utils_1.HookUtils.sendInfo('Debug.waitingForDebugger bypassed (returns false)');
                return false;
            };
        }
        catch (e) {
            utils_1.HookUtils.sendDebug(`Debug.waitingForDebugger hook failed: ${e}`);
        }
    }
    bypassTracerPid() {
        const BufferedReader = utils_1.HookUtils.safeGetJavaClass('java.io.BufferedReader');
        if (BufferedReader) {
            const originalReadLine = BufferedReader.readLine;
            BufferedReader.readLine.implementation = function () {
                const line = originalReadLine.call(this);
                if (line) {
                    const lineStr = String(line);
                    if (lineStr.startsWith('TracerPid:')) {
                        utils_1.HookUtils.sendInfo('TracerPid check bypassed (returns 0)');
                        return 'TracerPid:\t0';
                    }
                }
                return line;
            };
        }
        const fopenPtr = Module.findExportByName('libc.so', 'fopen');
        if (fopenPtr) {
            Interceptor.attach(fopenPtr, {
                onEnter: function (args) {
                    const path = args[0].readCString();
                    if (path && (path.includes('/proc/self/status') || path.includes('/proc/') && path.includes('/status'))) {
                        utils_1.HookUtils.sendInfo(`Detected /proc/*/status access: ${path}`);
                        this.isStatus = true;
                    }
                }
            });
        }
        const ptrace = Module.findExportByName('libc.so', 'ptrace');
        if (ptrace) {
            Interceptor.attach(ptrace, {
                onEnter: function (args) {
                    const request = args[0].toInt32();
                    if (request === 0) {
                        utils_1.HookUtils.sendInfo('ptrace(PTRACE_TRACEME) detected - allowing');
                    }
                },
                onLeave: function (retval) {
                    const ret = retval.toInt32();
                    if (ret === -1) {
                        utils_1.HookUtils.sendInfo('ptrace returned -1, replacing with 0');
                        retval.replace(ptr(0));
                    }
                }
            });
        }
    }
    bypassDebuggableFlag() {
        const ApplicationInfo = utils_1.HookUtils.safeGetJavaClass('android.content.pm.ApplicationInfo');
        if (!ApplicationInfo)
            return;
        const PackageManager = utils_1.HookUtils.safeGetJavaClass('android.app.ApplicationPackageManager');
        if (PackageManager) {
            try {
                PackageManager.getApplicationInfo.overload('java.lang.String', 'int').implementation = function (packageName, flags) {
                    const appInfo = this.getApplicationInfo(packageName, flags);
                    const FLAG_DEBUGGABLE = 0x00000002;
                    if ((appInfo.flags.value & FLAG_DEBUGGABLE) !== 0) {
                        utils_1.HookUtils.sendInfo(`Cleared FLAG_DEBUGGABLE for ${packageName}`);
                        appInfo.flags.value &= ~FLAG_DEBUGGABLE;
                    }
                    return appInfo;
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`getApplicationInfo hook failed: ${e}`);
            }
        }
        try {
            Java.choose('android.content.pm.ApplicationInfo', {
                onMatch: function (instance) {
                    const FLAG_DEBUGGABLE = 0x00000002;
                    if ((instance.flags.value & FLAG_DEBUGGABLE) !== 0) {
                        instance.flags.value &= ~FLAG_DEBUGGABLE;
                        utils_1.HookUtils.sendInfo('Cleared FLAG_DEBUGGABLE from ApplicationInfo instance');
                    }
                },
                onComplete: function () { }
            });
        }
        catch (e) {
            utils_1.HookUtils.sendDebug(`ApplicationInfo Java.choose failed: ${e}`);
        }
    }
    bypassTimingChecks() {
        const System = utils_1.HookUtils.safeGetJavaClass('java.lang.System');
        if (System) {
            utils_1.HookUtils.sendInfo('WARNING: Timing check bypass enabled - may affect app behavior');
            try {
                const originalNanoTime = System.nanoTime;
                System.nanoTime.implementation = function () {
                    return originalNanoTime.call(this);
                };
            }
            catch (e) {
            }
        }
        const clockGettime = Module.findExportByName('libc.so', 'clock_gettime');
        if (clockGettime) {
            Interceptor.attach(clockGettime, {
                onEnter: function (args) {
                    const clockId = args[0].toInt32();
                    if (clockId === 1) {
                    }
                }
            });
        }
    }
}
exports.DebugDetectionHooks = DebugDetectionHooks;
