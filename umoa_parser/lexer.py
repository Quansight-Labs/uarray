import ply.lex as lex

reserved = {
    # binary expresions
    'psi': 'PSI',
    'take': 'TAKE',
    'drop': 'DROP',
    'cat': 'CAT',
    'pdrop': 'PDROP',
    'ptake': 'PTAKE',
    'omega': 'OMEGA',
    # unary expresions
    'iota': 'IOTA',
    'dim': 'DIM',
    'tau': 'TAU',
    'shp': 'SHP',
    'rav': 'RAV',
}

tokens = (
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
    'PSI', 'TAKE', 'DROP', 'CAT', 'PDROP', 'PTAKE', 'OMEGA',
    'PLUSRED', 'MINUSRED', 'TIMESRED', 'DIVIDERED',
    'IOTA', 'DIM', 'TAU', 'SHP', 'RAV',
    'LANGLEBRACKET', 'RANGLEBRACKET',
    'LPAREN', 'RPAREN',
    'CARROT',
    'INTEGER', 'IDENTIFIER'
)

# Tokens

## containers
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LANGLEBRACKET = r'<'
t_RANGLEBRACKET = r'>'
t_CARROT = r'\^'

## binary operators
t_PLUS   = r'\+'
t_MINUS  = r'\-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'

## unary operators
t_PLUSRED   = r'\+red'
t_MINUSRED  = r'\-red'
t_TIMESRED  = r'\*red'
t_DIVIDERED = r'/red'


## symbols
def t_INTEGER(t):
    r'[+-]?\d+'
    t.value = int(t.value)
    return t


def t_IDENTIFIER(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t


def t_COMMENT(t):
    r'\#.*'
    pass
    # No return value. Token discarded


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
    raise ValueError(f"Illegal character '{t.value[0]}' no valid token can be formed from '{t.value}' on line {t.lexer.lineno}")


lexer = lex.lex()
