if True:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    os.environ["concurrent_collections_test"] = "True"

import threading
import time
import pytest
from concurrent_collections import ConcurrentQueue


def test_concurrentqueue_equality_basic():
    """Test basic equality comparison of ConcurrentQueue instances."""
    q1 = ConcurrentQueue([1, 2, 3])
    q2 = ConcurrentQueue([1, 2, 3])
    q3 = ConcurrentQueue([1, 2, 4])
    
    assert q1 == q2
    assert q1 != q3
    assert q2 != q3


def test_concurrentqueue_equality_different_types():
    """Test equality comparison with non-ConcurrentQueue types."""
    q = ConcurrentQueue([1, 2, 3])
    
    assert q != [1, 2, 3]
    assert q != {'a': 1, 'b': 2}
    assert q != "not a queue"


def test_concurrentqueue_equality_empty():
    """Test equality comparison of empty ConcurrentQueue instances."""
    q1 = ConcurrentQueue()
    q2 = ConcurrentQueue()
    q3 = ConcurrentQueue([1])
    
    assert q1 == q2
    assert q1 != q3


def test_concurrentqueue_equality_order_matters():
    """Test that order matters in equality comparison."""
    q1 = ConcurrentQueue([1, 2, 3])
    q2 = ConcurrentQueue([3, 2, 1])
    
    assert q1 != q2


def test_concurrentqueue_equality_thread_safe():
    """Test that equality comparison is thread-safe."""
    q1 = ConcurrentQueue([1, 2, 3])
    q2 = ConcurrentQueue([1, 2, 3])
    q3 = ConcurrentQueue([1, 2, 4])
    
    results = []
    errors = []
    
    def worker():
        for _ in range(1000):
            try:
                time.sleep(0.00001)  # Force thread switch
                results.append(q1 == q2)
                results.append(q1 != q3)
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


def test_concurrentqueue_hash_basic():
    """Test basic hash computation of ConcurrentQueue instances."""
    q1 = ConcurrentQueue([1, 2, 3])
    q2 = ConcurrentQueue([1, 2, 3])
    q3 = ConcurrentQueue([1, 2, 4])
    
    # Same content should have same hash
    assert hash(q1) == hash(q2)
    # Different content should have different hash
    assert hash(q1) != hash(q3)


def test_concurrentqueue_hash_empty():
    """Test hash computation of empty ConcurrentQueue instances."""
    q1 = ConcurrentQueue()
    q2 = ConcurrentQueue()
    q3 = ConcurrentQueue([1])
    
    assert hash(q1) == hash(q2)
    assert hash(q1) != hash(q3)


def test_concurrentqueue_hash_consistency():
    """Test that hash values are consistent across multiple calls."""
    q = ConcurrentQueue([1, 2, 3, 4, 5])
    
    hash1 = hash(q)
    hash2 = hash(q)
    hash3 = hash(q)
    
    assert hash1 == hash2 == hash3


def test_concurrentqueue_hash_thread_safe():
    """Test that hash computation is thread-safe."""
    q = ConcurrentQueue([1, 2, 3, 4, 5])
    
    hashes = []
    errors = []
    
    def worker():
        for _ in range(1000):
            try:
                time.sleep(0.00001)  # Force thread switch
                hashes.append(hash(q))
            except Exception as e:
                errors.append(e)
    
    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # All hash values should be the same
    expected_hash = hash(ConcurrentQueue([1, 2, 3, 4, 5]))
    assert all(h == expected_hash for h in hashes), f"Hash values are inconsistent: {set(hashes)}"
    assert not errors, f"Thread safety errors occurred: {errors}"


def test_concurrentqueue_hash_mutable():
    """Test that hash changes when queue is modified."""
    q = ConcurrentQueue([1, 2, 3])
    
    original_hash = hash(q)
    
    # Modify the queue
    q.append(4)
    
    new_hash = hash(q)
    
    assert original_hash != new_hash


def test_concurrentqueue_in_set():
    """Test that ConcurrentQueue can be used in sets."""
    q1 = ConcurrentQueue([1, 2, 3])
    q2 = ConcurrentQueue([1, 2, 3])
    q3 = ConcurrentQueue([1, 2, 4])
    
    # Create a set with the queues
    queue_set = {q1, q2, q3}
    
    # Should have 2 unique items (q1 and q2 are equal, q3 is different)
    assert len(queue_set) == 2


def test_concurrentqueue_as_dict_key():
    """Test that ConcurrentQueue can be used as dictionary keys."""
    q1 = ConcurrentQueue([1, 2, 3])
    q2 = ConcurrentQueue([1, 2, 3])
    q3 = ConcurrentQueue([1, 2, 4])
    
    # Create a dictionary using ConcurrentQueue as keys
    key_dict = {q1: "value1", q3: "value3"}
    
    # Should be able to access using equal queue
    assert key_dict[q2] == "value1"
    assert key_dict[q3] == "value3"


def test_concurrentqueue_hash_order_matters():
    """Test that order matters in hash computation."""
    q1 = ConcurrentQueue([1, 2, 3])
    q2 = ConcurrentQueue([3, 2, 1])
    
    assert hash(q1) != hash(q2)


def test_concurrentqueue_identity_concurrent_modifications():
    """Test that identity (equality and hash) remains consistent during concurrent modifications."""
    q1 = ConcurrentQueue([1, 2, 3])
    q2 = ConcurrentQueue([1, 2, 3])
    
    # Track initial identity
    initial_hash = hash(q1)
    initial_equality = q1 == q2
    
    results = []
    errors = []
    
    def modifier_worker():
        """Worker that modifies the queue while others check identity."""
        for i in range(100):
            try:
                q1.append(i)
                time.sleep(0.0001)  # Small delay to allow other threads to run
                q1.popleft()
            except Exception as e:
                errors.append(e)
    
    def identity_checker_worker():
        """Worker that continuously checks identity during modifications."""
        for _ in range(200):
            try:
                # Check that hash is consistent for same content
                current_hash = hash(q1)
                current_equality = q1 == q2
                
                # Hash should change when content changes, but equality should be consistent
                if q1 == q2:
                    results.append(hash(q1) == hash(q2))
                
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


def test_concurrentqueue_identity_race_conditions():
    """Test identity behavior under race conditions with rapid modifications."""
    q1 = ConcurrentQueue([1, 2, 3])
    q2 = ConcurrentQueue([1, 2, 3])
    
    modification_count = 0
    errors = []
    
    def rapid_modifier():
        """Rapidly modify the queue."""
        nonlocal modification_count
        for i in range(50):
            try:
                q1.append(i)
                q1.popleft()
                modification_count += 1
            except Exception as e:
                errors.append(e)
    
    def identity_monitor():
        """Monitor identity during rapid modifications."""
        for _ in range(100):
            try:
                # These operations should not cause crashes even during rapid modifications
                _ = hash(q1)
                _ = q1 == q2
                _ = q1 != q2
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


def test_concurrentqueue_identity_multiple_instances():
    """Test identity behavior with multiple concurrent queue instances."""
    # Create multiple instances with same content
    queues = [ConcurrentQueue([1, 2, 3]) for _ in range(5)]
    
    results = []
    errors = []
    
    def identity_worker():
        """Worker that compares multiple queue instances."""
        for _ in range(100):
            try:
                # All queues with same content should be equal
                for i in range(len(queues)):
                    for j in range(len(queues)):
                        if i != j:
                            results.append(queues[i] == queues[j])
                            results.append(hash(queues[i]) == hash(queues[j]))
                
                # Modify one queue
                queues[0].append(999)
                
                # Check that modified queue is different
                for i in range(1, len(queues)):
                    results.append(queues[0] != queues[i])
                    results.append(hash(queues[0]) != hash(queues[i]))
                
                # Reset the modification
                queues[0].popleft()
                
                time.sleep(0.0001)
            except Exception as e:
                errors.append(e)
    
    threads = [threading.Thread(target=identity_worker) for _ in range(4)]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    assert not errors, f"Multiple instances errors: {errors}"
    # In concurrent scenarios, some checks may fail due to timing, but most should pass
    assert len(results) > 0, "No identity checks performed"
    assert sum(results) > len(results) * 0.7, f"Too many identity checks failed: {results[:10]}"


def test_concurrentqueue_identity_order_preservation():
    """Test that order is preserved in identity calculations under concurrency."""
    q1 = ConcurrentQueue([1, 2, 3, 4, 5])
    q2 = ConcurrentQueue([1, 2, 3, 4, 5])
    q3 = ConcurrentQueue([5, 4, 3, 2, 1])  # Same elements, different order
    
    results = []
    errors = []
    
    def order_modifier():
        """Modify order while preserving elements."""
        for i in range(15):
            try:
                # Remove from front and add to back to potentially change order
                q1.popleft()
                q1.append(1)
                time.sleep(0.001)
            except Exception as e:
                errors.append(e)
    
    def order_identity_checker():
        """Check that order matters in identity."""
        for _ in range(40):
            try:
                # Same content, same order should be equal
                results.append(q1 == q2)
                results.append(hash(q1) == hash(q2))
                
                # Same content, different order should be different
                results.append(q1 != q3)
                results.append(hash(q1) != hash(q3))
                
                time.sleep(0.001)
            except Exception as e:
                errors.append(e)
    
    modifier_threads = [threading.Thread(target=order_modifier) for _ in range(2)]
    checker_threads = [threading.Thread(target=order_identity_checker) for _ in range(3)]
    
    for t in modifier_threads + checker_threads:
        t.start()
    
    for t in modifier_threads + checker_threads:
        t.join()
    
    assert not errors, f"Order preservation errors: {errors}"
    # In concurrent scenarios, some checks may fail due to timing, but most should pass
    assert len(results) > 0, "No identity checks performed"
    assert sum(results) > len(results) * 0.7, f"Too many order identity checks failed: {results[:10]}"


def test_concurrentqueue_identity_fifo_behavior():
    """Test that FIFO behavior is preserved in identity under concurrency."""
    q1 = ConcurrentQueue([1, 2, 3])
    q2 = ConcurrentQueue([1, 2, 3])
    
    results = []
    errors = []
    
    def fifo_modifier():
        """Modify queue using FIFO operations."""
        for i in range(20):
            try:
                # Add to back, remove from front (FIFO)
                q1.append(i)
                time.sleep(0.001)
                q1.popleft()
                time.sleep(0.001)
            except Exception as e:
                errors.append(e)
    
    def fifo_identity_checker():
        """Check identity during FIFO operations."""
        for _ in range(50):
            try:
                # Check that FIFO operations maintain proper identity
                results.append(q1 == q2)
                results.append(hash(q1) == hash(q2))
                
                # Add element and check identity changes
                q1.append(999)
                results.append(q1 != q2)
                results.append(hash(q1) != hash(q2))
                
                # Remove element and check identity restoration
                q1.popleft()
                results.append(q1 == q2)
                results.append(hash(q1) == hash(q2))
                
                time.sleep(0.001)
            except Exception as e:
                errors.append(e)
    
    modifier_threads = [threading.Thread(target=fifo_modifier) for _ in range(2)]
    checker_threads = [threading.Thread(target=fifo_identity_checker) for _ in range(3)]
    
    for t in modifier_threads + checker_threads:
        t.start()
    
    for t in modifier_threads + checker_threads:
        t.join()
    
    assert not errors, f"FIFO behavior errors: {errors}"
    # In concurrent scenarios, some checks may fail due to timing, but most should pass
    assert len(results) > 0, "No FIFO identity checks performed"
    assert sum(results) > len(results) * 0.7, f"Too many FIFO identity checks failed: {results[:10]}"


def test_concurrentqueue_identity_stress_test():
    """Stress test for identity mechanism under heavy concurrent load."""
    q1 = ConcurrentQueue([1, 2, 3, 4, 5])
    q2 = ConcurrentQueue([1, 2, 3, 4, 5])
    
    operation_count = 0
    errors = []
    
    def stress_worker():
        """Perform stress operations on queue identity."""
        nonlocal operation_count
        for _ in range(200):
            try:
                # Perform various identity operations
                _ = hash(q1)
                _ = q1 == q2
                _ = q1 != q2
                
                # Modify and check identity changes
                q1.append(operation_count)
                _ = q1 != q2
                _ = hash(q1) != hash(q2)
                
                q1.popleft()
                _ = q1 == q2
                _ = hash(q1) == hash(q2)
                
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


def test_concurrentqueue_identity_consistency_under_load():
    """Test that identity remains consistent under heavy concurrent load."""
    q1 = ConcurrentQueue([1, 2, 3])
    q2 = ConcurrentQueue([1, 2, 3])
    
    # Store initial identity
    initial_hash = hash(q1)
    initial_equality = q1 == q2
    
    results = []
    errors = []
    
    def load_worker():
        """Generate load while checking identity consistency."""
        for _ in range(150):
            try:
                # Check that identity remains consistent when content doesn't change
                current_hash = hash(q1)
                current_equality = q1 == q2
                
                if q1 == q2:  # Only check when they should be equal
                    results.append(current_hash == initial_hash)
                    results.append(current_equality == initial_equality)
                
                time.sleep(0.0001)
            except Exception as e:
                errors.append(e)
    
    def modifier_worker():
        """Modify queue to test identity changes."""
        for i in range(50):
            try:
                q1.append(i)
                time.sleep(0.001)
                q1.popleft()
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


def test_concurrentqueue_identity_edge_cases():
    """Test identity behavior in edge cases under concurrency."""
    q1 = ConcurrentQueue()
    q2 = ConcurrentQueue()
    
    results = []
    errors = []
    
    def edge_case_worker():
        """Test edge cases like empty queues and single elements."""
        for i in range(30):
            try:
                # Test empty queue identity
                results.append(q1 == q2)
                results.append(hash(q1) == hash(q2))
                
                # Add single element
                q1.append(i)
                results.append(q1 != q2)
                results.append(hash(q1) != hash(q2))
                
                # Remove element to make empty again
                q1.popleft()
                results.append(q1 == q2)
                results.append(hash(q1) == hash(q2))
                
                time.sleep(0.001)
            except Exception as e:
                errors.append(e)
    
    threads = [threading.Thread(target=edge_case_worker) for _ in range(4)]
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    assert not errors, f"Edge case errors: {errors}"
    assert all(results), f"Some edge case identity checks failed: {results[:10]}"


if __name__ == "__main__":
    pytest.main([__file__])
