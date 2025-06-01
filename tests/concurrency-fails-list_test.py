import pytest
from collections import deque
import threading
import time


def test_list_setitem_thread_safe():
    L = [0, 1, 2, 3, 4]
    errors = []

    def worker():
        for _ in range(10000):
            try:
                L[0] = L[1]
            except Exception as e:
                errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # This operation is thread-safe
    assert not errors, f"Thread safety errors occurred: {errors}"



def test_list_append_last_element_thread_safe():
    L = [0]
    errors = []

    def worker():
        for _ in range(10000):
            try:
                L.append(L[-1])
            except Exception as e:
                errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # This operation is thread-safe
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