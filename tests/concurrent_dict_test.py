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
      
    
if __name__ == "__main__":
    pytest.main([__file__])