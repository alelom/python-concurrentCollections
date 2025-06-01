if True:
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    os.environ["concurrent_collections_test"] = "True"

import pytest

def test_import_all_collections():
    try:
        from concurrent_collections import ConcurrentBag, ConcurrentDictionary, ConcurrentQueue
    except ImportError as e:
        assert False, f"Import failed: {e}"


if __name__ == "__main__":
    test_import_all_collections()