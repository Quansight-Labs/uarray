import typing

import weakref

__all__ = ["Singleton"]


class SingletonType(type):
    _instances: typing.MutableMapping[int, object] = weakref.WeakValueDictionary()

    def __call__(cls, *args, **kw):
        h = hash((cls, *args, *kw.items()))
        if h in SingletonType._instances:
            res = SingletonType._instances[h]
            return res
        new_instance = super().__call__(*args, **kw)
        SingletonType._instances[h] = new_instance
        return new_instance


class Singleton(metaclass=SingletonType):
    """
    If class would create a new instance with same hash
    as existing instance, it will just return the existing instance.
    """

    pass


# class Singleton:


#     def __init_subclass__(cls, **kwargs):
#         super().__init_subclass__(**kwargs)
#         cls._instances = weakref.WeakValueDictionary()

#     def __new__(cls, *args, **kwargs):

#         # don't pass args to new
#         # https://stackoverflow.com/a/34777831/907060
#         # https://stackoverflow.com/a/34054788/907060
#         inst = super().__new__(cls)
#         inst.__init__(*args, **kwargs)

#         h = hash(inst)
#         return cls._instances.setdefault(h, inst)
