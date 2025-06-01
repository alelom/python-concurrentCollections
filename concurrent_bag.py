import threading

class ConcurrentBag:
    """
    A thread-safe, list-like collection.
    All mutating and reading operations are protected by a lock.
    """
    def __init__(self, iterable=None):
        self._lock = threading.RLock()
        self._items = list(iterable) if iterable is not None else []

    def append(self, item):
        with self._lock:
            self._items.append(item)

    def extend(self, iterable):
        with self._lock:
            self._items.extend(iterable)

    def pop(self, index=-1):
        with self._lock:
            return self._items.pop(index)

    def remove(self, value):
        with self._lock:
            self._items.remove(value)

    def __getitem__(self, index):
        with self._lock:
            return self._items[index]

    def __setitem__(self, index, value):
        with self._lock:
            self._items[index] = value

    def __delitem__(self, index):
        with self._lock:
            del self._items[index]

    def __len__(self):
        with self._lock:
            return len(self._items)

    def __iter__(self):
        with self._lock:
            return iter(self._items.copy())

    def clear(self):
        with self._lock:
            self._items.clear()

    def __repr__(self):
        with self._lock:
            return f"ConcurrentBag({self._items!r})"