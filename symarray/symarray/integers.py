"""Symbolic integers.
"""

def add_pair(pairs, l, r, neutral):
    c = pairs.get(l)
    if c is None:
        pairs[l] = r
    else:
        c = c + r
        if c==neutral:
            del pairs[l]
        else:
            pairs[l] = c

number_types = (int,)

precedence = {'atom': 100,
              'tuple': 90, 'list': 90, 'dict': 90,
              'matrix': 87,
              'sup': 85, 'sub': 85,
              'item': 80, 'attr' : 80,  'call': 80,
              'integral': 75,
              'exp': 70,
              'unary': 60,
              'frac': 82,
              'dirder': 57,
              'cdot':55,
              'cross': 53,
              'curl': 52,
              'mul': 50,
              'divergence':80,
              'laplace':52,
              'add': 40,
              'shift': 35,
              '&': 34, '^': 33, '|': 32,
              'cmp': 30,
              'not': 25, 'and': 24, 'or' : 23,
              'ifelse': 15,
              'lambda': 10,
}

def fix_sign (s):
    if s.startswith ('-1 * '):
        return ' - ' + s[5:]
    if s.startswith ('-'):
        return ' - ' + s[1:]
    if s.startswith (' + -'):
        return ' - ' + s[4:]
    return s

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0  
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K

try: cmp
except NameError: # Python 3.x
    def cmp(a, b):
        return (a > b) - (a < b)

_lstrip_chars = '-+(*0123456789@ '
def pair_cmp(a, b):
    return cmp(a.lstrip(_lstrip_chars), b.lstrip(_lstrip_chars))


class BaseInteger(object):

    _hashable = None
    def _get_hashable(self):
        if isinstance (self.ops, dict):
            if self._hashable is not None:
                return self._hashable
            r = tuple(sorted(self.ops.items()))
            self._hashable = r
            return r
        return tuple(self.ops)
    
    def __hash__(self):
        return hash((type(self).__name__, self._get_hashable ()))

    def __eq__(self, other):
        if type(self) is type(other):
            if len(self.ops) != len(other.ops):
                return False
            return self._get_hashable () == other._get_hashable ()
        return False

    def __ne__ (self, other): return not (self == other)
    
    def __lt__ (self, other):
        if type(self) is type(other):
            return self._get_hashable () < other._get_hashable ()
        return type(self).__name__ < type (other).__name__


    def get_precedence(self, target='repr'):
        if target=='repr':
            return precedence['call']
        if target=='python':
            return precedence['call']
        raise NotImplementedError('base.{}.get_precedence({!r})'.format(type(self).__name__, target))

    def tostr(self, target='repr', parent=None, level=0):
        if target == 'python':
            return str(self.ops[0])
        if target == 'repr':
            return f'{type(self).__name__}({self.ops!r})'
        return BaseInteger.tostr(self, target=target, parent=parent, level=level)

    def __str__ (self):
        return self.tostr(target='python')

    def __repr__(self):
        return self.tostr(target = 'repr')

    def __add__ (self, other):
        if isinstance (other, number_types):
            other = Number(other)
        if isinstance (other, Number):
            if self == ONE:
                return Terms({self: ONE + other}).normalize()
            return Terms({self: ONE, ONE:other}).normalize()
        if isinstance (other, BaseInteger):
            if self == other:
                return Terms({self:ONE * 2}).normalize()
            return Terms({self:ONE, other:ONE}).normalize()
        return NotImplemented


    def __rmul__ (self, other):
        if isinstance (other, number_types):
            other = Number(other)
        if isinstance (other, Number):
            return Terms({self: other}).normalize()
        return NotImplemented

    
class Number(BaseInteger):

    def __init__(self, value):
        assert isinstance(value, int)
        self.ops = (value,)

    def __neg__(self):
        return type(self)(-self.ops[0])
        
    def get_precedence(self, target='repr'):
        if target == 'python':
            x = self.ops[0]
            if isinstance (x, str):
                return precedence['atom']
            if isinstance (x, number_types):
                if x < 0:
                    return precedence['unary']
                return precedence['atom']
        return BaseInteger.get_precedence(self, target)

    def tostr(self, target='python', parent=None, level=0):
        if target == 'python':
            return str(self.ops[0])
        if target == 'repr':
            return f'{type(self).__name__}({self.ops[0]!r})'
        return BaseInteger.tostr(self, target=target, parent=parent, level=level)

    def __add__(self, other):
        if isinstance(other, int):
            return type(self)(self.ops[0] + other)
        if isinstance(other, type(self)):
            return type(self)(self.ops[0] + other.ops[0])
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, int):
            return type(self)(self.ops[0] * other)
        if isinstance(other, type(self)):
            return type(self)(self.ops[0] * other.ops[0])
        return NotImplemented


    
ONE = Number(1)
ZERO = Number(0)
    
class Symbol(BaseInteger):

    def __init__(self, name):
        assert isinstance(name, str)
        self.ops = (name,)
        
class Terms(BaseInteger):

    def __init__(self, pairs):
        assert isinstance(pairs, dict)
        self.ops = pairs

    def tostr(self, target='python', parent=None, level=0):
        if target == 'python':
            prec = self.get_precedence(target)
            mulsym = ' * '
            if len(self.ops) == 0:
                return ZERO.tostr(target, parent=self)
            l = []
            for t, c in sorted(self.ops.items ()):
                st = t.tostr(target=target, parent=self)
                sc = c.tostr(target=target, parent=self)
                tprec = t.get_precedence(target)
                cprec = c.get_precedence(target)
                if t == ONE:
                    if cprec < precedence['add']:
                        sc = parens(sc, target)
                    if cprec == precedence['unary']:
                        l.append(sc)
                    else:
                        l.append(' @+@ '+sc)
                elif c == ONE:
                    if tprec < precedence['add']:
                        st = parens(st, target)
                    if tprec == precedence['unary']:
                        l.append (st)
                    else:
                        l.append (' @+@ {}'.format(st))
                elif c == -ONE:
                    if tprec < precedence['add']:
                        st = parens(st, target)
                    l.append (' @-@ {}'.format(st))
                else:
                    if cprec < precedence['mul']:
                        sc = parens(sc, target)
                    if tprec < precedence['mul']:
                        st = parens(st, target)
                    if cprec == precedence['unary']:
                        l.append ('{}{}{}'.format(sc, mulsym, st))
                    else:
                        l.append (' @+@ {}{}{}'.format(sc, mulsym, st))
            l = map (fix_sign, sorted(l, key=cmp_to_key(pair_cmp)))
            r = ''.join(l)
            if r.startswith (' @+@ '):
                r = r[5:]
            elif r.startswith (' @-@ '):
                r = '-' + r[5:]
            elif r.startswith (' - '):
                r = '-' + r[3:]
            r = r.replace(' @+@ -', ' @-@ ')
            return r.replace(' @+@ ', ' + ').replace(' @-@ ', ' - ')
        return BaseInteger.tostr(self, target=target, parent=parent, level=level)

    
    def normalize(self):
        terms = {}
        for l, r in self.ops.items():
            if l == ZERO  or r == ZERO:
                continue
            if isinstance(l, type(self)):
                for l1, r1 in l.ops.items():
                    add_pair(terms, l1, r * r1, ZERO)
            else:
                add_pair(terms, l, r, ZERO)
        if not terms:
            return ZERO
        if len(terms)==1:
            l, r = tuple(terms.items())[0]
            if l == ONE:
                return r
            if r == ONE:
                return l
        return type(self)(terms)
        
class Factors(BaseInteger):

    def __init__(self, ):
        assert isinstance(pairs, dict)
        self.ops = pairs
