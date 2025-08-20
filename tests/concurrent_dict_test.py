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
    dic["x"] = 0
    def worker():
        for _ in range(10000):
            old = dic['x']
            time.sleep(0.00001)
            # D.__setitem__('x', old + 1)
            dic.update_atomic("x", lambda v: v + 1)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # The expected value is 8 * 10000 = 80000
    assert dic['x'] == 80000, f"ConcurrentDictionary should be thread-safe, got {dic['x']}"


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