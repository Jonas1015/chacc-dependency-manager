"""
Test script to verify that hash calculations include environment factors.
"""

import sys
sys.path.insert(0, 'src')

from chacc.utils import calculate_module_hash, get_environment_hash


def test_hash_includes_environment():
    """Test that module hashes include environment information."""
    print("=== Testing Hash Environment Inclusion ===")

    env_hash = get_environment_hash()
    print(f"Environment hash: {env_hash}")

    module_hash = calculate_module_hash("test_module", "requests>=2.25.0")
    print(f"Module hash: {module_hash}")

    import hashlib
    content_only_hash = hashlib.sha256("test_module:requests>=2.25.0".encode()).hexdigest()
    print(f"Content-only hash: {content_only_hash}")

    if module_hash != content_only_hash:
        print("✅ Module hash includes environment factors")
    else:
        print("❌ Module hash does not include environment factors")

    module_hash2 = calculate_module_hash("test_module", "requests>=2.25.0")
    if module_hash == module_hash2:
        print("✅ Same content + environment produces consistent hash")
    else:
        print("❌ Hash is not consistent")

    print("\n🎉 Hash environment test completed!")


if __name__ == "__main__":
    test_hash_includes_environment()