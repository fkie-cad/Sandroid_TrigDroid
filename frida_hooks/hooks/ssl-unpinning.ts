/**
 * SSL/TLS Certificate Pinning Bypass hooks for TrigDroid.
 * Provides runtime bypass of common SSL pinning implementations.
 *
 * For authorized security testing and research purposes only.
 *
 * References and acknowledgments:
 * - httptoolkit/frida-interception-and-unpinning (MIT License)
 *   https://github.com/httptoolkit/frida-interception-and-unpinning
 * - Techniques based on android-certificate-unpinning.js and related files
 */

import { HookUtils } from '../utils';

/**
 * Configuration for SSL unpinning hooks.
 */
export interface SSLUnpinningConfig {
    enabled?: boolean;
    use_custom_cert?: boolean;
    custom_cert_path?: string;
    bypass_okhttp?: boolean;
    bypass_okhttp3?: boolean;
    bypass_trust_manager?: boolean;
    bypass_webview_client?: boolean;
    bypass_conscrypt?: boolean;
    bypass_network_security_config?: boolean;
    bypass_trustkit?: boolean;
    bypass_appcelerator?: boolean;
    bypass_phonegap?: boolean;
    bypass_ibm_worklight?: boolean;
    bypass_cwac_netsecurity?: boolean;
    bypass_cordova_advanced_http?: boolean;
    bypass_netty?: boolean;
    bypass_appmattus_ct?: boolean;
}

/**
 * SSL Unpinning Hooks class.
 *
 * Based on techniques from httptoolkit/frida-interception-and-unpinning.
 */
export class SSLUnpinningHooks {
    private config: SSLUnpinningConfig;

    constructor(config: SSLUnpinningConfig = {}) {
        this.config = {
            enabled: true,
            use_custom_cert: false,
            custom_cert_path: '/data/local/tmp/cert-der.crt',
            bypass_okhttp: true,
            bypass_okhttp3: true,
            bypass_trust_manager: true,
            bypass_webview_client: true,
            bypass_conscrypt: true,
            bypass_network_security_config: true,
            bypass_trustkit: true,
            bypass_appcelerator: true,
            bypass_phonegap: true,
            bypass_ibm_worklight: true,
            bypass_cwac_netsecurity: true,
            bypass_cordova_advanced_http: true,
            bypass_netty: true,
            bypass_appmattus_ct: true,
            ...config
        };
    }

    /**
     * Initialize all SSL unpinning hooks.
     */
    public initialize(): void {
        if (!this.config.enabled) {
            HookUtils.sendInfo('SSL Unpinning hooks disabled');
            return;
        }

        HookUtils.sendInfo('Initializing SSL unpinning hooks...');

        // Core Android hooks
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

        // OkHttp hooks
        if (this.config.bypass_okhttp) {
            this.bypassOkHttpV2();
        }

        if (this.config.bypass_okhttp3) {
            this.bypassOkHttp3();
        }

        // WebView hooks
        if (this.config.bypass_webview_client) {
            this.bypassWebViewClient();
        }

        // Third-party library hooks
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

        HookUtils.sendInfo('SSL unpinning hooks initialized');
    }

    /**
     * Bypass HttpsURLConnection hostname verification.
     * Reference: httptoolkit android-certificate-unpinning.js - HttpsURLConnection hooks
     */
    private bypassHttpsURLConnection(): void {
        const HttpsURLConnection = HookUtils.safeGetJavaClass('javax.net.ssl.HttpsURLConnection');
        if (!HttpsURLConnection) return;

        try {
            HttpsURLConnection.setHostnameVerifier.implementation = function(verifier: any) {
                HookUtils.sendInfo('HttpsURLConnection.setHostnameVerifier bypassed');
            };
        } catch (e) {
            HookUtils.sendDebug(`HttpsURLConnection.setHostnameVerifier hook failed: ${e}`);
        }

        try {
            HttpsURLConnection.setSSLSocketFactory.implementation = function(factory: any) {
                HookUtils.sendInfo('HttpsURLConnection.setSSLSocketFactory bypassed');
            };
        } catch (e) {
            HookUtils.sendDebug(`HttpsURLConnection.setSSLSocketFactory hook failed: ${e}`);
        }
    }

    /**
     * Bypass SSLContext.init with custom TrustManager.
     * Reference: httptoolkit android-certificate-unpinning.js - SSLContext hooks
     */
    private bypassSSLContext(): void {
        const SSLContext = HookUtils.safeGetJavaClass('javax.net.ssl.SSLContext');
        if (!SSLContext) return;

        try {
            const X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
            const TrustAllCerts = Java.registerClass({
                name: 'com.trigdroid.bypass.TrustAllCerts',
                implements: [X509TrustManager],
                methods: {
                    checkClientTrusted: function(chain: any, authType: any) {},
                    checkServerTrusted: function(chain: any, authType: any) {
                        HookUtils.sendInfo('TrustManager.checkServerTrusted bypassed');
                    },
                    getAcceptedIssuers: function() {
                        return [];
                    }
                }
            });

            SSLContext.init.overload(
                '[Ljavax.net.ssl.KeyManager;',
                '[Ljavax.net.ssl.TrustManager;',
                'java.security.SecureRandom'
            ).implementation = function(keyManagers: any, trustManagers: any, secureRandom: any) {
                HookUtils.sendInfo('SSLContext.init intercepted - injecting permissive TrustManager');
                const trustAllArray = Java.array('javax.net.ssl.TrustManager', [TrustAllCerts.$new()]);
                this.init(keyManagers, trustAllArray, secureRandom);

                HookUtils.sendChangelog({
                    property: 'SSLContext.init',
                    oldValue: 'original TrustManager',
                    newValue: 'TrustAllCerts (bypass)'
                });
            };
        } catch (e) {
            HookUtils.sendDebug(`SSLContext hook failed: ${e}`);
        }
    }

    /**
     * Bypass Conscrypt CertPinManager.
     * Reference: httptoolkit android-certificate-unpinning.js - Conscrypt hooks
     * Makes isChainValid() return true and checkChainPinning() a no-op.
     */
    private bypassConscrypt(): void {
        // TrustManagerImpl verifyChain (Android 7+)
        const TrustManagerImpl = HookUtils.safeGetJavaClass('com.android.org.conscrypt.TrustManagerImpl');
        if (TrustManagerImpl) {
            try {
                TrustManagerImpl.verifyChain.implementation = function(
                    untrustedChain: any,
                    trustAnchorChain: any,
                    host: any,
                    clientAuth: any,
                    ocspData: any,
                    tlsSctData: any
                ) {
                    HookUtils.sendInfo(`Conscrypt TrustManagerImpl.verifyChain bypassed for ${host}`);
                    return untrustedChain;
                };
            } catch (e) {
                HookUtils.sendDebug(`TrustManagerImpl.verifyChain hook failed: ${e}`);
            }
        }

        // CertPinManager
        const CertPinManager = HookUtils.safeGetJavaClass('com.android.org.conscrypt.CertPinManager');
        if (CertPinManager) {
            try {
                CertPinManager.isChainValid.overload('java.lang.String', 'java.util.List').implementation =
                    function(hostname: any, chain: any) {
                        HookUtils.sendInfo(`Conscrypt CertPinManager.isChainValid bypassed for ${hostname}`);
                        return true;
                    };
            } catch (e) {
                HookUtils.sendDebug(`CertPinManager.isChainValid hook failed: ${e}`);
            }

            try {
                CertPinManager.checkChainPinning.implementation = function(hostname: any, chain: any) {
                    HookUtils.sendInfo(`Conscrypt CertPinManager.checkChainPinning bypassed for ${hostname}`);
                };
            } catch (e) {
                HookUtils.sendDebug(`CertPinManager.checkChainPinning hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass NetworkSecurityConfig pin sets.
     * Reference: httptoolkit android-certificate-unpinning.js - NetworkSecurityConfig hooks
     * Replaces pin sets with empty sets during initialization.
     */
    private bypassNetworkSecurityConfig(): void {
        const NetworkSecurityConfig = HookUtils.safeGetJavaClass(
            'android.security.net.config.NetworkSecurityConfig'
        );
        if (!NetworkSecurityConfig) return;

        try {
            // Hook the Builder to remove pin sets
            const Builder = HookUtils.safeGetJavaClass(
                'android.security.net.config.NetworkSecurityConfig$Builder'
            );
            if (Builder) {
                Builder.setPinSet.implementation = function(pinSet: any) {
                    HookUtils.sendInfo('NetworkSecurityConfig.Builder.setPinSet bypassed');
                    // Don't set any pins
                    return this;
                };
            }
        } catch (e) {
            HookUtils.sendDebug(`NetworkSecurityConfig hook failed: ${e}`);
        }
    }

    /**
     * Bypass OkHttp v2 (com.android.okhttp).
     * Reference: httptoolkit android-certificate-unpinning.js - OkHttp v2 hooks
     */
    private bypassOkHttpV2(): void {
        const OkHostnameVerifier = HookUtils.safeGetJavaClass(
            'com.android.okhttp.internal.tls.OkHostnameVerifier'
        );
        if (OkHostnameVerifier) {
            try {
                OkHostnameVerifier.verify.overload('java.lang.String', 'java.security.cert.X509Certificate')
                    .implementation = function(hostname: any, certificate: any) {
                        HookUtils.sendInfo(`OkHttp v2 hostname verification bypassed for ${hostname}`);
                        return true;
                    };
            } catch (e) {
                HookUtils.sendDebug(`OkHttp v2 verify hook failed: ${e}`);
            }
        }

        // OkHttp Address replacement
        const Address = HookUtils.safeGetJavaClass('com.android.okhttp.Address');
        if (Address) {
            try {
                Address.$init.overload(
                    'java.lang.String', 'int',
                    'com.android.okhttp.Dns',
                    'javax.net.SocketFactory',
                    'javax.net.ssl.SSLSocketFactory',
                    'javax.net.ssl.HostnameVerifier',
                    'com.android.okhttp.CertificatePinner',
                    'com.android.okhttp.Authenticator',
                    'java.net.Proxy',
                    'java.util.List',
                    'java.util.List',
                    'java.net.ProxySelector'
                ).implementation = function(
                    uriHost: any, uriPort: any, dns: any, socketFactory: any,
                    sslSocketFactory: any, hostnameVerifier: any, certificatePinner: any,
                    authenticator: any, proxy: any, protocols: any, connectionSpecs: any, proxySelector: any
                ) {
                    HookUtils.sendInfo('OkHttp v2 Address constructor bypassed');
                    // Use default verifier and pinner
                    const CertificatePinner = Java.use('com.android.okhttp.CertificatePinner');
                    return this.$init(
                        uriHost, uriPort, dns, socketFactory, sslSocketFactory,
                        null, CertificatePinner.DEFAULT.value,
                        authenticator, proxy, protocols, connectionSpecs, proxySelector
                    );
                };
            } catch (e) {
                HookUtils.sendDebug(`OkHttp v2 Address hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass OkHttp3 CertificatePinner.
     * Reference: httptoolkit android-certificate-unpinning.js - OkHttp v3 hooks
     */
    private bypassOkHttp3(): void {
        const CertificatePinner = HookUtils.safeGetJavaClass('okhttp3.CertificatePinner');
        if (CertificatePinner) {
            // Try all known overloads of check()
            const checkOverloads = [
                ['java.lang.String', 'java.util.List'],
                ['java.lang.String', '[Ljava.security.cert.Certificate;'],
                ['java.lang.String', 'java.util.function.Supplier']
            ];

            for (const overload of checkOverloads) {
                try {
                    CertificatePinner.check.overload(...overload).implementation = function() {
                        HookUtils.sendInfo(`OkHttp3 CertificatePinner.check bypassed for ${arguments[0]}`);
                    };
                } catch (e) {
                    // Overload not found, continue to next
                }
            }

            // Also try check$ variants (Kotlin)
            try {
                CertificatePinner['check$okhttp'].implementation = function() {
                    HookUtils.sendInfo(`OkHttp3 CertificatePinner.check$okhttp bypassed`);
                };
            } catch (e) {
                // Not found
            }
        }

        // Bypass Builder.certificatePinner()
        const Builder = HookUtils.safeGetJavaClass('okhttp3.OkHttpClient$Builder');
        if (Builder) {
            try {
                Builder.certificatePinner.implementation = function(pinner: any) {
                    HookUtils.sendInfo('OkHttp3 Builder.certificatePinner bypassed');
                    return this;
                };
            } catch (e) {
                HookUtils.sendDebug(`OkHttp3 Builder hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass WebViewClient SSL errors.
     * Reference: httptoolkit android-certificate-unpinning.js - WebViewClient hooks
     */
    private bypassWebViewClient(): void {
        const WebViewClient = HookUtils.safeGetJavaClass('android.webkit.WebViewClient');
        if (!WebViewClient) return;

        try {
            WebViewClient.onReceivedSslError.implementation = function(
                view: any, handler: any, error: any
            ) {
                HookUtils.sendInfo(`WebViewClient SSL error bypassed: ${error.toString()}`);
                handler.proceed();
            };
        } catch (e) {
            HookUtils.sendDebug(`WebViewClient hook failed: ${e}`);
        }
    }

    /**
     * Bypass TrustKit certificate pinning.
     * Reference: httptoolkit android-certificate-unpinning.js - TrustKit hooks
     */
    private bypassTrustKit(): void {
        const TrustKit = HookUtils.safeGetJavaClass('com.datatheorem.android.trustkit.pinning.OkHostnameVerifier');
        if (TrustKit) {
            try {
                TrustKit.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession')
                    .implementation = function(hostname: any, session: any) {
                        HookUtils.sendInfo(`TrustKit hostname verification bypassed for ${hostname}`);
                        return true;
                    };
            } catch (e) {
                HookUtils.sendDebug(`TrustKit hook failed: ${e}`);
            }
        }

        const PinningTrustManager = HookUtils.safeGetJavaClass(
            'com.datatheorem.android.trustkit.pinning.PinningTrustManager'
        );
        if (PinningTrustManager) {
            try {
                PinningTrustManager.checkServerTrusted.implementation = function(
                    chain: any, authType: any
                ) {
                    HookUtils.sendInfo('TrustKit PinningTrustManager bypassed');
                };
            } catch (e) {
                HookUtils.sendDebug(`TrustKit TrustManager hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass Appcelerator HTTPS certificate pinning.
     * Reference: httptoolkit android-certificate-unpinning.js - Appcelerator hooks
     */
    private bypassAppcelerator(): void {
        const PinningTrustManager = HookUtils.safeGetJavaClass(
            'appcelerator.https.PinningTrustManager'
        );
        if (PinningTrustManager) {
            try {
                PinningTrustManager.checkServerTrusted.implementation = function(
                    chain: any, authType: any
                ) {
                    HookUtils.sendInfo('Appcelerator PinningTrustManager bypassed');
                };
            } catch (e) {
                HookUtils.sendDebug(`Appcelerator hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass PhoneGap SSL Certificate Checker.
     * Reference: httptoolkit android-certificate-unpinning.js - PhoneGap hooks
     */
    private bypassPhoneGap(): void {
        const SSLCertificateChecker = HookUtils.safeGetJavaClass(
            'nl.xservices.plugins.SSLCertificateChecker'
        );
        if (SSLCertificateChecker) {
            try {
                SSLCertificateChecker.execute.implementation = function(
                    action: any, args: any, callbackContext: any
                ) {
                    HookUtils.sendInfo('PhoneGap SSLCertificateChecker bypassed');
                    callbackContext.success('CONNECTION_SECURE');
                    return true;
                };
            } catch (e) {
                HookUtils.sendDebug(`PhoneGap hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass IBM WorkLight/MobileFirst certificate pinning.
     * Reference: httptoolkit android-certificate-unpinning.js - IBM WorkLight hooks
     */
    private bypassIBMWorkLight(): void {
        const WorkLightWebView = HookUtils.safeGetJavaClass(
            'com.worklight.wlclient.ui.UIWebViewClient'
        );
        if (WorkLightWebView) {
            try {
                WorkLightWebView.onReceivedSslError.implementation = function(
                    view: any, handler: any, error: any
                ) {
                    HookUtils.sendInfo('IBM WorkLight SSL error bypassed');
                    handler.proceed();
                };
            } catch (e) {
                HookUtils.sendDebug(`IBM WorkLight hook failed: ${e}`);
            }
        }

        const WLGap = HookUtils.safeGetJavaClass('com.worklight.androidgap.plugin.WLCertificatePinningPlugin');
        if (WLGap) {
            try {
                WLGap.isCertificatePinned.implementation = function() {
                    HookUtils.sendInfo('IBM WorkLight isCertificatePinned bypassed');
                    return true;
                };
            } catch (e) {
                HookUtils.sendDebug(`IBM WorkLight gap hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass CWAC-Netsecurity certificate validation.
     * Reference: httptoolkit android-certificate-unpinning.js - CWAC hooks
     */
    private bypassCWACNetsecurity(): void {
        const CertChainValidator = HookUtils.safeGetJavaClass(
            'com.commonsware.cwac.netsecurity.conscrypt.CertChainValidator'
        );
        if (CertChainValidator) {
            try {
                CertChainValidator.verifyChain.implementation = function() {
                    HookUtils.sendInfo('CWAC-Netsecurity CertChainValidator bypassed');
                    return Java.use('java.util.ArrayList').$new();
                };
            } catch (e) {
                HookUtils.sendDebug(`CWAC-Netsecurity hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass Cordova Advanced HTTP plugin.
     * Reference: httptoolkit android-certificate-unpinning.js - Cordova hooks
     * Converts "pinned" trust modes to "default" mode.
     */
    private bypassCordovaAdvancedHTTP(): void {
        const CordovaHTTP = HookUtils.safeGetJavaClass(
            'com.silkimen.cordovahttp.CordovaHttpPlugin'
        );
        if (CordovaHTTP) {
            try {
                CordovaHTTP.setSSLCertMode.implementation = function(mode: any, callbackContext: any) {
                    HookUtils.sendInfo(`Cordova setSSLCertMode bypassed (was: ${mode})`);
                    // Always use default mode
                    this.setSSLCertMode('default', callbackContext);
                };
            } catch (e) {
                HookUtils.sendDebug(`Cordova Advanced HTTP hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass Netty fingerprint-based trust manager.
     * Reference: httptoolkit android-certificate-unpinning.js - Netty hooks
     */
    private bypassNetty(): void {
        const FingerprintTrustManagerFactory = HookUtils.safeGetJavaClass(
            'io.netty.handler.ssl.util.FingerprintTrustManagerFactory'
        );
        if (FingerprintTrustManagerFactory) {
            try {
                FingerprintTrustManagerFactory.checkTrusted.implementation = function(
                    type: any, chain: any
                ) {
                    HookUtils.sendInfo('Netty FingerprintTrustManagerFactory bypassed');
                };
            } catch (e) {
                HookUtils.sendDebug(`Netty hook failed: ${e}`);
            }
        }
    }

    /**
     * Bypass Appmattus Certificate Transparency interceptor.
     * Reference: httptoolkit android-certificate-unpinning.js - Appmattus hooks
     */
    private bypassAppmattusCtInterceptor(): void {
        const CTInterceptor = HookUtils.safeGetJavaClass(
            'com.appmattus.certificatetransparency.internal.verifier.CertificateTransparencyInterceptor'
        );
        if (CTInterceptor) {
            try {
                CTInterceptor.intercept.implementation = function(chain: any) {
                    HookUtils.sendInfo('Appmattus CT Interceptor bypassed');
                    return chain.proceed(chain.request());
                };
            } catch (e) {
                HookUtils.sendDebug(`Appmattus CT hook failed: ${e}`);
            }
        }
    }
}
