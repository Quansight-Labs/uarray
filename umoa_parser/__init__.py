"""
MoA text parser.
"""

__version__ = "0.5.0"
__all__ = ["lexer", "build_parser", "parse"]

from .lexer import lexer
from .yaccer import build_parser

def parse(expression):
    parser = build_parser()
    return parser.parse(expression)
