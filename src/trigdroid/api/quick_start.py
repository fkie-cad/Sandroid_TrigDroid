"""Quick start convenience functions for TrigDroid API."""

from typing import Optional, List, Dict, Any, Union
import logging

from .main import TrigDroidAPI
from .config import TestConfiguration
from .results import TestResult
from .devices import DeviceManager, AndroidDevice
from ..exceptions import TrigDroidError, DeviceError, ConfigurationError


def scan_devices() -> List[Dict[str, str]]:
    """Quick scan for available Android devices.
    
    Returns:
        List of device information dictionaries
        
    Examples:
        devices = scan_devices()
        for device in devices:
            print(f"Device {device['id']}: {device['status']}")
    """
    manager = DeviceManager()
    return manager.list_devices()


def get_connected_devices() -> List[Dict[str, str]]:
    """Get only connected Android devices.
    
    Returns:
        List of connected device information dictionaries
    """
    devices = scan_devices()
    return [d for d in devices if d['status'] == 'device']


def auto_select_device() -> Optional[AndroidDevice]:
    """Automatically select a device for testing.
    
    If only one device is connected, selects it automatically.
    If multiple devices are connected, returns None.
    
    Returns:
        AndroidDevice instance or None
        
    Examples:
        device = auto_select_device()
        if device:
            print(f"Selected device: {device.device_id}")
        else:
            print("Please specify a device ID")
    """
    manager = DeviceManager()
    return manager.connect_to_device()


def quick_test(package: str, 
               device_id: Optional[str] = None,
               acceleration: int = 3,
               verbose: bool = False) -> TestResult:
    """Run a quick test with minimal configuration.
    
    Args:
        package: Android package name to test
        device_id: Device ID (auto-select if None)
        acceleration: Test elaborateness level (0-10)
        verbose: Enable verbose logging
        
    Returns:
        TestResult with execution details
        
    Raises:
        TrigDroidError: If test setup or execution fails
        
    Examples:
        # Test with auto-selected device
        result = quick_test("com.example.app")
        
        # Test with specific device
        result = quick_test("com.example.app", device_id="emulator-5554")
        
        # Intensive test
        result = quick_test("com.example.app", acceleration=8)
    """
    # Setup logging
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Create configuration
    config = TestConfiguration(
        package=package,
        acceleration=acceleration,
        verbose=verbose
    )
    
    # Connect to device
    manager = DeviceManager()
    device = manager.connect_to_device(device_id)
    if not device:
        raise DeviceError("No device available for testing")
    
    # Run test
    with TrigDroidAPI() as api:
        api.configure(config)
        api.set_device(device)
        return api.run_tests()


def test_package(package: str, 
                 config_dict: Optional[Dict[str, Any]] = None,
                 device_id: Optional[str] = None) -> TestResult:
    """Test a package with custom configuration.
    
    Args:
        package: Android package name to test
        config_dict: Configuration dictionary (optional)
        device_id: Device ID (auto-select if None)
        
    Returns:
        TestResult with execution details
        
    Examples:
        # Test with sensor manipulation
        result = test_package("com.example.app", {
            "acceleration": 5,
            "sensors": ["accelerometer", "gyroscope"],
            "network_states": ["wifi", "data"]
        })
    """
    # Create base configuration
    config_data = {"package": package}
    if config_dict:
        config_data.update(config_dict)
    
    config = TestConfiguration(**config_data)
    
    # Connect to device
    manager = DeviceManager()
    device = manager.connect_to_device(device_id)
    if not device:
        raise DeviceError("No device available for testing")
    
    # Run test
    with TrigDroidAPI() as api:
        api.configure(config)
        api.set_device(device)
        return api.run_tests()


def validate_environment() -> Dict[str, bool]:
    """Validate that the testing environment is ready.
    
    Returns:
        Dictionary with validation results
        
    Examples:
        status = validate_environment()
        if all(status.values()):
            print("Environment is ready!")
        else:
            print("Issues found:", [k for k, v in status.items() if not v])
    """
    import subprocess
    import os
    from pathlib import Path
    
    results = {}
    
    # Check ADB
    try:
        result = subprocess.run(['adb', 'version'], 
                              capture_output=True, 
                              timeout=5)
        results['adb_available'] = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        results['adb_available'] = False
    
    # Check for connected devices
    try:
        devices = get_connected_devices()
        results['devices_connected'] = len(devices) > 0
        results['device_count'] = len(devices)
    except Exception:
        results['devices_connected'] = False
        results['device_count'] = 0
    
    # Check Frida hooks
    project_root = Path(__file__).parent.parent.parent.parent
    hooks_dir = project_root / "frida-hooks"
    main_js = hooks_dir / "dist" / "main.js"
    
    results['frida_hooks_built'] = main_js.exists()
    results['frida_hooks_directory'] = hooks_dir.exists()
    
    # Check Node.js for TypeScript compilation
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, 
                              timeout=5)
        results['nodejs_available'] = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        results['nodejs_available'] = False
    
    # Check Python Frida module
    try:
        import frida
        results['frida_python'] = True
    except ImportError:
        results['frida_python'] = False
    
    return results


def setup_environment() -> bool:
    """Attempt to setup the testing environment.
    
    Returns:
        True if setup successful, False otherwise
        
    Examples:
        if setup_environment():
            print("Environment setup complete!")
        else:
            print("Setup failed - check logs")
    """
    import subprocess
    from pathlib import Path
    
    logger = logging.getLogger(__name__)
    
    try:
        # Build TypeScript hooks if needed
        project_root = Path(__file__).parent.parent.parent.parent
        hooks_dir = project_root / "frida-hooks"
        
        if hooks_dir.exists() and (hooks_dir / "package.json").exists():
            logger.info("Building TypeScript Frida hooks...")
            
            # Install dependencies
            result = subprocess.run(['npm', 'install'], 
                                  cwd=hooks_dir,
                                  capture_output=True,
                                  timeout=120)
            if result.returncode != 0:
                logger.error(f"npm install failed: {result.stderr.decode()}")
                return False
            
            # Build TypeScript
            result = subprocess.run(['npm', 'run', 'build'], 
                                  cwd=hooks_dir,
                                  capture_output=True,
                                  timeout=60)
            if result.returncode != 0:
                logger.error(f"TypeScript build failed: {result.stderr.decode()}")
                return False
            
            logger.info("TypeScript hooks built successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Environment setup failed: {e}")
        return False


def get_device_info(device_id: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about a device.
    
    Args:
        device_id: Device ID (auto-select if None)
        
    Returns:
        Dictionary with device information
        
    Examples:
        info = get_device_info()
        print(f"Device: {info['model']} running Android {info['version']}")
    """
    manager = DeviceManager()
    device = manager.connect_to_device(device_id)
    if not device:
        raise DeviceError("No device available")
    
    return device.get_device_info()


def list_installed_packages(device_id: Optional[str] = None, 
                           filter_user: bool = True) -> List[str]:
    """List installed packages on a device.
    
    Args:
        device_id: Device ID (auto-select if None)
        filter_user: Only show user-installed packages
        
    Returns:
        List of package names
        
    Examples:
        packages = list_installed_packages()
        user_apps = [p for p in packages if not p.startswith('com.android')]
    """
    manager = DeviceManager()
    device = manager.connect_to_device(device_id)
    if not device:
        raise DeviceError("No device available")
    
    # Get package list
    cmd = "pm list packages"
    if filter_user:
        cmd += " -3"  # Third-party packages only
    
    result = device.execute_command(cmd)
    packages = []
    
    for line in result.stdout.strip().split('\n'):
        if line.startswith('package:'):
            package = line.replace('package:', '').strip()
            packages.append(package)
    
    return sorted(packages)


# Convenience aliases
scan = scan_devices
test = quick_test
validate = validate_environment
setup = setup_environment