"""Dependency Injection Container for TrigDroid.

This module implements a simple but effective dependency injection container
that follows the Dependency Inversion Principle and enables loose coupling
between components.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Type, Callable, Dict, Any, Optional, Union
import logging

T = TypeVar('T')


class DIContainer:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._transients: Dict[str, Callable[[], Any]] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Union[Type[T], Callable[[], T]], name: Optional[str] = None) -> 'DIContainer':
        """Register a singleton service."""
        key = name or self._get_key(interface)
        
        if isinstance(implementation, type):
            # It's a class, create a factory
            self._factories[key] = lambda: implementation()
        else:
            # It's already a factory function or instance
            self._factories[key] = implementation
            
        return self
    
    def register_transient(self, interface: Type[T], implementation: Union[Type[T], Callable[[], T]], name: Optional[str] = None) -> 'DIContainer':
        """Register a transient service (new instance every time)."""
        key = name or self._get_key(interface)
        
        if isinstance(implementation, type):
            self._transients[key] = lambda: implementation()
        else:
            self._transients[key] = implementation
            
        return self
    
    def register_instance(self, interface: Type[T], instance: T, name: Optional[str] = None) -> 'DIContainer':
        """Register a specific instance."""
        key = name or self._get_key(interface)
        self._singletons[key] = instance
        return self
    
    def resolve(self, interface: Type[T], name: Optional[str] = None) -> T:
        """Resolve a service instance."""
        key = name or self._get_key(interface)
        
        # Check if it's already a singleton instance
        if key in self._singletons:
            return self._singletons[key]
        
        # Check if it's a singleton factory
        if key in self._factories:
            instance = self._factories[key]()
            self._singletons[key] = instance
            return instance
        
        # Check if it's a transient
        if key in self._transients:
            return self._transients[key]()
        
        raise ValueError(f"Service {key} not registered")
    
    def has_service(self, interface: Type[T], name: Optional[str] = None) -> bool:
        """Check if a service is registered."""
        key = name or self._get_key(interface)
        return (key in self._singletons or 
                key in self._factories or 
                key in self._transients)
    
    @staticmethod
    def _get_key(interface: Type[T]) -> str:
        """Get a key for the interface."""
        return f"{interface.__module__}.{interface.__qualname__}"


class ServiceLocator:
    """Service locator pattern implementation."""
    
    _container: Optional[DIContainer] = None
    
    @classmethod
    def set_container(cls, container: DIContainer) -> None:
        """Set the global container."""
        cls._container = container
    
    @classmethod
    def get_service(cls, interface: Type[T], name: Optional[str] = None) -> T:
        """Get a service from the global container."""
        if cls._container is None:
            raise RuntimeError("Container not initialized. Call ServiceLocator.set_container() first.")
        return cls._container.resolve(interface, name)


class Injectable(ABC):
    """Base class for injectable services."""
    
    def __init__(self):
        self._container: Optional[DIContainer] = None
    
    def set_container(self, container: DIContainer) -> None:
        """Set the DI container for this service."""
        self._container = container
    
    def get_service(self, interface: Type[T], name: Optional[str] = None) -> T:
        """Get a service from the container."""
        if self._container is None:
            raise RuntimeError("Container not set. Call set_container() first.")
        return self._container.resolve(interface, name)


def configure_container() -> DIContainer:
    """Configure the dependency injection container with TrigDroid services."""
    from ..interfaces import (
        ILogger, IConfigurationProvider, IConfigurationValidator,
        IAndroidDevice, ITestRunner, IFridaHookProvider, IChangelogWriter,
        IApplicationOrchestrator
    )
    from .logging import StandardLogger
    from .configuration import (
        CompositeConfigurationProvider, CommandLineConfigProvider,
        YamlConfigProvider, ConfigurationValidator
    )
    from .android import AndroidDevice
    from .changelog import FileChangelogWriter
    from ..test_runners import (
        FridaTestRunner, SensorTestRunner, NetworkTestRunner,
        BatteryTestRunner, ApplicationTestRunner
    )
    from .frida import TypeScriptFridaHookProvider
    from ..application import ApplicationOrchestrator
    
    container = DIContainer()
    
    # Register logger as singleton
    container.register_singleton(ILogger, StandardLogger)
    
    # Register configuration providers
    container.register_transient(IConfigurationProvider, lambda: CompositeConfigurationProvider([
        CommandLineConfigProvider(),
        YamlConfigProvider()
    ]), "composite")
    
    container.register_singleton(IConfigurationValidator, ConfigurationValidator)
    
    # Register Android device
    container.register_singleton(IAndroidDevice, AndroidDevice)
    
    # Register test runners
    container.register_transient(ITestRunner, FridaTestRunner, "frida")
    container.register_transient(ITestRunner, SensorTestRunner, "sensor")
    container.register_transient(ITestRunner, NetworkTestRunner, "network")
    container.register_transient(ITestRunner, BatteryTestRunner, "battery")
    container.register_transient(ITestRunner, ApplicationTestRunner, "application")
    
    # Register Frida hook provider
    container.register_singleton(IFridaHookProvider, TypeScriptFridaHookProvider)
    
    # Register changelog writer
    container.register_singleton(IChangelogWriter, FileChangelogWriter)
    
    # Register application orchestrator
    container.register_singleton(IApplicationOrchestrator, ApplicationOrchestrator)
    
    return container


# Dependency injection decorators
def inject(**dependencies):
    """Decorator to inject dependencies into a class constructor."""
    def decorator(cls):
        original_init = cls.__init__
        
        def new_init(self, *args, **kwargs):
            # Resolve dependencies
            container = ServiceLocator._container
            if container:
                for name, interface in dependencies.items():
                    if name not in kwargs:
                        kwargs[name] = container.resolve(interface)
            
            # Call original constructor
            original_init(self, *args, **kwargs)
        
        cls.__init__ = new_init
        return cls
    
    return decorator


def inject_service(interface: Type[T], name: Optional[str] = None):
    """Decorator to inject a single service."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            service = ServiceLocator.get_service(interface, name)
            return func(service, *args, **kwargs)
        return wrapper
    return decorator