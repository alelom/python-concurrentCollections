if True:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    os.environ["concurrent_collections_test"] = "True"

from typing import List
import pytest
from collections import deque
import threading
import time


def test_list_setitem_thread_safe():
    L = [0, 1, 2, 3, 4]
    errors : List[Exception]= []

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
    pytest.main([__file__])
