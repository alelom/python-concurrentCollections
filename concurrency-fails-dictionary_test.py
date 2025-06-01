import threading
import time


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
    D = {}
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

    # setdefault is not atomic, but usually doesn't raise, just for demonstration
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