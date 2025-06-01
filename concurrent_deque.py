import threading
from collections import deque

class ConcurrentQueue:
    def __init__(self, iterable=None):
        self._deque = deque(iterable) if iterable is not None else deque()
        self._lock = threading.RLock()

    def append(self, item):
        with self._lock:
            self._deque.append(item)

    def appendleft(self, item):
        with self._lock:
            self._deque.appendleft(item)

    def pop(self):
        with self._lock:
            return self._deque.pop()

    def popleft(self):
        with self._lock:
            return self._deque.popleft()

    def __len__(self):
        with self._lock:
            return len(self._deque)

    def __iter__(self):
        # Make a snapshot copy for safe iteration
        with self._lock:
            return iter(list(self._deque))

    def clear(self):
        with self._lock:
            self._deque.clear()

    def extend(self, iterable):
        with self._lock:
            self._deque.extend(iterable)

    def extendleft(self, iterable):
        with self._lock:
            self._deque.extendleft(iterable)

    def __repr__(self):
        with self._lock:
            return f"ConcurrentQueue({list(self._deque)})"