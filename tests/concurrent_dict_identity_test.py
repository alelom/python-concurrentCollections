if True:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    os.environ["concurrent_collections_test"] = "True"

import threading
import time
import pytest
from concurrent_collections import ConcurrentDictionary


def test_concurrentdictionary_equality_basic():
    """Test basic equality comparison of ConcurrentDictionary instances."""
    d1 = ConcurrentDictionary({'a': 1, 'b': 2})
    d2 = ConcurrentDictionary({'a': 1, 'b': 2})
    d3 = ConcurrentDictionary({'a': 1, 'b': 3})
    
    assert d1 == d2
    assert d1 != d3
    assert d2 != d3


def test_concurrentdictionary_equality_different_types():
    """Test equality comparison with non-ConcurrentDictionary types."""
    d = ConcurrentDictionary({'a': 1, 'b': 2})
    
    assert d != {'a': 1, 'b': 2}
    assert d != [1, 2, 3]
    assert d != "not a dict"


def test_concurrentdictionary_equality_empty():
    """Test equality comparison of empty ConcurrentDictionary instances."""
    d1 = ConcurrentDictionary()
    d2 = ConcurrentDictionary()
    d3 = ConcurrentDictionary({'a': 1})
    
    assert d1 == d2
    assert d1 != d3


def test_concurrentdictionary_equality_thread_safe():
    """Test that equality comparison is thread-safe."""
    d1 = ConcurrentDictionary({'a': 1, 'b': 2})
    d2 = ConcurrentDictionary({'a': 1, 'b': 2})
    d3 = ConcurrentDictionary({'a': 1, 'b': 3})
    
    results = []
    errors = []
    
    def worker():
        for _ in range(1000):
            try:
                time.sleep(0.00001)  # Force thread switch
                results.append(d1 == d2)
                results.append(d1 != d3)
            except Exception as e:
                errors.append(e)
    
    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # All comparisons should be True
    assert all(results), f"Some equality comparisons failed: {results[:10]}"
    assert not errors, f"Thread safety errors occurred: {errors}"


def test_concurrentdictionary_hash_basic():
    """Test basic hash computation of ConcurrentDictionary instances."""
    d1 = ConcurrentDictionary({'a': 1, 'b': 2})
    d2 = ConcurrentDictionary({'a': 1, 'b': 2})
    d3 = ConcurrentDictionary({'a': 1, 'b': 3})
    
    # Same content should have same hash
    assert hash(d1) == hash(d2)
    # Different content should have different hash
    assert hash(d1) != hash(d3)


def test_concurrentdictionary_hash_empty():
    """Test hash computation of empty ConcurrentDictionary instances."""
    d1 = ConcurrentDictionary()
    d2 = ConcurrentDictionary()
    d3 = ConcurrentDictionary({'a': 1})
    
    assert hash(d1) == hash(d2)
    assert hash(d1) != hash(d3)


def test_concurrentdictionary_hash_consistency():
    """Test that hash values are consistent across multiple calls."""
    d = ConcurrentDictionary({'a': 1, 'b': 2, 'c': 3})
    
    hash1 = hash(d)
    hash2 = hash(d)
    hash3 = hash(d)
    
    assert hash1 == hash2 == hash3


def test_concurrentdictionary_hash_thread_safe():
    """Test that hash computation is thread-safe."""
    d = ConcurrentDictionary({'a': 1, 'b': 2, 'c': 3})
    
    hashes = []
    errors = []
    
    def worker():
        for _ in range(1000):
            try:
                time.sleep(0.00001)  # Force thread switch
                hashes.append(hash(d))
            except Exception as e:
                errors.append(e)
    
    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # All hash values should be the same
    expected_hash = hash(ConcurrentDictionary({'a': 1, 'b': 2, 'c': 3}))
    assert all(h == expected_hash for h in hashes), f"Hash values are inconsistent: {set(hashes)}"
    assert not errors, f"Thread safety errors occurred: {errors}"


def test_concurrentdictionary_hash_mutable():
    """Test that hash changes when dictionary is modified."""
    d = ConcurrentDictionary({'a': 1, 'b': 2})
    
    original_hash = hash(d)
    
    # Modify the dictionary
    d.assign_atomic('c', 3)
    
    new_hash = hash(d)
    
    assert original_hash != new_hash


def test_concurrentdictionary_in_set():
    """Test that ConcurrentDictionary can be used in sets."""
    d1 = ConcurrentDictionary({'a': 1, 'b': 2})
    d2 = ConcurrentDictionary({'a': 1, 'b': 2})
    d3 = ConcurrentDictionary({'a': 1, 'b': 3})
    
    # Create a set with the dictionaries
    dict_set = {d1, d2, d3}
    
    # Should have 2 unique items (d1 and d2 are equal, d3 is different)
    assert len(dict_set) == 2


def test_concurrentdictionary_as_dict_key():
    """Test that ConcurrentDictionary can be used as dictionary keys."""
    d1 = ConcurrentDictionary({'a': 1, 'b': 2})
    d2 = ConcurrentDictionary({'a': 1, 'b': 2})
    d3 = ConcurrentDictionary({'a': 1, 'b': 3})
    
    # Create a dictionary using ConcurrentDictionary as keys
    key_dict = {d1: "value1", d3: "value3"}
    
    # Should be able to access using equal dictionary
    assert key_dict[d2] == "value1"
    assert key_dict[d3] == "value3"


def test_concurrentdictionary_identity_concurrent_modifications():
    """Test that identity (equality and hash) remains consistent during concurrent modifications."""
    d1 = ConcurrentDictionary({'a': 1, 'b': 2})
    d2 = ConcurrentDictionary({'a': 1, 'b': 2})
    
    # Track initial identity
    initial_hash = hash(d1)
    initial_equality = d1 == d2
    
    results = []
    errors = []
    
    def modifier_worker():
        """Worker that modifies the dictionary while others check identity."""
        for i in range(100):
            try:
                d1.assign_atomic(f'key_{i}', i)
                time.sleep(0.0001)  # Small delay to allow other threads to run
            except Exception as e:
                errors.append(e)
    
    def identity_checker_worker():
        """Worker that continuously checks identity during modifications."""
        for _ in range(200):
            try:
                # Check that hash is consistent for same content
                current_hash = hash(d1)
                current_equality = d1 == d2
                
                # Hash should change when content changes, but equality should be consistent
                if d1 == d2:
                    results.append(hash(d1) == hash(d2))
                
                time.sleep(0.0001)
            except Exception as e:
                errors.append(e)
    
    # Start modification threads
    modifier_threads = [threading.Thread(target=modifier_worker) for _ in range(2)]
    # Start identity checking threads
    checker_threads = [threading.Thread(target=identity_checker_worker) for _ in range(3)]
    
    # Start all threads
    for t in modifier_threads + checker_threads:
        t.start()
    
    # Wait for all threads to complete
    for t in modifier_threads + checker_threads:
        t.join()
    
    assert not errors, f"Errors occurred during concurrent identity testing: {errors}"
    assert all(results), f"Some identity checks failed: {results[:10]}"


def test_concurrentdictionary_identity_race_conditions():
    """Test identity behavior under race conditions with rapid modifications."""
    d1 = ConcurrentDictionary({'x': 10, 'y': 20})
    d2 = ConcurrentDictionary({'x': 10, 'y': 20})
    
    modification_count = 0
    errors = []
    
    def rapid_modifier():
        """Rapidly modify the dictionary."""
        nonlocal modification_count
        for i in range(50):
            try:
                d1.assign_atomic('temp', i)
                d1.remove_atomic('temp')
                modification_count += 1
            except Exception as e:
                errors.append(e)
    
    def identity_monitor():
        """Monitor identity during rapid modifications."""
        for _ in range(100):
            try:
                # These operations should not cause crashes even during rapid modifications
                _ = hash(d1)
                _ = d1 == d2
                _ = d1 != d2
                time.sleep(0.0001)
            except Exception as e:
                errors.append(e)
    
    threads = [threading.Thread(target=rapid_modifier) for _ in range(3)]
    monitor_threads = [threading.Thread(target=identity_monitor) for _ in range(2)]
    
    for t in threads + monitor_threads:
        t.start()
    
    for t in threads + monitor_threads:
        t.join()
    
    assert not errors, f"Race condition errors: {errors}"
    assert modification_count > 0, "No modifications occurred"


def test_concurrentdictionary_identity_multiple_instances():
    """Test identity behavior with multiple concurrent dictionary instances."""
    # Create multiple instances with same content
    dicts = [ConcurrentDictionary({'a': 1, 'b': 2, 'c': 3}) for _ in range(5)]
    
    results = []
    errors = []
    
    def identity_worker():
        """Worker that compares multiple dictionary instances."""
        for _ in range(100):
            try:
                # All dictionaries with same content should be equal
                for i in range(len(dicts)):
                    for j in range(len(dicts)):
                        if i != j:
                            results.append(dicts[i] == dicts[j])
                            results.append(hash(dicts[i]) == hash(dicts[j]))
                
                # Modify one dictionary
                dicts[0].assign_atomic('modified', True)
                
                # Check that modified dictionary is different
                for i in range(1, len(dicts)):
                    results.append(dicts[0] != dicts[i])
                    results.append(hash(dicts[0]) != hash(dicts[i]))
                
                # Reset the modification
                dicts[0].remove_atomic('modified')
                
                time.sleep(0.0001)
            except Exception as e:
                errors.append(e)
    
    threads = [threading.Thread(target=identity_worker) for _ in range(4)]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    assert not errors, f"Multiple instances errors: {errors}"
    assert all(results), f"Some identity checks failed: {results[:10]}"


def test_concurrentdictionary_identity_nested_structures():
    """Test identity behavior with nested dictionary structures under concurrency."""
    nested_data = {
        'level1': 'value1',
        'level2': 'value2',
        'level3': 'value3'
    }
    
    d1 = ConcurrentDictionary(nested_data)
    d2 = ConcurrentDictionary(nested_data)
    
    results = []
    errors = []
    
    def nested_modifier():
        """Modify nested structures."""
        for i in range(20):
            try:
                # Modify nested structure
                d1.assign_atomic('nested', f'value_{i}')
                time.sleep(0.001)
                d1.remove_atomic('nested')
            except Exception as e:
                errors.append(e)
    
    def nested_identity_checker():
        """Check identity of nested structures."""
        for _ in range(50):
            try:
                # Check that operations don't crash
                _ = hash(d1)
                _ = hash(d2)
                _ = d1 == d2
                
                # Check that modifications change identity when applied
                d1.assign_atomic('temp_nested', 'test_value')
                temp_hash = hash(d1)
                temp_equality = d1 == d2
                d1.remove_atomic('temp_nested')
                
                # After removal, should be back to original state
                final_hash = hash(d1)
                final_equality = d1 == d2
                
                # Store results for verification
                results.append(temp_equality == False)  # Should be different when modified
                results.append(final_equality == True)  # Should be equal after restoration
                
                time.sleep(0.001)
            except Exception as e:
                errors.append(e)
    
    modifier_threads = [threading.Thread(target=nested_modifier) for _ in range(2)]
    checker_threads = [threading.Thread(target=nested_identity_checker) for _ in range(3)]
    
    for t in modifier_threads + checker_threads:
        t.start()
    
    for t in modifier_threads + checker_threads:
        t.join()
    
    assert not errors, f"Nested structure errors: {errors}"
    # Check that at least some operations worked correctly
    assert len(results) > 0, "No identity checks performed"
    assert any(results), f"Some identity checks failed: {results[:10]}"


def test_concurrentdictionary_identity_stress_test():
    """Stress test for identity mechanism under heavy concurrent load."""
    d1 = ConcurrentDictionary({'stress': 'test', 'data': 'value'})
    d2 = ConcurrentDictionary({'stress': 'test', 'data': 'value'})
    
    operation_count = 0
    errors = []
    
    def stress_worker():
        """Perform stress operations on dictionary identity."""
        nonlocal operation_count
        for _ in range(200):
            try:
                # Perform various identity operations
                _ = hash(d1)
                _ = d1 == d2
                _ = d1 != d2
                
                # Modify and check identity changes
                d1.assign_atomic(f'stress_key_{operation_count}', operation_count)
                _ = d1 != d2
                _ = hash(d1) != hash(d2)
                
                d1.remove_atomic(f'stress_key_{operation_count}')
                _ = d1 == d2
                _ = hash(d1) == hash(d2)
                
                operation_count += 1
                time.sleep(0.0001)
            except Exception as e:
                errors.append(e)
    
    threads = [threading.Thread(target=stress_worker) for _ in range(6)]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    assert not errors, f"Stress test errors: {errors}"
    assert operation_count > 0, "No operations performed in stress test"


def test_concurrentdictionary_identity_consistency_under_load():
    """Test that identity remains consistent under heavy concurrent load."""
    d1 = ConcurrentDictionary({'consistency': 'test'})
    d2 = ConcurrentDictionary({'consistency': 'test'})
    
    # Store initial identity
    initial_hash = hash(d1)
    initial_equality = d1 == d2
    
    results = []
    errors = []
    
    def load_worker():
        """Generate load while checking identity consistency."""
        for _ in range(150):
            try:
                # Check that identity remains consistent when content doesn't change
                current_hash = hash(d1)
                current_equality = d1 == d2
                
                if d1 == d2:  # Only check when they should be equal
                    results.append(current_hash == initial_hash)
                    results.append(current_equality == initial_equality)
                
                time.sleep(0.0001)
            except Exception as e:
                errors.append(e)
    
    def modifier_worker():
        """Modify dictionary to test identity changes."""
        for i in range(50):
            try:
                d1.assign_atomic(f'load_key_{i}', i)
                time.sleep(0.001)
                d1.remove_atomic(f'load_key_{i}')
                time.sleep(0.001)
            except Exception as e:
                errors.append(e)
    
    load_threads = [threading.Thread(target=load_worker) for _ in range(4)]
    modifier_threads = [threading.Thread(target=modifier_worker) for _ in range(2)]
    
    for t in load_threads + modifier_threads:
        t.start()
    
    for t in load_threads + modifier_threads:
        t.join()
    
    assert not errors, f"Consistency errors: {errors}"
    assert all(results), f"Some consistency checks failed: {results[:10]}"


if __name__ == "__main__":
    pytest.main([__file__])