if True:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    os.environ["concurrent_collections_test"] = "True"

import threading
import time
from concurrent_collections import ConcurrentDictionary


def test_concurrentdictionary_update_thread_safe():
    D = ConcurrentDictionary({'x': 0})
    def worker():
        for _ in range(10000):
            old = D['x']
            time.sleep(0.00001)
            # D.__setitem__('x', old + 1)
            D.update_atomic("x", lambda v: v + 1)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # The expected value is 8 * 10000 = 80000
    assert D['x'] == 80000, f"ConcurrentDictionary should be thread-safe, got {D['x']}"


def test_concurrentdictionary_setdefault_thread_safe():
    D = ConcurrentDictionary()
    errors = []

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
    D = ConcurrentDictionary({'x': 0})
    errors = []

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
    D = ConcurrentDictionary({i: i for i in range(100)})
    errors = []

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
    import types

    # Collect all functions in globals() that start with 'test_' and are functions
    test_functions = [
        func for name, func in globals().items()
        if name.startswith("test_") and isinstance(func, types.FunctionType)
    ]
    failed = 0
    for func in test_functions:
        try:
            print(f"Running {func.__name__} ...")
            func()
        except Exception as e:
            failed += 1
            print(f"***\nFAILED: {func.__name__}: {e}\n***")

    print(f"\n{len(test_functions) - failed} passed, {failed} failed.")