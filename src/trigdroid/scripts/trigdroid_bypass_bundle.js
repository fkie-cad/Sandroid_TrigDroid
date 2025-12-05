📦
72818 /dist/trigdroid_bypass_rpc.js
38579 /dist/trigdroid_bypass_rpc.js.map
✄
var __getOwnPropNames = Object.getOwnPropertyNames;
var __esm = (fn, res) => function __init() {
  return fn && (res = (0, fn[__getOwnPropNames(fn)[0]])(fn = 0)), res;
};
var __commonJS = (cb, mod) => function __require() {
  return mod || (0, cb[__getOwnPropNames(cb)[0]])((mod = { exports: {} }).exports, mod), mod.exports;
};

// frida-builtins:/node-globals.js
var init_node_globals = __esm({
  "frida-builtins:/node-globals.js"() {
  }
});

// dist/utils.js
var require_utils = __commonJS({
  "dist/utils.js"(exports) {
    "use strict";
    init_node_globals();
    Object.defineProperty(exports, "__esModule", { value: true });
    exports.HookUtils = void 0;
    var HookUtils = class {
      static sendChangelog(entry) {
        const { property, oldValue, newValue, description } = entry;
        let message = `#changelog ${property}`;
        if (oldValue !== void 0) {
          message += ` 0${oldValue}`;
        }
        if (newValue !== void 0) {
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
          throw new Error("The byte array must contain 16 elements.");
        }
        const hexArray = bytes.map((byte) => byte.toString(16).padStart(2, "0"));
        const ipv6String = [];
        for (let i = 0; i < hexArray.length; i += 2) {
          ipv6String.push(hexArray[i] + hexArray[i + 1]);
        }
        const withoutLeadingZeros = ipv6String.map((group) => parseInt(group, 16).toString(16));
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
        if (longestIndex !== -1) {
          if (longestSequence === withoutLeadingZeros.length) {
            withoutLeadingZeros.splice(0, withoutLeadingZeros.length, "", "", "");
          } else if (longestIndex - longestSequence + 1 === 0) {
            withoutLeadingZeros.splice(0, longestSequence, "", "");
          } else if (longestIndex + longestSequence === withoutLeadingZeros.length - 1) {
            withoutLeadingZeros.splice(longestIndex - longestSequence + 1, longestSequence, "", "");
          } else {
            withoutLeadingZeros.splice(longestIndex - longestSequence + 1, longestSequence, "");
          }
        }
        const result = withoutLeadingZeros.join(":");
        return result.length > 0 ? result : "::";
      }
      static intToIPv4(ipInt) {
        const bytes = [];
        bytes.push(ipInt >>> 24 & 255);
        bytes.push(ipInt >>> 16 & 255);
        bytes.push(ipInt >>> 8 & 255);
        bytes.push(ipInt & 255);
        return bytes.join(".");
      }
      static findIPReplacementIndex(replacements, originalBytes) {
        return replacements.findIndex((replacement) => replacement.old.every((byteRange, index) => {
          const min = parseInt(byteRange.min, 10);
          const max = parseInt(byteRange.max, 10);
          return min <= originalBytes[index] && originalBytes[index] <= max;
        }));
      }
      static applyIPReplacement(replacement, originalBytes) {
        return replacement.new.map((newByte, index) => newByte === "x" ? originalBytes[index] : parseInt(newByte, 10));
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
        } catch (error) {
          this.sendDebug(`Failed to get Java class ${className}: ${error}`);
          return null;
        }
      }
      static hasMethod(javaObject, methodName) {
        try {
          return javaObject[methodName] !== void 0;
        } catch (_a) {
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
    };
    exports.HookUtils = HookUtils;
    HookUtils.timeDelayOfSleep = 0;
  }
});

// dist/hooks/ssl-unpinning.js
var require_ssl_unpinning = __commonJS({
  "dist/hooks/ssl-unpinning.js"(exports) {
    "use strict";
    init_node_globals();
    Object.defineProperty(exports, "__esModule", { value: true });
    exports.SSLUnpinningHooks = void 0;
    var utils_1 = require_utils();
    var SSLUnpinningHooks = class {
      constructor(config = {}) {
        this.config = Object.assign({ enabled: true, use_custom_cert: false, custom_cert_path: "/data/local/tmp/cert-der.crt", bypass_okhttp: true, bypass_okhttp3: true, bypass_trust_manager: true, bypass_webview_client: true, bypass_conscrypt: true, bypass_network_security_config: true, bypass_trustkit: true, bypass_appcelerator: true, bypass_phonegap: true, bypass_ibm_worklight: true, bypass_cwac_netsecurity: true, bypass_cordova_advanced_http: true, bypass_netty: true, bypass_appmattus_ct: true }, config);
      }
      initialize() {
        if (!this.config.enabled) {
          utils_1.HookUtils.sendInfo("SSL Unpinning hooks disabled");
          return;
        }
        utils_1.HookUtils.sendInfo("Initializing SSL unpinning hooks...");
        if (this.config.bypass_trust_manager) {
          this.bypassHttpsURLConnection();
          this.bypassSSLContext();
        }
        if (this.config.bypass_conscrypt) {
          this.bypassConscrypt();
        }
        if (this.config.bypass_network_security_config) {
          this.bypassNetworkSecurityConfig();
        }
        if (this.config.bypass_okhttp) {
          this.bypassOkHttpV2();
        }
        if (this.config.bypass_okhttp3) {
          this.bypassOkHttp3();
        }
        if (this.config.bypass_webview_client) {
          this.bypassWebViewClient();
        }
        if (this.config.bypass_trustkit) {
          this.bypassTrustKit();
        }
        if (this.config.bypass_appcelerator) {
          this.bypassAppcelerator();
        }
        if (this.config.bypass_phonegap) {
          this.bypassPhoneGap();
        }
        if (this.config.bypass_ibm_worklight) {
          this.bypassIBMWorkLight();
        }
        if (this.config.bypass_cwac_netsecurity) {
          this.bypassCWACNetsecurity();
        }
        if (this.config.bypass_cordova_advanced_http) {
          this.bypassCordovaAdvancedHTTP();
        }
        if (this.config.bypass_netty) {
          this.bypassNetty();
        }
        if (this.config.bypass_appmattus_ct) {
          this.bypassAppmattusCtInterceptor();
        }
        utils_1.HookUtils.sendInfo("SSL unpinning hooks initialized");
      }
      bypassHttpsURLConnection() {
        const HttpsURLConnection = utils_1.HookUtils.safeGetJavaClass("javax.net.ssl.HttpsURLConnection");
        if (!HttpsURLConnection)
          return;
        try {
          HttpsURLConnection.setHostnameVerifier.implementation = function(verifier) {
            utils_1.HookUtils.sendInfo("HttpsURLConnection.setHostnameVerifier bypassed");
          };
        } catch (e) {
          utils_1.HookUtils.sendDebug(`HttpsURLConnection.setHostnameVerifier hook failed: ${e}`);
        }
        try {
          HttpsURLConnection.setSSLSocketFactory.implementation = function(factory) {
            utils_1.HookUtils.sendInfo("HttpsURLConnection.setSSLSocketFactory bypassed");
          };
        } catch (e) {
          utils_1.HookUtils.sendDebug(`HttpsURLConnection.setSSLSocketFactory hook failed: ${e}`);
        }
      }
      bypassSSLContext() {
        const SSLContext = utils_1.HookUtils.safeGetJavaClass("javax.net.ssl.SSLContext");
        if (!SSLContext)
          return;
        try {
          const X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
          const TrustAllCerts = Java.registerClass({
            name: "com.trigdroid.bypass.TrustAllCerts",
            implements: [X509TrustManager],
            methods: {
              checkClientTrusted: function(chain, authType) {
              },
              checkServerTrusted: function(chain, authType) {
                utils_1.HookUtils.sendInfo("TrustManager.checkServerTrusted bypassed");
              },
              getAcceptedIssuers: function() {
                return [];
              }
            }
          });
          SSLContext.init.overload("[Ljavax.net.ssl.KeyManager;", "[Ljavax.net.ssl.TrustManager;", "java.security.SecureRandom").implementation = function(keyManagers, trustManagers, secureRandom) {
            utils_1.HookUtils.sendInfo("SSLContext.init intercepted - injecting permissive TrustManager");
            const trustAllArray = Java.array("javax.net.ssl.TrustManager", [TrustAllCerts.$new()]);
            this.init(keyManagers, trustAllArray, secureRandom);
            utils_1.HookUtils.sendChangelog({
              property: "SSLContext.init",
              oldValue: "original TrustManager",
              newValue: "TrustAllCerts (bypass)"
            });
          };
        } catch (e) {
          utils_1.HookUtils.sendDebug(`SSLContext hook failed: ${e}`);
        }
      }
      bypassConscrypt() {
        const TrustManagerImpl = utils_1.HookUtils.safeGetJavaClass("com.android.org.conscrypt.TrustManagerImpl");
        if (TrustManagerImpl) {
          try {
            TrustManagerImpl.verifyChain.implementation = function(untrustedChain, trustAnchorChain, host, clientAuth, ocspData, tlsSctData) {
              utils_1.HookUtils.sendInfo(`Conscrypt TrustManagerImpl.verifyChain bypassed for ${host}`);
              return untrustedChain;
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`TrustManagerImpl.verifyChain hook failed: ${e}`);
          }
        }
        const CertPinManager = utils_1.HookUtils.safeGetJavaClass("com.android.org.conscrypt.CertPinManager");
        if (CertPinManager) {
          try {
            CertPinManager.isChainValid.overload("java.lang.String", "java.util.List").implementation = function(hostname, chain) {
              utils_1.HookUtils.sendInfo(`Conscrypt CertPinManager.isChainValid bypassed for ${hostname}`);
              return true;
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`CertPinManager.isChainValid hook failed: ${e}`);
          }
          try {
            CertPinManager.checkChainPinning.implementation = function(hostname, chain) {
              utils_1.HookUtils.sendInfo(`Conscrypt CertPinManager.checkChainPinning bypassed for ${hostname}`);
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`CertPinManager.checkChainPinning hook failed: ${e}`);
          }
        }
      }
      bypassNetworkSecurityConfig() {
        const NetworkSecurityConfig = utils_1.HookUtils.safeGetJavaClass("android.security.net.config.NetworkSecurityConfig");
        if (!NetworkSecurityConfig)
          return;
        try {
          const Builder = utils_1.HookUtils.safeGetJavaClass("android.security.net.config.NetworkSecurityConfig$Builder");
          if (Builder) {
            Builder.setPinSet.implementation = function(pinSet) {
              utils_1.HookUtils.sendInfo("NetworkSecurityConfig.Builder.setPinSet bypassed");
              return this;
            };
          }
        } catch (e) {
          utils_1.HookUtils.sendDebug(`NetworkSecurityConfig hook failed: ${e}`);
        }
      }
      bypassOkHttpV2() {
        const OkHostnameVerifier = utils_1.HookUtils.safeGetJavaClass("com.android.okhttp.internal.tls.OkHostnameVerifier");
        if (OkHostnameVerifier) {
          try {
            OkHostnameVerifier.verify.overload("java.lang.String", "java.security.cert.X509Certificate").implementation = function(hostname, certificate) {
              utils_1.HookUtils.sendInfo(`OkHttp v2 hostname verification bypassed for ${hostname}`);
              return true;
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`OkHttp v2 verify hook failed: ${e}`);
          }
        }
        const Address = utils_1.HookUtils.safeGetJavaClass("com.android.okhttp.Address");
        if (Address) {
          try {
            Address.$init.overload("java.lang.String", "int", "com.android.okhttp.Dns", "javax.net.SocketFactory", "javax.net.ssl.SSLSocketFactory", "javax.net.ssl.HostnameVerifier", "com.android.okhttp.CertificatePinner", "com.android.okhttp.Authenticator", "java.net.Proxy", "java.util.List", "java.util.List", "java.net.ProxySelector").implementation = function(uriHost, uriPort, dns, socketFactory, sslSocketFactory, hostnameVerifier, certificatePinner, authenticator, proxy, protocols, connectionSpecs, proxySelector) {
              utils_1.HookUtils.sendInfo("OkHttp v2 Address constructor bypassed");
              const CertificatePinner = Java.use("com.android.okhttp.CertificatePinner");
              return this.$init(uriHost, uriPort, dns, socketFactory, sslSocketFactory, null, CertificatePinner.DEFAULT.value, authenticator, proxy, protocols, connectionSpecs, proxySelector);
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`OkHttp v2 Address hook failed: ${e}`);
          }
        }
      }
      bypassOkHttp3() {
        const CertificatePinner = utils_1.HookUtils.safeGetJavaClass("okhttp3.CertificatePinner");
        if (CertificatePinner) {
          const checkOverloads = [
            ["java.lang.String", "java.util.List"],
            ["java.lang.String", "[Ljava.security.cert.Certificate;"],
            ["java.lang.String", "java.util.function.Supplier"]
          ];
          for (const overload of checkOverloads) {
            try {
              CertificatePinner.check.overload(...overload).implementation = function() {
                utils_1.HookUtils.sendInfo(`OkHttp3 CertificatePinner.check bypassed for ${arguments[0]}`);
              };
            } catch (e) {
            }
          }
          try {
            CertificatePinner["check$okhttp"].implementation = function() {
              utils_1.HookUtils.sendInfo(`OkHttp3 CertificatePinner.check$okhttp bypassed`);
            };
          } catch (e) {
          }
        }
        const Builder = utils_1.HookUtils.safeGetJavaClass("okhttp3.OkHttpClient$Builder");
        if (Builder) {
          try {
            Builder.certificatePinner.implementation = function(pinner) {
              utils_1.HookUtils.sendInfo("OkHttp3 Builder.certificatePinner bypassed");
              return this;
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`OkHttp3 Builder hook failed: ${e}`);
          }
        }
      }
      bypassWebViewClient() {
        const WebViewClient = utils_1.HookUtils.safeGetJavaClass("android.webkit.WebViewClient");
        if (!WebViewClient)
          return;
        try {
          WebViewClient.onReceivedSslError.implementation = function(view, handler, error) {
            utils_1.HookUtils.sendInfo(`WebViewClient SSL error bypassed: ${error.toString()}`);
            handler.proceed();
          };
        } catch (e) {
          utils_1.HookUtils.sendDebug(`WebViewClient hook failed: ${e}`);
        }
      }
      bypassTrustKit() {
        const TrustKit = utils_1.HookUtils.safeGetJavaClass("com.datatheorem.android.trustkit.pinning.OkHostnameVerifier");
        if (TrustKit) {
          try {
            TrustKit.verify.overload("java.lang.String", "javax.net.ssl.SSLSession").implementation = function(hostname, session) {
              utils_1.HookUtils.sendInfo(`TrustKit hostname verification bypassed for ${hostname}`);
              return true;
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`TrustKit hook failed: ${e}`);
          }
        }
        const PinningTrustManager = utils_1.HookUtils.safeGetJavaClass("com.datatheorem.android.trustkit.pinning.PinningTrustManager");
        if (PinningTrustManager) {
          try {
            PinningTrustManager.checkServerTrusted.implementation = function(chain, authType) {
              utils_1.HookUtils.sendInfo("TrustKit PinningTrustManager bypassed");
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`TrustKit TrustManager hook failed: ${e}`);
          }
        }
      }
      bypassAppcelerator() {
        const PinningTrustManager = utils_1.HookUtils.safeGetJavaClass("appcelerator.https.PinningTrustManager");
        if (PinningTrustManager) {
          try {
            PinningTrustManager.checkServerTrusted.implementation = function(chain, authType) {
              utils_1.HookUtils.sendInfo("Appcelerator PinningTrustManager bypassed");
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`Appcelerator hook failed: ${e}`);
          }
        }
      }
      bypassPhoneGap() {
        const SSLCertificateChecker = utils_1.HookUtils.safeGetJavaClass("nl.xservices.plugins.SSLCertificateChecker");
        if (SSLCertificateChecker) {
          try {
            SSLCertificateChecker.execute.implementation = function(action, args, callbackContext) {
              utils_1.HookUtils.sendInfo("PhoneGap SSLCertificateChecker bypassed");
              callbackContext.success("CONNECTION_SECURE");
              return true;
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`PhoneGap hook failed: ${e}`);
          }
        }
      }
      bypassIBMWorkLight() {
        const WorkLightWebView = utils_1.HookUtils.safeGetJavaClass("com.worklight.wlclient.ui.UIWebViewClient");
        if (WorkLightWebView) {
          try {
            WorkLightWebView.onReceivedSslError.implementation = function(view, handler, error) {
              utils_1.HookUtils.sendInfo("IBM WorkLight SSL error bypassed");
              handler.proceed();
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`IBM WorkLight hook failed: ${e}`);
          }
        }
        const WLGap = utils_1.HookUtils.safeGetJavaClass("com.worklight.androidgap.plugin.WLCertificatePinningPlugin");
        if (WLGap) {
          try {
            WLGap.isCertificatePinned.implementation = function() {
              utils_1.HookUtils.sendInfo("IBM WorkLight isCertificatePinned bypassed");
              return true;
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`IBM WorkLight gap hook failed: ${e}`);
          }
        }
      }
      bypassCWACNetsecurity() {
        const CertChainValidator = utils_1.HookUtils.safeGetJavaClass("com.commonsware.cwac.netsecurity.conscrypt.CertChainValidator");
        if (CertChainValidator) {
          try {
            CertChainValidator.verifyChain.implementation = function() {
              utils_1.HookUtils.sendInfo("CWAC-Netsecurity CertChainValidator bypassed");
              return Java.use("java.util.ArrayList").$new();
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`CWAC-Netsecurity hook failed: ${e}`);
          }
        }
      }
      bypassCordovaAdvancedHTTP() {
        const CordovaHTTP = utils_1.HookUtils.safeGetJavaClass("com.silkimen.cordovahttp.CordovaHttpPlugin");
        if (CordovaHTTP) {
          try {
            CordovaHTTP.setSSLCertMode.implementation = function(mode, callbackContext) {
              utils_1.HookUtils.sendInfo(`Cordova setSSLCertMode bypassed (was: ${mode})`);
              this.setSSLCertMode("default", callbackContext);
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`Cordova Advanced HTTP hook failed: ${e}`);
          }
        }
      }
      bypassNetty() {
        const FingerprintTrustManagerFactory = utils_1.HookUtils.safeGetJavaClass("io.netty.handler.ssl.util.FingerprintTrustManagerFactory");
        if (FingerprintTrustManagerFactory) {
          try {
            FingerprintTrustManagerFactory.checkTrusted.implementation = function(type, chain) {
              utils_1.HookUtils.sendInfo("Netty FingerprintTrustManagerFactory bypassed");
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`Netty hook failed: ${e}`);
          }
        }
      }
      bypassAppmattusCtInterceptor() {
        const CTInterceptor = utils_1.HookUtils.safeGetJavaClass("com.appmattus.certificatetransparency.internal.verifier.CertificateTransparencyInterceptor");
        if (CTInterceptor) {
          try {
            CTInterceptor.intercept.implementation = function(chain) {
              utils_1.HookUtils.sendInfo("Appmattus CT Interceptor bypassed");
              return chain.proceed(chain.request());
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`Appmattus CT hook failed: ${e}`);
          }
        }
      }
    };
    exports.SSLUnpinningHooks = SSLUnpinningHooks;
  }
});

// dist/hooks/root-detection.js
var require_root_detection = __commonJS({
  "dist/hooks/root-detection.js"(exports) {
    "use strict";
    init_node_globals();
    Object.defineProperty(exports, "__esModule", { value: true });
    exports.RootDetectionHooks = void 0;
    var utils_1 = require_utils();
    var ROOT_INDICATOR_PATHS = [
      "/sbin/su",
      "/system/bin/su",
      "/system/xbin/su",
      "/system/app/Superuser.apk",
      "/system/app/SuperSU.apk",
      "/system/app/SuperUser.apk",
      "/data/data/com.noshufou.android.su",
      "/data/data/com.thirdparty.superuser",
      "/data/data/eu.chainfire.supersu",
      "/data/data/com.koushikdutta.superuser",
      "/data/data/com.zachspong.temprootremovejb",
      "/data/data/com.ramdroid.appquarantine",
      "/data/data/com.topjohnwu.magisk",
      "/data/adb/",
      "/data/adb/magisk",
      "/data/adb/modules",
      "/system/xbin/busybox",
      "/sbin/busybox",
      "/system/bin/busybox",
      "/sbin/.magisk",
      "/sbin/.core",
      "/sbin/magisk",
      "/system/xbin/daemonsu",
      "/system/etc/.installed_su_daemon",
      "/dev/.superuser.marker",
      "/system/su.d",
      "/dev/com.koushikdutta.superuser.daemon",
      "/data/local/xbin/su",
      "/data/local/bin/su",
      "/data/local/tmp/frida-server",
      "/data/local/tmp/re.frida.server",
      "/data/adb/ksud",
      "/data/adb/ksu"
    ];
    var ROOT_PACKAGES = [
      "com.noshufou.android.su",
      "com.noshufou.android.su.elite",
      "eu.chainfire.supersu",
      "com.koushikdutta.superuser",
      "com.thirdparty.superuser",
      "com.yellowes.su",
      "com.topjohnwu.magisk",
      "com.kingroot.kinguser",
      "com.kingo.root",
      "com.smedialink.oneclean",
      "com.zhiqupk.root.global",
      "com.alephzain.framaroot",
      "com.formyhm.hidelocation",
      "com.amphoras.hidemyroot",
      "com.amphoras.hidemyrootadfree",
      "com.zachspong.temprootremovejb",
      "com.ramdroid.appquarantine",
      "com.devadvance.rootcloak",
      "com.devadvance.rootcloakplus",
      "de.robv.android.xposed.installer",
      "com.saurik.substrate",
      "com.zachspong.temprootremovejb",
      "com.formyhm.hideroot",
      "me.weishu.kernelsu"
    ];
    var BLOCKED_COMMANDS = [
      "su",
      "which su",
      "busybox",
      "magisk",
      "ksud"
    ];
    var RootDetectionHooks = class {
      constructor(config = {}) {
        this.config = Object.assign({ enabled: true, bypass_file_checks: true, bypass_package_manager: true, bypass_command_execution: true, bypass_build_properties: true, bypass_rootbeer: true, bypass_system_properties: true, custom_blocked_paths: [], custom_blocked_packages: [] }, config);
        this.blockedPaths = [
          ...ROOT_INDICATOR_PATHS,
          ...this.config.custom_blocked_paths || []
        ];
        this.blockedPackages = [
          ...ROOT_PACKAGES,
          ...this.config.custom_blocked_packages || []
        ];
      }
      initialize() {
        if (!this.config.enabled) {
          utils_1.HookUtils.sendInfo("Root detection bypass hooks disabled");
          return;
        }
        utils_1.HookUtils.sendInfo("Initializing root detection bypass hooks...");
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
        utils_1.HookUtils.sendInfo("Root detection bypass hooks initialized");
      }
      isRootIndicatorPath(path) {
        return this.blockedPaths.some((indicator) => path.includes(indicator) || path.toLowerCase().includes(indicator.toLowerCase()));
      }
      isRootPackage(packageName) {
        return this.blockedPackages.includes(packageName);
      }
      bypassFileChecks() {
        const File = utils_1.HookUtils.safeGetJavaClass("java.io.File");
        if (File) {
          File.exists.implementation = function() {
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
          File.length.implementation = function() {
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
        const FileInputStream = utils_1.HookUtils.safeGetJavaClass("java.io.FileInputStream");
        if (FileInputStream) {
          try {
            FileInputStream.$init.overload("java.io.File").implementation = function(file) {
              const path = file.getAbsolutePath();
              const pathStr = String(path);
              for (const indicator of ROOT_INDICATOR_PATHS) {
                if (pathStr.includes(indicator)) {
                  utils_1.HookUtils.sendInfo(`FileInputStream blocked for: ${pathStr}`);
                  const FileNotFoundException = Java.use("java.io.FileNotFoundException");
                  throw FileNotFoundException.$new(`${pathStr} (No such file or directory)`);
                }
              }
              return this.$init(file);
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`FileInputStream hook failed: ${e}`);
          }
          try {
            FileInputStream.$init.overload("java.lang.String").implementation = function(path) {
              const pathStr = String(path);
              for (const indicator of ROOT_INDICATOR_PATHS) {
                if (pathStr.includes(indicator)) {
                  utils_1.HookUtils.sendInfo(`FileInputStream blocked for: ${pathStr}`);
                  const FileNotFoundException = Java.use("java.io.FileNotFoundException");
                  throw FileNotFoundException.$new(`${pathStr} (No such file or directory)`);
                }
              }
              return this.$init(path);
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`FileInputStream string hook failed: ${e}`);
          }
        }
        const UnixFileSystem = utils_1.HookUtils.safeGetJavaClass("java.io.UnixFileSystem");
        if (UnixFileSystem) {
          try {
            UnixFileSystem.checkAccess.implementation = function(file, access) {
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
          } catch (e) {
            utils_1.HookUtils.sendDebug(`UnixFileSystem hook failed: ${e}`);
          }
        }
      }
      bypassNativeFileAccess() {
        const libc = Module.findExportByName("libc.so", "fopen");
        if (libc) {
          Interceptor.attach(libc, {
            onEnter: function(args) {
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
            onLeave: function(retval) {
              if (this.blocked) {
                retval.replace(ptr(0));
              }
            }
          });
        }
        const access = Module.findExportByName("libc.so", "access");
        if (access) {
          Interceptor.attach(access, {
            onEnter: function(args) {
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
            onLeave: function(retval) {
              if (this.blocked) {
                retval.replace(ptr(-1));
              }
            }
          });
        }
        const stat = Module.findExportByName("libc.so", "stat");
        if (stat) {
          Interceptor.attach(stat, {
            onEnter: function(args) {
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
            onLeave: function(retval) {
              if (this.blocked) {
                retval.replace(ptr(-1));
              }
            }
          });
        }
      }
      bypassPackageManager() {
        const ApplicationPackageManager = utils_1.HookUtils.safeGetJavaClass("android.app.ApplicationPackageManager");
        if (ApplicationPackageManager) {
          try {
            ApplicationPackageManager.getPackageInfo.overload("java.lang.String", "int").implementation = function(packageName, flags) {
              const pkgStr = String(packageName);
              for (const rootPkg of ROOT_PACKAGES) {
                if (pkgStr === rootPkg) {
                  utils_1.HookUtils.sendInfo(`PackageManager.getPackageInfo blocked for: ${pkgStr}`);
                  const NameNotFoundException = Java.use("android.content.pm.PackageManager$NameNotFoundException");
                  throw NameNotFoundException.$new(pkgStr);
                }
              }
              return this.getPackageInfo(packageName, flags);
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`PackageManager.getPackageInfo hook failed: ${e}`);
          }
          try {
            ApplicationPackageManager.getInstalledPackages.implementation = function(flags) {
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
          } catch (e) {
            utils_1.HookUtils.sendDebug(`PackageManager.getInstalledPackages hook failed: ${e}`);
          }
          try {
            ApplicationPackageManager.getInstalledApplications.implementation = function(flags) {
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
          } catch (e) {
            utils_1.HookUtils.sendDebug(`PackageManager.getInstalledApplications hook failed: ${e}`);
          }
        }
      }
      bypassCommandExecution() {
        const Runtime = utils_1.HookUtils.safeGetJavaClass("java.lang.Runtime");
        if (Runtime) {
          const execOverloads = [
            ["java.lang.String"],
            ["[Ljava.lang.String;"],
            ["java.lang.String", "[Ljava.lang.String;"],
            ["[Ljava.lang.String;", "[Ljava.lang.String;"]
          ];
          for (const overload of execOverloads) {
            try {
              Runtime.exec.overload(...overload).implementation = function() {
                let command = "";
                if (arguments[0]) {
                  command = typeof arguments[0] === "string" ? arguments[0] : Array.from(arguments[0]).join(" ");
                }
                for (const blocked of BLOCKED_COMMANDS) {
                  if (command.includes(blocked)) {
                    utils_1.HookUtils.sendInfo(`Runtime.exec blocked: ${command}`);
                    const IOException = Java.use("java.io.IOException");
                    throw IOException.$new(`Cannot run program "${blocked}"`);
                  }
                }
                return this.exec.apply(this, arguments);
              };
            } catch (e) {
            }
          }
        }
        const ProcessBuilder = utils_1.HookUtils.safeGetJavaClass("java.lang.ProcessBuilder");
        if (ProcessBuilder) {
          try {
            ProcessBuilder.command.overload("java.util.List").implementation = function(commands) {
              const cmdList = Java.cast(commands, Java.use("java.util.List"));
              const size = cmdList.size();
              for (let i = 0; i < size; i++) {
                const cmd = String(cmdList.get(i));
                for (const blocked of BLOCKED_COMMANDS) {
                  if (cmd.includes(blocked)) {
                    utils_1.HookUtils.sendInfo(`ProcessBuilder.command blocked: ${cmd}`);
                    return this.command(Java.use("java.util.ArrayList").$new());
                  }
                }
              }
              return this.command(commands);
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`ProcessBuilder hook failed: ${e}`);
          }
        }
      }
      bypassBuildProperties() {
        const Build = utils_1.HookUtils.safeGetJavaClass("android.os.Build");
        if (!Build)
          return;
        try {
          const TAGS = Build.TAGS;
          if (TAGS && TAGS.value) {
            const originalTags = TAGS.value;
            if (String(originalTags).includes("test-keys")) {
              TAGS.value = "release-keys";
              utils_1.HookUtils.sendChangelog({
                property: "Build.TAGS",
                oldValue: originalTags,
                newValue: "release-keys"
              });
            }
          }
          const TYPE = Build.TYPE;
          if (TYPE && TYPE.value) {
            const originalType = TYPE.value;
            if (String(originalType) !== "user") {
              TYPE.value = "user";
              utils_1.HookUtils.sendChangelog({
                property: "Build.TYPE",
                oldValue: originalType,
                newValue: "user"
              });
            }
          }
          const FINGERPRINT = Build.FINGERPRINT;
          if (FINGERPRINT && FINGERPRINT.value) {
            const originalFP = String(FINGERPRINT.value);
            if (originalFP.includes("test-keys") || originalFP.includes("dev-keys")) {
              const newFP = originalFP.replace("test-keys", "release-keys").replace("dev-keys", "release-keys");
              FINGERPRINT.value = newFP;
              utils_1.HookUtils.sendChangelog({
                property: "Build.FINGERPRINT",
                oldValue: originalFP,
                newValue: newFP
              });
            }
          }
        } catch (e) {
          utils_1.HookUtils.sendDebug(`Build property hooks failed: ${e}`);
        }
      }
      bypassRootBeer() {
        const RootBeer = utils_1.HookUtils.safeGetJavaClass("com.scottyab.rootbeer.RootBeer");
        if (RootBeer) {
          utils_1.HookUtils.sendInfo("RootBeer library detected - applying bypasses");
          const methodsToBypass = [
            "isRooted",
            "isRootedWithoutBusyBoxCheck",
            "detectRootManagementApps",
            "detectPotentiallyDangerousApps",
            "detectTestKeys",
            "checkForBusyBoxBinary",
            "checkForSuBinary",
            "checkForMagiskBinary",
            "checkSuExists",
            "checkForRWPaths",
            "checkForDangerousProps",
            "checkForRootNative",
            "detectRootCloakingApps"
          ];
          for (const method of methodsToBypass) {
            try {
              RootBeer[method].implementation = function() {
                utils_1.HookUtils.sendInfo(`RootBeer.${method} bypassed`);
                return false;
              };
            } catch (e) {
            }
          }
        }
        const JailMonkey = utils_1.HookUtils.safeGetJavaClass("com.gantix.JailMonkey.JailMonkeyModule");
        if (JailMonkey) {
          utils_1.HookUtils.sendInfo("JailMonkey library detected - applying bypasses");
          try {
            JailMonkey.isJailBroken.implementation = function() {
              utils_1.HookUtils.sendInfo("JailMonkey.isJailBroken bypassed");
              return false;
            };
          } catch (e) {
          }
          try {
            JailMonkey.canMockLocation.implementation = function() {
              utils_1.HookUtils.sendInfo("JailMonkey.canMockLocation bypassed");
              return false;
            };
          } catch (e) {
          }
          try {
            JailMonkey.isOnExternalStorage.implementation = function() {
              utils_1.HookUtils.sendInfo("JailMonkey.isOnExternalStorage bypassed");
              return false;
            };
          } catch (e) {
          }
        }
      }
      bypassSystemProperties() {
        const systemPropertyGet = Module.findExportByName("libc.so", "__system_property_get");
        if (systemPropertyGet) {
          Interceptor.attach(systemPropertyGet, {
            onEnter: function(args) {
              this.name = args[0].readCString();
              this.value = args[1];
            },
            onLeave: function(retval) {
              const name = this.name;
              if (name === "ro.debuggable") {
                this.value.writeUtf8String("0");
                utils_1.HookUtils.sendInfo("System property ro.debuggable spoofed to 0");
              } else if (name === "ro.secure") {
                this.value.writeUtf8String("1");
                utils_1.HookUtils.sendInfo("System property ro.secure spoofed to 1");
              } else if (name === "ro.build.type") {
                this.value.writeUtf8String("user");
                utils_1.HookUtils.sendInfo("System property ro.build.type spoofed to user");
              } else if (name === "ro.build.tags") {
                this.value.writeUtf8String("release-keys");
                utils_1.HookUtils.sendInfo("System property ro.build.tags spoofed to release-keys");
              }
            }
          });
        }
      }
    };
    exports.RootDetectionHooks = RootDetectionHooks;
  }
});

// dist/hooks/frida-detection.js
var require_frida_detection = __commonJS({
  "dist/hooks/frida-detection.js"(exports) {
    "use strict";
    init_node_globals();
    Object.defineProperty(exports, "__esModule", { value: true });
    exports.FridaDetectionHooks = void 0;
    var utils_1 = require_utils();
    var FRIDA_PATHS = [
      "frida",
      "frida-server",
      "re.frida.server",
      "/data/local/tmp/frida",
      "/data/local/tmp/re.frida.server",
      "linjector",
      "libfrida",
      "frida-agent",
      "frida-gadget",
      "gum-js-loop",
      "gmain"
    ];
    var FRIDA_PORT = 27042;
    var FRIDA_STRINGS = [
      "frida",
      "LIBFRIDA",
      "frida-server",
      "frida-agent",
      "frida-gadget",
      "gum-js-loop",
      "linjector"
    ];
    var FridaDetectionHooks = class {
      constructor(config = {}) {
        this.config = Object.assign({ enabled: true, bypass_file_checks: true, bypass_port_checks: true, bypass_maps_checks: true, bypass_named_pipe_checks: true, bypass_string_checks: true }, config);
      }
      initialize() {
        if (!this.config.enabled) {
          utils_1.HookUtils.sendInfo("Frida detection bypass hooks disabled");
          return;
        }
        utils_1.HookUtils.sendInfo("Initializing Frida detection bypass hooks...");
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
        utils_1.HookUtils.sendInfo("Frida detection bypass hooks initialized");
      }
      bypassFridaFileChecks() {
        const File = utils_1.HookUtils.safeGetJavaClass("java.io.File");
        if (File) {
          const originalExists = File.exists;
          File.exists.implementation = function() {
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
        const fopen = Module.findExportByName("libc.so", "fopen");
        if (fopen) {
          Interceptor.attach(fopen, {
            onEnter: function(args) {
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
            onLeave: function(retval) {
              if (this.blocked) {
                retval.replace(ptr(0));
              }
            }
          });
        }
      }
      bypassFridaPortChecks() {
        const connect = Module.findExportByName("libc.so", "connect");
        if (connect) {
          Interceptor.attach(connect, {
            onEnter: function(args) {
              const sockaddr = args[1];
              const family = sockaddr.readU16();
              if (family === 2) {
                const port = sockaddr.add(2).readU8() << 8 | sockaddr.add(3).readU8();
                if (port === FRIDA_PORT) {
                  utils_1.HookUtils.sendInfo(`Frida port detection bypassed (port ${FRIDA_PORT})`);
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
        const Socket = utils_1.HookUtils.safeGetJavaClass("java.net.Socket");
        if (Socket) {
          try {
            Socket.connect.overload("java.net.SocketAddress", "int").implementation = function(endpoint, timeout) {
              const endpointStr = String(endpoint.toString());
              if (endpointStr.includes(`:${FRIDA_PORT}`)) {
                utils_1.HookUtils.sendInfo(`Socket.connect to Frida port bypassed`);
                const SocketException = Java.use("java.net.SocketException");
                throw SocketException.$new("Connection refused");
              }
              return this.connect(endpoint, timeout);
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`Socket.connect hook failed: ${e}`);
          }
        }
      }
      bypassMapsChecks() {
        const BufferedReader = utils_1.HookUtils.safeGetJavaClass("java.io.BufferedReader");
        if (BufferedReader) {
          BufferedReader.readLine.implementation = function() {
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
        const openPtr = Module.findExportByName("libc.so", "open");
        if (openPtr) {
          Interceptor.attach(openPtr, {
            onEnter: function(args) {
              const path = args[0].readCString();
              if (path && (path.includes("/proc/self/maps") || path.includes("/proc/") && path.includes("/maps"))) {
                utils_1.HookUtils.sendInfo(`/proc/maps access detected: ${path}`);
                this.isMaps = true;
              }
            }
          });
        }
      }
      bypassNamedPipeChecks() {
        const access = Module.findExportByName("libc.so", "access");
        if (access) {
          Interceptor.attach(access, {
            onEnter: function(args) {
              const path = args[0].readCString();
              if (path) {
                if (path.includes("linjector") || path.includes("frida")) {
                  utils_1.HookUtils.sendInfo(`Named pipe access blocked: ${path}`);
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
      bypassStringChecks() {
        const String2 = utils_1.HookUtils.safeGetJavaClass("java.lang.String");
        if (String2) {
          try {
            const originalContains = String2.contains;
            String2.contains.implementation = function(s) {
              if (s) {
                const searchStr = String2(s).toLowerCase();
                for (const indicator of FRIDA_STRINGS) {
                  if (searchStr === indicator.toLowerCase()) {
                    utils_1.HookUtils.sendInfo(`String.contains bypassed for: ${searchStr}`);
                    return false;
                  }
                }
              }
              return originalContains.call(this, s);
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`String.contains hook failed: ${e}`);
          }
        }
        const strstr = Module.findExportByName("libc.so", "strstr");
        if (strstr) {
          Interceptor.attach(strstr, {
            onEnter: function(args) {
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
            onLeave: function(retval) {
              if (this.blocked) {
                retval.replace(ptr(0));
              }
            }
          });
        }
      }
    };
    exports.FridaDetectionHooks = FridaDetectionHooks;
  }
});

// dist/hooks/emulator-detection.js
var require_emulator_detection = __commonJS({
  "dist/hooks/emulator-detection.js"(exports) {
    "use strict";
    init_node_globals();
    Object.defineProperty(exports, "__esModule", { value: true });
    exports.EmulatorDetectionHooks = void 0;
    var utils_1 = require_utils();
    var DEVICE_PROFILES = {
      pixel_4_xl: {
        MODEL: "Pixel 4 XL",
        MANUFACTURER: "Google",
        BRAND: "google",
        DEVICE: "coral",
        HARDWARE: "coral",
        PRODUCT: "coral",
        FINGERPRINT: "google/coral/coral:12/SP1A.210812.016.C1/7676683:user/release-keys",
        BOARD: "coral"
      },
      pixel_6_pro: {
        MODEL: "Pixel 6 Pro",
        MANUFACTURER: "Google",
        BRAND: "google",
        DEVICE: "raven",
        HARDWARE: "raven",
        PRODUCT: "raven",
        FINGERPRINT: "google/raven/raven:13/TP1A.220624.021/8877034:user/release-keys",
        BOARD: "raven"
      },
      samsung_s21: {
        MODEL: "SM-G991B",
        MANUFACTURER: "samsung",
        BRAND: "samsung",
        DEVICE: "o1s",
        HARDWARE: "exynos2100",
        PRODUCT: "o1sxeea",
        FINGERPRINT: "samsung/o1sxeea/o1s:12/SP1A.210812.016/G991BXXU4BULF:user/release-keys",
        BOARD: "exynos2100"
      },
      oneplus_9: {
        MODEL: "LE2115",
        MANUFACTURER: "OnePlus",
        BRAND: "OnePlus",
        DEVICE: "lemonade",
        HARDWARE: "qcom",
        PRODUCT: "OnePlus9",
        FINGERPRINT: "OnePlus/OnePlus9/OnePlus9:12/SKQ1.211113.001/R.202205090123:user/release-keys",
        BOARD: "lahaina"
      },
      generic: {
        MODEL: "SM-G950F",
        MANUFACTURER: "samsung",
        BRAND: "samsung",
        DEVICE: "dreamlte",
        HARDWARE: "samsungexynos8895",
        PRODUCT: "dreamltexx",
        FINGERPRINT: "samsung/dreamltexx/dreamlte:9/PPR1.180610.011/G950FXXS9DSK1:user/release-keys",
        BOARD: "exynos8895"
      }
    };
    var EMULATOR_INDICATORS = {
      models: ["sdk", "google_sdk", "Emulator", "Android SDK", "Genymotion", "generic"],
      devices: ["generic", "generic_x86", "vbox86p", "goldfish"],
      hardware: ["goldfish", "ranchu", "vbox86", "nox"],
      products: ["sdk", "google_sdk", "sdk_x86", "vbox86p", "emulator"],
      manufacturers: ["Genymotion", "unknown", "Android"],
      fingerprints: ["generic", "unknown", "google/sdk_gphone", "sdk_gphone_x86"]
    };
    var EmulatorDetectionHooks = class {
      constructor(config = {}) {
        this.config = Object.assign({ enabled: true, device_profile: "pixel_4_xl", bypass_telephony: true, bypass_sensors: false }, config);
        this.profile = DEVICE_PROFILES[this.config.device_profile || "generic"] || DEVICE_PROFILES.generic;
        if (this.config.custom_model)
          this.profile.MODEL = this.config.custom_model;
        if (this.config.custom_manufacturer)
          this.profile.MANUFACTURER = this.config.custom_manufacturer;
        if (this.config.custom_brand)
          this.profile.BRAND = this.config.custom_brand;
        if (this.config.custom_device)
          this.profile.DEVICE = this.config.custom_device;
        if (this.config.custom_hardware)
          this.profile.HARDWARE = this.config.custom_hardware;
        if (this.config.custom_fingerprint)
          this.profile.FINGERPRINT = this.config.custom_fingerprint;
        if (this.config.custom_product)
          this.profile.PRODUCT = this.config.custom_product;
      }
      initialize() {
        if (!this.config.enabled) {
          utils_1.HookUtils.sendInfo("Emulator detection bypass hooks disabled");
          return;
        }
        utils_1.HookUtils.sendInfo(`Initializing emulator detection bypass (profile: ${this.config.device_profile})...`);
        this.bypassBuildProperties();
        this.bypassSystemProperties();
        if (this.config.bypass_telephony) {
          this.bypassTelephonyChecks();
        }
        utils_1.HookUtils.sendInfo("Emulator detection bypass hooks initialized");
      }
      isEmulatorValue(value, type) {
        const indicators = EMULATOR_INDICATORS[type];
        const valueLower = value.toLowerCase();
        return indicators.some((ind) => valueLower.includes(ind.toLowerCase()));
      }
      bypassBuildProperties() {
        const Build = utils_1.HookUtils.safeGetJavaClass("android.os.Build");
        if (!Build)
          return;
        const propsToSpoof = ["MODEL", "MANUFACTURER", "BRAND", "DEVICE", "HARDWARE", "PRODUCT", "FINGERPRINT", "BOARD"];
        for (const prop of propsToSpoof) {
          try {
            const field = Build[prop];
            if (field && field.value) {
              const originalValue = String(field.value);
              const newValue = this.profile[prop];
              if (newValue && originalValue !== newValue) {
                field.value = newValue;
                utils_1.HookUtils.sendChangelog({
                  property: `Build.${prop}`,
                  oldValue: originalValue,
                  newValue
                });
                utils_1.HookUtils.sendInfo(`Build.${prop} spoofed: ${originalValue} -> ${newValue}`);
              }
            }
          } catch (e) {
            utils_1.HookUtils.sendDebug(`Failed to spoof Build.${prop}: ${e}`);
          }
        }
        try {
          Build.getSerial.implementation = function() {
            const fakeSerial = "RF8M33XXXXX";
            utils_1.HookUtils.sendInfo(`Build.getSerial spoofed to ${fakeSerial}`);
            return fakeSerial;
          };
        } catch (e) {
        }
      }
      bypassSystemProperties() {
        const propertyGet = Module.findExportByName("libc.so", "__system_property_get");
        if (!propertyGet)
          return;
        const profile = this.profile;
        Interceptor.attach(propertyGet, {
          onEnter: function(args) {
            this.name = args[0].readCString();
            this.value = args[1];
          },
          onLeave: function(retval) {
            const name = this.name;
            const mappings = {
              "ro.product.model": profile.MODEL,
              "ro.product.manufacturer": profile.MANUFACTURER,
              "ro.product.brand": profile.BRAND,
              "ro.product.device": profile.DEVICE,
              "ro.product.board": profile.BOARD,
              "ro.hardware": profile.HARDWARE,
              "ro.build.fingerprint": profile.FINGERPRINT,
              "ro.build.product": profile.PRODUCT,
              "ro.kernel.qemu": "0",
              "ro.kernel.qemu.gles": "",
              "ro.boot.qemu": "0",
              "init.svc.qemud": "",
              "init.svc.qemu-props": "",
              "ro.bootloader": "unknown",
              "ro.bootmode": "unknown",
              "ro.secure": "1",
              "ro.debuggable": "0"
            };
            if (name && mappings[name]) {
              this.value.writeUtf8String(mappings[name]);
              utils_1.HookUtils.sendInfo(`System property ${name} spoofed`);
            }
          }
        });
      }
      bypassTelephonyChecks() {
        const TelephonyManager = utils_1.HookUtils.safeGetJavaClass("android.telephony.TelephonyManager");
        if (!TelephonyManager)
          return;
        try {
          TelephonyManager.getDeviceId.overload().implementation = function() {
            const fakeId = "358240051111110";
            utils_1.HookUtils.sendInfo(`TelephonyManager.getDeviceId spoofed to ${fakeId}`);
            return fakeId;
          };
        } catch (e) {
        }
        try {
          TelephonyManager.getDeviceId.overload("int").implementation = function(slot) {
            const fakeId = "358240051111110";
            utils_1.HookUtils.sendInfo(`TelephonyManager.getDeviceId(${slot}) spoofed`);
            return fakeId;
          };
        } catch (e) {
        }
        try {
          TelephonyManager.getSubscriberId.implementation = function() {
            const fakeImsi = "310260000000000";
            utils_1.HookUtils.sendInfo(`TelephonyManager.getSubscriberId spoofed`);
            return fakeImsi;
          };
        } catch (e) {
        }
        try {
          TelephonyManager.getLine1Number.implementation = function() {
            const fakeNumber = "+15551234567";
            utils_1.HookUtils.sendInfo(`TelephonyManager.getLine1Number spoofed`);
            return fakeNumber;
          };
        } catch (e) {
        }
        try {
          TelephonyManager.getSimSerialNumber.implementation = function() {
            const fakeSim = "89014103211118510720";
            utils_1.HookUtils.sendInfo(`TelephonyManager.getSimSerialNumber spoofed`);
            return fakeSim;
          };
        } catch (e) {
        }
        try {
          TelephonyManager.getNetworkOperatorName.implementation = function() {
            utils_1.HookUtils.sendInfo(`TelephonyManager.getNetworkOperatorName spoofed`);
            return "T-Mobile";
          };
        } catch (e) {
        }
        try {
          TelephonyManager.getNetworkOperator.implementation = function() {
            utils_1.HookUtils.sendInfo(`TelephonyManager.getNetworkOperator spoofed`);
            return "310260";
          };
        } catch (e) {
        }
        try {
          TelephonyManager.getPhoneType.implementation = function() {
            utils_1.HookUtils.sendInfo(`TelephonyManager.getPhoneType spoofed to GSM`);
            return 1;
          };
        } catch (e) {
        }
        try {
          TelephonyManager.getSimState.implementation = function() {
            utils_1.HookUtils.sendInfo(`TelephonyManager.getSimState spoofed to READY`);
            return 5;
          };
        } catch (e) {
        }
      }
    };
    exports.EmulatorDetectionHooks = EmulatorDetectionHooks;
  }
});

// dist/hooks/debug-detection.js
var require_debug_detection = __commonJS({
  "dist/hooks/debug-detection.js"(exports) {
    "use strict";
    init_node_globals();
    Object.defineProperty(exports, "__esModule", { value: true });
    exports.DebugDetectionHooks = void 0;
    var utils_1 = require_utils();
    var DebugDetectionHooks = class {
      constructor(config = {}) {
        this.config = Object.assign({ enabled: true, bypass_debug_class: true, bypass_tracer_pid: true, bypass_debuggable_flag: true, bypass_timing_checks: false }, config);
      }
      initialize() {
        if (!this.config.enabled) {
          utils_1.HookUtils.sendInfo("Debug detection bypass hooks disabled");
          return;
        }
        utils_1.HookUtils.sendInfo("Initializing debug detection bypass hooks...");
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
        utils_1.HookUtils.sendInfo("Debug detection bypass hooks initialized");
      }
      bypassDebugClass() {
        const Debug = utils_1.HookUtils.safeGetJavaClass("android.os.Debug");
        if (!Debug)
          return;
        try {
          Debug.isDebuggerConnected.implementation = function() {
            utils_1.HookUtils.sendInfo("Debug.isDebuggerConnected bypassed (returns false)");
            return false;
          };
        } catch (e) {
          utils_1.HookUtils.sendDebug(`Debug.isDebuggerConnected hook failed: ${e}`);
        }
        try {
          Debug.waitingForDebugger.implementation = function() {
            utils_1.HookUtils.sendInfo("Debug.waitingForDebugger bypassed (returns false)");
            return false;
          };
        } catch (e) {
          utils_1.HookUtils.sendDebug(`Debug.waitingForDebugger hook failed: ${e}`);
        }
      }
      bypassTracerPid() {
        const BufferedReader = utils_1.HookUtils.safeGetJavaClass("java.io.BufferedReader");
        if (BufferedReader) {
          const originalReadLine = BufferedReader.readLine;
          BufferedReader.readLine.implementation = function() {
            const line = originalReadLine.call(this);
            if (line) {
              const lineStr = String(line);
              if (lineStr.startsWith("TracerPid:")) {
                utils_1.HookUtils.sendInfo("TracerPid check bypassed (returns 0)");
                return "TracerPid:	0";
              }
            }
            return line;
          };
        }
        const fopenPtr = Module.findExportByName("libc.so", "fopen");
        if (fopenPtr) {
          Interceptor.attach(fopenPtr, {
            onEnter: function(args) {
              const path = args[0].readCString();
              if (path && (path.includes("/proc/self/status") || path.includes("/proc/") && path.includes("/status"))) {
                utils_1.HookUtils.sendInfo(`Detected /proc/*/status access: ${path}`);
                this.isStatus = true;
              }
            }
          });
        }
        const ptrace = Module.findExportByName("libc.so", "ptrace");
        if (ptrace) {
          Interceptor.attach(ptrace, {
            onEnter: function(args) {
              const request = args[0].toInt32();
              if (request === 0) {
                utils_1.HookUtils.sendInfo("ptrace(PTRACE_TRACEME) detected - allowing");
              }
            },
            onLeave: function(retval) {
              const ret = retval.toInt32();
              if (ret === -1) {
                utils_1.HookUtils.sendInfo("ptrace returned -1, replacing with 0");
                retval.replace(ptr(0));
              }
            }
          });
        }
      }
      bypassDebuggableFlag() {
        const ApplicationInfo = utils_1.HookUtils.safeGetJavaClass("android.content.pm.ApplicationInfo");
        if (!ApplicationInfo)
          return;
        const PackageManager = utils_1.HookUtils.safeGetJavaClass("android.app.ApplicationPackageManager");
        if (PackageManager) {
          try {
            PackageManager.getApplicationInfo.overload("java.lang.String", "int").implementation = function(packageName, flags) {
              const appInfo = this.getApplicationInfo(packageName, flags);
              const FLAG_DEBUGGABLE = 2;
              if ((appInfo.flags.value & FLAG_DEBUGGABLE) !== 0) {
                utils_1.HookUtils.sendInfo(`Cleared FLAG_DEBUGGABLE for ${packageName}`);
                appInfo.flags.value &= ~FLAG_DEBUGGABLE;
              }
              return appInfo;
            };
          } catch (e) {
            utils_1.HookUtils.sendDebug(`getApplicationInfo hook failed: ${e}`);
          }
        }
        try {
          Java.choose("android.content.pm.ApplicationInfo", {
            onMatch: function(instance) {
              const FLAG_DEBUGGABLE = 2;
              if ((instance.flags.value & FLAG_DEBUGGABLE) !== 0) {
                instance.flags.value &= ~FLAG_DEBUGGABLE;
                utils_1.HookUtils.sendInfo("Cleared FLAG_DEBUGGABLE from ApplicationInfo instance");
              }
            },
            onComplete: function() {
            }
          });
        } catch (e) {
          utils_1.HookUtils.sendDebug(`ApplicationInfo Java.choose failed: ${e}`);
        }
      }
      bypassTimingChecks() {
        const System = utils_1.HookUtils.safeGetJavaClass("java.lang.System");
        if (System) {
          utils_1.HookUtils.sendInfo("WARNING: Timing check bypass enabled - may affect app behavior");
          try {
            const originalNanoTime = System.nanoTime;
            System.nanoTime.implementation = function() {
              return originalNanoTime.call(this);
            };
          } catch (e) {
          }
        }
        const clockGettime = Module.findExportByName("libc.so", "clock_gettime");
        if (clockGettime) {
          Interceptor.attach(clockGettime, {
            onEnter: function(args) {
              const clockId = args[0].toInt32();
              if (clockId === 1) {
              }
            }
          });
        }
      }
    };
    exports.DebugDetectionHooks = DebugDetectionHooks;
  }
});

// dist/trigdroid_bypass_rpc.js
var require_trigdroid_bypass_rpc = __commonJS({
  "dist/trigdroid_bypass_rpc.js"(exports) {
    init_node_globals();
    Object.defineProperty(exports, "__esModule", { value: true });
    var utils_1 = require_utils();
    var ssl_unpinning_1 = require_ssl_unpinning();
    var root_detection_1 = require_root_detection();
    var frida_detection_1 = require_frida_detection();
    var emulator_detection_1 = require_emulator_detection();
    var debug_detection_1 = require_debug_detection();
    var sslHooks = null;
    var rootHooks = null;
    var fridaHooks = null;
    var emulatorHooks = null;
    var debugHooks = null;
    var loadedAt = (/* @__PURE__ */ new Date()).toISOString();
    rpc.exports = {
      enableSSLUnpinning: function(config) {
        if (sslHooks !== null) {
          return { status: "already_enabled", type: "ssl_unpinning" };
        }
        try {
          Java.perform(() => {
            sslHooks = new ssl_unpinning_1.SSLUnpinningHooks(Object.assign({ enabled: true }, config));
            sslHooks.initialize();
          });
          return { status: "enabled", type: "ssl_unpinning" };
        } catch (e) {
          return { status: "error", type: "ssl_unpinning", message: String(e) };
        }
      },
      enableRootBypass: function(config) {
        if (rootHooks !== null) {
          return { status: "already_enabled", type: "root_detection" };
        }
        try {
          Java.perform(() => {
            rootHooks = new root_detection_1.RootDetectionHooks(Object.assign({ enabled: true }, config));
            rootHooks.initialize();
          });
          return { status: "enabled", type: "root_detection" };
        } catch (e) {
          return { status: "error", type: "root_detection", message: String(e) };
        }
      },
      enableFridaBypass: function(config) {
        if (fridaHooks !== null) {
          return { status: "already_enabled", type: "frida_detection" };
        }
        try {
          Java.perform(() => {
            fridaHooks = new frida_detection_1.FridaDetectionHooks(Object.assign({ enabled: true }, config));
            fridaHooks.initialize();
          });
          return { status: "enabled", type: "frida_detection" };
        } catch (e) {
          return { status: "error", type: "frida_detection", message: String(e) };
        }
      },
      enableEmulatorBypass: function(config) {
        if (emulatorHooks !== null) {
          return { status: "already_enabled", type: "emulator_detection" };
        }
        try {
          Java.perform(() => {
            emulatorHooks = new emulator_detection_1.EmulatorDetectionHooks(Object.assign({ enabled: true }, config));
            emulatorHooks.initialize();
          });
          return { status: "enabled", type: "emulator_detection" };
        } catch (e) {
          return { status: "error", type: "emulator_detection", message: String(e) };
        }
      },
      enableDebugBypass: function(config) {
        if (debugHooks !== null) {
          return { status: "already_enabled", type: "debug_detection" };
        }
        try {
          Java.perform(() => {
            debugHooks = new debug_detection_1.DebugDetectionHooks(Object.assign({ enabled: true }, config));
            debugHooks.initialize();
          });
          return { status: "enabled", type: "debug_detection" };
        } catch (e) {
          return { status: "error", type: "debug_detection", message: String(e) };
        }
      },
      enableBypasses: function(config) {
        const results = [];
        if (config.ssl) {
          const sslConfig = typeof config.ssl === "boolean" ? {} : config.ssl;
          results.push(rpc.exports.enableSSLUnpinning(sslConfig));
        }
        if (config.root) {
          const rootConfig = typeof config.root === "boolean" ? {} : config.root;
          results.push(rpc.exports.enableRootBypass(rootConfig));
        }
        if (config.frida) {
          const fridaConfig = typeof config.frida === "boolean" ? {} : config.frida;
          results.push(rpc.exports.enableFridaBypass(fridaConfig));
        }
        if (config.emulator) {
          const emulatorConfig = typeof config.emulator === "boolean" ? {} : config.emulator;
          results.push(rpc.exports.enableEmulatorBypass(emulatorConfig));
        }
        if (config.debug) {
          const debugConfig = typeof config.debug === "boolean" ? {} : config.debug;
          results.push(rpc.exports.enableDebugBypass(debugConfig));
        }
        return results;
      },
      getStatus: function() {
        return {
          ssl_unpinning: sslHooks !== null,
          root_detection: rootHooks !== null,
          frida_detection: fridaHooks !== null,
          emulator_detection: emulatorHooks !== null,
          debug_detection: debugHooks !== null,
          loaded_at: loadedAt
        };
      },
      getDeviceProfiles: function() {
        return ["pixel_4_xl", "pixel_6_pro", "samsung_s21", "oneplus_9", "generic"];
      },
      isSpawnMode: function() {
        try {
          const ActivityThread = Java.use("android.app.ActivityThread");
          const currentApp = ActivityThread.currentApplication();
          return currentApp === null;
        } catch (e) {
          return false;
        }
      },
      getVersion: function() {
        return {
          script: "trigdroid_bypass_rpc",
          version: "1.0.0",
          loadedAt
        };
      }
    };
    send("TrigDroid bypass script loaded (RPC mode) - awaiting configuration via RPC exports");
    utils_1.HookUtils.sendInfo("Available RPC methods: enableSSLUnpinning, enableRootBypass, enableFridaBypass, enableEmulatorBypass, enableDebugBypass, enableBypasses, getStatus");
  }
});
export default require_trigdroid_bypass_rpc();

✄
{
  "version": 3,
  "sources": ["frida-builtins:/node-globals.js", "dist/utils.js", "dist/hooks/ssl-unpinning.js", "dist/hooks/root-detection.js", "dist/hooks/frida-detection.js", "dist/hooks/emulator-detection.js", "dist/hooks/debug-detection.js", "dist/trigdroid_bypass_rpc.js"],
  "mappings": "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",
  "names": ["String"]
}
