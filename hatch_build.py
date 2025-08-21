"""Custom build hook for TrigDroid to compile TypeScript Frida hooks."""

import subprocess
import logging
import os
from pathlib import Path
from typing import Any, Dict

from hatchling.plugin import hookimpl


class TrigDroidBuildHook:
    """Build hook to compile TypeScript Frida hooks during package build."""
    
    PLUGIN_NAME = "trigdroid"
    
    def __init__(self, root: str, config: Dict[str, Any]) -> None:
        self.root = Path(root)
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def initialize(self, version: str, build_data: Dict[str, Any]) -> None:
        """Initialize the build hook."""
        self.logger.info("Initializing TrigDroid build hook")
        
        # Check if we need to build TypeScript hooks
        hooks_dir = self.root / "frida-hooks"
        if not hooks_dir.exists():
            self.logger.info("No frida-hooks directory found, skipping TypeScript compilation")
            return
        
        # Check for package.json
        package_json = hooks_dir / "package.json"
        if not package_json.exists():
            self.logger.warning("No package.json found in frida-hooks, skipping TypeScript compilation")
            return
        
        # Build TypeScript hooks
        try:
            self._build_typescript_hooks(hooks_dir)
            
            # Add compiled hooks to build artifacts
            dist_dir = hooks_dir / "dist"
            if dist_dir.exists():
                # Include all JavaScript files from dist
                for js_file in dist_dir.glob("**/*.js"):
                    relative_path = js_file.relative_to(self.root)
                    build_data.setdefault("artifacts", []).append(str(relative_path))
                    self.logger.info(f"Added hook artifact: {relative_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to build TypeScript hooks: {e}")
            raise
    
    def _build_typescript_hooks(self, hooks_dir: Path) -> None:
        """Build TypeScript hooks to JavaScript."""
        self.logger.info("Building TypeScript Frida hooks...")
        
        # Check for Node.js
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError("Node.js not available")
            self.logger.info(f"Using Node.js version: {result.stdout.strip()}")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise RuntimeError("Node.js is required to build TypeScript hooks") from e
        
        # Install dependencies
        self.logger.info("Installing Node.js dependencies...")
        result = subprocess.run(
            ["npm", "install"],
            cwd=hooks_dir,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )
        
        if result.returncode != 0:
            self.logger.error(f"npm install failed: {result.stderr}")
            raise RuntimeError(f"npm install failed: {result.stderr}")
        
        # Build TypeScript
        self.logger.info("Compiling TypeScript...")
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=hooks_dir,
            capture_output=True,
            text=True,
            timeout=120  # 2 minutes
        )
        
        if result.returncode != 0:
            self.logger.error(f"TypeScript build failed: {result.stderr}")
            raise RuntimeError(f"TypeScript build failed: {result.stderr}")
        
        self.logger.info("TypeScript compilation completed successfully")


@hookimpl
def hatch_register_build_hook():
    """Register the TrigDroid build hook with Hatchling."""
    return TrigDroidBuildHook