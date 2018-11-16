"""Universal array library"""
from . import ast_higher  # NOQA

from .optimize import *  # type: ignore
from .moa import *  # type: ignore
from .logging import enable_logging


__version__ = "0.2"
