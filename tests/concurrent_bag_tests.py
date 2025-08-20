if True:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    os.environ["concurrent_collections_test"] = "True"

import threading
import time
from typing import List
import pytest
from concurrent_collections import ConcurrentBag

def test_concurrent_bag_thread_safety():
    bag : ConcurrentBag[int] = ConcurrentBag()
    errors : List[Exception] = []

    def add_items():
        try:
            for i in range(10000):
                bag.append(i)
        except Exception as e:
            errors.append(e)

    def remove_items():
        try:
            for _ in range(10000):
                try:
                    bag.pop()
                except IndexError:
                    pass
        except Exception as e:
            errors.append(e)

    threads : List[threading.Thread] = []
    for _ in range(5):
        t1 = threading.Thread(target=add_items)
        t2 = threading.Thread(target=remove_items)
        threads.extend([t1, t2])

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"Thread safety errors occurred: {errors}"


def test_concurrent_bag_iteration_safe():
    bag = ConcurrentBag(range(100))
    errors : List[Exception] = []

    def iterate():
        try:
            for _ in bag:
                time.sleep(0.0001)
        except Exception as e:
            errors.append(e)

    def mutate():
        try:
            for i in range(100, 200):
                bag.append(i)
                time.sleep(0.0001)
        except Exception as e:
            errors.append(e)

    t1 = threading.Thread(target=iterate)
    t2 = threading.Thread(target=mutate)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert not errors, f"Iteration/mutation errors: {errors}"


def test_concurrent_bag_setitem_thread_safe():
    bag = ConcurrentBag([0, 1, 2, 3, 4])
    errors : List[Exception] = []

    def worker():
        for _ in range(10000):
            try:
                bag[0] = bag[1]
            except Exception as e:
                errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # This operation should be thread-safe in ConcurrentBag
    assert not errors, f"Thread safety errors occurred: {errors}"


def test_concurrent_bag_append_last_element_thread_safe():
    bag = ConcurrentBag([0])
    errors : List[Exception] = []

    def worker():
        for _ in range(10000):
            try:
                bag.append(bag[-1])
            except Exception as e:
                errors.append(e)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # This operation should be thread-safe in ConcurrentBag
    assert not errors, f"Thread safety errors occurred: {errors}"



if __name__ == "__main__":
    pytest.main([__file__])