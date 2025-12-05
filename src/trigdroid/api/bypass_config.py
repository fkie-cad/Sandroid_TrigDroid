"""Bypass configuration classes for TrigDroid.

This module provides dataclasses for configuring security bypass hooks
used during malware analysis and security testing.

These bypasses are for authorized security testing purposes only.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class SSLUnpinningConfig:
    """Configuration for SSL/TLS certificate pinning bypass.

    Corresponds to hooks/ssl-unpinning.ts

    Attributes:
        enabled: Enable SSL unpinning hooks.
        use_custom_cert: Use a custom certificate for trust.
        custom_cert_path: Path to custom certificate on device.
        bypass_okhttp: Bypass OkHttp v2 pinning.
        bypass_okhttp3: Bypass OkHttp v3 pinning.
        bypass_trust_manager: Bypass Android TrustManager.
        bypass_webview_client: Bypass WebViewClient SSL errors.
        bypass_conscrypt: Bypass Conscrypt CertPinManager.
        bypass_network_security_config: Bypass Network Security Config.
        bypass_trustkit: Bypass TrustKit library.
        bypass_appcelerator: Bypass Appcelerator HTTPS.
        bypass_phonegap: Bypass PhoneGap SSL checker.
        bypass_ibm_worklight: Bypass IBM WorkLight/MobileFirst.
        bypass_cwac_netsecurity: Bypass CWAC-Netsecurity.
        bypass_cordova_advanced_http: Bypass Cordova Advanced HTTP.
        bypass_netty: Bypass Netty fingerprint trust.
        bypass_appmattus_ct: Bypass Appmattus Certificate Transparency.
    """

    enabled: bool = False
    use_custom_cert: bool = False
    custom_cert_path: str = "/data/local/tmp/cert-der.crt"
    bypass_okhttp: bool = True
    bypass_okhttp3: bool = True
    bypass_trust_manager: bool = True
    bypass_webview_client: bool = True
    bypass_conscrypt: bool = True
    bypass_network_security_config: bool = True
    bypass_trustkit: bool = True
    bypass_appcelerator: bool = True
    bypass_phonegap: bool = True
    bypass_ibm_worklight: bool = True
    bypass_cwac_netsecurity: bool = True
    bypass_cordova_advanced_http: bool = True
    bypass_netty: bool = True
    bypass_appmattus_ct: bool = True

    def to_frida_config(self) -> Dict[str, Any]:
        """Convert to Frida hook configuration dictionary."""
        return {
            "enabled": self.enabled,
            "use_custom_cert": self.use_custom_cert,
            "custom_cert_path": self.custom_cert_path,
            "bypass_okhttp": self.bypass_okhttp,
            "bypass_okhttp3": self.bypass_okhttp3,
            "bypass_trust_manager": self.bypass_trust_manager,
            "bypass_webview_client": self.bypass_webview_client,
            "bypass_conscrypt": self.bypass_conscrypt,
            "bypass_network_security_config": self.bypass_network_security_config,
            "bypass_trustkit": self.bypass_trustkit,
            "bypass_appcelerator": self.bypass_appcelerator,
            "bypass_phonegap": self.bypass_phonegap,
            "bypass_ibm_worklight": self.bypass_ibm_worklight,
            "bypass_cwac_netsecurity": self.bypass_cwac_netsecurity,
            "bypass_cordova_advanced_http": self.bypass_cordova_advanced_http,
            "bypass_netty": self.bypass_netty,
            "bypass_appmattus_ct": self.bypass_appmattus_ct,
        }


@dataclass
class RootDetectionConfig:
    """Configuration for root detection bypass.

    Corresponds to hooks/root-detection.ts

    Attributes:
        enabled: Enable root detection bypass hooks.
        bypass_file_checks: Bypass file existence checks (su, busybox, etc.).
        bypass_package_manager: Hide root packages from PackageManager.
        bypass_command_execution: Block root commands (su, busybox, etc.).
        bypass_build_properties: Spoof Build.TAGS, Build.TYPE, etc.
        bypass_rootbeer: Bypass RootBeer library detection.
        bypass_system_properties: Spoof system properties (ro.debuggable, etc.).
        custom_blocked_paths: Additional paths to block.
        custom_blocked_packages: Additional packages to hide.
    """

    enabled: bool = False
    bypass_file_checks: bool = True
    bypass_package_manager: bool = True
    bypass_command_execution: bool = True
    bypass_build_properties: bool = True
    bypass_rootbeer: bool = True
    bypass_system_properties: bool = True
    custom_blocked_paths: List[str] = field(default_factory=list)
    custom_blocked_packages: List[str] = field(default_factory=list)

    def to_frida_config(self) -> Dict[str, Any]:
        """Convert to Frida hook configuration dictionary."""
        return {
            "enabled": self.enabled,
            "bypass_file_checks": self.bypass_file_checks,
            "bypass_package_manager": self.bypass_package_manager,
            "bypass_command_execution": self.bypass_command_execution,
            "bypass_build_properties": self.bypass_build_properties,
            "bypass_rootbeer": self.bypass_rootbeer,
            "bypass_system_properties": self.bypass_system_properties,
            "custom_blocked_paths": self.custom_blocked_paths,
            "custom_blocked_packages": self.custom_blocked_packages,
        }


@dataclass
class EmulatorDetectionConfig:
    """Configuration for emulator detection bypass.

    Corresponds to hooks/emulator-detection.ts

    Attributes:
        enabled: Enable emulator detection bypass hooks.
        device_profile: Device profile to spoof ('pixel_4_xl', 'samsung_s21', etc.).
        custom_model: Custom Build.MODEL value.
        custom_manufacturer: Custom Build.MANUFACTURER value.
        custom_brand: Custom Build.BRAND value.
        custom_device: Custom Build.DEVICE value.
        custom_hardware: Custom Build.HARDWARE value.
        custom_fingerprint: Custom Build.FINGERPRINT value.
        custom_product: Custom Build.PRODUCT value.
        bypass_telephony: Spoof TelephonyManager values.
        bypass_sensors: Enable sensor spoofing (handled by android-sensors.ts).
    """

    enabled: bool = False
    device_profile: str = "pixel_4_xl"
    custom_model: Optional[str] = None
    custom_manufacturer: Optional[str] = None
    custom_brand: Optional[str] = None
    custom_device: Optional[str] = None
    custom_hardware: Optional[str] = None
    custom_fingerprint: Optional[str] = None
    custom_product: Optional[str] = None
    bypass_telephony: bool = True
    bypass_sensors: bool = False

    def to_frida_config(self) -> Dict[str, Any]:
        """Convert to Frida hook configuration dictionary."""
        config = {
            "enabled": self.enabled,
            "device_profile": self.device_profile,
            "bypass_telephony": self.bypass_telephony,
            "bypass_sensors": self.bypass_sensors,
        }
        if self.custom_model:
            config["custom_model"] = self.custom_model
        if self.custom_manufacturer:
            config["custom_manufacturer"] = self.custom_manufacturer
        if self.custom_brand:
            config["custom_brand"] = self.custom_brand
        if self.custom_device:
            config["custom_device"] = self.custom_device
        if self.custom_hardware:
            config["custom_hardware"] = self.custom_hardware
        if self.custom_fingerprint:
            config["custom_fingerprint"] = self.custom_fingerprint
        if self.custom_product:
            config["custom_product"] = self.custom_product
        return config


@dataclass
class FridaDetectionConfig:
    """Configuration for Frida detection bypass.

    Corresponds to hooks/frida-detection.ts

    Note: Frida detection bypass is most effective in SPAWN mode,
    as detection often occurs during app startup.

    Attributes:
        enabled: Enable Frida detection bypass hooks.
        bypass_file_checks: Hide Frida-related files.
        bypass_port_checks: Block connections to Frida port (27042).
        bypass_maps_checks: Filter Frida references from /proc/self/maps.
        bypass_named_pipe_checks: Hide Frida named pipes.
        bypass_string_checks: Filter Frida strings from memory searches.
    """

    enabled: bool = False
    bypass_file_checks: bool = True
    bypass_port_checks: bool = True
    bypass_maps_checks: bool = True
    bypass_named_pipe_checks: bool = True
    bypass_string_checks: bool = True

    def to_frida_config(self) -> Dict[str, Any]:
        """Convert to Frida hook configuration dictionary."""
        return {
            "enabled": self.enabled,
            "bypass_file_checks": self.bypass_file_checks,
            "bypass_port_checks": self.bypass_port_checks,
            "bypass_maps_checks": self.bypass_maps_checks,
            "bypass_named_pipe_checks": self.bypass_named_pipe_checks,
            "bypass_string_checks": self.bypass_string_checks,
        }


@dataclass
class DebugDetectionConfig:
    """Configuration for debugger detection bypass.

    Corresponds to hooks/debug-detection.ts

    Attributes:
        enabled: Enable debug detection bypass hooks.
        bypass_debug_class: Bypass android.os.Debug checks.
        bypass_tracer_pid: Spoof TracerPid in /proc/self/status.
        bypass_debuggable_flag: Clear FLAG_DEBUGGABLE from ApplicationInfo.
        bypass_timing_checks: Bypass timing-based debug detection (may affect app).
    """

    enabled: bool = False
    bypass_debug_class: bool = True
    bypass_tracer_pid: bool = True
    bypass_debuggable_flag: bool = True
    bypass_timing_checks: bool = False  # Can affect app behavior

    def to_frida_config(self) -> Dict[str, Any]:
        """Convert to Frida hook configuration dictionary."""
        return {
            "enabled": self.enabled,
            "bypass_debug_class": self.bypass_debug_class,
            "bypass_tracer_pid": self.bypass_tracer_pid,
            "bypass_debuggable_flag": self.bypass_debuggable_flag,
            "bypass_timing_checks": self.bypass_timing_checks,
        }


@dataclass
class BypassConfig:
    """Combined bypass configuration for all security bypasses.

    This is the main configuration class that aggregates all bypass types.
    Use this in TrigDroid's TestConfiguration.

    Example:
        config = BypassConfig(
            ssl_unpinning=SSLUnpinningConfig(enabled=True),
            root_detection=RootDetectionConfig(enabled=True),
        )

        # Check if any bypasses are enabled
        if config.has_any_enabled():
            print("Bypass hooks will be loaded")

        # Get Frida configuration
        frida_config = config.to_frida_config()
    """

    ssl_unpinning: SSLUnpinningConfig = field(default_factory=SSLUnpinningConfig)
    root_detection: RootDetectionConfig = field(default_factory=RootDetectionConfig)
    emulator_detection: EmulatorDetectionConfig = field(default_factory=EmulatorDetectionConfig)
    frida_detection: FridaDetectionConfig = field(default_factory=FridaDetectionConfig)
    debug_detection: DebugDetectionConfig = field(default_factory=DebugDetectionConfig)

    def has_any_enabled(self) -> bool:
        """Check if any bypass is enabled.

        Returns:
            True if any bypass configuration has enabled=True.
        """
        return any([
            self.ssl_unpinning.enabled,
            self.root_detection.enabled,
            self.emulator_detection.enabled,
            self.frida_detection.enabled,
            self.debug_detection.enabled,
        ])

    def get_enabled_bypasses(self) -> List[str]:
        """Get list of enabled bypass types.

        Returns:
            List of enabled bypass type names.
        """
        enabled = []
        if self.ssl_unpinning.enabled:
            enabled.append("ssl_unpinning")
        if self.root_detection.enabled:
            enabled.append("root_detection")
        if self.emulator_detection.enabled:
            enabled.append("emulator_detection")
        if self.frida_detection.enabled:
            enabled.append("frida_detection")
        if self.debug_detection.enabled:
            enabled.append("debug_detection")
        return enabled

    def to_frida_config(self) -> Dict[str, Any]:
        """Convert to Frida hook configuration dictionary.

        This dictionary is passed to the TrigDroid Frida script.

        Returns:
            Dictionary with bypass configurations for Frida.
        """
        return {
            "ssl_unpinning": self.ssl_unpinning.to_frida_config(),
            "root_detection": self.root_detection.to_frida_config(),
            "emulator_detection": self.emulator_detection.to_frida_config(),
            "frida_detection": self.frida_detection.to_frida_config(),
            "debug_detection": self.debug_detection.to_frida_config(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BypassConfig":
        """Create BypassConfig from a dictionary.

        Args:
            data: Dictionary with bypass configuration.

        Returns:
            BypassConfig instance.
        """
        return cls(
            ssl_unpinning=SSLUnpinningConfig(**data.get("ssl_unpinning", {})),
            root_detection=RootDetectionConfig(**data.get("root_detection", {})),
            emulator_detection=EmulatorDetectionConfig(**data.get("emulator_detection", {})),
            frida_detection=FridaDetectionConfig(**data.get("frida_detection", {})),
            debug_detection=DebugDetectionConfig(**data.get("debug_detection", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation of the bypass configuration.
        """
        return {
            "ssl_unpinning": self.ssl_unpinning.to_frida_config(),
            "root_detection": self.root_detection.to_frida_config(),
            "emulator_detection": self.emulator_detection.to_frida_config(),
            "frida_detection": self.frida_detection.to_frida_config(),
            "debug_detection": self.debug_detection.to_frida_config(),
        }
