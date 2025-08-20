if True:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    os.environ["concurrent_collections_test"] = "True"

import threading
import time
from typing import List
import pytest
from concurrent_collections import ConcurrentQueue
from collections import deque


def test_concurrentqueue_thread_safe_append_pop():
    q : ConcurrentQueue[int] = ConcurrentQueue()
    errors : List[Exception] = []

    def append_items():
        try:
            for i in range(10000):
                q.append(i)
        except Exception as e:
            errors.append(e)

    def pop_items():
        try:
            for _ in range(10000):
                try:
                    q.pop()
                except IndexError:
                    pass
        except Exception as e:
            errors.append(e)

    threads : List[threading.Thread] = []
    for _ in range(5):
        t1 = threading.Thread(target=append_items)
        t2 = threading.Thread(target=pop_items)
        threads.extend([t1, t2])

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # There should be no thread safety errors
    assert not errors, f"Thread safety errors occurred: {errors}"


def test_concurrentqueue_thread_safe_iteration_and_mutation():
    q = ConcurrentQueue(range(100))
    errors : List[Exception] = []

    def iterate():
        try:
            for _ in q:
                time.sleep(0.0001)
        except Exception as e:
            errors.append(e)

    def mutate():
        try:
            for i in range(100, 200):
                q.append(i)
                time.sleep(0.0001)
        except Exception as e:
            errors.append(e)

    t1 = threading.Thread(target=iterate)
    t2 = threading.Thread(target=mutate)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # There should be no thread safety errors
    assert not errors, f"Thread safety errors occurred: {errors}"


def test_concurrentqueue_thread_safe_appendleft_popleft():
    q : ConcurrentQueue[int] = ConcurrentQueue()
    errors : List[Exception] = []

    def appendleft_items():
        try:
            for i in range(10000):
                q.appendleft(i)
        except Exception as e:
            errors.append(e)

    def popleft_items():
        try:
            for _ in range(10000):
                try:
                    q.popleft()
                except IndexError:
                    pass
        except Exception as e:
            errors.append(e)

    threads : List[threading.Thread] = []
    for _ in range(5):
        t1 = threading.Thread(target=appendleft_items)
        t2 = threading.Thread(target=popleft_items)
        threads.extend([t1, t2])

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # There should be no thread safety errors
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
    
    
if __name__ == "__main__":
    pytest.main([__file__])