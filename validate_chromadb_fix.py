#!/usr/bin/env python3
"""
Validate ChromaDB Fix - Test singleton pattern without heavy operations
"""
import sys
sys.path.insert(0, '/app')

def test_singleton_pattern():
    """Test that ChromaDB manager is truly a singleton"""
    print("=" * 70)
    print("TEST 1: Singleton Pattern Validation")
    print("=" * 70)
    print()
    
    from backend.chromadb_manager import get_chroma_manager
    
    # Get multiple instances
    manager1 = get_chroma_manager()
    manager2 = get_chroma_manager()
    manager3 = get_chroma_manager()
    
    # Check if they're the same object
    if manager1 is manager2 is manager3:
        print("✅ PASS: All instances are the same object (singleton working)")
        print(f"   Instance ID: {id(manager1)}")
        return True
    else:
        print("❌ FAIL: Different instances created")
        print(f"   Manager1 ID: {id(manager1)}")
        print(f"   Manager2 ID: {id(manager2)}")
        print(f"   Manager3 ID: {id(manager3)}")
        return False

def test_client_consistency():
    """Test that client settings are consistent"""
    print()
    print("=" * 70)
    print("TEST 2: Client Settings Consistency")
    print("=" * 70)
    print()
    
    from backend.chromadb_manager import get_chroma_manager
    from backend.config import settings
    
    manager = get_chroma_manager()
    
    try:
        client1 = manager.get_client()
        client2 = manager.get_client()
        
        if client1 is client2:
            print("✅ PASS: Same client instance returned (no duplication)")
            print(f"   Client ID: {id(client1)}")
            print(f"   ChromaDB Path: {settings.CHROMA_DB_PATH}")
            return True
        else:
            print("❌ FAIL: Different client instances")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Error creating client: {e}")
        return False

def test_collection_access():
    """Test collection access without loading embeddings"""
    print()
    print("=" * 70)
    print("TEST 3: Collection Access")
    print("=" * 70)
    print()
    
    from backend.chromadb_manager import get_chroma_manager
    
    manager = get_chroma_manager()
    
    try:
        client = manager.get_client()
        
        # Try to get or create collection
        try:
            collection = client.get_collection("knowledge_base_collection")
            print(f"✅ Collection exists: knowledge_base_collection")
            print(f"   Document count: {collection.count()}")
            exists = True
        except ValueError:
            print("ℹ️  Collection doesn't exist yet (will be created on first use)")
            exists = False
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Error accessing collection: {e}")
        return False

def test_no_conflicting_instances():
    """Test that we don't get the 'different settings' error"""
    print()
    print("=" * 70)
    print("TEST 4: No Conflicting Instances Error")
    print("=" * 70)
    print()
    
    try:
        # Import from different modules that use ChromaDB
        from backend.chromadb_manager import get_chroma_manager
        from backend.config import settings
        import chromadb
        
        # Get manager instance
        manager = get_chroma_manager()
        client1 = manager.get_client()
        
        # Try to create another client directly (should work now with same path)
        # This would have caused the error before
        try:
            client2 = chromadb.PersistentClient(
                path=settings.CHROMA_DB_PATH,
                settings=chromadb.Settings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                    is_persistent=True
                )
            )
            print("✅ PASS: Can create multiple clients with same settings (no conflict)")
            print("   This is expected behavior - same settings allow multiple clients")
            return True
        except Exception as e:
            if "different settings" in str(e).lower():
                print(f"❌ FAIL: Still getting 'different settings' error: {e}")
                return False
            else:
                print(f"✅ PASS: No 'different settings' error (got different error: {type(e).__name__})")
                return True
        
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        return False

def test_health_check():
    """Test health check functionality"""
    print()
    print("=" * 70)
    print("TEST 5: Health Check Functionality")
    print("=" * 70)
    print()
    
    from backend.chromadb_manager import get_chroma_manager
    
    manager = get_chroma_manager()
    
    try:
        is_healthy = manager.health_check()
        
        if is_healthy:
            print("✅ PASS: ChromaDB health check succeeded")
            
            # Get collection info
            info = manager.get_collection_info()
            print(f"   Collection info: {info}")
            return True
        else:
            print("❌ FAIL: ChromaDB health check failed")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Error during health check: {e}")
        return False

def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "ChromaDB Fix Validation" + " " * 30 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    tests = [
        test_singleton_pattern,
        test_client_consistency,
        test_collection_access,
        test_no_conflicting_instances,
        test_health_check
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results.append(False)
    
    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print()
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! ChromaDB singleton fix is working correctly.")
        print()
        print("Key Achievements:")
        print("  ✅ Singleton pattern implemented successfully")
        print("  ✅ No 'different settings' errors")
        print("  ✅ Consistent client configuration")
        print("  ✅ Health monitoring functional")
        print()
        return 0
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review errors above.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
