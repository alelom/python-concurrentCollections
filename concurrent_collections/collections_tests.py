import pytest

def test_import_all_collections():
    try:
        from concurrent_collections import ConcurrentBag, ConcurrentDictionary, ConcurrentQueue
    except ImportError as e:
        assert False, f"Import failed: {e}"


if __name__ == "__main__":
    test_import_all_collections()