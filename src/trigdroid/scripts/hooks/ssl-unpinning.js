"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SSLUnpinningHooks = void 0;
const utils_1 = require("../utils");
class SSLUnpinningHooks {
    constructor(config = {}) {
        this.config = Object.assign({ enabled: true, use_custom_cert: false, custom_cert_path: '/data/local/tmp/cert-der.crt', bypass_okhttp: true, bypass_okhttp3: true, bypass_trust_manager: true, bypass_webview_client: true, bypass_conscrypt: true, bypass_network_security_config: true, bypass_trustkit: true, bypass_appcelerator: true, bypass_phonegap: true, bypass_ibm_worklight: true, bypass_cwac_netsecurity: true, bypass_cordova_advanced_http: true, bypass_netty: true, bypass_appmattus_ct: true }, config);
    }
    initialize() {
        if (!this.config.enabled) {
            utils_1.HookUtils.sendInfo('SSL Unpinning hooks disabled');
            return;
        }
        utils_1.HookUtils.sendInfo('Initializing SSL unpinning hooks...');
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
        utils_1.HookUtils.sendInfo('SSL unpinning hooks initialized');
    }
    bypassHttpsURLConnection() {
        const HttpsURLConnection = utils_1.HookUtils.safeGetJavaClass('javax.net.ssl.HttpsURLConnection');
        if (!HttpsURLConnection)
            return;
        try {
            HttpsURLConnection.setHostnameVerifier.implementation = function (verifier) {
                utils_1.HookUtils.sendInfo('HttpsURLConnection.setHostnameVerifier bypassed');
            };
        }
        catch (e) {
            utils_1.HookUtils.sendDebug(`HttpsURLConnection.setHostnameVerifier hook failed: ${e}`);
        }
        try {
            HttpsURLConnection.setSSLSocketFactory.implementation = function (factory) {
                utils_1.HookUtils.sendInfo('HttpsURLConnection.setSSLSocketFactory bypassed');
            };
        }
        catch (e) {
            utils_1.HookUtils.sendDebug(`HttpsURLConnection.setSSLSocketFactory hook failed: ${e}`);
        }
    }
    bypassSSLContext() {
        const SSLContext = utils_1.HookUtils.safeGetJavaClass('javax.net.ssl.SSLContext');
        if (!SSLContext)
            return;
        try {
            const X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
            const TrustAllCerts = Java.registerClass({
                name: 'com.trigdroid.bypass.TrustAllCerts',
                implements: [X509TrustManager],
                methods: {
                    checkClientTrusted: function (chain, authType) { },
                    checkServerTrusted: function (chain, authType) {
                        utils_1.HookUtils.sendInfo('TrustManager.checkServerTrusted bypassed');
                    },
                    getAcceptedIssuers: function () {
                        return [];
                    }
                }
            });
            SSLContext.init.overload('[Ljavax.net.ssl.KeyManager;', '[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom').implementation = function (keyManagers, trustManagers, secureRandom) {
                utils_1.HookUtils.sendInfo('SSLContext.init intercepted - injecting permissive TrustManager');
                const trustAllArray = Java.array('javax.net.ssl.TrustManager', [TrustAllCerts.$new()]);
                this.init(keyManagers, trustAllArray, secureRandom);
                utils_1.HookUtils.sendChangelog({
                    property: 'SSLContext.init',
                    oldValue: 'original TrustManager',
                    newValue: 'TrustAllCerts (bypass)'
                });
            };
        }
        catch (e) {
            utils_1.HookUtils.sendDebug(`SSLContext hook failed: ${e}`);
        }
    }
    bypassConscrypt() {
        const TrustManagerImpl = utils_1.HookUtils.safeGetJavaClass('com.android.org.conscrypt.TrustManagerImpl');
        if (TrustManagerImpl) {
            try {
                TrustManagerImpl.verifyChain.implementation = function (untrustedChain, trustAnchorChain, host, clientAuth, ocspData, tlsSctData) {
                    utils_1.HookUtils.sendInfo(`Conscrypt TrustManagerImpl.verifyChain bypassed for ${host}`);
                    return untrustedChain;
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`TrustManagerImpl.verifyChain hook failed: ${e}`);
            }
        }
        const CertPinManager = utils_1.HookUtils.safeGetJavaClass('com.android.org.conscrypt.CertPinManager');
        if (CertPinManager) {
            try {
                CertPinManager.isChainValid.overload('java.lang.String', 'java.util.List').implementation =
                    function (hostname, chain) {
                        utils_1.HookUtils.sendInfo(`Conscrypt CertPinManager.isChainValid bypassed for ${hostname}`);
                        return true;
                    };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`CertPinManager.isChainValid hook failed: ${e}`);
            }
            try {
                CertPinManager.checkChainPinning.implementation = function (hostname, chain) {
                    utils_1.HookUtils.sendInfo(`Conscrypt CertPinManager.checkChainPinning bypassed for ${hostname}`);
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`CertPinManager.checkChainPinning hook failed: ${e}`);
            }
        }
    }
    bypassNetworkSecurityConfig() {
        const NetworkSecurityConfig = utils_1.HookUtils.safeGetJavaClass('android.security.net.config.NetworkSecurityConfig');
        if (!NetworkSecurityConfig)
            return;
        try {
            const Builder = utils_1.HookUtils.safeGetJavaClass('android.security.net.config.NetworkSecurityConfig$Builder');
            if (Builder) {
                Builder.setPinSet.implementation = function (pinSet) {
                    utils_1.HookUtils.sendInfo('NetworkSecurityConfig.Builder.setPinSet bypassed');
                    return this;
                };
            }
        }
        catch (e) {
            utils_1.HookUtils.sendDebug(`NetworkSecurityConfig hook failed: ${e}`);
        }
    }
    bypassOkHttpV2() {
        const OkHostnameVerifier = utils_1.HookUtils.safeGetJavaClass('com.android.okhttp.internal.tls.OkHostnameVerifier');
        if (OkHostnameVerifier) {
            try {
                OkHostnameVerifier.verify.overload('java.lang.String', 'java.security.cert.X509Certificate')
                    .implementation = function (hostname, certificate) {
                    utils_1.HookUtils.sendInfo(`OkHttp v2 hostname verification bypassed for ${hostname}`);
                    return true;
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`OkHttp v2 verify hook failed: ${e}`);
            }
        }
        const Address = utils_1.HookUtils.safeGetJavaClass('com.android.okhttp.Address');
        if (Address) {
            try {
                Address.$init.overload('java.lang.String', 'int', 'com.android.okhttp.Dns', 'javax.net.SocketFactory', 'javax.net.ssl.SSLSocketFactory', 'javax.net.ssl.HostnameVerifier', 'com.android.okhttp.CertificatePinner', 'com.android.okhttp.Authenticator', 'java.net.Proxy', 'java.util.List', 'java.util.List', 'java.net.ProxySelector').implementation = function (uriHost, uriPort, dns, socketFactory, sslSocketFactory, hostnameVerifier, certificatePinner, authenticator, proxy, protocols, connectionSpecs, proxySelector) {
                    utils_1.HookUtils.sendInfo('OkHttp v2 Address constructor bypassed');
                    const CertificatePinner = Java.use('com.android.okhttp.CertificatePinner');
                    return this.$init(uriHost, uriPort, dns, socketFactory, sslSocketFactory, null, CertificatePinner.DEFAULT.value, authenticator, proxy, protocols, connectionSpecs, proxySelector);
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`OkHttp v2 Address hook failed: ${e}`);
            }
        }
    }
    bypassOkHttp3() {
        const CertificatePinner = utils_1.HookUtils.safeGetJavaClass('okhttp3.CertificatePinner');
        if (CertificatePinner) {
            const checkOverloads = [
                ['java.lang.String', 'java.util.List'],
                ['java.lang.String', '[Ljava.security.cert.Certificate;'],
                ['java.lang.String', 'java.util.function.Supplier']
            ];
            for (const overload of checkOverloads) {
                try {
                    CertificatePinner.check.overload(...overload).implementation = function () {
                        utils_1.HookUtils.sendInfo(`OkHttp3 CertificatePinner.check bypassed for ${arguments[0]}`);
                    };
                }
                catch (e) {
                }
            }
            try {
                CertificatePinner['check$okhttp'].implementation = function () {
                    utils_1.HookUtils.sendInfo(`OkHttp3 CertificatePinner.check$okhttp bypassed`);
                };
            }
            catch (e) {
            }
        }
        const Builder = utils_1.HookUtils.safeGetJavaClass('okhttp3.OkHttpClient$Builder');
        if (Builder) {
            try {
                Builder.certificatePinner.implementation = function (pinner) {
                    utils_1.HookUtils.sendInfo('OkHttp3 Builder.certificatePinner bypassed');
                    return this;
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`OkHttp3 Builder hook failed: ${e}`);
            }
        }
    }
    bypassWebViewClient() {
        const WebViewClient = utils_1.HookUtils.safeGetJavaClass('android.webkit.WebViewClient');
        if (!WebViewClient)
            return;
        try {
            WebViewClient.onReceivedSslError.implementation = function (view, handler, error) {
                utils_1.HookUtils.sendInfo(`WebViewClient SSL error bypassed: ${error.toString()}`);
                handler.proceed();
            };
        }
        catch (e) {
            utils_1.HookUtils.sendDebug(`WebViewClient hook failed: ${e}`);
        }
    }
    bypassTrustKit() {
        const TrustKit = utils_1.HookUtils.safeGetJavaClass('com.datatheorem.android.trustkit.pinning.OkHostnameVerifier');
        if (TrustKit) {
            try {
                TrustKit.verify.overload('java.lang.String', 'javax.net.ssl.SSLSession')
                    .implementation = function (hostname, session) {
                    utils_1.HookUtils.sendInfo(`TrustKit hostname verification bypassed for ${hostname}`);
                    return true;
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`TrustKit hook failed: ${e}`);
            }
        }
        const PinningTrustManager = utils_1.HookUtils.safeGetJavaClass('com.datatheorem.android.trustkit.pinning.PinningTrustManager');
        if (PinningTrustManager) {
            try {
                PinningTrustManager.checkServerTrusted.implementation = function (chain, authType) {
                    utils_1.HookUtils.sendInfo('TrustKit PinningTrustManager bypassed');
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`TrustKit TrustManager hook failed: ${e}`);
            }
        }
    }
    bypassAppcelerator() {
        const PinningTrustManager = utils_1.HookUtils.safeGetJavaClass('appcelerator.https.PinningTrustManager');
        if (PinningTrustManager) {
            try {
                PinningTrustManager.checkServerTrusted.implementation = function (chain, authType) {
                    utils_1.HookUtils.sendInfo('Appcelerator PinningTrustManager bypassed');
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`Appcelerator hook failed: ${e}`);
            }
        }
    }
    bypassPhoneGap() {
        const SSLCertificateChecker = utils_1.HookUtils.safeGetJavaClass('nl.xservices.plugins.SSLCertificateChecker');
        if (SSLCertificateChecker) {
            try {
                SSLCertificateChecker.execute.implementation = function (action, args, callbackContext) {
                    utils_1.HookUtils.sendInfo('PhoneGap SSLCertificateChecker bypassed');
                    callbackContext.success('CONNECTION_SECURE');
                    return true;
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`PhoneGap hook failed: ${e}`);
            }
        }
    }
    bypassIBMWorkLight() {
        const WorkLightWebView = utils_1.HookUtils.safeGetJavaClass('com.worklight.wlclient.ui.UIWebViewClient');
        if (WorkLightWebView) {
            try {
                WorkLightWebView.onReceivedSslError.implementation = function (view, handler, error) {
                    utils_1.HookUtils.sendInfo('IBM WorkLight SSL error bypassed');
                    handler.proceed();
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`IBM WorkLight hook failed: ${e}`);
            }
        }
        const WLGap = utils_1.HookUtils.safeGetJavaClass('com.worklight.androidgap.plugin.WLCertificatePinningPlugin');
        if (WLGap) {
            try {
                WLGap.isCertificatePinned.implementation = function () {
                    utils_1.HookUtils.sendInfo('IBM WorkLight isCertificatePinned bypassed');
                    return true;
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`IBM WorkLight gap hook failed: ${e}`);
            }
        }
    }
    bypassCWACNetsecurity() {
        const CertChainValidator = utils_1.HookUtils.safeGetJavaClass('com.commonsware.cwac.netsecurity.conscrypt.CertChainValidator');
        if (CertChainValidator) {
            try {
                CertChainValidator.verifyChain.implementation = function () {
                    utils_1.HookUtils.sendInfo('CWAC-Netsecurity CertChainValidator bypassed');
                    return Java.use('java.util.ArrayList').$new();
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`CWAC-Netsecurity hook failed: ${e}`);
            }
        }
    }
    bypassCordovaAdvancedHTTP() {
        const CordovaHTTP = utils_1.HookUtils.safeGetJavaClass('com.silkimen.cordovahttp.CordovaHttpPlugin');
        if (CordovaHTTP) {
            try {
                CordovaHTTP.setSSLCertMode.implementation = function (mode, callbackContext) {
                    utils_1.HookUtils.sendInfo(`Cordova setSSLCertMode bypassed (was: ${mode})`);
                    this.setSSLCertMode('default', callbackContext);
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`Cordova Advanced HTTP hook failed: ${e}`);
            }
        }
    }
    bypassNetty() {
        const FingerprintTrustManagerFactory = utils_1.HookUtils.safeGetJavaClass('io.netty.handler.ssl.util.FingerprintTrustManagerFactory');
        if (FingerprintTrustManagerFactory) {
            try {
                FingerprintTrustManagerFactory.checkTrusted.implementation = function (type, chain) {
                    utils_1.HookUtils.sendInfo('Netty FingerprintTrustManagerFactory bypassed');
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`Netty hook failed: ${e}`);
            }
        }
    }
    bypassAppmattusCtInterceptor() {
        const CTInterceptor = utils_1.HookUtils.safeGetJavaClass('com.appmattus.certificatetransparency.internal.verifier.CertificateTransparencyInterceptor');
        if (CTInterceptor) {
            try {
                CTInterceptor.intercept.implementation = function (chain) {
                    utils_1.HookUtils.sendInfo('Appmattus CT Interceptor bypassed');
                    return chain.proceed(chain.request());
                };
            }
            catch (e) {
                utils_1.HookUtils.sendDebug(`Appmattus CT hook failed: ${e}`);
            }
        }
    }
}
exports.SSLUnpinningHooks = SSLUnpinningHooks;
