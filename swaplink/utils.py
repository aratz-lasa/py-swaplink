import random
from collections.abc import Sequence
from typing import Any, Callable


def random_choice_safe(sequence: Sequence, default: Any = None) -> Any:
    try:
        return random.choice(sequence)
    except IndexError:
        return default


class DictWithCallback(dict):
    """
    Send all changes to an observer.
    """

    _callback: Callable

    def __init__(self, *args, callback=None, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.set_callback(callback)

    def set_callback(self, callback):
        """
        All changes to this dictionary will trigger calls to observer methods
        """
        self._callback = callback

    def __setitem__(self, key, value):
        """
        Intercept the l[key]=value operations.
        Also covers slice assignment.
        """
        result = dict.__setitem__(self, key, value)
        self._call_callback()
        return result

    def __delitem__(self, key):
        result = dict.__delitem__(self, key)
        self._call_callback()
        return result

    def clear(self):
        result = dict.clear(self)
        self._call_callback()
        return result

    def update(self, *args, **kwargs):
        result = dict.update(self, *args, **kwargs)
        self._call_callback()
        return result

    def setdefault(self, key, value=None):
        result = dict.setdefault(self, key, value)
        self._call_callback()
        return result

    def pop(self, k, x=None):
        result = dict.pop(self, k, x)
        self._call_callback()
        return result

    def popitem(self):
        result = dict.popitem(self)
        self._call_callback()
        return result

    def _call_callback(self) -> None:
        if self._callback:
            self._callback(self)
