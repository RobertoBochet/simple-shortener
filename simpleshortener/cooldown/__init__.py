import functools
from datetime import datetime, timedelta
from typing import Union

from cooldown.exceptions import CooldownError


class CooldownMethod:
    def __init__(self, cooldown: Union[timedelta, int]):
        self._cooldown: timedelta = cooldown if isinstance(cooldown, timedelta) else timedelta(seconds=cooldown)

    def __get__(self, obj, objtype):
        """Support instance methods."""
        return functools.partial(self.__call__, obj)

    def __call__(self, func, *args, **kwargs):

        def wrapper(*args, **kwargs):
            _self = args[0]
            func_name = func.__name__

            try:
                _self.__cooldown__
            except AttributeError:
                _self.__cooldown__ = {}

            try:
                if _self.__cooldown__[func_name] > datetime.now():
                    raise CooldownError

            except KeyError:
                pass

            _self.__cooldown__[func_name] = datetime.now() + self._cooldown

            func(*args, **kwargs)

        return wrapper
