"""Universal array library"""


from .dispatch import *  # NOQA
from .core import *  # NOQA
from .moa import *  # NOQA
from .nested_sequence import *  # NOQA
from .numpy import *  # NOQA
from .optimize import *  # NOQA

__all__ = (
    dispatch.__all__
    + core.__all__
    + moa.__all__
    + nested_sequence.__all__
    + numpy.__all__
    + optimize.__all__
)

__version__ = "0.4"
