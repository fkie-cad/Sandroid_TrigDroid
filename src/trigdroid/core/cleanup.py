"""Resource cleanup handlers for TrigDroid."""

import logging
import tempfile
import shutil
from typing import List, Optional, Callable, Any
from pathlib import Path
import atexit
import weakref


class CleanupManager:
    """Manages cleanup of resources during TrigDroid execution.
    
    This class ensures that temporary files, processes, and other resources
    are properly cleaned up when TrigDroid exits, even if execution is interrupted.
    
    Examples:
        # Register a cleanup function
        cleanup = CleanupManager()
        cleanup.register_file("/tmp/trigdroid_temp.log")
        cleanup.register_callback(lambda: print("Cleaning up..."))
        
        # Use as context manager
        with CleanupManager() as cleanup:
            cleanup.register_file(temp_file)
            # ... do work ...
        # Cleanup happens automatically
    """
    
    _instances: List[weakref.ReferenceType] = []
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self._logger = logger or logging.getLogger(__name__)
        self._temp_files: List[Path] = []
        self._temp_dirs: List[Path] = []
        self._callbacks: List[Callable[[], Any]] = []
        self._processes: List[Any] = []  # Process objects to terminate
        self._frida_sessions: List[Any] = []  # Frida sessions to detach
        self._cleaned_up = False
        
        # Register this instance for global cleanup
        CleanupManager._instances.append(weakref.ref(self))
    
    def __enter__(self) -> 'CleanupManager':
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and perform cleanup."""
        self.cleanup()
    
    def register_file(self, file_path: str) -> None:
        """Register a file for cleanup.
        
        Args:
            file_path: Path to file to delete on cleanup
        """
        path = Path(file_path)
        if path not in self._temp_files:
            self._temp_files.append(path)
            self._logger.debug(f"Registered file for cleanup: {path}")
    
    def register_directory(self, dir_path: str) -> None:
        """Register a directory for cleanup.
        
        Args:
            dir_path: Path to directory to delete on cleanup
        """
        path = Path(dir_path)
        if path not in self._temp_dirs:
            self._temp_dirs.append(path)
            self._logger.debug(f"Registered directory for cleanup: {path}")
    
    def register_callback(self, callback: Callable[[], Any]) -> None:
        """Register a callback function for cleanup.
        
        Args:
            callback: Function to call during cleanup
        """
        self._callbacks.append(callback)
        self._logger.debug(f"Registered callback for cleanup: {callback.__name__}")
    
    def register_process(self, process: Any) -> None:
        """Register a process for termination.
        
        Args:
            process: Process object with terminate() method
        """
        self._processes.append(process)
        self._logger.debug(f"Registered process for cleanup: {process}")
    
    def register_frida_session(self, session: Any) -> None:
        """Register a Frida session for detachment.
        
        Args:
            session: Frida session object
        """
        self._frida_sessions.append(session)
        self._logger.debug(f"Registered Frida session for cleanup: {session}")
    
    def create_temp_file(self, suffix: str = "", prefix: str = "trigdroid_") -> Path:
        """Create a temporary file that will be cleaned up.
        
        Args:
            suffix: File suffix
            prefix: File prefix
            
        Returns:
            Path to temporary file
        """
        fd, temp_path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
        import os
        os.close(fd)  # Close the file descriptor
        
        path = Path(temp_path)
        self.register_file(path)
        return path
    
    def create_temp_dir(self, prefix: str = "trigdroid_") -> Path:
        """Create a temporary directory that will be cleaned up.
        
        Args:
            prefix: Directory prefix
            
        Returns:
            Path to temporary directory
        """
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        path = Path(temp_dir)
        self.register_directory(path)
        return path
    
    def cleanup(self) -> None:
        """Perform all registered cleanup operations."""
        if self._cleaned_up:
            return
        
        self._logger.debug("Starting cleanup process...")
        
        # Clean up Frida sessions first
        for session in self._frida_sessions:
            try:
                if hasattr(session, 'detach'):
                    session.detach()
                    self._logger.debug(f"Detached Frida session: {session}")
            except Exception as e:
                self._logger.warning(f"Failed to detach Frida session {session}: {e}")
        
        # Terminate processes
        for process in self._processes:
            try:
                if hasattr(process, 'terminate'):
                    process.terminate()
                    self._logger.debug(f"Terminated process: {process}")
                elif hasattr(process, 'kill'):
                    process.kill()
                    self._logger.debug(f"Killed process: {process}")
            except Exception as e:
                self._logger.warning(f"Failed to terminate process {process}: {e}")
        
        # Run cleanup callbacks
        for callback in self._callbacks:
            try:
                callback()
                self._logger.debug(f"Executed cleanup callback: {callback.__name__}")
            except Exception as e:
                self._logger.warning(f"Cleanup callback {callback.__name__} failed: {e}")
        
        # Clean up temporary files
        for file_path in self._temp_files:
            try:
                if file_path.exists():
                    file_path.unlink()
                    self._logger.debug(f"Deleted temporary file: {file_path}")
            except Exception as e:
                self._logger.warning(f"Failed to delete file {file_path}: {e}")
        
        # Clean up temporary directories
        for dir_path in self._temp_dirs:
            try:
                if dir_path.exists() and dir_path.is_dir():
                    shutil.rmtree(dir_path)
                    self._logger.debug(f"Deleted temporary directory: {dir_path}")
            except Exception as e:
                self._logger.warning(f"Failed to delete directory {dir_path}: {e}")
        
        self._cleaned_up = True
        self._logger.debug("Cleanup process completed")
    
    @classmethod
    def cleanup_all(cls) -> None:
        """Cleanup all active CleanupManager instances."""
        for ref in cls._instances[:]:  # Copy list to avoid modification during iteration
            instance = ref()
            if instance is not None:
                instance.cleanup()
            else:
                cls._instances.remove(ref)


# Global cleanup manager instance
_global_cleanup_manager: Optional[CleanupManager] = None


def get_global_cleanup_manager() -> CleanupManager:
    """Get the global cleanup manager instance.
    
    Returns:
        Global CleanupManager instance
    """
    global _global_cleanup_manager
    if _global_cleanup_manager is None:
        _global_cleanup_manager = CleanupManager()
    return _global_cleanup_manager


def register_cleanup_file(file_path: str) -> None:
    """Register a file for cleanup using the global manager.
    
    Args:
        file_path: Path to file to delete on cleanup
    """
    get_global_cleanup_manager().register_file(file_path)


def register_cleanup_dir(dir_path: str) -> None:
    """Register a directory for cleanup using the global manager.
    
    Args:
        dir_path: Path to directory to delete on cleanup
    """
    get_global_cleanup_manager().register_directory(dir_path)


def register_cleanup_callback(callback: Callable[[], Any]) -> None:
    """Register a callback for cleanup using the global manager.
    
    Args:
        callback: Function to call during cleanup
    """
    get_global_cleanup_manager().register_callback(callback)


def create_temp_file(suffix: str = "", prefix: str = "trigdroid_") -> Path:
    """Create a temporary file using the global cleanup manager.
    
    Args:
        suffix: File suffix
        prefix: File prefix
        
    Returns:
        Path to temporary file
    """
    return get_global_cleanup_manager().create_temp_file(suffix, prefix)


def create_temp_dir(prefix: str = "trigdroid_") -> Path:
    """Create a temporary directory using the global cleanup manager.
    
    Args:
        prefix: Directory prefix
        
    Returns:
        Path to temporary directory
    """
    return get_global_cleanup_manager().create_temp_dir(prefix)


# Register global cleanup on exit
def _global_cleanup_handler():
    """Global cleanup handler for atexit."""
    CleanupManager.cleanup_all()


atexit.register(_global_cleanup_handler)


# Context manager for temporary resources
class TempResource:
    """Context manager for temporary resources with automatic cleanup.
    
    Examples:
        # Temporary file
        with TempResource.file() as temp_file:
            temp_file.write_text("test data")
            # ... use file ...
        # File is automatically deleted
        
        # Temporary directory
        with TempResource.dir() as temp_dir:
            (temp_dir / "test.txt").write_text("test")
            # ... use directory ...
        # Directory is automatically deleted
    """
    
    def __init__(self, cleanup_manager: Optional[CleanupManager] = None):
        self._cleanup_manager = cleanup_manager or get_global_cleanup_manager()
    
    @classmethod
    def file(cls, suffix: str = "", prefix: str = "trigdroid_") -> 'TempFileResource':
        """Create a temporary file resource.
        
        Args:
            suffix: File suffix
            prefix: File prefix
            
        Returns:
            TempFileResource context manager
        """
        return TempFileResource(suffix, prefix)
    
    @classmethod
    def dir(cls, prefix: str = "trigdroid_") -> 'TempDirResource':
        """Create a temporary directory resource.
        
        Args:
            prefix: Directory prefix
            
        Returns:
            TempDirResource context manager
        """
        return TempDirResource(prefix)


class TempFileResource:
    """Context manager for temporary files."""
    
    def __init__(self, suffix: str = "", prefix: str = "trigdroid_"):
        self._suffix = suffix
        self._prefix = prefix
        self._path: Optional[Path] = None
        self._cleanup_manager = get_global_cleanup_manager()
    
    def __enter__(self) -> Path:
        self._path = self._cleanup_manager.create_temp_file(self._suffix, self._prefix)
        return self._path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._path and self._path.exists():
            try:
                self._path.unlink()
            except Exception:
                pass  # Cleanup manager will handle it


class TempDirResource:
    """Context manager for temporary directories."""
    
    def __init__(self, prefix: str = "trigdroid_"):
        self._prefix = prefix
        self._path: Optional[Path] = None
        self._cleanup_manager = get_global_cleanup_manager()
    
    def __enter__(self) -> Path:
        self._path = self._cleanup_manager.create_temp_dir(self._prefix)
        return self._path
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._path and self._path.exists():
            try:
                shutil.rmtree(self._path)
            except Exception:
                pass  # Cleanup manager will handle it