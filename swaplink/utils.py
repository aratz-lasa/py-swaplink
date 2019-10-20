import random


def get_random_int_min_zero(max):
    """
    Generates random integer in the range [0,max)
    :param max: range biggest number
    :return: random integer
    """
    return int(random.randint(0, max - 1))


class ListWithCallback(set):
    """
    Send all changes to an observer.
    """

    def __init__(self, value=None, callback=None):
        if value:
            set.__init__(self, value)
        else:
            set.__init__(self)
        self.set_callback(callback)

    def set_callback(self, callback):
        """
        All changes to this list will trigger calls to observer methods.
        """
        self.callback = callback

    def add(self, *args, **kwargs):  # real signature unknown
        set.add(self, *args, **kwargs)
        self._call_callback()

    def clear(self, *args, **kwargs):  # real signature unknown
        set.clear(self)
        self._call_callback()

    def difference_update(self, *args, **kwargs):  # real signature unknown
        set.difference_update(self, *args)
        self._call_callback()

    def discard(self, *args, **kwargs):  # real signature unknown
        set.discard(self, *args, **kwargs)
        self._call_callback()

    def intersection_update(self, *args, **kwargs):  # real signature unknown
        set.intersection_update(self, *args)
        self._call_callback()

    def pop(self, *args, **kwargs):  # real signature unknown
        set.pop(self)
        self._call_callback()

    def remove(self, *args, **kwargs):  # real signature unknown
        set.remove(self, *args, **kwargs)
        self._call_callback()

    def symmetric_difference_update(self, *args, **kwargs):  # real signature unknown
        set.symmetric_difference_update(self, *args, **kwargs)
        self._call_callback()

    def update(self, *args, **kwargs):  # real signature unknown
        set.update(self, *args)
        self._call_callback()

    def _call_callback(self):
        if self.callback:
            self.callback(self)
