if True:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    os.environ["concurrent_collections_test"] = "True"

from typing import List
import pytest
from collections import deque
import threading
import time


def test_deque_mutation_during_iteration_raises():
    q = deque([1, 2, 3, 4])
    with pytest.raises(RuntimeError, match="deque mutated during iteration"):
        for item in q:
            if item % 2:
                q.append(item * 2)


def test_deque_not_fully_thread_safe_append_pop():
    q : deque[int] = deque()
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
                if q:
                    q.pop()
        except Exception as e:
            errors.append(e)

    t1 = threading.Thread(target=append_items)
    t2 = threading.Thread(target=pop_items)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # There may not always be an exception, but if there is, it will be due to thread unsafety.
    # We assert that no fatal interpreter crash occurred and that errors, if any, are due to race conditions.
    for err in errors:
        assert isinstance(err, (IndexError,)), f"Unexpected error: {err}"

def test_deque_thread_unsafe_iteration_and_mutation():
    q = deque(range(100))
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

    # If a RuntimeError occurs, it demonstrates lack of thread safety for iteration+mutation
    assert any(isinstance(e, RuntimeError) for e in errors)


def test_deque_mutation_during_iteration():
    q = deque([1, 2, 3, 4])
    with pytest.raises(RuntimeError, match="deque mutated during iteration"):
        for item in q:
            if item % 2:
                q.append(item * 2)


def test_deque_not_fully_thread_safe():
    # This test attempts to expose thread safety issues by having multiple threads
    # append and pop items concurrently.
    q :deque[int] = deque()
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
                if q:
                    q.popleft()
        except Exception as e:
            errors.append(e)

    threads : List[threading.Thread]= []
    for _ in range(5):
        t1 = threading.Thread(target=append_items)
        t2 = threading.Thread(target=pop_items)
        threads.extend([t1, t2])

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # If deque was fully thread-safe, there should be no errors.
    # This test may not always fail, but on some runs it may expose issues.
    assert not errors, f"Thread safety errors occurred: {errors}"

    
    
    
if __name__ == "__main__":
    pytest.main([__file__])
