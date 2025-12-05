/**
 * Frida Detection Bypass hooks for TrigDroid.
 * Provides runtime bypass of common Frida detection techniques.
 *
 * For authorized security testing and research purposes only.
 *
 * Note: Some Frida detection bypasses require SPAWN mode (not ATTACH)
 * because detection may occur during app startup.
 */

import { HookUtils } from '../utils';

/**
 * Configuration for Frida detection bypass hooks.
 */
export interface FridaDetectionConfig {
    enabled?: boolean;
    bypass_file_checks?: boolean;
    bypass_port_checks?: boolean;
    bypass_maps_checks?: boolean;
    bypass_named_pipe_checks?: boolean;
    bypass_string_checks?: boolean;
}

// Frida-related paths to hide
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

// Frida default port
const FRIDA_PORT = 27042;

// Strings that indicate Frida presence
const FRIDA_STRINGS = [
    'frida',
    'LIBFRIDA',
    'frida-server',
    'frida-agent',
    'frida-gadget',
    'gum-js-loop',
    'linjector',
];

/**
 * Frida Detection Bypass Hooks class.
 */
export class FridaDetectionHooks {
    private config: FridaDetectionConfig;

    constructor(config: FridaDetectionConfig = {}) {
        this.config = {
            enabled: true,
            bypass_file_checks: true,
            bypass_port_checks: true,
            bypass_maps_checks: true,
            bypass_named_pipe_checks: true,
            bypass_string_checks: true,
            ...config
        };
    }

    /**
     * Initialize all Frida detection bypass hooks.
     */
    public initialize(): void {
        if (!this.config.enabled) {
            HookUtils.sendInfo('Frida detection bypass hooks disabled');
            return;
        }

        HookUtils.sendInfo('Initializing Frida detection bypass hooks...');

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

        HookUtils.sendInfo('Frida detection bypass hooks initialized');
    }

    /**
     * Bypass file-based Frida detection.
     */
    private bypassFridaFileChecks(): void {
        const File = HookUtils.safeGetJavaClass('java.io.File');
        if (File) {
            const originalExists = File.exists;
            File.exists.implementation = function() {
                const path = String(this.getAbsolutePath());

                for (const fridaPath of FRIDA_PATHS) {
                    if (path.toLowerCase().includes(fridaPath.toLowerCase())) {
                        HookUtils.sendInfo(`Frida file check bypassed: ${path}`);
                        return false;
                    }
                }
                return originalExists.call(this);
            };
        }

        // Native fopen
        const fopen = Module.findExportByName('libc.so', 'fopen');
        if (fopen) {
            Interceptor.attach(fopen, {
                onEnter: function(args) {
                    const path = args[0].readCString();
                    if (path) {
                        for (const fridaPath of FRIDA_PATHS) {
                            if (path.toLowerCase().includes(fridaPath.toLowerCase())) {
                                HookUtils.sendInfo(`Native fopen blocked for Frida path: ${path}`);
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
    }

    /**
     * Bypass port-based Frida detection (default port 27042).
     */
    private bypassFridaPortChecks(): void {
        // Hook connect() to prevent connections to Frida port
        const connect = Module.findExportByName('libc.so', 'connect');
        if (connect) {
            Interceptor.attach(connect, {
                onEnter: function(args) {
                    const sockaddr = args[1];
                    const family = sockaddr.readU16();

                    // AF_INET = 2
                    if (family === 2) {
                        const port = (sockaddr.add(2).readU8() << 8) | sockaddr.add(3).readU8();
                        if (port === FRIDA_PORT) {
                            HookUtils.sendInfo(`Frida port detection bypassed (port ${FRIDA_PORT})`);
                            this.blocked = true;
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

        // Hook Java Socket to prevent Frida port scanning
        const Socket = HookUtils.safeGetJavaClass('java.net.Socket');
        if (Socket) {
            try {
                Socket.connect.overload('java.net.SocketAddress', 'int').implementation = function(
                    endpoint: any,
                    timeout: any
                ) {
                    const endpointStr = String(endpoint.toString());
                    if (endpointStr.includes(`:${FRIDA_PORT}`)) {
                        HookUtils.sendInfo(`Socket.connect to Frida port bypassed`);
                        const SocketException = Java.use('java.net.SocketException');
                        throw SocketException.$new('Connection refused');
                    }
                    return this.connect(endpoint, timeout);
                };
            } catch (e) {
                HookUtils.sendDebug(`Socket.connect hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass /proc/self/maps checks for Frida libraries.
     */
    private bypassMapsChecks(): void {
        // Hook read() to filter /proc/self/maps content
        const BufferedReader = HookUtils.safeGetJavaClass('java.io.BufferedReader');
        if (BufferedReader) {
            BufferedReader.readLine.implementation = function() {
                const line = this.readLine();

                if (line) {
                    const lineStr = String(line);

                    // Check if this line contains Frida indicators
                    for (const indicator of FRIDA_STRINGS) {
                        if (lineStr.toLowerCase().includes(indicator.toLowerCase())) {
                            HookUtils.sendInfo(`BufferedReader filtered Frida reference: ${indicator}`);
                            // Return next line instead (skip this one)
                            return this.readLine();
                        }
                    }
                }
                return line;
            };
        }

        // Native open for /proc/self/maps - more aggressive approach
        // Filter the content when reading
        const openPtr = Module.findExportByName('libc.so', 'open');
        if (openPtr) {
            Interceptor.attach(openPtr, {
                onEnter: function(args) {
                    const path = args[0].readCString();
                    if (path && (path.includes('/proc/self/maps') || path.includes('/proc/') && path.includes('/maps'))) {
                        HookUtils.sendInfo(`/proc/maps access detected: ${path}`);
                        this.isMaps = true;
                    }
                }
            });
        }
    }

    /**
     * Bypass named pipe checks for Frida.
     */
    private bypassNamedPipeChecks(): void {
        // Some apps check for /data/local/tmp/linjector* named pipes
        const access = Module.findExportByName('libc.so', 'access');
        if (access) {
            Interceptor.attach(access, {
                onEnter: function(args) {
                    const path = args[0].readCString();
                    if (path) {
                        if (path.includes('linjector') || path.includes('frida')) {
                            HookUtils.sendInfo(`Named pipe access blocked: ${path}`);
                            this.blocked = true;
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
     * Bypass string-based Frida detection in memory.
     */
    private bypassStringChecks(): void {
        // Hook String contains/indexOf to filter Frida strings
        const String = HookUtils.safeGetJavaClass('java.lang.String');
        if (String) {
            try {
                const originalContains = String.contains;
                String.contains.implementation = function(s: any) {
                    if (s) {
                        const searchStr = String(s).toLowerCase();
                        for (const indicator of FRIDA_STRINGS) {
                            if (searchStr === indicator.toLowerCase()) {
                                HookUtils.sendInfo(`String.contains bypassed for: ${searchStr}`);
                                return false;
                            }
                        }
                    }
                    return originalContains.call(this, s);
                };
            } catch (e) {
                HookUtils.sendDebug(`String.contains hook failed: ${e}`);
            }
        }

        // Hook strstr for native string searches
        const strstr = Module.findExportByName('libc.so', 'strstr');
        if (strstr) {
            Interceptor.attach(strstr, {
                onEnter: function(args) {
                    const needle = args[1].readCString();
                    if (needle) {
                        for (const indicator of FRIDA_STRINGS) {
                            if (needle.toLowerCase().includes(indicator.toLowerCase())) {
                                HookUtils.sendInfo(`strstr blocked for: ${needle}`);
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
    }
}
