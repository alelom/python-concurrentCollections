# Python Concurrent (thread-safe) collections

![Run all tests](https://github.com/alelom/python-concurrentCollections/actions/workflows/run-all-tests.yml/badge.svg)

## tl;dr

Despite what many people think, Python's built-in `list`, `dict`, and `deque` are **NOT thread-safe**.  
They may be thread safe for [_some operations_, but not all](https://docs.python.org/3/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe).  
This created a lot of confusion in the Python community.  
[Google style-guide recommends to not rely on atomicity of built-in collections](https://github.com/google/styleguide/blob/91d6e367e384b0d8aaaf7ce95029514fcdf38651/pyguide.md#218-threading).

`concurrent_collections` provides thread-safe alternatives by using locks internally to ensure safe concurrent access and mutation from multiple threads.

Inspired from the amazing [C#'s concurrent collections](https://learn.microsoft.com/en-us/dotnet/api/system.collections.concurrent?view=net-9.0).

## Why use these collections?

**_There is a lot of confusion on whether Python collections are thread-safe or not_**<sup>1, 2, 3</sup>.

The bottom line is that Python's built-in collections are **not fully thread-safe** for all operations.  
While some simple operations (like `list.append()` or `dict[key] = value`) are thread-safe due to the Global Interpreter Lock (GIL), **compound operations and iteration with mutation are not**. This can lead to subtle bugs, race conditions, or even crashes in multi-threaded programs.

See the [Python FAQ: "What kinds of global value mutation are thread-safe?"](https://docs.python.org/3/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe) for details. The FAQ explains that only some (if common) operations are guaranteed to be atomic and thread-safe, but for anything more complex, you must use your own locking.  
The docs even go as far as to say:

> When in doubt, use a mutex!

Which is telling.

Even [Google recommends to not rely on atomicity of built-in collections](https://github.com/google/styleguide/blob/91d6e367e384b0d8aaaf7ce95029514fcdf38651/pyguide.md#218-threading).

This **`concurrent_collections`** library provides drop-in replacements that handle locking for you.  
Suggestions and feedbacks are welcome.

<sub>

1. [Are lists thread-safe?](https://stackoverflow.com/a/79645609/3873799)  

2. [Google style guide advises against relying on Python's assignment atomicity](https://stackoverflow.com/a/55279169/3873799)  

3. [What kind of "thread safe" are deque's actually?](https://groups.google.com/g/comp.lang.python/c/MAv5MVakB_4)  

</sub>

## Installation

Pip:

```bash
pip install concurrent_collections
```

My recommendation is to always use [`uv`](https://docs.astral.sh/uv/) instead of pip – I personally think it's the best package and environment manager for Python.

```bash
uv add concurrent_collections
```

## Collections

### ConcurrentBag

A thread-safe, list-like collection.

```python
from concurrent_collections import ConcurrentBag

bag = ConcurrentBag([1, 2, 3])
bag.append(4)
print(list(bag))  # [1, 2, 3, 4]
```

### ConcurrentDictionary

A thread-safe dictionary. It has several atomic methods for safe concurrent operations:

- `assign_atomic()` - Atomically assign a value to a key
- `update_atomic()` - Atomically update a value using a function
- `remove_atomic()` - Atomically remove a key and return its value
- `put_if_absent()` - Atomically put a value only if the key doesn't exist
- `replace_if_present()` - Atomically replace a value only if the key exists
- `replace_if_equal()` - Atomically replace a value only if it equals the expected value
- `remove_if_exists()` - Atomically remove a key if it exists
- `get_and_remove()` - Atomically get and remove a value
- `get_locked()` - Context manager for safe read-modify-write operations

#### ConcurrentDictionary's `assign_atomic()`

Assigns a dictionary value under a key in a thread-safe way.
While `dict["somekey"] = value` is allowed, it's best to use `assign_atomic()` for clarity of intent. Using normal assignment will work but raise a UserWarning.

#### ConcurrentDictionary's `remove_atomic()`

Atomically removes a key from the dictionary and returns its value, or None if the key doesn't exist.

```python
from concurrent_collections import ConcurrentDictionary

d = ConcurrentDictionary({'x': 1, 'y': 2})
value = d.remove_atomic('x')  # Returns 1, removes 'x'
```

#### ConcurrentDictionary's `put_if_absent()`

Atomically puts a value for a key only if the key is not already present. Returns the existing value if the key exists, None if the key was added.

```python
from concurrent_collections import ConcurrentDictionary

d = ConcurrentDictionary({'x': 1})
existing = d.put_if_absent('x', 2)  # Returns 1, no change
existing = d.put_if_absent('y', 3)  # Returns None, adds 'y': 3
```

#### ConcurrentDictionary's `replace_if_present()`

Atomically replaces the value for a key only if the key exists. Returns True if the key was replaced, False if the key doesn't exist.

```python
from concurrent_collections import ConcurrentDictionary

d = ConcurrentDictionary({'x': 1})
replaced = d.replace_if_present('x', 2)  # Returns True
replaced = d.replace_if_present('y', 3)  # Returns False
```

#### ConcurrentDictionary's `replace_if_equal()`

Atomically replaces the value for a key only if the current value equals the expected value. Returns True if the value was replaced, False otherwise.

```python
from concurrent_collections import ConcurrentDictionary

d = ConcurrentDictionary({'x': 1})
replaced = d.replace_if_equal('x', 1, 2)  # Returns True
replaced = d.replace_if_equal('x', 1, 3)  # Returns False (current value is 2)
```

#### ConcurrentDictionary's `get_locked()`

When working with `ConcurrentDictionary`, you should use the `get_locked` method to safely read or update the value for a specific key in a multi-threaded environment. This ensures that only one thread can access or modify the value for a given key at a time, preventing race conditions.

```python
from concurrent_collections import ConcurrentDictionary

d = ConcurrentDictionary({'x': "some value" })

# Safely read and update the value for 'x'
with d.get_locked('x') as value:
    # value is locked for this thread
    d['x'] = "new value"
```

#### ConcurrentDictionary's `update_atomic()`

Performs a thread-safe, in-place update to an existing value under a key.

```python

d = ConcurrentDictionary({'x': 1 })
d.update_atomic("x", lambda v: v + 1) # d now contains 2 under the 'x' key.
```

### ConcurrentQueue
For thread-safe queues, Python offers already a lot of alternatives, even too many, so I'm not going to add another. Please refer to the following.

In the [`queue`](https://docs.python.org/3/library/queue.html) module, there are the following thread-safe queue classes:
- `Queue`
- `SimpleQueue`
- `LifoQueue`,
- `PriorityQueue`

:warning: Note these queue collections are thread-safe, although _it isn't explicitly clear from their type name_, making it **dangerously confusing** for people mistakenly thinking that thread-safety applies also to e.g. the [`deque`](https://docs.python.org/3/library/collections.html#collections.deque), which is absolutely **not** thread-safe.

Additionally, there are [other queue classes in the `multiprocessing` module](https://docs.python.org/3/library/multiprocessing.html#pipes-and-queues), which makes it even more confusing due to the redundancy with the above queue classes. This defines:
- `JoinableQueue`
- `Queue` (again)
- `SimpleQueue` (again)


## Equality and Identity Semantics

### ConcurrentBag Equality

`ConcurrentBag` compares as a **multiset** - order doesn't matter, but element frequency does:

```python
from concurrent_collections import ConcurrentBag

# These are equal (same elements, same frequencies)
bag1 = ConcurrentBag([1, 2, 2, 3])
bag2 = ConcurrentBag([2, 1, 3, 2])
assert bag1 == bag2  # True

# These are not equal (different frequencies)
bag3 = ConcurrentBag([1, 2, 3, 3])
assert bag1 != bag3  # True
```

### ConcurrentQueue Equality

`ConcurrentQueue` compares elements in order, taking snapshots for consistency during concurrent operations:

```python
from concurrent_collections import ConcurrentQueue

# These are equal (same elements, same order)
queue1 = ConcurrentQueue([1, 2, 3])
queue2 = ConcurrentQueue([1, 2, 3])
assert queue1 == queue2  # True

# These are not equal (different order)
queue3 = ConcurrentQueue([3, 2, 1])
assert queue1 != queue3  # True
```

### ConcurrentDictionary Equality

`ConcurrentDictionary` compares key-value pairs, order doesn't matter:

```python
from concurrent_collections import ConcurrentDictionary

# These are equal (same key-value pairs)
dict1 = ConcurrentDictionary({'a': 1, 'b': 2})
dict2 = ConcurrentDictionary({'b': 2, 'a': 1})
assert dict1 == dict2  # True

# These are not equal (different values)
dict3 = ConcurrentDictionary({'a': 1, 'b': 3})
assert dict1 != dict3  # True
```

## Thread Safety Guarantees

All collections provide the following guarantees:

1. **Atomic Operations**: All individual operations (append, remove, get, set) are atomic
2. **Consistent Snapshots**: Iteration and equality comparisons take consistent snapshots
3. **No Race Conditions**: Multiple threads can safely access and modify the collections
4. **Identity Consistency**: Hash values and equality comparisons are consistent within a single operation

**Note**: While individual operations are thread-safe, compound operations (like checking length then conditionally modifying) should use the provided atomic methods or context managers to ensure consistency.

## License

MIT License
