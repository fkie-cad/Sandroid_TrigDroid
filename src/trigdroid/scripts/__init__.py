"""TrigDroid Frida Scripts Access Module.

This module provides programmatic access to TrigDroid's compiled Frida scripts.
Scripts are bundled with the package and can be accessed via helper functions.

Usage:
    from trigdroid.scripts import get_bypass_script_path, get_main_script_path

    # For objection integration
    bypass_path = get_bypass_script_path()
    if bypass_path:
        os.system(f"objection -g com.example.app explore -s {bypass_path}")

    # For JobManager/Frida integration
    main_path = get_main_script_path()

    # For individual hooks
    ssl_hook = get_hook_script_path("ssl-unpinning")
"""

import os
from pathlib import Path
from typing import Optional

# Script filenames
BYPASS_SCRIPT = "trigdroid_bypass_bundle.js"
MAIN_SCRIPT = "main_bundle.js"  # Bundled version (self-contained)
MAIN_SCRIPT_UNBUNDLED = "main.js"  # Unbundled version (requires hooks/)

# Individual hook scripts (in hooks/ subdirectory)
HOOK_SCRIPTS = {
    "ssl-unpinning": "ssl-unpinning.js",
    "root-detection": "root-detection.js",
    "frida-detection": "frida-detection.js",
    "emulator-detection": "emulator-detection.js",
    "debug-detection": "debug-detection.js",
    "android-build": "android-build.js",
    "android-sensors": "android-sensors.js",
}


def get_scripts_directory() -> Path:
    """Get the directory containing TrigDroid Frida scripts.

    Returns:
        Path to the scripts directory within the trigdroid package.
    """
    return Path(__file__).parent


def get_bypass_script_path() -> Optional[str]:
    """Get the path to the TrigDroid bypass script.

    This is the unified bypass script with RPC exports for:
    - SSL unpinning
    - Root detection bypass
    - Frida detection bypass
    - Emulator detection bypass
    - Debug detection bypass

    The script can be loaded into objection via `-s` flag or used
    with Frida's `session.create_script()`.

    Returns:
        Absolute path to the bypass script, or None if not found.

    Example:
        >>> from trigdroid.scripts import get_bypass_script_path
        >>> path = get_bypass_script_path()
        >>> # Use with objection
        >>> subprocess.run(["objection", "-g", package, "-s", path, "explore"])
        >>> # Or load with Frida
        >>> with open(path) as f:
        ...     script = session.create_script(f.read())
    """
    scripts_dir = get_scripts_directory()
    script_path = scripts_dir / BYPASS_SCRIPT

    if script_path.exists():
        return str(script_path.resolve())

    # Fallback: check development location
    dev_path = Path(__file__).parent.parent.parent.parent / "frida_hooks" / "dist" / BYPASS_SCRIPT
    if dev_path.exists():
        return str(dev_path.resolve())

    return None


def get_main_script_path(bundled: bool = True) -> Optional[str]:
    """Get the path to the main TrigDroid Frida script.

    This is the primary instrumentation script for TrigDroid testing,
    including sensor manipulation and trigger detection.

    Args:
        bundled: If True (default), returns the bundled self-contained version.
                 If False, returns the unbundled version (requires hooks/ directory).

    Returns:
        Absolute path to the main script, or None if not found.
    """
    scripts_dir = get_scripts_directory()
    script_name = MAIN_SCRIPT if bundled else MAIN_SCRIPT_UNBUNDLED
    script_path = scripts_dir / script_name

    if script_path.exists():
        return str(script_path.resolve())

    # Fallback: check development location
    dev_path = Path(__file__).parent.parent.parent.parent / "frida_hooks" / "dist" / script_name
    if dev_path.exists():
        return str(dev_path.resolve())

    return None


def get_hooks_directory() -> Path:
    """Get the directory containing individual hook scripts.

    Returns:
        Path to the hooks/ subdirectory within scripts.
    """
    return get_scripts_directory() / "hooks"


def get_hook_script_path(hook_name: str) -> Optional[str]:
    """Get the path to an individual hook script.

    Available hooks:
    - ssl-unpinning: SSL/TLS certificate pinning bypass
    - root-detection: Root/su detection bypass
    - frida-detection: Frida detection bypass
    - emulator-detection: Emulator detection bypass
    - debug-detection: Debug detection bypass
    - android-build: Android Build property manipulation
    - android-sensors: Android sensor data manipulation

    Args:
        hook_name: Name of the hook (e.g., "ssl-unpinning", "root-detection")

    Returns:
        Absolute path to the hook script, or None if not found.

    Example:
        >>> path = get_hook_script_path("ssl-unpinning")
        >>> with open(path) as f:
        ...     script = session.create_script(f.read())
    """
    if hook_name not in HOOK_SCRIPTS:
        return None

    script_filename = HOOK_SCRIPTS[hook_name]
    hooks_dir = get_hooks_directory()
    script_path = hooks_dir / script_filename

    if script_path.exists():
        return str(script_path.resolve())

    # Fallback: check development location
    dev_path = Path(__file__).parent.parent.parent.parent / "frida_hooks" / "dist" / "hooks" / script_filename
    if dev_path.exists():
        return str(dev_path.resolve())

    return None


def list_available_hooks() -> list[str]:
    """List all available individual hook scripts.

    Returns:
        List of hook names that can be used with get_hook_script_path().
    """
    return list(HOOK_SCRIPTS.keys())


def get_script_path(script_name: str) -> Optional[str]:
    """Get the path to a specific Frida script by name.

    Args:
        script_name: Name of the script file (e.g., "android-sensors.js")

    Returns:
        Absolute path to the script, or None if not found.
    """
    scripts_dir = get_scripts_directory()
    script_path = scripts_dir / script_name

    if script_path.exists():
        return str(script_path.resolve())

    # Fallback: check development location
    dev_path = Path(__file__).parent.parent.parent.parent / "frida_hooks" / "dist" / script_name
    if dev_path.exists():
        return str(dev_path.resolve())

    return None


def list_available_scripts(include_hooks: bool = True) -> list[str]:
    """List all available Frida scripts.

    Args:
        include_hooks: If True (default), includes individual hook scripts
                      from the hooks/ subdirectory.

    Returns:
        List of script filenames available in the package.
    """
    scripts_dir = get_scripts_directory()
    scripts = []

    # Check package directory for main scripts
    for f in scripts_dir.glob("*.js"):
        scripts.append(f.name)

    # Include hooks if requested
    if include_hooks:
        hooks_dir = get_hooks_directory()
        if hooks_dir.exists():
            for f in hooks_dir.glob("*.js"):
                scripts.append(f"hooks/{f.name}")

    # Also check development location if empty
    if not scripts:
        dev_dir = Path(__file__).parent.parent.parent.parent / "frida_hooks" / "dist"
        if dev_dir.exists():
            for f in dev_dir.glob("*.js"):
                scripts.append(f.name)
            if include_hooks:
                hooks_dev_dir = dev_dir / "hooks"
                if hooks_dev_dir.exists():
                    for f in hooks_dev_dir.glob("*.js"):
                        scripts.append(f"hooks/{f.name}")

    return sorted(set(scripts))


def read_script(script_name: str) -> Optional[str]:
    """Read and return the contents of a Frida script.

    This is useful when you need to pass the script source directly
    to Frida's `create_script()` method.

    Args:
        script_name: Name of the script file

    Returns:
        Script source code as string, or None if not found.

    Example:
        >>> source = read_script("trigdroid_bypass_bundle.js")
        >>> script = session.create_script(source)
    """
    path = get_script_path(script_name)
    if path is None:
        return None

    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


# Convenience exports
__all__ = [
    "get_scripts_directory",
    "get_hooks_directory",
    "get_bypass_script_path",
    "get_main_script_path",
    "get_hook_script_path",
    "get_script_path",
    "list_available_scripts",
    "list_available_hooks",
    "read_script",
    "BYPASS_SCRIPT",
    "MAIN_SCRIPT",
    "MAIN_SCRIPT_UNBUNDLED",
    "HOOK_SCRIPTS",
]
