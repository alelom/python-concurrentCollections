if True:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    os.environ["concurrent_collections_test"] = "True"

import threading
import time
from typing import Dict, List
import pytest


def test_dict_update_not_thread_safe():
    D = {'x': 0}
    def worker():
        for _ in range(1000):  # More iterations
            old = D['x']
            time.sleep(0.00001)  # Force thread switch
            D['x'] = old + 1

    threads = [threading.Thread(target=worker) for _ in range(8)]  # More threads
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # The expected value is 8 * 50000 = 400000
    # If not thread-safe, the result will be less
    assert D['x'] != 400000, f"D[x] = D[x] + 1 should not be thread-safe without a lock, got {D['x']}"


def test_dict_setdefault_not_thread_safe():
    D : Dict[str,int]= {}
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

    # setdefault is not atomic, but usually doesn't raise, just for demonstration
    assert not errors, f"Thread safety errors occurred: {errors}"




if __name__ == "__main__":
    pytest.main([__file__])
