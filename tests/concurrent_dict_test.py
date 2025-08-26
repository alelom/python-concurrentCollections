if True:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    os.environ["concurrent_collections_test"] = "True"

import threading
import time
from typing import List
from concurrent_collections import ConcurrentDictionary
import pytest


def test_concurrentdictionary_update_thread_safe():
    dic : ConcurrentDictionary[str, int] = ConcurrentDictionary()
    update_actions : int = 10000
    dic.assign_atomic("x", 0)
    def worker():
        for _ in range(update_actions):
            time.sleep(0.00001)
            # D.__setitem__('x', old + 1)
            dic.update_atomic("x", lambda v: v + 1)

    threads_num : int = 8
    threads = [threading.Thread(target=worker) for _ in range(threads_num)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # The expected value is 8 * 10000 = 80000
    expected_value = threads_num * update_actions
    assert dic['x'] == expected_value, f"ConcurrentDictionary should be thread-safe and with a value of {expected_value} for the `x` key, got {dic['x']}"


def test_concurrentdictionary_setdefault_thread_safe():
    D : ConcurrentDictionary[str,int] = ConcurrentDictionary()
    errors : List[Exception] = []

    def worker():
        for _ in range(10000):
            try:
                D.setdefault('y', 0)
            except Exception as e:
                errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # No thread safety errors should occur
    assert not errors, f"Thread safety errors occurred: {errors}"


def test_concurrentdictionary_pop_thread_safe():
    D : ConcurrentDictionary[str,int] = ConcurrentDictionary({'x': 0})
    errors : List[Exception] = []

    def worker():
        for _ in range(1000):
            try:
                time.sleep(0.00001)  # Force thread switch
                D.pop('x', None)
            except Exception as e:
                errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # No thread safety errors should occur
    assert not errors, f"Thread safety errors occurred: {errors}"


def test_concurrentdictionary_clear_thread_safe():
    D : ConcurrentDictionary[str,int] = ConcurrentDictionary({i: i for i in range(100)})
    errors : List[Exception] = []

    def worker():
        for _ in range(100):
            try:
                time.sleep(0.00001)  # Force thread switch
                D.clear()
            except Exception as e:
                errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # No thread safety errors should occur
    assert not errors, f"Thread safety errors occurred: {errors}"
    
def test_get_locked_context_manager_empty_value():
    d: ConcurrentDictionary[str, int] = ConcurrentDictionary({})
    with d.get_locked('a') as value:
        assert not value
    
def test_get_locked_context_manager_returns_value_and_locks():
    d: ConcurrentDictionary[str, int] = ConcurrentDictionary({'a': 1})
    
    with d.get_locked('a') as value:
        assert value == 1
        # Update inside lock
        d['a'] = value + 1
        assert d['a'] == 2

def test_get_locked_default_value():
    d: ConcurrentDictionary[str, int] = ConcurrentDictionary()
    try:
        with d.get_locked('missing', 3) as value:
            assert value == 3, f"Expected default value 3, got {value}"
    except KeyError:
        pass
        pass

def test_key_lock_context_manager_locks_and_unlocks():
    d: ConcurrentDictionary[str, int] = ConcurrentDictionary({'b': 10})
    lock = d.key_lock('b')
    # Should be a context manager (RLock)
    assert hasattr(lock, '__enter__') and hasattr(lock, '__exit__')
    with lock:
        d['b'] = 20
        assert d['b'] == 20

def test_get_locked_allows_nested_access():
    d: ConcurrentDictionary[str, int] = ConcurrentDictionary({'c': 5})
    with d.get_locked('c') as value:
        assert value == 5
        # Nested get_locked should not deadlock
        with d.get_locked('c') as value2:
            assert value2 == 5

def test_get_locked_thread_safety():
    d: ConcurrentDictionary[str, int] = ConcurrentDictionary({'x': 0})
    errors : List[Exception] = []

    def worker():
        try:
            for _ in range(1000):
                with d.get_locked('x') as v:
                    d['x'] = v + 1
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Thread safety errors occurred: {errors}"
    assert d['x'] == 4000

def test_modify_without_get_locked_causes_race_condition():
    """
    Demonstrates that modifying a value at a key without using get_locked
    can result in a race condition and incorrect result.
    """
    d: ConcurrentDictionary[str, int] = ConcurrentDictionary({'x': 0})

    def worker():
        # Not using get_locked or any locking
        for _ in range(1000):
            v = d['x']  # Read without lock
            # Simulate context switch
            time.sleep(0.000001)
            d['x'] = v + 1  # Write without lock

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # The correct value should be 4000, but due to race conditions, it will likely be less
    assert d['x'] != 4000, (
        "Modifying without get_locked should result in incorrect value due to race conditions, "
        f"but got {d['x']}"
    )
    
if __name__ == "__main__":
    pytest.main([__file__])