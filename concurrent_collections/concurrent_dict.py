import threading
from typing import Any, Callable, Dict, Iterator, List, Optional, TypeVar, Generic, Tuple, ContextManager
import warnings

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class ConcurrentDictionary(Generic[K, V]):
    """
    A thread-safe dictionary implementation using a re-entrant lock.
    All operations that mutate or access the dictionary are protected.

    Example usage of update_atomic:

        d = ConcurrentDictionary({'x': 0})
        # Atomically increment the value for 'x'
        d.update_atomic('x', lambda v: v + 1)
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._lock = threading.RLock()
        self._dict: Dict[K, V] = dict(*args, **kwargs)  # type: ignore
        self._key_locks: Dict[K, threading.RLock] = {}

    def _get_key_lock(self, key: K) -> threading.RLock:
        with self._lock:
            if key not in self._key_locks:
                self._key_locks[key] = threading.RLock()
            return self._key_locks[key]

    class _KeyLockContext:
        def __init__(self, outer : "ConcurrentDictionary[K,V]", key: K, default_value: Optional[V]):
            self._outer = outer
            self._key = key
            self._lock = outer._get_key_lock(key)
            self._default_value = default_value

        def __enter__(self) -> Optional[V]:
            self._lock.acquire()
            return self._outer._dict.get(self._key, self._default_value)

        def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
            self._lock.release()

    def get_locked(self, key: K, default_value : Optional[V] = None) -> ContextManager[Optional[V]]:
        """
        Context manager: lock the key, yield its value, unlock on exit.

        Usage:
            with d.get_locked('x') as value:
                # safely read/update value for 'x'
        """
        return self._KeyLockContext(self, key, default_value)

    def key_lock(self, key: K):
        """
        Context manager: lock the key, yield nothing, unlock on exit.

        Usage:
            with d.key_lock('x'):
                # safely update d['x'] or perform multiple operations
        """
        lock = self._get_key_lock(key)
        return lock

    def __getitem__(self, key: K) -> V:
        with self._lock:
            return self._dict[key]

    def __setitem__(self, key: K, value: V) -> None:
        warnings.warn(
            f"Direct assignment (D[key] = value) is discouraged. "
            f"Use assign_atomic() for assigning a value to a new key safely, "
            f"or update_atomic() for thread-safe update of an existing dictionary key.",
            stacklevel=2
        )
        self.assign_atomic(key, value)


    def __delitem__(self, key: K) -> None:
        with self._lock:
            del self._dict[key]


    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        with self._lock:
            return self._dict.get(key, default)


    def setdefault(self, key: K, default: V) -> V:
        with self._lock:
            return self._dict.setdefault(key, default)


    def assign_atomic(self, key: K, value: V) -> None:
        """
        Atomically assign a value to a key.

        This method ensures that the assignment is performed atomically,
        preventing
        """
        self.update_atomic(key, lambda _: value)
        
    
    def update_atomic(self, key: K, func: Callable[[V], V]) -> None:
        """
        Atomically modify the value for a key using func(old_value) -> new_value.

        This method ensures that the read-modify-write sequence is performed atomically,
        preventing race conditions in concurrent environments.

        Example:
            d = ConcurrentDictionary({'x': 0})
            # Atomically increment the value for 'x'
            d.update_atomic('x', lambda v: v + 1)
        """
        with self._lock:
            if key in self._dict:
                old_value = self._dict[key]
                new_value = func(old_value)
                self._dict[key] = new_value
            else:
                # If the key does not exist, we can set it directly
                self._dict[key] = func(None) # type: ignore

    def remove_atomic(self, key: K) -> Optional[V]:
        """
        Atomically remove a key from the dictionary and return its value.
        
        This method ensures that the removal is performed atomically,
        preventing race conditions in concurrent environments.
        
        Returns the value associated with the key, or None if the key doesn't exist.
        
        Example:
            d = ConcurrentDictionary({'x': 1, 'y': 2})
            value = d.remove_atomic('x')  # Returns 1, removes 'x'
        """
        with self._lock:
            return self._dict.pop(key, None)

    def remove_if_exists(self, key: K) -> bool:
        """
        Atomically remove a key from the dictionary if it exists.
        
        Returns True if the key was removed, False if it didn't exist.
        
        Example:
            d = ConcurrentDictionary({'x': 1})
            removed = d.remove_if_exists('x')  # Returns True
            removed = d.remove_if_exists('y')  # Returns False
        """
        with self._lock:
            if key in self._dict:
                del self._dict[key]
                return True
            return False

    def get_and_remove(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """
        Atomically get the value for a key and remove it from the dictionary.
        
        This is equivalent to pop(key, default) but with a more descriptive name
        for atomic operations.
        
        Example:
            d = ConcurrentDictionary({'x': 1})
            value = d.get_and_remove('x')  # Returns 1, removes 'x'
        """
        return self.pop(key, default)

    def put_if_absent(self, key: K, value: V) -> Optional[V]:
        """
        Atomically put a value for a key only if the key is not already present.
        
        Returns the existing value if the key exists, None if the key was added.
        
        Example:
            d = ConcurrentDictionary({'x': 1})
            existing = d.put_if_absent('x', 2)  # Returns 1, no change
            existing = d.put_if_absent('y', 3)  # Returns None, adds 'y': 3
        """
        with self._lock:
            if key in self._dict:
                return self._dict[key]
            else:
                self._dict[key] = value
                return None

    def replace_if_present(self, key: K, value: V) -> bool:
        """
        Atomically replace the value for a key only if the key exists.
        
        Returns True if the key was replaced, False if the key doesn't exist.
        
        Example:
            d = ConcurrentDictionary({'x': 1})
            replaced = d.replace_if_present('x', 2)  # Returns True
            replaced = d.replace_if_present('y', 3)  # Returns False
        """
        with self._lock:
            if key in self._dict:
                self._dict[key] = value
                return True
            return False

    def replace_if_equal(self, key: K, old_value: V, new_value: V) -> bool:
        """
        Atomically replace the value for a key only if the current value equals old_value.
        
        Returns True if the value was replaced, False otherwise.
        
        Example:
            d = ConcurrentDictionary({'x': 1})
            replaced = d.replace_if_equal('x', 1, 2)  # Returns True
            replaced = d.replace_if_equal('x', 1, 3)  # Returns False (current value is 2)
        """
        with self._lock:
            if key in self._dict and self._dict[key] == old_value:
                self._dict[key] = new_value
                return True
            return False

    def pop(self, key: K, default: Optional[V] = None) -> Optional[V]:
        with self._lock:
            return self._dict.pop(key, default)


    def popitem(self) -> tuple[K, V]:
        with self._lock:
            return self._dict.popitem()


    def clear(self) -> None:
        with self._lock:
            self._dict.clear()


    def keys(self) -> List[K]:
        with self._lock:
            return list(self._dict.keys())


    def values(self) -> List[V]:
        with self._lock:
            return list(self._dict.values())


    def items(self) -> List[Tuple[K, V]]:
        with self._lock:
            return list(self._dict.items())


    def __contains__(self, key: K) -> bool:
        with self._lock:
            return key in self._dict


    def __len__(self) -> int:
        with self._lock:
            return len(self._dict)


    def __iter__(self) -> Iterator[K]:
        with self._lock:
            return iter(list(self._dict))


    def __repr__(self) -> str:
        with self._lock:
            return f"ConcurrentDictionary({self._dict!r})"

    def __eq__(self, other: Any) -> bool:
        """
        Thread-safe equality comparison.
        
        Two ConcurrentDictionary instances are equal if they have the same key-value pairs.
        """
        if not isinstance(other, ConcurrentDictionary):
            return False
        
        with self._lock:
            with other._lock:
                return self._dict == other._dict

    def __hash__(self) -> int:
        """
        Thread-safe hash computation.
        
        The hash is computed based on the current state of the dictionary.
        Note: The hash will change if the dictionary is modified.
        """
        with self._lock:
            # Convert to frozenset of items for consistent hashing
            items = frozenset(self._dict.items())
            return hash(items)