"""Integration tests for device management components."""

import pytest
from unittest.mock import Mock, patch, call
import subprocess

from trigdroid.api.devices import DeviceManager, AndroidDevice, scan_devices
from trigdroid.exceptions import DeviceError


@pytest.mark.integration
class TestDeviceManagerIntegration:
    """Integration tests for DeviceManager class."""
    
    @patch('subprocess.run')
    def test_scan_devices_should_parse_adb_output_correctly(self, mock_run):
        """Test scan_devices parses ADB output correctly."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = """List of devices attached
emulator-5554\tdevice
emulator-5556\toffline
physical-device\tunauthorized

"""
        mock_run.return_value = mock_result
        
        # Act
        devices = scan_devices()
        
        # Assert
        assert len(devices) == 3
        
        device_ids = [d['id'] for d in devices]
        assert 'emulator-5554' in device_ids
        assert 'emulator-5556' in device_ids
        assert 'physical-device' in device_ids
        
        # Check statuses
        device_dict = {d['id']: d['status'] for d in devices}
        assert device_dict['emulator-5554'] == 'device'
        assert device_dict['emulator-5556'] == 'offline'
        assert device_dict['physical-device'] == 'unauthorized'
    
    @patch('subprocess.run')
    def test_scan_devices_should_handle_no_devices(self, mock_run):
        """Test scan_devices handles no devices scenario."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "List of devices attached\n\n"
        mock_run.return_value = mock_result
        
        # Act
        devices = scan_devices()
        
        # Assert
        assert devices == []
    
    @patch('subprocess.run')
    def test_scan_devices_should_handle_adb_failure(self, mock_run):
        """Test scan_devices handles ADB command failure."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "adb: command not found"
        mock_run.return_value = mock_result
        
        # Act & Assert
        with pytest.raises(DeviceError):
            scan_devices()
    
    @patch('subprocess.run')
    def test_device_manager_connect_should_choose_first_available_device(self, mock_run):
        """Test DeviceManager chooses first available device when no specific device requested."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "emulator-5554\tdevice\nemulator-5556\tdevice\n"
        mock_run.return_value = mock_result
        
        manager = DeviceManager()
        
        # Act
        with patch.object(AndroidDevice, '__init__', return_value=None) as mock_device_init:
            with patch.object(AndroidDevice, 'is_connected', return_value=True):
                device = manager.connect_to_device()
        
        # Assert
        assert device is not None
        mock_device_init.assert_called_with('emulator-5554')
    
    @patch('subprocess.run')
    def test_device_manager_connect_should_use_specific_device_when_requested(self, mock_run):
        """Test DeviceManager uses specific device when requested."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "emulator-5554\tdevice\nemulator-5556\tdevice\n"
        mock_run.return_value = mock_result
        
        manager = DeviceManager()
        
        # Act
        with patch.object(AndroidDevice, '__init__', return_value=None) as mock_device_init:
            with patch.object(AndroidDevice, 'is_connected', return_value=True):
                device = manager.connect_to_device('emulator-5556')
        
        # Assert
        assert device is not None
        mock_device_init.assert_called_with('emulator-5556')
    
    @patch('subprocess.run')
    def test_device_manager_connect_should_return_none_for_unavailable_device(self, mock_run):
        """Test DeviceManager returns None for unavailable device."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "emulator-5554\tdevice\n"
        mock_run.return_value = mock_result
        
        manager = DeviceManager()
        
        # Act
        device = manager.connect_to_device('nonexistent-device')
        
        # Assert
        assert device is None
    
    @patch('subprocess.run')
    def test_device_manager_should_filter_offline_devices(self, mock_run):
        """Test DeviceManager filters out offline and unauthorized devices."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = """emulator-5554\tdevice
emulator-5556\toffline
physical-device\tunauthorized
emulator-5558\tdevice
"""
        mock_run.return_value = mock_result
        
        manager = DeviceManager()
        
        # Act
        with patch.object(AndroidDevice, '__init__', return_value=None) as mock_device_init:
            with patch.object(AndroidDevice, 'is_connected', return_value=True):
                device = manager.connect_to_device()
        
        # Assert
        # Should choose first available device (emulator-5554)
        mock_device_init.assert_called_with('emulator-5554')


@pytest.mark.integration
class TestAndroidDeviceIntegration:
    """Integration tests for AndroidDevice class."""
    
    @patch('subprocess.run')
    def test_android_device_execute_command_should_run_adb_command(self, mock_run):
        """Test AndroidDevice executes ADB commands correctly."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = b"test output"
        mock_result.stderr = b""
        mock_run.return_value = mock_result
        
        device = AndroidDevice('test-device')
        
        # Act
        result = device.execute_command('shell echo test')
        
        # Assert
        mock_run.assert_called_with(
            ['adb', '-s', 'test-device', 'shell', 'echo', 'test'],
            capture_output=True,
            timeout=30
        )
        assert result.return_code == 0
        assert result.stdout == b"test output"
        assert result.success is True
    
    @patch('subprocess.run')
    def test_android_device_install_app_should_run_install_command(self, mock_run):
        """Test AndroidDevice app installation."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = b"Success"
        mock_run.return_value = mock_result
        
        device = AndroidDevice('test-device')
        
        # Act
        success = device.install_app('/path/to/app.apk')
        
        # Assert
        mock_run.assert_called_with(
            ['adb', '-s', 'test-device', 'install', '/path/to/app.apk'],
            capture_output=True,
            timeout=120
        )
        assert success is True
    
    @patch('subprocess.run')
    def test_android_device_install_app_should_handle_failure(self, mock_run):
        """Test AndroidDevice app installation handles failures."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = b"INSTALL_FAILED_ALREADY_EXISTS"
        mock_run.return_value = mock_result
        
        device = AndroidDevice('test-device')
        
        # Act
        success = device.install_app('/path/to/app.apk')
        
        # Assert
        assert success is False
    
    @patch('subprocess.run')
    def test_android_device_uninstall_app_should_run_uninstall_command(self, mock_run):
        """Test AndroidDevice app uninstallation."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = b"Success"
        mock_run.return_value = mock_result
        
        device = AndroidDevice('test-device')
        
        # Act
        success = device.uninstall_app('com.example.test')
        
        # Assert
        mock_run.assert_called_with(
            ['adb', '-s', 'test-device', 'uninstall', 'com.example.test'],
            capture_output=True,
            timeout=60
        )
        assert success is True
    
    @patch('subprocess.run')
    def test_android_device_start_app_should_run_start_command(self, mock_run):
        """Test AndroidDevice app starting."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        device = AndroidDevice('test-device')
        
        # Act
        success = device.start_app('com.example.test')
        
        # Assert
        expected_command = [
            'adb', '-s', 'test-device', 'shell', 'am', 'start',
            '-n', 'com.example.test/.MainActivity'
        ]
        mock_run.assert_called_with(expected_command, capture_output=True, timeout=30)
        assert success is True
    
    @patch('subprocess.run')
    def test_android_device_stop_app_should_run_stop_command(self, mock_run):
        """Test AndroidDevice app stopping."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        device = AndroidDevice('test-device')
        
        # Act
        success = device.stop_app('com.example.test')
        
        # Assert
        expected_command = [
            'adb', '-s', 'test-device', 'shell', 'am', 'force-stop',
            'com.example.test'
        ]
        mock_run.assert_called_with(expected_command, capture_output=True, timeout=30)
        assert success is True
    
    @patch('subprocess.run')
    def test_android_device_is_app_installed_should_check_package_list(self, mock_run):
        """Test AndroidDevice app installation check."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = b"package:com.example.test\npackage:com.other.app"
        mock_run.return_value = mock_result
        
        device = AndroidDevice('test-device')
        
        # Act
        is_installed = device.is_app_installed('com.example.test')
        
        # Assert
        expected_command = ['adb', '-s', 'test-device', 'shell', 'pm', 'list', 'packages']
        mock_run.assert_called_with(expected_command, capture_output=True, timeout=30)
        assert is_installed is True
    
    @patch('subprocess.run')
    def test_android_device_is_app_installed_should_return_false_for_missing_package(self, mock_run):
        """Test AndroidDevice returns False for non-installed packages."""
        # Arrange
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = b"package:com.other.app"
        mock_run.return_value = mock_result
        
        device = AndroidDevice('test-device')
        
        # Act
        is_installed = device.is_app_installed('com.example.test')
        
        # Assert
        assert is_installed is False
    
    @patch('subprocess.run')
    def test_android_device_get_device_info_should_return_device_information(self, mock_run):
        """Test AndroidDevice returns device information."""
        # Arrange
        # Mock multiple ADB calls for different device properties
        mock_results = [
            Mock(returncode=0, stdout=b"Android SDK built for x86"),  # model
            Mock(returncode=0, stdout=b"10"),  # android version
            Mock(returncode=0, stdout=b"29"),  # API level
            Mock(returncode=0, stdout=b"x86"),  # architecture
        ]
        mock_run.side_effect = mock_results
        
        device = AndroidDevice('emulator-5554')
        
        # Act
        device_info = device.get_device_info()
        
        # Assert
        assert device_info['id'] == 'emulator-5554'
        assert device_info['model'] == 'Android SDK built for x86'
        assert device_info['android_version'] == '10'
        assert device_info['api_level'] == '29'
        assert device_info['arch'] == 'x86'
    
    @patch('subprocess.run')
    def test_android_device_command_timeout_should_be_handled(self, mock_run):
        """Test AndroidDevice handles command timeouts."""
        # Arrange
        mock_run.side_effect = subprocess.TimeoutExpired(['adb'], 30)
        device = AndroidDevice('test-device')
        
        # Act
        result = device.execute_command('shell echo test')
        
        # Assert
        assert result.success is False
        assert result.return_code != 0
    
    def test_android_device_is_connected_should_check_connectivity(self):
        """Test AndroidDevice connectivity check."""
        # Arrange
        device = AndroidDevice('test-device')
        
        # Act & Assert - this would require actual device connection
        # For now, test the method exists and returns boolean
        with patch.object(device, 'execute_command') as mock_execute:
            mock_result = Mock()
            mock_result.success = True
            mock_execute.return_value = mock_result
            
            is_connected = device.is_connected()
            assert isinstance(is_connected, bool)


@pytest.mark.integration
@pytest.mark.requires_device
class TestDeviceIntegrationWithRealDevice:
    """Integration tests requiring real Android device."""
    
    def test_scan_devices_should_find_real_devices(self, real_android_device):
        """Test scan_devices finds connected real devices."""
        # Act
        devices = scan_devices()
        
        # Assert
        assert len(devices) > 0
        device_ids = [d['id'] for d in devices]
        assert real_android_device in device_ids
        
        # Find our device
        our_device = next(d for d in devices if d['id'] == real_android_device)
        assert our_device['status'] == 'device'
    
    def test_device_manager_can_connect_to_real_device(self, real_android_device):
        """Test DeviceManager can connect to real device."""
        # Arrange
        manager = DeviceManager()
        
        # Act
        device = manager.connect_to_device(real_android_device)
        
        # Assert
        assert device is not None
        assert device.device_id == real_android_device
        assert device.is_connected()
    
    def test_real_device_basic_operations_work(self, real_android_device):
        """Test basic operations work with real device."""
        # Arrange
        device = AndroidDevice(real_android_device)
        
        # Act & Assert
        # Test connectivity
        assert device.is_connected()
        
        # Test command execution
        result = device.execute_command('shell echo "test"')
        assert result.success
        assert b'test' in result.stdout
        
        # Test device info
        info = device.get_device_info()
        assert info['id'] == real_android_device
        assert 'model' in info
        assert 'android_version' in info
        
        # Test package check (system app should exist)
        assert device.is_app_installed('com.android.settings')
        assert not device.is_app_installed('com.nonexistent.package')
    
    def test_real_device_app_management(self, real_android_device):
        """Test app management operations with real device."""
        # Note: This test doesn't actually install/uninstall to avoid side effects
        # It just tests that the commands execute without errors
        
        # Arrange
        device = AndroidDevice(real_android_device)
        
        # Act & Assert
        # Test that methods don't raise exceptions (don't actually install/uninstall)
        try:
            # Just check if package exists (should not throw)
            device.is_app_installed('com.android.settings')
            
            # Test app start/stop with system app (less risky)
            # Note: In real testing, you might want to use a test app
            device.start_app('com.android.settings')  # Start settings
            device.stop_app('com.android.settings')   # Stop settings
            
        except Exception as e:
            pytest.fail(f"Basic app management operations failed: {e}")