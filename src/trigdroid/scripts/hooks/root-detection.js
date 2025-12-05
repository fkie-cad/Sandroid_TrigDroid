"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RootDetectionHooks = void 0;
const utils_1 = require("../utils");
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
    '/data/local/tmp/frida-server',
    '/data/local/tmp/re.frida.server',
    '/data/adb/ksud',
    '/data/adb/ksu',
];
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
    'me.weishu.kernelsu',
];
const BLOCKED_COMMANDS = [
    'su',
    'which su',
    'busybox',
    'magisk',
    'ksud',
];
class RootDetectionHooks {
    constructor(config = {}) {
        this.config = Object.assign({ enabled: true, bypass_file_checks: true, bypass_package_manager: true, bypass_command_execution: true, bypass_build_properties: true, bypass_rootbeer: true, bypass_system_properties: true, custom_blocked_paths: [], custom_blocked_packages: [] }, config);
        this.blockedPaths = [
            ...ROOT_INDICATOR_PATHS,
            ...(this.config.custom_blocked_paths || [])
        ];
        this.blockedPackages = [
            ...ROOT_PACKAGES,
            ...(this.config.custom_blocked_packages || [])
        ];
    }
    initialize() {
        if (!this.config.enabled) {
            utils_1.HookUtils.sendInfo('Root detection bypass hooks disabled');
            return;
        }
        utils_1.HookUtils.sendInfo('Initializing root detection bypass hooks...');
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
        utils_1.HookUtils.sendInfo('Root detection bypass hooks initialized');
    }
    isRootIndicatorPath(path) {
        return this.blockedPaths.some(indicator => path.includes(indicator) || path.toLowerCase().includes(indicator.toLowerCase()));
    }
    isRootPackage(packageName) {
        return this.blockedPackages.includes(packageName);
    }
    bypassFileChecks() {
        const File = utils_1.HookUtils.safeGetJavaClass('java.io.File');
        if (File) {
            File.exists.implementation = function () {
                const path = this.getAbsolutePath();
                const pathStr = String(path);
                for (const indicator of ROOT_INDICATOR_PATHS) {
                    if (pathStr.includes(indicator)) {
                        utils_1.HookUtils.sendInfo(`File.exists blocked for: ${pathStr}`);
                        return false;
                    }
                }
                return this.exists();
            };
            File.length.implementation = function () {
                const path = this.getAbsolutePath();
                const pathStr = String(path);
                for (const indicator of ROOT_INDICATOR_PATHS) {
                    if (pathStr.includes(indicator)) {
                        utils_1.HookUtils.sendInfo(`File.length blocked for: ${pathStr}`);
                        return 0;
                    }
                }
                return this.length();
            };
        }
        const FileInputStream = utils_1.HookUtils.safeGetJavaClass('java.io.FileInputStream');
        if (FileInputStream) {
            try {
                FileInputStream.$init.overload('java.io.File').implementation = function (file) {
                    const path = file.getAbsolutePath();
                    const pathStr = String(path);
                    for (const indicator of ROOT_INDICATOR_PATHS) {
                        if (pathStr.includes(indicator)) {
                            utils_1.HookUtils.sendInfo(`FileInputStream blocked for: ${pathStr}`);
                            const FileNotFoundException = Java.use('java.io.FileNotFoundException');
                            throw FileNotFoundException.$new(`${pathStr} (No such file or directory)`);
                        }
                    }
                    return this.$init(file);
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`FileInputStream hook failed: ${e}`);
            }
            try {
                FileInputStream.$init.overload('java.lang.String').implementation = function (path) {
                    const pathStr = String(path);
                    for (const indicator of ROOT_INDICATOR_PATHS) {
                        if (pathStr.includes(indicator)) {
                            utils_1.HookUtils.sendInfo(`FileInputStream blocked for: ${pathStr}`);
                            const FileNotFoundException = Java.use('java.io.FileNotFoundException');
                            throw FileNotFoundException.$new(`${pathStr} (No such file or directory)`);
                        }
                    }
                    return this.$init(path);
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`FileInputStream string hook failed: ${e}`);
            }
        }
        const UnixFileSystem = utils_1.HookUtils.safeGetJavaClass('java.io.UnixFileSystem');
        if (UnixFileSystem) {
            try {
                UnixFileSystem.checkAccess.implementation = function (file, access) {
                    const path = file.getAbsolutePath();
                    const pathStr = String(path);
                    for (const indicator of ROOT_INDICATOR_PATHS) {
                        if (pathStr.includes(indicator)) {
                            utils_1.HookUtils.sendInfo(`UnixFileSystem.checkAccess blocked for: ${pathStr}`);
                            return false;
                        }
                    }
                    return this.checkAccess(file, access);
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`UnixFileSystem hook failed: ${e}`);
            }
        }
    }
    bypassNativeFileAccess() {
        const libc = Module.findExportByName('libc.so', 'fopen');
        if (libc) {
            Interceptor.attach(libc, {
                onEnter: function (args) {
                    const path = args[0].readCString();
                    if (path) {
                        for (const indicator of ROOT_INDICATOR_PATHS) {
                            if (path.includes(indicator)) {
                                utils_1.HookUtils.sendInfo(`Native fopen blocked for: ${path}`);
                                this.blocked = true;
                                return;
                            }
                        }
                    }
                },
                onLeave: function (retval) {
                    if (this.blocked) {
                        retval.replace(ptr(0));
                    }
                }
            });
        }
        const access = Module.findExportByName('libc.so', 'access');
        if (access) {
            Interceptor.attach(access, {
                onEnter: function (args) {
                    const path = args[0].readCString();
                    if (path) {
                        for (const indicator of ROOT_INDICATOR_PATHS) {
                            if (path.includes(indicator)) {
                                utils_1.HookUtils.sendInfo(`Native access blocked for: ${path}`);
                                this.blocked = true;
                                return;
                            }
                        }
                    }
                },
                onLeave: function (retval) {
                    if (this.blocked) {
                        retval.replace(ptr(-1));
                    }
                }
            });
        }
        const stat = Module.findExportByName('libc.so', 'stat');
        if (stat) {
            Interceptor.attach(stat, {
                onEnter: function (args) {
                    const path = args[0].readCString();
                    if (path) {
                        for (const indicator of ROOT_INDICATOR_PATHS) {
                            if (path.includes(indicator)) {
                                utils_1.HookUtils.sendInfo(`Native stat blocked for: ${path}`);
                                this.blocked = true;
                                return;
                            }
                        }
                    }
                },
                onLeave: function (retval) {
                    if (this.blocked) {
                        retval.replace(ptr(-1));
                    }
                }
            });
        }
    }
    bypassPackageManager() {
        const ApplicationPackageManager = utils_1.HookUtils.safeGetJavaClass('android.app.ApplicationPackageManager');
        if (ApplicationPackageManager) {
            try {
                ApplicationPackageManager.getPackageInfo.overload('java.lang.String', 'int').implementation = function (packageName, flags) {
                    const pkgStr = String(packageName);
                    for (const rootPkg of ROOT_PACKAGES) {
                        if (pkgStr === rootPkg) {
                            utils_1.HookUtils.sendInfo(`PackageManager.getPackageInfo blocked for: ${pkgStr}`);
                            const NameNotFoundException = Java.use('android.content.pm.PackageManager$NameNotFoundException');
                            throw NameNotFoundException.$new(pkgStr);
                        }
                    }
                    return this.getPackageInfo(packageName, flags);
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`PackageManager.getPackageInfo hook failed: ${e}`);
            }
            try {
                ApplicationPackageManager.getInstalledPackages.implementation = function (flags) {
                    const packages = this.getInstalledPackages(flags);
                    const iterator = packages.iterator();
                    const toRemove = [];
                    while (iterator.hasNext()) {
                        const pkg = iterator.next();
                        const pkgName = String(pkg.packageName.value);
                        for (const rootPkg of ROOT_PACKAGES) {
                            if (pkgName === rootPkg) {
                                utils_1.HookUtils.sendInfo(`Filtering root package: ${pkgName}`);
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
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`PackageManager.getInstalledPackages hook failed: ${e}`);
            }
            try {
                ApplicationPackageManager.getInstalledApplications.implementation = function (flags) {
                    const apps = this.getInstalledApplications(flags);
                    const iterator = apps.iterator();
                    const toRemove = [];
                    while (iterator.hasNext()) {
                        const app = iterator.next();
                        const pkgName = String(app.packageName.value);
                        for (const rootPkg of ROOT_PACKAGES) {
                            if (pkgName === rootPkg) {
                                utils_1.HookUtils.sendInfo(`Filtering root app: ${pkgName}`);
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
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`PackageManager.getInstalledApplications hook failed: ${e}`);
            }
        }
    }
    bypassCommandExecution() {
        const Runtime = utils_1.HookUtils.safeGetJavaClass('java.lang.Runtime');
        if (Runtime) {
            const execOverloads = [
                ['java.lang.String'],
                ['[Ljava.lang.String;'],
                ['java.lang.String', '[Ljava.lang.String;'],
                ['[Ljava.lang.String;', '[Ljava.lang.String;'],
            ];
            for (const overload of execOverloads) {
                try {
                    Runtime.exec.overload(...overload).implementation = function () {
                        let command = '';
                        if (arguments[0]) {
                            command = typeof arguments[0] === 'string'
                                ? arguments[0]
                                : Array.from(arguments[0]).join(' ');
                        }
                        for (const blocked of BLOCKED_COMMANDS) {
                            if (command.includes(blocked)) {
                                utils_1.HookUtils.sendInfo(`Runtime.exec blocked: ${command}`);
                                const IOException = Java.use('java.io.IOException');
                                throw IOException.$new(`Cannot run program "${blocked}"`);
                            }
                        }
                        return this.exec.apply(this, arguments);
                    };
                }
                catch (e) {
                }
            }
        }
        const ProcessBuilder = utils_1.HookUtils.safeGetJavaClass('java.lang.ProcessBuilder');
        if (ProcessBuilder) {
            try {
                ProcessBuilder.command.overload('java.util.List').implementation = function (commands) {
                    const cmdList = Java.cast(commands, Java.use('java.util.List'));
                    const size = cmdList.size();
                    for (let i = 0; i < size; i++) {
                        const cmd = String(cmdList.get(i));
                        for (const blocked of BLOCKED_COMMANDS) {
                            if (cmd.includes(blocked)) {
                                utils_1.HookUtils.sendInfo(`ProcessBuilder.command blocked: ${cmd}`);
                                return this.command(Java.use('java.util.ArrayList').$new());
                            }
                        }
                    }
                    return this.command(commands);
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`ProcessBuilder hook failed: ${e}`);
            }
        }
    }
    bypassBuildProperties() {
        const Build = utils_1.HookUtils.safeGetJavaClass('android.os.Build');
        if (!Build)
            return;
        try {
            const TAGS = Build.TAGS;
            if (TAGS && TAGS.value) {
                const originalTags = TAGS.value;
                if (String(originalTags).includes('test-keys')) {
                    TAGS.value = 'release-keys';
                    utils_1.HookUtils.sendChangelog({
                        property: 'Build.TAGS',
                        oldValue: originalTags,
                        newValue: 'release-keys'
                    });
                }
            }
            const TYPE = Build.TYPE;
            if (TYPE && TYPE.value) {
                const originalType = TYPE.value;
                if (String(originalType) !== 'user') {
                    TYPE.value = 'user';
                    utils_1.HookUtils.sendChangelog({
                        property: 'Build.TYPE',
                        oldValue: originalType,
                        newValue: 'user'
                    });
                }
            }
            const FINGERPRINT = Build.FINGERPRINT;
            if (FINGERPRINT && FINGERPRINT.value) {
                const originalFP = String(FINGERPRINT.value);
                if (originalFP.includes('test-keys') || originalFP.includes('dev-keys')) {
                    const newFP = originalFP
                        .replace('test-keys', 'release-keys')
                        .replace('dev-keys', 'release-keys');
                    FINGERPRINT.value = newFP;
                    utils_1.HookUtils.sendChangelog({
                        property: 'Build.FINGERPRINT',
                        oldValue: originalFP,
                        newValue: newFP
                    });
                }
            }
        }
        catch (e) {
            utils_1.HookUtils.sendDebug(`Build property hooks failed: ${e}`);
        }
    }
    bypassRootBeer() {
        const RootBeer = utils_1.HookUtils.safeGetJavaClass('com.scottyab.rootbeer.RootBeer');
        if (RootBeer) {
            utils_1.HookUtils.sendInfo('RootBeer library detected - applying bypasses');
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
                    RootBeer[method].implementation = function () {
                        utils_1.HookUtils.sendInfo(`RootBeer.${method} bypassed`);
                        return false;
                    };
                }
                catch (e) {
                }
            }
        }
        const JailMonkey = utils_1.HookUtils.safeGetJavaClass('com.gantix.JailMonkey.JailMonkeyModule');
        if (JailMonkey) {
            utils_1.HookUtils.sendInfo('JailMonkey library detected - applying bypasses');
            try {
                JailMonkey.isJailBroken.implementation = function () {
                    utils_1.HookUtils.sendInfo('JailMonkey.isJailBroken bypassed');
                    return false;
                };
            }
            catch (e) { }
            try {
                JailMonkey.canMockLocation.implementation = function () {
                    utils_1.HookUtils.sendInfo('JailMonkey.canMockLocation bypassed');
                    return false;
                };
            }
            catch (e) { }
            try {
                JailMonkey.isOnExternalStorage.implementation = function () {
                    utils_1.HookUtils.sendInfo('JailMonkey.isOnExternalStorage bypassed');
                    return false;
                };
            }
            catch (e) { }
        }
    }
    bypassSystemProperties() {
        const systemPropertyGet = Module.findExportByName('libc.so', '__system_property_get');
        if (systemPropertyGet) {
            Interceptor.attach(systemPropertyGet, {
                onEnter: function (args) {
                    this.name = args[0].readCString();
                    this.value = args[1];
                },
                onLeave: function (retval) {
                    const name = this.name;
                    if (name === 'ro.debuggable') {
                        this.value.writeUtf8String('0');
                        utils_1.HookUtils.sendInfo('System property ro.debuggable spoofed to 0');
                    }
                    else if (name === 'ro.secure') {
                        this.value.writeUtf8String('1');
                        utils_1.HookUtils.sendInfo('System property ro.secure spoofed to 1');
                    }
                    else if (name === 'ro.build.type') {
                        this.value.writeUtf8String('user');
                        utils_1.HookUtils.sendInfo('System property ro.build.type spoofed to user');
                    }
                    else if (name === 'ro.build.tags') {
                        this.value.writeUtf8String('release-keys');
                        utils_1.HookUtils.sendInfo('System property ro.build.tags spoofed to release-keys');
                    }
                }
            });
        }
    }
}
exports.RootDetectionHooks = RootDetectionHooks;
