"""Core enumerations for TrigDroid."""

from enum import Enum, IntEnum


class LogLevel(Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TestPhase(Enum):
    """Test execution phases."""
    SETUP = "setup"
    EXECUTION = "execution"
    TEARDOWN = "teardown"


class TestResult(Enum):
    """Test execution results."""
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"
    ERROR = "error"


class DeviceConnectionState(Enum):
    """Android device connection states."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    UNAUTHORIZED = "unauthorized"
    OFFLINE = "offline"


class SensorType(Enum):
    """Android sensor types."""
    ACCELEROMETER = "accelerometer"
    GYROSCOPE = "gyroscope"
    LIGHT = "light"
    PRESSURE = "pressure"
    MAGNETOMETER = "magnetometer"
    TEMPERATURE = "temperature"
    PROXIMITY = "proximity"


class ConnectionType(Enum):
    """Network connection types."""
    WIFI = "wifi"
    DATA = "data"
    BLUETOOTH = "bluetooth"
    NFC = "nfc"


class BatteryRotationLevel(IntEnum):
    """Battery rotation elaborateness levels."""
    DISABLED = 0
    SUPER_FAST = 1
    FAST = 2
    DETAILED = 3
    SUPER_DETAILED = 4


class SensorElaboratenessLevel(IntEnum):
    """Sensor test elaborateness levels."""
    DISABLED = 0
    MINIMAL = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5
    EXTREME = 6
    MAXIMUM = 7
    ULTRA = 8
    INSANE = 9
    ULTIMATE = 10


class PhoneType(IntEnum):
    """Phone types from Android TelephonyManager."""
    NONE = 0
    GSM = 1
    CDMA = 2
    SIP = 3


class NetworkType(IntEnum):
    """Network types from Android TelephonyManager."""
    UNKNOWN = 0
    GPRS = 1
    EDGE = 2
    UMTS = 3
    CDMA = 4
    EVDO_0 = 5
    EVDO_A = 6
    RTT = 7
    HSDPA = 8
    HSUPA = 9
    HSPA = 10
    IDEN = 11
    EVDO_B = 12
    LTE = 13
    EHRPD = 14
    HSPAP = 15
    GSM = 16
    TD_SCDMA = 17
    IWLAN = 18
    NR = 20  # 5G