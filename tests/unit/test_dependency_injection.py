"""Unit tests for dependency injection container."""

import pytest
from unittest.mock import Mock
from typing import Protocol, runtime_checkable

from TrigDroid_Infrastructure.infrastructure.dependency_injection import (
    DIContainer, ServiceLocator, configure_container
)
from TrigDroid_Infrastructure.interfaces import ILogger


@runtime_checkable
class ITestService(Protocol):
    """Test service interface for DI testing."""
    def test_method(self) -> str: ...


class MockTestService:
    """Mock implementation of test service."""
    
    def test_method(self) -> str:
        return "mock_result"


class AnotherMockTestService:
    """Another mock implementation of test service."""
    
    def test_method(self) -> str:
        return "another_mock_result"


class TestDIContainer:
    """Test suite for DIContainer class."""
    
    def test_container_initialization_should_succeed(self):
        """Test container can be initialized."""
        # Act
        container = DIContainer()
        
        # Assert
        assert container is not None
        assert hasattr(container, '_services')
        assert hasattr(container, '_instances')
    
    def test_register_singleton_should_store_service_factory(self):
        """Test singleton service registration."""
        # Arrange
        container = DIContainer()
        
        # Act
        container.register_singleton(ITestService, MockTestService)
        
        # Assert
        assert container.has_service(ITestService)
    
    def test_register_transient_should_store_service_factory(self):
        """Test transient service registration."""
        # Arrange
        container = DIContainer()
        
        # Act
        container.register_transient(ITestService, MockTestService)
        
        # Assert
        assert container.has_service(ITestService)
    
    def test_register_instance_should_store_service_instance(self):
        """Test instance service registration."""
        # Arrange
        container = DIContainer()
        service_instance = MockTestService()
        
        # Act
        container.register_instance(ITestService, service_instance)
        
        # Assert
        assert container.has_service(ITestService)
    
    def test_resolve_singleton_should_return_same_instance(self):
        """Test singleton resolution returns same instance."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestService, MockTestService)
        
        # Act
        instance1 = container.resolve(ITestService)
        instance2 = container.resolve(ITestService)
        
        # Assert
        assert instance1 is instance2
        assert isinstance(instance1, MockTestService)
        assert instance1.test_method() == "mock_result"
    
    def test_resolve_transient_should_return_different_instances(self):
        """Test transient resolution returns different instances."""
        # Arrange
        container = DIContainer()
        container.register_transient(ITestService, MockTestService)
        
        # Act
        instance1 = container.resolve(ITestService)
        instance2 = container.resolve(ITestService)
        
        # Assert
        assert instance1 is not instance2
        assert isinstance(instance1, MockTestService)
        assert isinstance(instance2, MockTestService)
        assert instance1.test_method() == "mock_result"
        assert instance2.test_method() == "mock_result"
    
    def test_resolve_instance_should_return_registered_instance(self):
        """Test instance resolution returns registered instance."""
        # Arrange
        container = DIContainer()
        service_instance = MockTestService()
        container.register_instance(ITestService, service_instance)
        
        # Act
        resolved_instance = container.resolve(ITestService)
        
        # Assert
        assert resolved_instance is service_instance
    
    def test_resolve_with_key_should_return_correct_service(self):
        """Test resolution with key returns correct service."""
        # Arrange
        container = DIContainer()
        container.register_transient(ITestService, MockTestService, "mock1")
        container.register_transient(ITestService, AnotherMockTestService, "mock2")
        
        # Act
        service1 = container.resolve(ITestService, "mock1")
        service2 = container.resolve(ITestService, "mock2")
        
        # Assert
        assert isinstance(service1, MockTestService)
        assert isinstance(service2, AnotherMockTestService)
        assert service1.test_method() == "mock_result"
        assert service2.test_method() == "another_mock_result"
    
    def test_resolve_unregistered_service_should_raise_error(self):
        """Test resolving unregistered service raises appropriate error."""
        # Arrange
        container = DIContainer()
        
        # Act & Assert
        with pytest.raises((KeyError, ValueError, RuntimeError)):
            container.resolve(ITestService)
    
    def test_resolve_with_invalid_key_should_raise_error(self):
        """Test resolving with invalid key raises appropriate error."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestService, MockTestService)
        
        # Act & Assert
        with pytest.raises((KeyError, ValueError, RuntimeError)):
            container.resolve(ITestService, "invalid_key")
    
    def test_has_service_should_return_true_for_registered_services(self):
        """Test has_service returns True for registered services."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestService, MockTestService)
        
        # Act & Assert
        assert container.has_service(ITestService) is True
    
    def test_has_service_should_return_false_for_unregistered_services(self):
        """Test has_service returns False for unregistered services."""
        # Arrange
        container = DIContainer()
        
        # Act & Assert
        assert container.has_service(ITestService) is False
    
    def test_has_service_with_key_should_work_correctly(self):
        """Test has_service with key works correctly."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestService, MockTestService, "test_key")
        
        # Act & Assert
        assert container.has_service(ITestService, "test_key") is True
        assert container.has_service(ITestService, "other_key") is False
    
    def test_register_factory_function_should_work(self):
        """Test registering factory functions works."""
        # Arrange
        container = DIContainer()
        
        def service_factory():
            return MockTestService()
        
        # Act
        container.register_singleton(ITestService, service_factory)
        
        # Assert
        service = container.resolve(ITestService)
        assert isinstance(service, MockTestService)
        assert service.test_method() == "mock_result"
    
    def test_register_lambda_factory_should_work(self):
        """Test registering lambda factories works."""
        # Arrange
        container = DIContainer()
        
        # Act
        container.register_transient(ITestService, lambda: MockTestService())
        
        # Assert
        service = container.resolve(ITestService)
        assert isinstance(service, MockTestService)
    
    def test_clear_should_remove_all_services(self):
        """Test clear removes all registered services."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestService, MockTestService)
        assert container.has_service(ITestService)
        
        # Act
        container.clear()
        
        # Assert
        assert not container.has_service(ITestService)


class TestServiceLocator:
    """Test suite for ServiceLocator class."""
    
    def test_set_container_should_store_container(self):
        """Test setting container stores it correctly."""
        # Arrange
        container = DIContainer()
        
        # Act
        ServiceLocator.set_container(container)
        
        # Assert
        # Note: This tests internal implementation - adjust if needed
        assert ServiceLocator._container is container
    
    def test_get_service_should_resolve_from_container(self):
        """Test get_service resolves from stored container."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestService, MockTestService)
        ServiceLocator.set_container(container)
        
        # Act
        service = ServiceLocator.get_service(ITestService)
        
        # Assert
        assert isinstance(service, MockTestService)
        assert service.test_method() == "mock_result"
    
    def test_get_service_with_key_should_work(self):
        """Test get_service with key works correctly."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestService, MockTestService, "test_key")
        ServiceLocator.set_container(container)
        
        # Act
        service = ServiceLocator.get_service(ITestService, "test_key")
        
        # Assert
        assert isinstance(service, MockTestService)
    
    def test_get_service_without_container_should_raise_error(self):
        """Test get_service without container raises error."""
        # Arrange
        ServiceLocator.set_container(None)  # Clear container
        
        # Act & Assert
        with pytest.raises((RuntimeError, AttributeError, ValueError)):
            ServiceLocator.get_service(ITestService)
    
    def test_has_service_should_check_container(self):
        """Test has_service checks stored container."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestService, MockTestService)
        ServiceLocator.set_container(container)
        
        # Act & Assert
        assert ServiceLocator.has_service(ITestService) is True
    
    def test_clear_should_remove_container_reference(self):
        """Test clear removes container reference."""
        # Arrange
        container = DIContainer()
        ServiceLocator.set_container(container)
        
        # Act
        ServiceLocator.clear()
        
        # Assert
        assert ServiceLocator._container is None


class TestConfigureContainer:
    """Test suite for configure_container function."""
    
    def test_configure_container_should_return_configured_container(self):
        """Test configure_container returns properly configured container."""
        # Act
        container = configure_container()
        
        # Assert
        assert isinstance(container, DIContainer)
        # Should have standard services registered
        assert container.has_service(ILogger)
    
    def test_configure_container_should_register_standard_services(self):
        """Test configure_container registers expected services."""
        # Act
        container = configure_container()
        
        # Assert
        # Check for expected service registrations
        # Note: Adjust based on actual implementation
        standard_services = [ILogger]  # Add other expected services
        
        for service in standard_services:
            assert container.has_service(service), f"Service {service} should be registered"
    
    def test_configured_services_should_be_resolvable(self):
        """Test configured services can be resolved."""
        # Act
        container = configure_container()
        
        # Assert
        try:
            logger = container.resolve(ILogger)
            assert logger is not None
        except Exception as e:
            pytest.fail(f"Should be able to resolve ILogger: {e}")
    
    def test_multiple_configure_calls_should_return_different_containers(self):
        """Test multiple configure_container calls return different instances."""
        # Act
        container1 = configure_container()
        container2 = configure_container()
        
        # Assert
        assert container1 is not container2
        # But should have same services
        assert container1.has_service(ILogger)
        assert container2.has_service(ILogger)


class TestDependencyInjectionIntegration:
    """Integration tests for DI system components."""
    
    def test_full_di_workflow_should_work(self):
        """Test complete DI workflow from registration to resolution."""
        # Arrange
        container = DIContainer()
        container.register_singleton(ITestService, MockTestService)
        ServiceLocator.set_container(container)
        
        # Act
        # Resolve via container
        service1 = container.resolve(ITestService)
        
        # Resolve via service locator
        service2 = ServiceLocator.get_service(ITestService)
        
        # Assert
        assert service1 is service2  # Same singleton instance
        assert service1.test_method() == "mock_result"
    
    def test_container_isolation_should_work(self):
        """Test different containers maintain isolation."""
        # Arrange
        container1 = DIContainer()
        container2 = DIContainer()
        
        container1.register_singleton(ITestService, MockTestService)
        container2.register_singleton(ITestService, AnotherMockTestService)
        
        # Act
        service1 = container1.resolve(ITestService)
        service2 = container2.resolve(ITestService)
        
        # Assert
        assert isinstance(service1, MockTestService)
        assert isinstance(service2, AnotherMockTestService)
        assert service1.test_method() != service2.test_method()
    
    def test_service_locator_container_switching_should_work(self):
        """Test switching containers in ServiceLocator works."""
        # Arrange
        container1 = DIContainer()
        container2 = DIContainer()
        
        container1.register_singleton(ITestService, MockTestService)
        container2.register_singleton(ITestService, AnotherMockTestService)
        
        # Act & Assert
        ServiceLocator.set_container(container1)
        service1 = ServiceLocator.get_service(ITestService)
        assert isinstance(service1, MockTestService)
        
        ServiceLocator.set_container(container2)
        service2 = ServiceLocator.get_service(ITestService)
        assert isinstance(service2, AnotherMockTestService)
    
    def teardown_method(self):
        """Clean up after each test."""
        ServiceLocator.clear()