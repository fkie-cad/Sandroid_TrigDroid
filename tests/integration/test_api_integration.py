"""Integration tests for TrigDroid API components."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch

from trigdroid.api.main import TrigDroidAPI, quick_test
from trigdroid.api.config import TestConfiguration
from trigdroid.api.devices import DeviceManager
from trigdroid.core.enums import LogLevel, TestPhase
from trigdroid.exceptions import TrigDroidError, DeviceError, ConfigurationError


@pytest.mark.integration
class TestTrigDroidAPIIntegration:
    """Integration tests for TrigDroidAPI class."""
    
    def test_api_context_manager_should_initialize_and_cleanup(self):
        """Test API context manager properly initializes and cleans up."""
        # Arrange
        config = TestConfiguration(package="com.example.test")
        
        # Act & Assert
        with patch('trigdroid.api.main.DeviceManager') as mock_device_manager:
            mock_device = Mock()
            mock_device_manager.return_value.connect_to_device.return_value = mock_device
            
            with patch('trigdroid.api.main.configure_container') as mock_configure:
                mock_container = Mock()
                mock_configure.return_value = mock_container
                mock_orchestrator = Mock()
                mock_container.resolve.return_value = mock_orchestrator
                
                with TrigDroidAPI(config) as api:
                    # Should be initialized
                    assert api._initialized is True
                    assert api._device is mock_device
                    assert api._container is mock_container
                
                # Should be cleaned up after context exit
                assert api._initialized is False
    
    def test_api_initialization_with_invalid_config_should_raise_error(self):
        """Test API initialization with invalid configuration raises error."""
        # Arrange
        config = TestConfiguration(package="")  # Invalid empty package
        
        # Act & Assert
        with pytest.raises(ConfigurationError):
            TrigDroidAPI(config)
    
    def test_api_with_custom_device_should_use_provided_device(self):
        """Test API uses provided device instead of creating one."""
        # Arrange
        config = TestConfiguration(package="com.example.test")
        custom_device = Mock()
        
        # Act
        with patch('trigdroid.api.main.configure_container') as mock_configure:
            mock_container = Mock()
            mock_configure.return_value = mock_container
            mock_orchestrator = Mock()
            mock_container.resolve.return_value = mock_orchestrator
            
            with TrigDroidAPI(config, device=custom_device) as api:
                # Assert
                assert api._device is custom_device
    
    @patch('trigdroid.api.main.DeviceManager')
    @patch('trigdroid.api.main.configure_container')
    def test_run_tests_should_execute_full_workflow(self, mock_configure, mock_device_manager):
        """Test run_tests executes complete workflow."""
        # Arrange
        config = TestConfiguration(package="com.example.test")
        
        mock_device = Mock()
        mock_device_manager.return_value.connect_to_device.return_value = mock_device
        
        mock_container = Mock()
        mock_configure.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_orchestrator.setup.return_value = True
        mock_orchestrator.execute_tests.return_value = True
        mock_orchestrator.teardown.return_value = True
        mock_container.resolve.return_value = mock_orchestrator
        
        # Act
        with TrigDroidAPI(config) as api:
            result = api.run_tests()
        
        # Assert
        assert result.success is True
        assert result.phase == TestPhase.EXECUTION
        mock_orchestrator.setup.assert_called_once()
        mock_orchestrator.execute_tests.assert_called_once()
        mock_orchestrator.teardown.assert_called_once()
    
    @patch('trigdroid.api.main.DeviceManager')
    @patch('trigdroid.api.main.configure_container')
    def test_run_tests_should_handle_setup_failure(self, mock_configure, mock_device_manager):
        """Test run_tests handles setup phase failures."""
        # Arrange
        config = TestConfiguration(package="com.example.test")
        
        mock_device = Mock()
        mock_device_manager.return_value.connect_to_device.return_value = mock_device
        
        mock_container = Mock()
        mock_configure.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_orchestrator.setup.return_value = False  # Setup fails
        mock_orchestrator.teardown.return_value = True
        mock_container.resolve.return_value = mock_orchestrator
        
        # Act
        with TrigDroidAPI(config) as api:
            result = api.run_tests()
        
        # Assert
        assert result.success is False
        assert result.phase == TestPhase.SETUP
        assert "Setup phase failed" in result.error
        mock_orchestrator.teardown.assert_called_once()
    
    @patch('trigdroid.api.main.DeviceManager')
    @patch('trigdroid.api.main.configure_container')
    def test_run_tests_should_handle_execution_failure(self, mock_configure, mock_device_manager):
        """Test run_tests handles execution phase failures."""
        # Arrange
        config = TestConfiguration(package="com.example.test")
        
        mock_device = Mock()
        mock_device_manager.return_value.connect_to_device.return_value = mock_device
        
        mock_container = Mock()
        mock_configure.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_orchestrator.setup.return_value = True
        mock_orchestrator.execute_tests.return_value = False  # Execution fails
        mock_orchestrator.teardown.return_value = True
        mock_container.resolve.return_value = mock_orchestrator
        
        # Act
        with TrigDroidAPI(config) as api:
            result = api.run_tests()
        
        # Assert
        assert result.success is False
        assert result.phase == TestPhase.EXECUTION
        assert "Test execution failed" in result.error
    
    @patch('trigdroid.api.main.DeviceManager')
    @patch('trigdroid.api.main.configure_container')
    def test_run_tests_should_always_call_teardown(self, mock_configure, mock_device_manager):
        """Test run_tests always calls teardown even on exceptions."""
        # Arrange
        config = TestConfiguration(package="com.example.test")
        
        mock_device = Mock()
        mock_device_manager.return_value.connect_to_device.return_value = mock_device
        
        mock_container = Mock()
        mock_configure.return_value = mock_container
        
        mock_orchestrator = Mock()
        mock_orchestrator.setup.side_effect = Exception("Test exception")
        mock_orchestrator.teardown.return_value = True
        mock_container.resolve.return_value = mock_orchestrator
        
        # Act
        with TrigDroidAPI(config) as api:
            result = api.run_tests()
        
        # Assert
        assert result.success is False
        mock_orchestrator.teardown.assert_called_once()
    
    @patch('trigdroid.api.main.DeviceManager')
    def test_get_device_info_should_return_device_information(self, mock_device_manager):
        """Test get_device_info returns device information."""
        # Arrange
        config = TestConfiguration(package="com.example.test")
        mock_device = Mock()
        expected_info = {'id': 'test_device', 'model': 'Test Model'}
        mock_device.get_device_info.return_value = expected_info
        mock_device_manager.return_value.connect_to_device.return_value = mock_device
        
        # Act
        with patch('trigdroid.api.main.configure_container'):
            with TrigDroidAPI(config) as api:
                device_info = api.get_device_info()
        
        # Assert
        assert device_info == expected_info
        mock_device.get_device_info.assert_called_once()
    
    def test_get_device_info_without_device_should_raise_error(self):
        """Test get_device_info without device raises error."""
        # Arrange
        config = TestConfiguration(package="com.example.test")
        api = TrigDroidAPI(config)
        api._device = None
        
        # Act & Assert
        with pytest.raises(DeviceError):
            api.get_device_info()
    
    @patch('trigdroid.api.main.DeviceManager')
    def test_list_installed_packages_should_return_package_list(self, mock_device_manager):
        """Test list_installed_packages returns list of packages."""
        # Arrange
        config = TestConfiguration(package="com.example.test")
        mock_device = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.stdout = b'package:com.example.app1\npackage:com.example.app2\n'
        mock_device.execute_command.return_value = mock_result
        mock_device_manager.return_value.connect_to_device.return_value = mock_device
        
        # Act
        with patch('trigdroid.api.main.configure_container'):
            with TrigDroidAPI(config) as api:
                packages = api.list_installed_packages()
        
        # Assert
        assert 'com.example.app1' in packages
        assert 'com.example.app2' in packages
        mock_device.execute_command.assert_called_with("shell pm list packages")
    
    @patch('trigdroid.api.main.DeviceManager')
    def test_is_package_installed_should_check_package_installation(self, mock_device_manager):
        """Test is_package_installed checks package installation status."""
        # Arrange
        config = TestConfiguration(package="com.example.test")
        mock_device = Mock()
        mock_device.is_app_installed.return_value = True
        mock_device_manager.return_value.connect_to_device.return_value = mock_device
        
        # Act
        with patch('trigdroid.api.main.configure_container'):
            with TrigDroidAPI(config) as api:
                is_installed = api.is_package_installed("com.example.target")
        
        # Assert
        assert is_installed is True
        mock_device.is_app_installed.assert_called_with("com.example.target")


@pytest.mark.integration
class TestQuickTestFunction:
    """Integration tests for quick_test convenience function."""
    
    @patch('trigdroid.api.main.TrigDroidAPI')
    def test_quick_test_should_create_api_and_run_tests(self, mock_api_class):
        """Test quick_test creates API and runs tests."""
        # Arrange
        mock_api_instance = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_api_instance.run_tests.return_value = mock_result
        mock_api_class.return_value.__enter__.return_value = mock_api_instance
        mock_api_class.return_value.__exit__.return_value = None
        
        # Act
        result = quick_test("com.example.test", acceleration=5)
        
        # Assert
        assert result is mock_result
        mock_api_class.assert_called_once()
        mock_api_instance.run_tests.assert_called_once()
    
    @patch('trigdroid.api.main.TrigDroidAPI')
    def test_quick_test_with_device_id_should_pass_device_id(self, mock_api_class):
        """Test quick_test passes device_id to configuration."""
        # Arrange
        mock_api_instance = Mock()
        mock_result = Mock()
        mock_api_instance.run_tests.return_value = mock_result
        mock_api_class.return_value.__enter__.return_value = mock_api_instance
        mock_api_class.return_value.__exit__.return_value = None
        
        # Act
        result = quick_test("com.example.test", device_id="emulator-5554")
        
        # Assert
        # Verify the configuration was created with correct device_id
        call_args = mock_api_class.call_args[0]
        config = call_args[0]
        assert config.package == "com.example.test"
        assert config.device_id == "emulator-5554"
    
    @patch('trigdroid.api.main.TrigDroidAPI')
    def test_quick_test_with_test_options_should_pass_options(self, mock_api_class):
        """Test quick_test passes test options to configuration."""
        # Arrange
        mock_api_instance = Mock()
        mock_result = Mock()
        mock_api_instance.run_tests.return_value = mock_result
        mock_api_class.return_value.__enter__.return_value = mock_api_instance
        mock_api_class.return_value.__exit__.return_value = None
        
        # Act
        result = quick_test(
            "com.example.test",
            acceleration=8,
            battery_rotation=3,
            frida_hooks=True,
            verbose=True
        )
        
        # Assert
        call_args = mock_api_class.call_args[0]
        config = call_args[0]
        assert config.package == "com.example.test"
        assert config.acceleration == 8
        assert config.battery_rotation == 3
        assert config.frida_hooks is True
        assert config.verbose is True


@pytest.mark.integration
@pytest.mark.requires_device
class TestTrigDroidAPIWithRealDevice:
    """Integration tests requiring real Android device."""
    
    def test_api_with_real_device_should_connect(self, real_android_device):
        """Test API can connect to real Android device."""
        # Arrange
        config = TestConfiguration(
            package="com.android.settings",  # System app that should exist
            min_runtime=1,
            acceleration=0  # Minimal test to avoid issues
        )
        
        # Act & Assert
        try:
            with TrigDroidAPI(config) as api:
                device_info = api.get_device_info()
                assert 'id' in device_info
                assert device_info['id'] == real_android_device
        except DeviceError:
            pytest.skip("Could not connect to real device")
    
    def test_api_can_check_package_installation(self, real_android_device):
        """Test API can check package installation on real device."""
        # Arrange
        config = TestConfiguration(package="com.android.settings")
        
        # Act & Assert
        try:
            with TrigDroidAPI(config) as api:
                # System settings should be installed
                is_installed = api.is_package_installed("com.android.settings")
                assert is_installed is True
                
                # Non-existent package should not be installed
                is_installed = api.is_package_installed("com.nonexistent.package")
                assert is_installed is False
        except DeviceError:
            pytest.skip("Could not connect to real device")
    
    def test_api_can_list_packages(self, real_android_device):
        """Test API can list installed packages on real device."""
        # Arrange
        config = TestConfiguration(package="com.android.settings")
        
        # Act & Assert
        try:
            with TrigDroidAPI(config) as api:
                packages = api.list_installed_packages()
                assert isinstance(packages, list)
                assert len(packages) > 0
                assert "com.android.settings" in packages
        except DeviceError:
            pytest.skip("Could not connect to real device")


@pytest.mark.integration
class TestConfigurationIntegration:
    """Integration tests for configuration handling."""
    
    def test_configuration_yaml_roundtrip_should_preserve_data(self):
        """Test configuration YAML save/load preserves all data."""
        # Arrange
        original_config = TestConfiguration(
            package="com.example.test",
            device_id="emulator-5554",
            acceleration=8,
            gyroscope=5,
            battery_rotation=3,
            frida_hooks=True,
            verbose=True,
            timeout=600
        )
        
        # Act
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_file = f.name
        
        try:
            original_config.to_yaml_file(yaml_file)
            loaded_config = TestConfiguration.from_yaml_file(yaml_file)
            
            # Assert
            assert loaded_config.package == original_config.package
            assert loaded_config.device_id == original_config.device_id
            assert loaded_config.acceleration == original_config.acceleration
            assert loaded_config.gyroscope == original_config.gyroscope
            assert loaded_config.battery_rotation == original_config.battery_rotation
            assert loaded_config.frida_hooks == original_config.frida_hooks
            assert loaded_config.verbose == original_config.verbose
            assert loaded_config.timeout == original_config.timeout
            
        finally:
            if os.path.exists(yaml_file):
                os.unlink(yaml_file)
    
    def test_configuration_validation_integration_should_work(self):
        """Test configuration validation works in practice."""
        # Test valid configuration
        valid_config = TestConfiguration(
            package="com.example.test",
            acceleration=5,
            battery_rotation=2,
            min_runtime=1
        )
        assert valid_config.is_valid()
        assert len(valid_config.validation_errors) == 0
        
        # Test invalid configuration
        invalid_config = TestConfiguration(
            package="",  # Invalid empty package
            acceleration=15,  # Invalid high value
            battery_rotation=10,  # Invalid high value
            min_runtime=-1  # Invalid negative value
        )
        assert not invalid_config.is_valid()
        assert len(invalid_config.validation_errors) > 0