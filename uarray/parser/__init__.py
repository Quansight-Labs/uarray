from .lexer import lexer
from .yaccer import build_parser

def parse(expression):
    parser = build_parser()
    return parser.parse(expression)
