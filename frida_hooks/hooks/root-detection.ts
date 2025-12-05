/**
 * Root Detection Bypass hooks for TrigDroid.
 * Provides runtime bypass of common root detection libraries.
 *
 * For authorized security testing and research purposes only.
 *
 * References and acknowledgments:
 * - httptoolkit/frida-interception-and-unpinning (MIT License)
 *   https://github.com/httptoolkit/frida-interception-and-unpinning
 * - Techniques based on android-disable-root-detection.js
 */

import { HookUtils } from '../utils';

/**
 * Configuration for root detection bypass hooks.
 */
export interface RootDetectionConfig {
    enabled?: boolean;
    bypass_file_checks?: boolean;
    bypass_package_manager?: boolean;
    bypass_command_execution?: boolean;
    bypass_build_properties?: boolean;
    bypass_rootbeer?: boolean;
    bypass_system_properties?: boolean;
    custom_blocked_paths?: string[];
    custom_blocked_packages?: string[];
}

// Root indicator files/paths to block
const ROOT_INDICATOR_PATHS = [
    '/sbin/su',
    '/system/bin/su',
    '/system/xbin/su',
    '/system/app/Superuser.apk',
    '/system/app/SuperSU.apk',
    '/system/app/SuperUser.apk',
    '/data/data/com.noshufou.android.su',
    '/data/data/com.thirdparty.superuser',
    '/data/data/eu.chainfire.supersu',
    '/data/data/com.koushikdutta.superuser',
    '/data/data/com.zachspong.temprootremovejb',
    '/data/data/com.ramdroid.appquarantine',
    '/data/data/com.topjohnwu.magisk',
    '/data/adb/',
    '/data/adb/magisk',
    '/data/adb/modules',
    '/system/xbin/busybox',
    '/sbin/busybox',
    '/system/bin/busybox',
    '/sbin/.magisk',
    '/sbin/.core',
    '/sbin/magisk',
    '/system/xbin/daemonsu',
    '/system/etc/.installed_su_daemon',
    '/dev/.superuser.marker',
    '/system/su.d',
    '/dev/com.koushikdutta.superuser.daemon',
    '/data/local/xbin/su',
    '/data/local/bin/su',
    // Frida detection paths
    '/data/local/tmp/frida-server',
    '/data/local/tmp/re.frida.server',
    // KernelSU paths
    '/data/adb/ksud',
    '/data/adb/ksu',
];

// Root-related packages to hide
const ROOT_PACKAGES = [
    'com.noshufou.android.su',
    'com.noshufou.android.su.elite',
    'eu.chainfire.supersu',
    'com.koushikdutta.superuser',
    'com.thirdparty.superuser',
    'com.yellowes.su',
    'com.topjohnwu.magisk',
    'com.kingroot.kinguser',
    'com.kingo.root',
    'com.smedialink.oneclean',
    'com.zhiqupk.root.global',
    'com.alephzain.framaroot',
    'com.formyhm.hidelocation',
    'com.amphoras.hidemyroot',
    'com.amphoras.hidemyrootadfree',
    'com.zachspong.temprootremovejb',
    'com.ramdroid.appquarantine',
    'com.devadvance.rootcloak',
    'com.devadvance.rootcloakplus',
    'de.robv.android.xposed.installer',
    'com.saurik.substrate',
    'com.zachspong.temprootremovejb',
    'com.formyhm.hideroot',
    // KernelSU
    'me.weishu.kernelsu',
];

// Commands to block
const BLOCKED_COMMANDS = [
    'su',
    'which su',
    'busybox',
    'magisk',
    'ksud',
];

/**
 * Root Detection Bypass Hooks class.
 *
 * Based on techniques from httptoolkit/frida-interception-and-unpinning.
 */
export class RootDetectionHooks {
    private config: RootDetectionConfig;
    private blockedPaths: string[];
    private blockedPackages: string[];

    constructor(config: RootDetectionConfig = {}) {
        this.config = {
            enabled: true,
            bypass_file_checks: true,
            bypass_package_manager: true,
            bypass_command_execution: true,
            bypass_build_properties: true,
            bypass_rootbeer: true,
            bypass_system_properties: true,
            custom_blocked_paths: [],
            custom_blocked_packages: [],
            ...config
        };

        this.blockedPaths = [
            ...ROOT_INDICATOR_PATHS,
            ...(this.config.custom_blocked_paths || [])
        ];

        this.blockedPackages = [
            ...ROOT_PACKAGES,
            ...(this.config.custom_blocked_packages || [])
        ];
    }

    /**
     * Initialize all root detection bypass hooks.
     */
    public initialize(): void {
        if (!this.config.enabled) {
            HookUtils.sendInfo('Root detection bypass hooks disabled');
            return;
        }

        HookUtils.sendInfo('Initializing root detection bypass hooks...');

        if (this.config.bypass_file_checks) {
            this.bypassFileChecks();
            this.bypassNativeFileAccess();
        }

        if (this.config.bypass_package_manager) {
            this.bypassPackageManager();
        }

        if (this.config.bypass_command_execution) {
            this.bypassCommandExecution();
        }

        if (this.config.bypass_build_properties) {
            this.bypassBuildProperties();
        }

        if (this.config.bypass_rootbeer) {
            this.bypassRootBeer();
        }

        if (this.config.bypass_system_properties) {
            this.bypassSystemProperties();
        }

        HookUtils.sendInfo('Root detection bypass hooks initialized');
    }

    /**
     * Check if a path is a root indicator.
     */
    private isRootIndicatorPath(path: string): boolean {
        return this.blockedPaths.some(indicator =>
            path.includes(indicator) || path.toLowerCase().includes(indicator.toLowerCase())
        );
    }

    /**
     * Check if a package is root-related.
     */
    private isRootPackage(packageName: string): boolean {
        return this.blockedPackages.includes(packageName);
    }

    /**
     * Bypass Java File system checks.
     * Reference: httptoolkit android-disable-root-detection.js - File hooks
     */
    private bypassFileChecks(): void {
        // File.exists()
        const File = HookUtils.safeGetJavaClass('java.io.File');
        if (File) {
            File.exists.implementation = function() {
                const path = this.getAbsolutePath();
                const pathStr = String(path);

                for (const indicator of ROOT_INDICATOR_PATHS) {
                    if (pathStr.includes(indicator)) {
                        HookUtils.sendInfo(`File.exists blocked for: ${pathStr}`);
                        return false;
                    }
                }
                return this.exists();
            };

            // File.length()
            File.length.implementation = function() {
                const path = this.getAbsolutePath();
                const pathStr = String(path);

                for (const indicator of ROOT_INDICATOR_PATHS) {
                    if (pathStr.includes(indicator)) {
                        HookUtils.sendInfo(`File.length blocked for: ${pathStr}`);
                        return 0;
                    }
                }
                return this.length();
            };
        }

        // FileInputStream constructor
        const FileInputStream = HookUtils.safeGetJavaClass('java.io.FileInputStream');
        if (FileInputStream) {
            try {
                FileInputStream.$init.overload('java.io.File').implementation = function(file: any) {
                    const path = file.getAbsolutePath();
                    const pathStr = String(path);

                    for (const indicator of ROOT_INDICATOR_PATHS) {
                        if (pathStr.includes(indicator)) {
                            HookUtils.sendInfo(`FileInputStream blocked for: ${pathStr}`);
                            const FileNotFoundException = Java.use('java.io.FileNotFoundException');
                            throw FileNotFoundException.$new(`${pathStr} (No such file or directory)`);
                        }
                    }
                    return this.$init(file);
                };
            } catch (e) {
                HookUtils.sendDebug(`FileInputStream hook failed: ${e}`);
            }

            try {
                FileInputStream.$init.overload('java.lang.String').implementation = function(path: any) {
                    const pathStr = String(path);

                    for (const indicator of ROOT_INDICATOR_PATHS) {
                        if (pathStr.includes(indicator)) {
                            HookUtils.sendInfo(`FileInputStream blocked for: ${pathStr}`);
                            const FileNotFoundException = Java.use('java.io.FileNotFoundException');
                            throw FileNotFoundException.$new(`${pathStr} (No such file or directory)`);
                        }
                    }
                    return this.$init(path);
                };
            } catch (e) {
                HookUtils.sendDebug(`FileInputStream string hook failed: ${e}`);
            }
        }

        // UnixFileSystem.checkAccess
        const UnixFileSystem = HookUtils.safeGetJavaClass('java.io.UnixFileSystem');
        if (UnixFileSystem) {
            try {
                UnixFileSystem.checkAccess.implementation = function(file: any, access: any) {
                    const path = file.getAbsolutePath();
                    const pathStr = String(path);

                    for (const indicator of ROOT_INDICATOR_PATHS) {
                        if (pathStr.includes(indicator)) {
                            HookUtils.sendInfo(`UnixFileSystem.checkAccess blocked for: ${pathStr}`);
                            return false;
                        }
                    }
                    return this.checkAccess(file, access);
                };
            } catch (e) {
                HookUtils.sendDebug(`UnixFileSystem hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass native file access functions (libc).
     * Reference: httptoolkit android-disable-root-detection.js - Native hooks
     */
    private bypassNativeFileAccess(): void {
        const libc = Module.findExportByName('libc.so', 'fopen');
        if (libc) {
            Interceptor.attach(libc, {
                onEnter: function(args) {
                    const path = args[0].readCString();
                    if (path) {
                        for (const indicator of ROOT_INDICATOR_PATHS) {
                            if (path.includes(indicator)) {
                                HookUtils.sendInfo(`Native fopen blocked for: ${path}`);
                                this.blocked = true;
                                return;
                            }
                        }
                    }
                },
                onLeave: function(retval) {
                    if (this.blocked) {
                        retval.replace(ptr(0));
                    }
                }
            });
        }

        const access = Module.findExportByName('libc.so', 'access');
        if (access) {
            Interceptor.attach(access, {
                onEnter: function(args) {
                    const path = args[0].readCString();
                    if (path) {
                        for (const indicator of ROOT_INDICATOR_PATHS) {
                            if (path.includes(indicator)) {
                                HookUtils.sendInfo(`Native access blocked for: ${path}`);
                                this.blocked = true;
                                return;
                            }
                        }
                    }
                },
                onLeave: function(retval) {
                    if (this.blocked) {
                        retval.replace(ptr(-1));
                    }
                }
            });
        }

        const stat = Module.findExportByName('libc.so', 'stat');
        if (stat) {
            Interceptor.attach(stat, {
                onEnter: function(args) {
                    const path = args[0].readCString();
                    if (path) {
                        for (const indicator of ROOT_INDICATOR_PATHS) {
                            if (path.includes(indicator)) {
                                HookUtils.sendInfo(`Native stat blocked for: ${path}`);
                                this.blocked = true;
                                return;
                            }
                        }
                    }
                },
                onLeave: function(retval) {
                    if (this.blocked) {
                        retval.replace(ptr(-1));
                    }
                }
            });
        }
    }

    /**
     * Bypass PackageManager queries for root apps.
     * Reference: httptoolkit android-disable-root-detection.js - PackageManager hooks
     */
    private bypassPackageManager(): void {
        const ApplicationPackageManager = HookUtils.safeGetJavaClass(
            'android.app.ApplicationPackageManager'
        );

        if (ApplicationPackageManager) {
            // getPackageInfo - return fake for root packages
            try {
                ApplicationPackageManager.getPackageInfo.overload(
                    'java.lang.String', 'int'
                ).implementation = function(packageName: any, flags: any) {
                    const pkgStr = String(packageName);

                    for (const rootPkg of ROOT_PACKAGES) {
                        if (pkgStr === rootPkg) {
                            HookUtils.sendInfo(`PackageManager.getPackageInfo blocked for: ${pkgStr}`);
                            const NameNotFoundException = Java.use(
                                'android.content.pm.PackageManager$NameNotFoundException'
                            );
                            throw NameNotFoundException.$new(pkgStr);
                        }
                    }
                    return this.getPackageInfo(packageName, flags);
                };
            } catch (e) {
                HookUtils.sendDebug(`PackageManager.getPackageInfo hook failed: ${e}`);
            }

            // getInstalledPackages - filter out root packages
            try {
                ApplicationPackageManager.getInstalledPackages.implementation = function(flags: any) {
                    const packages = this.getInstalledPackages(flags);
                    const iterator = packages.iterator();
                    const toRemove: any[] = [];

                    while (iterator.hasNext()) {
                        const pkg = iterator.next();
                        const pkgName = String(pkg.packageName.value);

                        for (const rootPkg of ROOT_PACKAGES) {
                            if (pkgName === rootPkg) {
                                HookUtils.sendInfo(`Filtering root package: ${pkgName}`);
                                toRemove.push(pkg);
                                break;
                            }
                        }
                    }

                    for (const pkg of toRemove) {
                        packages.remove(pkg);
                    }

                    return packages;
                };
            } catch (e) {
                HookUtils.sendDebug(`PackageManager.getInstalledPackages hook failed: ${e}`);
            }

            // getInstalledApplications - filter out root apps
            try {
                ApplicationPackageManager.getInstalledApplications.implementation = function(flags: any) {
                    const apps = this.getInstalledApplications(flags);
                    const iterator = apps.iterator();
                    const toRemove: any[] = [];

                    while (iterator.hasNext()) {
                        const app = iterator.next();
                        const pkgName = String(app.packageName.value);

                        for (const rootPkg of ROOT_PACKAGES) {
                            if (pkgName === rootPkg) {
                                HookUtils.sendInfo(`Filtering root app: ${pkgName}`);
                                toRemove.push(app);
                                break;
                            }
                        }
                    }

                    for (const app of toRemove) {
                        apps.remove(app);
                    }

                    return apps;
                };
            } catch (e) {
                HookUtils.sendDebug(`PackageManager.getInstalledApplications hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass command execution checks (su, busybox, etc).
     * Reference: httptoolkit android-disable-root-detection.js - Runtime hooks
     */
    private bypassCommandExecution(): void {
        // Runtime.exec
        const Runtime = HookUtils.safeGetJavaClass('java.lang.Runtime');
        if (Runtime) {
            const execOverloads = [
                ['java.lang.String'],
                ['[Ljava.lang.String;'],
                ['java.lang.String', '[Ljava.lang.String;'],
                ['[Ljava.lang.String;', '[Ljava.lang.String;'],
            ];

            for (const overload of execOverloads) {
                try {
                    Runtime.exec.overload(...overload).implementation = function() {
                        let command = '';
                        if (arguments[0]) {
                            command = typeof arguments[0] === 'string'
                                ? arguments[0]
                                : Array.from(arguments[0]).join(' ');
                        }

                        for (const blocked of BLOCKED_COMMANDS) {
                            if (command.includes(blocked)) {
                                HookUtils.sendInfo(`Runtime.exec blocked: ${command}`);
                                const IOException = Java.use('java.io.IOException');
                                throw IOException.$new(`Cannot run program "${blocked}"`);
                            }
                        }

                        return this.exec.apply(this, arguments);
                    };
                } catch (e) {
                    // Overload not found
                }
            }
        }

        // ProcessBuilder.command
        const ProcessBuilder = HookUtils.safeGetJavaClass('java.lang.ProcessBuilder');
        if (ProcessBuilder) {
            try {
                ProcessBuilder.command.overload('java.util.List').implementation = function(commands: any) {
                    const cmdList = Java.cast(commands, Java.use('java.util.List'));
                    const size = cmdList.size();

                    for (let i = 0; i < size; i++) {
                        const cmd = String(cmdList.get(i));
                        for (const blocked of BLOCKED_COMMANDS) {
                            if (cmd.includes(blocked)) {
                                HookUtils.sendInfo(`ProcessBuilder.command blocked: ${cmd}`);
                                return this.command(Java.use('java.util.ArrayList').$new());
                            }
                        }
                    }

                    return this.command(commands);
                };
            } catch (e) {
                HookUtils.sendDebug(`ProcessBuilder hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass Build property checks.
     * Reference: httptoolkit android-disable-root-detection.js - Build hooks
     */
    private bypassBuildProperties(): void {
        const Build = HookUtils.safeGetJavaClass('android.os.Build');
        if (!Build) return;

        try {
            // Make device appear as a stock release build
            const TAGS = Build.TAGS;
            if (TAGS && TAGS.value) {
                const originalTags = TAGS.value;
                if (String(originalTags).includes('test-keys')) {
                    TAGS.value = 'release-keys';
                    HookUtils.sendChangelog({
                        property: 'Build.TAGS',
                        oldValue: originalTags,
                        newValue: 'release-keys'
                    });
                }
            }

            // Spoof Build.TYPE to 'user' (non-debug)
            const TYPE = Build.TYPE;
            if (TYPE && TYPE.value) {
                const originalType = TYPE.value;
                if (String(originalType) !== 'user') {
                    TYPE.value = 'user';
                    HookUtils.sendChangelog({
                        property: 'Build.TYPE',
                        oldValue: originalType,
                        newValue: 'user'
                    });
                }
            }

            // Remove 'dev-keys' or 'test-keys' from fingerprint
            const FINGERPRINT = Build.FINGERPRINT;
            if (FINGERPRINT && FINGERPRINT.value) {
                const originalFP = String(FINGERPRINT.value);
                if (originalFP.includes('test-keys') || originalFP.includes('dev-keys')) {
                    const newFP = originalFP
                        .replace('test-keys', 'release-keys')
                        .replace('dev-keys', 'release-keys');
                    FINGERPRINT.value = newFP;
                    HookUtils.sendChangelog({
                        property: 'Build.FINGERPRINT',
                        oldValue: originalFP,
                        newValue: newFP
                    });
                }
            }
        } catch (e) {
            HookUtils.sendDebug(`Build property hooks failed: ${e}`);
        }
    }

    /**
     * Bypass RootBeer library detection.
     * Reference: Additional bypass for popular root detection library.
     */
    private bypassRootBeer(): void {
        const RootBeer = HookUtils.safeGetJavaClass('com.scottyab.rootbeer.RootBeer');
        if (RootBeer) {
            HookUtils.sendInfo('RootBeer library detected - applying bypasses');

            const methodsToBypass = [
                'isRooted',
                'isRootedWithoutBusyBoxCheck',
                'detectRootManagementApps',
                'detectPotentiallyDangerousApps',
                'detectTestKeys',
                'checkForBusyBoxBinary',
                'checkForSuBinary',
                'checkForMagiskBinary',
                'checkSuExists',
                'checkForRWPaths',
                'checkForDangerousProps',
                'checkForRootNative',
                'detectRootCloakingApps',
            ];

            for (const method of methodsToBypass) {
                try {
                    RootBeer[method].implementation = function() {
                        HookUtils.sendInfo(`RootBeer.${method} bypassed`);
                        return false;
                    };
                } catch (e) {
                    // Method may not exist
                }
            }
        }

        // JailMonkey (React Native)
        const JailMonkey = HookUtils.safeGetJavaClass('com.gantix.JailMonkey.JailMonkeyModule');
        if (JailMonkey) {
            HookUtils.sendInfo('JailMonkey library detected - applying bypasses');
            try {
                JailMonkey.isJailBroken.implementation = function() {
                    HookUtils.sendInfo('JailMonkey.isJailBroken bypassed');
                    return false;
                };
            } catch (e) {}

            try {
                JailMonkey.canMockLocation.implementation = function() {
                    HookUtils.sendInfo('JailMonkey.canMockLocation bypassed');
                    return false;
                };
            } catch (e) {}

            try {
                JailMonkey.isOnExternalStorage.implementation = function() {
                    HookUtils.sendInfo('JailMonkey.isOnExternalStorage bypassed');
                    return false;
                };
            } catch (e) {}
        }
    }

    /**
     * Bypass system property checks.
     * Reference: httptoolkit android-disable-root-detection.js - __system_property_get
     */
    private bypassSystemProperties(): void {
        const systemPropertyGet = Module.findExportByName('libc.so', '__system_property_get');
        if (systemPropertyGet) {
            Interceptor.attach(systemPropertyGet, {
                onEnter: function(args) {
                    this.name = args[0].readCString();
                    this.value = args[1];
                },
                onLeave: function(retval) {
                    const name = this.name;
                    if (name === 'ro.debuggable') {
                        this.value.writeUtf8String('0');
                        HookUtils.sendInfo('System property ro.debuggable spoofed to 0');
                    } else if (name === 'ro.secure') {
                        this.value.writeUtf8String('1');
                        HookUtils.sendInfo('System property ro.secure spoofed to 1');
                    } else if (name === 'ro.build.type') {
                        this.value.writeUtf8String('user');
                        HookUtils.sendInfo('System property ro.build.type spoofed to user');
                    } else if (name === 'ro.build.tags') {
                        this.value.writeUtf8String('release-keys');
                        HookUtils.sendInfo('System property ro.build.tags spoofed to release-keys');
                    }
                }
            });
        }
    }
}
