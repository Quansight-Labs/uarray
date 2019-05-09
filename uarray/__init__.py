import uarray.backend as backend
from .backend import *
from ._version import get_versions  # type: ignore

__version__ = get_versions()["version"]
del get_versions
