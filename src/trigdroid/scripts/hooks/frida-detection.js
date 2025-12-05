"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FridaDetectionHooks = void 0;
const utils_1 = require("../utils");
const FRIDA_PATHS = [
    'frida',
    'frida-server',
    're.frida.server',
    '/data/local/tmp/frida',
    '/data/local/tmp/re.frida.server',
    'linjector',
    'libfrida',
    'frida-agent',
    'frida-gadget',
    'gum-js-loop',
    'gmain',
];
const FRIDA_PORT = 27042;
const FRIDA_STRINGS = [
    'frida',
    'LIBFRIDA',
    'frida-server',
    'frida-agent',
    'frida-gadget',
    'gum-js-loop',
    'linjector',
];
class FridaDetectionHooks {
    constructor(config = {}) {
        this.config = Object.assign({ enabled: true, bypass_file_checks: true, bypass_port_checks: true, bypass_maps_checks: true, bypass_named_pipe_checks: true, bypass_string_checks: true }, config);
    }
    initialize() {
        if (!this.config.enabled) {
            utils_1.HookUtils.sendInfo('Frida detection bypass hooks disabled');
            return;
        }
        utils_1.HookUtils.sendInfo('Initializing Frida detection bypass hooks...');
        if (this.config.bypass_file_checks) {
            this.bypassFridaFileChecks();
        }
        if (this.config.bypass_port_checks) {
            this.bypassFridaPortChecks();
        }
        if (this.config.bypass_maps_checks) {
            this.bypassMapsChecks();
        }
        if (this.config.bypass_named_pipe_checks) {
            this.bypassNamedPipeChecks();
        }
        if (this.config.bypass_string_checks) {
            this.bypassStringChecks();
        }
        utils_1.HookUtils.sendInfo('Frida detection bypass hooks initialized');
    }
    bypassFridaFileChecks() {
        const File = utils_1.HookUtils.safeGetJavaClass('java.io.File');
        if (File) {
            const originalExists = File.exists;
            File.exists.implementation = function () {
                const path = String(this.getAbsolutePath());
                for (const fridaPath of FRIDA_PATHS) {
                    if (path.toLowerCase().includes(fridaPath.toLowerCase())) {
                        utils_1.HookUtils.sendInfo(`Frida file check bypassed: ${path}`);
                        return false;
                    }
                }
                return originalExists.call(this);
            };
        }
        const fopen = Module.findExportByName('libc.so', 'fopen');
        if (fopen) {
            Interceptor.attach(fopen, {
                onEnter: function (args) {
                    const path = args[0].readCString();
                    if (path) {
                        for (const fridaPath of FRIDA_PATHS) {
                            if (path.toLowerCase().includes(fridaPath.toLowerCase())) {
                                utils_1.HookUtils.sendInfo(`Native fopen blocked for Frida path: ${path}`);
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
    }
    bypassFridaPortChecks() {
        const connect = Module.findExportByName('libc.so', 'connect');
        if (connect) {
            Interceptor.attach(connect, {
                onEnter: function (args) {
                    const sockaddr = args[1];
                    const family = sockaddr.readU16();
                    if (family === 2) {
                        const port = (sockaddr.add(2).readU8() << 8) | sockaddr.add(3).readU8();
                        if (port === FRIDA_PORT) {
                            utils_1.HookUtils.sendInfo(`Frida port detection bypassed (port ${FRIDA_PORT})`);
                            this.blocked = true;
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
        const Socket = utils_1.HookUtils.safeGetJavaClass('java.net.Socket');
        if (Socket) {
            try {
                Socket.connect.overload('java.net.SocketAddress', 'int').implementation = function (endpoint, timeout) {
                    const endpointStr = String(endpoint.toString());
                    if (endpointStr.includes(`:${FRIDA_PORT}`)) {
                        utils_1.HookUtils.sendInfo(`Socket.connect to Frida port bypassed`);
                        const SocketException = Java.use('java.net.SocketException');
                        throw SocketException.$new('Connection refused');
                    }
                    return this.connect(endpoint, timeout);
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`Socket.connect hook failed: ${e}`);
            }
        }
    }
    bypassMapsChecks() {
        const BufferedReader = utils_1.HookUtils.safeGetJavaClass('java.io.BufferedReader');
        if (BufferedReader) {
            BufferedReader.readLine.implementation = function () {
                const line = this.readLine();
                if (line) {
                    const lineStr = String(line);
                    for (const indicator of FRIDA_STRINGS) {
                        if (lineStr.toLowerCase().includes(indicator.toLowerCase())) {
                            utils_1.HookUtils.sendInfo(`BufferedReader filtered Frida reference: ${indicator}`);
                            return this.readLine();
                        }
                    }
                }
                return line;
            };
        }
        const openPtr = Module.findExportByName('libc.so', 'open');
        if (openPtr) {
            Interceptor.attach(openPtr, {
                onEnter: function (args) {
                    const path = args[0].readCString();
                    if (path && (path.includes('/proc/self/maps') || path.includes('/proc/') && path.includes('/maps'))) {
                        utils_1.HookUtils.sendInfo(`/proc/maps access detected: ${path}`);
                        this.isMaps = true;
                    }
                }
            });
        }
    }
    bypassNamedPipeChecks() {
        const access = Module.findExportByName('libc.so', 'access');
        if (access) {
            Interceptor.attach(access, {
                onEnter: function (args) {
                    const path = args[0].readCString();
                    if (path) {
                        if (path.includes('linjector') || path.includes('frida')) {
                            utils_1.HookUtils.sendInfo(`Named pipe access blocked: ${path}`);
                            this.blocked = true;
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
    bypassStringChecks() {
        const String = utils_1.HookUtils.safeGetJavaClass('java.lang.String');
        if (String) {
            try {
                const originalContains = String.contains;
                String.contains.implementation = function (s) {
                    if (s) {
                        const searchStr = String(s).toLowerCase();
                        for (const indicator of FRIDA_STRINGS) {
                            if (searchStr === indicator.toLowerCase()) {
                                utils_1.HookUtils.sendInfo(`String.contains bypassed for: ${searchStr}`);
                                return false;
                            }
                        }
                    }
                    return originalContains.call(this, s);
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`String.contains hook failed: ${e}`);
            }
        }
        const strstr = Module.findExportByName('libc.so', 'strstr');
        if (strstr) {
            Interceptor.attach(strstr, {
                onEnter: function (args) {
                    const needle = args[1].readCString();
                    if (needle) {
                        for (const indicator of FRIDA_STRINGS) {
                            if (needle.toLowerCase().includes(indicator.toLowerCase())) {
                                utils_1.HookUtils.sendInfo(`strstr blocked for: ${needle}`);
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
    }
}
exports.FridaDetectionHooks = FridaDetectionHooks;
