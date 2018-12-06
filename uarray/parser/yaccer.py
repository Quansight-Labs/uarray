import ply.yacc as yacc

from .lexer import tokens

from .. import moa, core

# binary operators need precedence
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('left', 'PSI', 'TAKE', 'DROP', 'CAT', 'PDROP', 'PTAKE', 'OMEGA'),
    ('right', 'IOTA', 'DIM', 'TAU', 'SHP', 'RAV', 'PLUSRED', 'MINUSRED', 'TIMESRED', 'DIVIDERED'),
)


def p_main(p):
    '''main : term'''
    p[0] = p[1]


# Ex. "1 2 3", ""
def p_number_list(p):
    '''number_list : number_list INTEGER
                   | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + (int(p[2]),)
    else:
        p[0] = tuple()

# Ex. "<1 2 3>", "<>"
def p_vector(p):
    '''vector : LANGLEBRACKET number_list RANGLEBRACKET'''
    p[0] = core.vector(*p[2])


def p_unary_operation(p):
    """unary_operation : IOTA       term
                       | DIM        term
                       | TAU        term
                       | SHP        term
                       | RAV        term
                       | PLUSRED    term
                       | MINUSRED   term
                       | TIMESRED   term
                       | DIVIDERED  term
    """
    operation_mappings = {
        'iota': moa.Iota,
        'dim': moa.Dim,
        'tau': moa.Total,
        'shp': moa.Shape,
        'rav': moa.Ravel,
    }
    operation = operation_mappings.get(p[1])
    if operation is None:
        print(p)
        raise NotImplementedError(f'no support for unary operation "{p[1]}" yet')
    p[0] = operation(p[2])


def p_binary_operation(p):
    """binary_operation : term PLUS   term
                        | term MINUS  term
                        | term TIMES  term
                        | term DIVIDE term
                        | term PSI    term
                        | term TAKE   term
                        | term DROP   term
                        | term CAT    term
                        | term PDROP  term
                        | term PTAKE  term
                        | term OMEGA  term
    """
    operation_mappings = {
        '+': moa.Add,
        '*': moa.Multiply,
        'psi': moa.Index,
    }
    operation = operation_mappings.get(p[2])
    if operation is None:
        raise NotImplementedError(f'no support for binary operation "{p[2]}" yet')
    p[0] = operation(p[1], p[3])


def p_variable(p):
    """variable : IDENTIFIER
                | IDENTIFIER CARROT vector
    """
    if len(p) == 2:
        p[0] = core.unbound(p[1])
    else:
        p[0] = core.with_shape(core.unbound(p[1]), p[3])


def p_term(p):
    """term : LPAREN binary_operation RPAREN
            | LPAREN unary_operation  RPAREN
            | binary_operation
            | unary_operation
            | vector
            | variable
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]


def p_empty(p):
    'empty :'
    pass


# Error rule for syntax errors
def p_error(p):
    raise ValueError("Syntax error in input!")


def build_parser(start=None):
    return yacc.yacc(start=start)
