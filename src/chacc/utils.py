"""
Utility functions for the ChaCC Dependency Manager.

Provides logging setup, hash calculations, and package management utilities.
"""

import hashlib
import logging
import platform
import subprocess
import sys
from typing import Dict, Set

try:
    from packaging.utils import canonicalize_name
except ImportError:
    def canonicalize_name(name: str) -> str:
        return name.replace('_', '-').lower()


default_logger = logging.getLogger('dependency_manager')
default_logger.setLevel(logging.DEBUG)
if not default_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(name)s - %(message)s')
    handler.setFormatter(formatter)
    default_logger.addHandler(handler)


def get_environment_hash() -> str:
    """Calculate hash of the current environment (Python version and OS)."""
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    os_info = f"{platform.system()}-{platform.release()}-{platform.machine()}"
    env_content = f"python:{python_version}:os:{os_info}"
    return hashlib.sha256(env_content.encode()).hexdigest()


def calculate_module_hash(module_name: str, requirements_content: str) -> str:
    """Calculate hash of a specific module's requirements including environment."""
    env_hash = get_environment_hash()
    content = f"{module_name}:{requirements_content}:env:{env_hash}"
    return hashlib.sha256(content.encode()).hexdigest()


def calculate_combined_requirements_hash(module_hashes: Dict[str, str]) -> str:
    """Calculate hash of all module requirement hashes combined."""
    sorted_hashes = sorted(module_hashes.items())
    combined = "|".join(f"{name}:{hash}" for name, hash in sorted_hashes)
    return hashlib.sha256(combined.encode()).hexdigest()


def get_installed_packages() -> Set[str]:
    """Get set of currently installed packages (canonicalized names)."""
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'list', '--format=freeze'
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            packages = set()
            for line in result.stdout.strip().split('\n'):
                if '==' in line:
                    package_name = line.split('==')[0]
                    canonical_name = canonicalize_name(package_name)
                    packages.add(canonical_name)
            return packages
        else:
            default_logger.warning(f"Failed to get installed packages: {result.stderr}")
            return set()
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        default_logger.warning(f"Error getting installed packages: {e}")
        return set()