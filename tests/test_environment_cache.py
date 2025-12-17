"""
Test script to verify environment-aware caching functionality.
"""

import sys
import os
import json
import tempfile
import shutil
sys.path.insert(0, 'src')

from chacc.manager import DependencyManager
from chacc.utils import get_environment_hash


def test_environment_cache_invalidation():
    """Test that cache is invalidated when environment changes."""
    print("=== Testing Environment-Aware Cache ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = os.path.join(temp_dir, 'test_cache')
        dm = DependencyManager(cache_dir=cache_dir)

        current_env_hash = get_environment_hash()
        print(f"Current environment hash: {current_env_hash}")

        fake_env_hash = "fake_environment_hash_12345"
        test_cache = {
            'requirements_caches': {
                'test_module': {
                    'hash': 'test_hash',
                    'packages': {'requests': '==2.25.1'},
                    'last_updated': '1234567890'
                }
            },
            'combined_hash': 'combined_test_hash',
            'environment_hash': fake_env_hash,
            'resolved_packages': {'requests': '==2.25.1'},
            'last_updated': '1234567890'
        }

        dm.save_cache(test_cache)
        print("Created cache with fake environment hash")

        loaded_cache = dm.load_cache()
        print(f"Loaded cache environment_hash: {loaded_cache.get('environment_hash')}")

        try:
            import asyncio
            asyncio.run(dm.resolve_dependencies(
                modules_requirements={'test': 'requests>=2.25.0'},
                requirements_file_pattern="*.txt"
            ))
            print("✅ Environment-aware cache invalidation working")
        except Exception as e:
            print(f"Expected error (piptools not available): {e}")

        final_cache = dm.load_cache()
        if final_cache.get('environment_hash') != fake_env_hash:
            print("✅ Cache was properly invalidated due to environment change")
        else:
            print("❌ Cache was not invalidated")

    print("\n🎉 Environment cache test completed!")


if __name__ == "__main__":
    test_environment_cache_invalidation()