"""Bounded, short-lived, process-local cache with same-request coalescing."""
from collections import OrderedDict
from concurrent.futures import Future
from copy import deepcopy
from threading import Lock
from time import monotonic

_results = OrderedDict()
_pending = {}
_lock = Lock()
TTL = 600
MAX_RESULTS = 96


def cached_result(key, builder):
    with _lock:
        saved = _results.get(key)
        if saved and monotonic() - saved[0] < TTL:
            _results.move_to_end(key)
            return deepcopy(saved[1])
        _results.pop(key, None)
        future = _pending.get(key)
        owner = future is None
        if owner:
            future = Future()
            _pending[key] = future
    if not owner:
        return deepcopy(future.result(timeout=180))
    try:
        value = builder()
        with _lock:
            _results[key] = (monotonic(), deepcopy(value))
            while len(_results) > MAX_RESULTS:
                _results.popitem(last=False)
        future.set_result(value)
        return deepcopy(value)
    except Exception as exc:
        future.set_exception(exc)
        raise
    finally:
        with _lock:
            _pending.pop(key, None)
