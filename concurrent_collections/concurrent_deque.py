import threading
from collections import deque
from typing import Generic, Iterable, Iterator, Optional, TypeVar, Any

T = TypeVar('T')

class ConcurrentQueue(Generic[T]):
    def __init__(self, iterable: Optional[Iterable[T]] = None) -> None:
        self._deque: deque[T] = deque(iterable) if iterable is not None else deque()
        self._lock: threading.RLock = threading.RLock()

    def append(self, item: T) -> None:
        with self._lock:
            self._deque.append(item)

    def appendleft(self, item: T) -> None:
        with self._lock:
            self._deque.appendleft(item)

    def pop(self) -> T:
        with self._lock:
            return self._deque.pop()

    def popleft(self) -> T:
        with self._lock:
            return self._deque.popleft()

    def __len__(self) -> int:
        with self._lock:
            return len(self._deque)

    def __iter__(self) -> Iterator[T]:
        # Make a snapshot copy for safe iteration
        with self._lock:
            return iter(list(self._deque))

    def clear(self) -> None:
        with self._lock:
            self._deque.clear()

    def extend(self, iterable: Iterable[T]) -> None:
        with self._lock:
            self._deque.extend(iterable)

    def extendleft(self, iterable: Iterable[T]) -> None:
        with self._lock:
            self._deque.extendleft(iterable)

    def __repr__(self) -> str:
        with self._lock:
            return f"ConcurrentQueue({list(self._deque)})"

    def __eq__(self, other: Any) -> bool:
        """
        Thread-safe equality comparison.
        
        Two ConcurrentQueue instances are equal if they have the same elements in the same order.
        For concurrent operations, this comparison takes a snapshot of both queues at the time
        of comparison to ensure consistency.
        
        Note: Due to the concurrent nature of the queue, the order may change between
        comparisons, but this method provides a consistent snapshot-based comparison.
        """
        if not isinstance(other, ConcurrentQueue):
            return False
        
        with self._lock:
            with other._lock:
                # Take snapshots for consistent comparison
                self_snapshot = list(self._deque)
                other_snapshot = list(other._deque)
                return self_snapshot == other_snapshot

    def __hash__(self) -> int:
        """
        Thread-safe hash computation.
        
        The hash is computed based on the current state of the queue.
        Note: The hash will change if the queue is modified.
        """
        with self._lock:
            # Convert to tuple for consistent hashing
            items = tuple(self._deque)
            return hash(items)