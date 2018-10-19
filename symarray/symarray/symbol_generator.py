"""Provides symbol generator module magic.

Origin of the idea:
https://stackoverflow.com/questions/51087634/overriding-from-my-module-import
"""
# Author: Pearu Peterson
# Created: October 2018
import sys
import importlib

class ModuleWrapper:
    def __init__(self, module_name, getter):
        self.__module = importlib.import_module(module_name)
        self.__getter = getter
        sys.modules[module_name] = self

    @property
    def __path__(self):
        return None

    def __getattr__(self, name):
        try:
            return getattr(self.__module, name)
        except AttributeError:
            return self.__getter(name)
