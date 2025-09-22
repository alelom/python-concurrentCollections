if True:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    os.environ["concurrent_collections_test"] = "True"

import threading
import time
import pytest
from concurrent_collections import ConcurrentBag


def test_concurrentbag_equality_basic():
    """Test basic equality comparison of ConcurrentBag instances."""
    b1 = ConcurrentBag([1, 2, 3])
    b2 = ConcurrentBag([1, 2, 3])
    b3 = ConcurrentBag([1, 2, 4])
    
    assert b1 == b2
    assert b1 != b3
    assert b2 != b3


def test_concurrentbag_equality_different_types():
    """Test equality comparison with non-ConcurrentBag types."""
    b = ConcurrentBag([1, 2, 3])
    
    assert b != [1, 2, 3]
    assert b != {'a': 1, 'b': 2}
    assert b != "not a bag"


def test_concurrentbag_equality_empty():
    """Test equality comparison of empty ConcurrentBag instances."""
    b1 = ConcurrentBag()
    b2 = ConcurrentBag()
    b3 = ConcurrentBag([1])
    
    assert b1 == b2
    assert b1 != b3


def test_concurrentbag_equality_order_does_not_matter():
    """Test that order does not matter in equality comparison (multiset behavior)."""
    b1 = ConcurrentBag([1, 2, 3])
    b2 = ConcurrentBag([3, 2, 1])
    
    assert b1 == b2


def test_concurrentbag_equality_thread_safe():
    """Test that equality comparison is thread-safe."""
    b1 = ConcurrentBag([1, 2, 3])
    b2 = ConcurrentBag([1, 2, 3])
    b3 = ConcurrentBag([1, 2, 4])
    
    results = []
    errors = []
    
    def worker():
        for _ in range(1000):
            try:
                time.sleep(0.00001)  # Force thread switch
                results.append(b1 == b2)
                results.append(b1 != b3)
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


def test_concurrentbag_hash_basic():
    """Test basic hash computation of ConcurrentBag instances."""
    b1 = ConcurrentBag([1, 2, 3])
    b2 = ConcurrentBag([1, 2, 3])
    b3 = ConcurrentBag([1, 2, 4])
    
    # Same content should have same hash
    assert hash(b1) == hash(b2)
    # Different content should have different hash
    assert hash(b1) != hash(b3)


def test_concurrentbag_hash_empty():
    """Test hash computation of empty ConcurrentBag instances."""
    b1 = ConcurrentBag()
    b2 = ConcurrentBag()
    b3 = ConcurrentBag([1])
    
    assert hash(b1) == hash(b2)
    assert hash(b1) != hash(b3)


def test_concurrentbag_hash_consistency():
    """Test that hash values are consistent across multiple calls."""
    b = ConcurrentBag([1, 2, 3, 4, 5])
    
    hash1 = hash(b)
    hash2 = hash(b)
    hash3 = hash(b)
    
    assert hash1 == hash2 == hash3


def test_concurrentbag_hash_thread_safe():
    """Test that hash computation is thread-safe."""
    b = ConcurrentBag([1, 2, 3, 4, 5])
    
    hashes = []
    errors = []
    
    def worker():
        for _ in range(1000):
            try:
                time.sleep(0.00001)  # Force thread switch
                hashes.append(hash(b))
            except Exception as e:
                errors.append(e)
    
    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # All hash values should be the same
    expected_hash = hash(ConcurrentBag([1, 2, 3, 4, 5]))
    assert all(h == expected_hash for h in hashes), f"Hash values are inconsistent: {set(hashes)}"
    assert not errors, f"Thread safety errors occurred: {errors}"


def test_concurrentbag_hash_mutable():
    """Test that hash changes when bag is modified."""
    b = ConcurrentBag([1, 2, 3])
    
    original_hash = hash(b)
    
    # Modify the bag
    b.append(4)
    
    new_hash = hash(b)
    
    assert original_hash != new_hash


def test_concurrentbag_in_set():
    """Test that ConcurrentBag can be used in sets."""
    b1 = ConcurrentBag([1, 2, 3])
    b2 = ConcurrentBag([1, 2, 3])
    b3 = ConcurrentBag([1, 2, 4])
    
    # Create a set with the bags
    bag_set = {b1, b2, b3}
    
    # Should have 2 unique items (b1 and b2 are equal, b3 is different)
    assert len(bag_set) == 2


def test_concurrentbag_as_dict_key():
    """Test that ConcurrentBag can be used as dictionary keys."""
    b1 = ConcurrentBag([1, 2, 3])
    b2 = ConcurrentBag([1, 2, 3])
    b3 = ConcurrentBag([1, 2, 4])
    
    # Create a dictionary using ConcurrentBag as keys
    key_dict = {b1: "value1", b3: "value3"}
    
    # Should be able to access using equal bag
    assert key_dict[b2] == "value1"
    assert key_dict[b3] == "value3"


def test_concurrentbag_hash_order_does_not_matter():
    """Test that order does not matter in hash computation (multiset behavior)."""
    b1 = ConcurrentBag([1, 2, 3])
    b2 = ConcurrentBag([3, 2, 1])
    
    assert hash(b1) == hash(b2)


def test_concurrentbag_equality_with_duplicates():
    """Test equality comparison with duplicate elements."""
    b1 = ConcurrentBag([1, 2, 2, 3])
    b2 = ConcurrentBag([1, 2, 2, 3])
    b3 = ConcurrentBag([1, 2, 3, 3])
    
    assert b1 == b2
    assert b1 != b3


def test_concurrentbag_hash_with_duplicates():
    """Test hash computation with duplicate elements."""
    b1 = ConcurrentBag([1, 2, 2, 3])
    b2 = ConcurrentBag([1, 2, 2, 3])
    b3 = ConcurrentBag([1, 2, 3, 3])
    
    assert hash(b1) == hash(b2)
    assert hash(b1) != hash(b3)


def test_concurrentbag_identity_concurrent_modifications():
    """Test that identity (equality and hash) remains consistent during concurrent modifications."""
    b1 = ConcurrentBag([1, 2, 3])
    b2 = ConcurrentBag([1, 2, 3])
    
    # Track initial identity
    initial_hash = hash(b1)
    initial_equality = b1 == b2
    
    results = []
    errors = []
    
    def modifier_worker():
        """Worker that modifies the bag while others check identity."""
        for i in range(100):
            try:
                b1.append(i)
                time.sleep(0.0001)  # Small delay to allow other threads to run
                b1.remove(i)
            except Exception as e:
                errors.append(e)
    
    def identity_checker_worker():
        """Worker that continuously checks identity during modifications."""
        for _ in range(200):
            try:
                # Check that hash is consistent for same content
                current_hash = hash(b1)
                current_equality = b1 == b2
                
                # Hash should change when content changes, but equality should be consistent
                if b1 == b2:
                    results.append(hash(b1) == hash(b2))
                
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


def test_concurrentbag_identity_race_conditions():
    """Test identity behavior under race conditions with rapid modifications."""
    b1 = ConcurrentBag([1, 2, 3])
    b2 = ConcurrentBag([1, 2, 3])
    
    modification_count = 0
    errors = []
    
    def rapid_modifier():
        """Rapidly modify the bag."""
        nonlocal modification_count
        for i in range(50):
            try:
                b1.append(i)
                b1.remove(i)
                modification_count += 1
            except Exception as e:
                errors.append(e)
    
    def identity_monitor():
        """Monitor identity during rapid modifications."""
        for _ in range(100):
            try:
                # These operations should not cause crashes even during rapid modifications
                _ = hash(b1)
                _ = b1 == b2
                _ = b1 != b2
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


def test_concurrentbag_identity_multiple_instances():
    """Test identity behavior with multiple concurrent bag instances."""
    # Create multiple instances with same content
    bags = [ConcurrentBag([1, 2, 3]) for _ in range(5)]
    
    results = []
    errors = []
    
    def identity_worker():
        """Worker that compares multiple bag instances."""
        for _ in range(100):
            try:
                # All bags with same content should be equal
                for i in range(len(bags)):
                    for j in range(len(bags)):
                        if i != j:
                            results.append(bags[i] == bags[j])
                            results.append(hash(bags[i]) == hash(bags[j]))
                
                # Modify one bag
                bags[0].append(999)
                
                # Check that modified bag is different
                for i in range(1, len(bags)):
                    results.append(bags[0] != bags[i])
                    results.append(hash(bags[0]) != hash(bags[i]))
                
                # Reset the modification
                bags[0].remove(999)
                
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


def test_concurrentbag_identity_duplicate_handling():
    """Test identity behavior with duplicate elements under concurrency."""
    b1 = ConcurrentBag([1, 1, 2, 2, 3])
    b2 = ConcurrentBag([1, 1, 2, 2, 3])
    b3 = ConcurrentBag([1, 2, 2, 3, 3])  # Different duplicate pattern
    
    results = []
    errors = []
    
    def duplicate_modifier():
        """Add and remove duplicate elements."""
        for i in range(20):
            try:
                # Add duplicates
                b1.append(i)
                b1.append(i)  # Create duplicate
                time.sleep(0.001)
                
                # Remove duplicates
                b1.remove(i)
                b1.remove(i)
                time.sleep(0.001)
            except Exception as e:
                errors.append(e)
    
    def duplicate_identity_checker():
        """Check identity with duplicate elements."""
        for _ in range(50):
            try:
                # Check equality and hash with duplicates
                results.append(b1 == b2)
                results.append(hash(b1) == hash(b2))
                
                # Check that different duplicate patterns are different
                results.append(b1 != b3)
                results.append(hash(b1) != hash(b3))
                
                # Add temporary duplicates and check identity changes
                b1.append(999)
                b1.append(999)
                results.append(b1 != b2)
                results.append(hash(b1) != hash(b2))
                
                b1.remove(999)
                b1.remove(999)
                
                time.sleep(0.001)
            except Exception as e:
                errors.append(e)
    
    modifier_threads = [threading.Thread(target=duplicate_modifier) for _ in range(2)]
    checker_threads = [threading.Thread(target=duplicate_identity_checker) for _ in range(3)]
    
    for t in modifier_threads + checker_threads:
        t.start()
    
    for t in modifier_threads + checker_threads:
        t.join()
    
    assert not errors, f"Duplicate handling errors: {errors}"
    assert all(results), f"Some duplicate identity checks failed: {results[:10]}"


def test_concurrentbag_identity_multiset_behavior():
    """Test that bag behaves as a multiset in identity calculations under concurrency."""
    b1 = ConcurrentBag([1, 2, 3, 4, 5])
    b2 = ConcurrentBag([1, 2, 3, 4, 5])
    b3 = ConcurrentBag([5, 4, 3, 2, 1])  # Same elements, different order
    
    results = []
    errors = []
    
    def element_modifier():
        """Modify elements while preserving multiset content."""
        for i in range(15):
            try:
                # Remove and re-add elements to potentially change order
                b1.remove(1)
                b1.append(1)
                time.sleep(0.001)
            except Exception as e:
                errors.append(e)
    
    def multiset_identity_checker():
        """Check that multiset behavior is maintained in identity."""
        for _ in range(40):
            try:
                # Same content should be equal regardless of order
                results.append(b1 == b2)
                results.append(hash(b1) == hash(b2))
                
                # Same content, different order should still be equal (multiset)
                results.append(b1 == b3)
                results.append(hash(b1) == hash(b3))
                
                time.sleep(0.001)
            except Exception as e:
                errors.append(e)
    
    modifier_threads = [threading.Thread(target=element_modifier) for _ in range(2)]
    checker_threads = [threading.Thread(target=multiset_identity_checker) for _ in range(3)]
    
    for t in modifier_threads + checker_threads:
        t.start()
    
    for t in modifier_threads + checker_threads:
        t.join()
    
    assert not errors, f"Multiset behavior errors: {errors}"
    assert all(results), f"Some multiset identity checks failed: {results[:10]}"


def test_concurrentbag_identity_stress_test():
    """Stress test for identity mechanism under heavy concurrent load."""
    b1 = ConcurrentBag([1, 2, 3, 4, 5])
    b2 = ConcurrentBag([1, 2, 3, 4, 5])
    
    operation_count = 0
    errors = []
    
    def stress_worker():
        """Perform stress operations on bag identity."""
        nonlocal operation_count
        for _ in range(200):
            try:
                # Perform various identity operations
                _ = hash(b1)
                _ = b1 == b2
                _ = b1 != b2
                
                # Modify and check identity changes
                b1.append(operation_count)
                _ = b1 != b2
                _ = hash(b1) != hash(b2)
                
                b1.remove(operation_count)
                _ = b1 == b2
                _ = hash(b1) == hash(b2)
                
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


def test_concurrentbag_identity_consistency_under_load():
    """Test that identity remains consistent under heavy concurrent load."""
    b1 = ConcurrentBag([1, 2, 3])
    b2 = ConcurrentBag([1, 2, 3])
    
    # Store initial identity
    initial_hash = hash(b1)
    initial_equality = b1 == b2
    
    results = []
    errors = []
    
    def load_worker():
        """Generate load while checking identity consistency."""
        for _ in range(150):
            try:
                # Check that identity remains consistent when content doesn't change
                current_hash = hash(b1)
                current_equality = b1 == b2
                
                if b1 == b2:  # Only check when they should be equal
                    results.append(current_hash == initial_hash)
                    results.append(current_equality == initial_equality)
                
                time.sleep(0.0001)
            except Exception as e:
                errors.append(e)
    
    def modifier_worker():
        """Modify bag to test identity changes."""
        for i in range(50):
            try:
                b1.append(i)
                time.sleep(0.001)
                b1.remove(i)
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
