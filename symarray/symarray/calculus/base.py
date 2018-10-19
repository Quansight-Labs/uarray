""" Provides base classes to Calculus.

BaseCalculus
  BaseAtom
  BaseNumber
  BaseTerms
  BaseFactors
  BaseComposite
  BaseComponent
"""
# Author: Pearu Peterson
# Created: October 2018

from fractions import Fraction
from collections import defaultdict

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

# Utility functions

def parens (s, target):
    if target == 'python': return '('+s+')'
    raise NotImplementedError (repr(target))

def fix_sign (s):
    if s.startswith ('-1 * '):
        return ' - ' + s[5:]
    if s.startswith ('-'):
        return ' - ' + s[1:]
    if s.startswith (' + -'):
        return ' - ' + s[4:]
    return s


def check_rtype(func):
    #return func # comment in when debugging
    def wrapper (self, *arguments, **parameters):
        r = func (self, *arguments, **parameters)
        if r is NotImplemented:
            return r
        assert isinstance (r, self.algebra_type), '{}.{} returned {} instance, expected {}'\
            .format(type(self).__name__, func.__name__, type(r).__name__, self.algebra_type.__name__)
        return r
    wrapper.__name__ = 'check_rtype@' + func.__name__
    return wrapper


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


def cmp(a, b):
    return (a > b) - (a < b)


_lstrip_chars = '-+(*0123456789@ '


def pair_cmp(a, b):
    return cmp(a.lstrip(_lstrip_chars), b.lstrip(_lstrip_chars))


#

class BaseCalculus(object):
    """Base class for Calculus classes.

    Here we introduce the following notions:

    algebra - represents arbitrary field, calculus expressions are the
      members of this field

    scalar - represents scalar field of the algebra, algebra object
      multiplied scalar is the member of algebra

    number - represents a number used for counting the operations with
      the same operands, for instance, a+a is 2*a, or `a*a is
      a**2`.

    In many cases the concepts of scalar and number coincide but not
    always, for instance, in the case of complex array algebra where
    algreba is a set of arrays, scalar is a set of complex numbers,
    and number is a set of positive integers.

    In other cases, the concepts of algerba, scalar, and number all
    coincide, for instance, in the case where algebra is a set of real
    numbers.
    """
    
    # Python types that are mapped to BaseNumeric instances
    number_types = (int, float, Fraction)
    
    @property
    def algebra_type (self):
        return BaseCalculus
    @property
    def scalar_type (self):
        return BaseCalculus
    @property
    def number_type (self):
        return int
    @property
    def index_type (self):
        return int
    @property
    def slice_type (self):
        return slice
    @property
    def exponent_type(self):
        return BaseCalculus
    @property
    def terms_type (self):
        return BaseTerms
    @property
    def factors_type (self):
        return BaseFactors
    @property
    def composite_type (self):
        return BaseComposite
    @property
    def component_type (self):
        return BaseComponent
    @property
    def atom_type(self):
        return BaseAtom
    @property
    def pairs_type(self):
        return BasePairs
    @property
    def floordiv_type(self):
        return BaseFloorDiv

    @property
    def algebra_zero(self):
        raise NotImplementedError ('{}.algebra_zero property'.format (type (self).__name__))
    @property
    def scalar_zero(self):
        raise NotImplementedError ('{}.scalar_zero property'.format (type (self).__name__))
    @property
    def number_zero(self):
        raise NotImplementedError ('{}.number_zero property'.format (type (self).__name__))
    @property
    def algebra_one(self):
        raise NotImplementedError ('{}.algebra_one property'.format (type (self).__name__))
    @property
    def scalar_one(self):
        raise NotImplementedError ('{}.scalar_one property'.format (type (self).__name__))
    @property
    def number_one(self):
        raise NotImplementedError ('{}.number_one property'.format (type (self).__name__))
    @property
    def is_scalar_algebra(self):
        # in scalar algebra the exponent is allowed to be algebra element
        return issubclass(self.scalar_type, self.algebra_type)
    @property
    def is_number_scalar(self):
        # in number scalar the coefficient is allowed to be scalar element
        return issubclass(self.number_type, self.scalar_type)

    def __init__(self, ops):
        self.ops = ops
        self._check()

    def _check(self):
        """ Check object integrity """
        assert isinstance(self.ops, (dict, tuple)),repr(type(self.ops))

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
        return hash((type(self).__name__, self._get_hashable()))

    def __eq__(self, other):
        if type(self) is type(other):
            if len(self.ops) != len(other.ops):
                return False
            return self._get_hashable() == other._get_hashable()
        return False

    def __ne__ (self, other): return not (self == other)
    
    def __lt__ (self, other):
        if type(self) is type(other):
            return self._get_hashable () < other._get_hashable ()
        return type(self).__name__ < type (other).__name__
    
    def __repr__(self):
        return self.tostr(target = 'repr')

    def __str__ (self):
        return self.tostr(target = 'python')

    def __pos__(self):
        return self

    @check_rtype
    def __neg__ (self):
        return self * (-self.scalar_one)

    @check_rtype
    def __add__ (self, other):
        if isinstance (other, self.number_types):
            other = self.number_type(other)
        if isinstance (other, self.scalar_type): # scalar algebra
            if self == self.algebra_one:
                return self.terms_type ({self: self.scalar_one + other}).normalize()
            return self.terms_type ({self: self.scalar_one, self.algebra_one:other}).normalize()
        if isinstance (other, self.algebra_type):
            if self == other:
                return self.terms_type ({self:self.number_one * 2}).normalize()
            return self.terms_type ({self:self.number_one, other:self.number_one}).normalize()
        return NotImplemented

    __radd__ = __add__

    @check_rtype
    def __mul__ (self, other):
        r = NotImplemented
        if isinstance (other, self.number_types):
            other = self.number_type(other)
        if isinstance (other, self.scalar_type):
            r = self.terms_type({self: other})
        elif isinstance (other, self.algebra_type):
            if self == other:
                r = self.factors_type({self: self.number_one * 2})
            else:
                r = self.factors_type({self: self.number_one, other: self.number_one})
        if r is NotImplemented:
            return r
        return r.normalize()

    @check_rtype
    def __rmul__ (self, other):
        if isinstance (other, self.number_types):
            other = self.number_type(other)
        if isinstance (other, self.scalar_type):
            return self.terms_type({self: other}).normalize()
        return NotImplemented

    @check_rtype
    def __pow__ (self, other):
        if isinstance (other, self.number_types):
            other = self.number_type(other)
        if isinstance (other, self.exponent_type):
            return self.factors_type({self: other}).normalize()
        #if isinstance (other, self.number_type):
        #    return self.factors_type({self: other}).normalize()
        if isinstance (other, self.algebra_type) and self.is_scalar_algebra:
            return self.factors_type({self: other}).normalize()
        return NotImplemented

    def __rpow__ (self, other):
        if isinstance (other, self.number_types):
            return self.number_type(other) ** self
        return NotImplemented

    def __sub__ (self, other):
        return self + (-other)

    def __rsub__(self, other):
        return other + (-self)

    @check_rtype
    def __div__ (self, other):
        if isinstance (other, self.number_types):
            other = self.number_type(other)
        if self.is_scalar_algebra:
            if self == other:
                return self.scalar_one
        return self * other ** (-self.number_one)

    __truediv__ = __div__
    
    def __rdiv__ (self, other):
        if isinstance (other, self.number_types):
            return self.number_type(other) / self
        return other * self ** (-self.number_one)

    __rtruediv__ = __rdiv__

    def __floordiv__(self, other):
        if isinstance (other, self.number_types):
            other = self.number_type(other)
        return self.floordiv_type(self, other).normalize()

    def __rfloordiv__ (self, other):
        if isinstance (other, self.number_types):
            return self.number_type(other) // self
        return NotImplemented
    
    @check_rtype
    #@_normalize
    def __call__(self, *arguments):
        args = []
        for a in arguments:
            if isinstance(a, self.number_types):
                a = self.number_type(a)
            args.append(a)
        return self.composite_type(self, *args)

    def normalize(self):
        """ Return normalized expression.
        """
        sops = ', '.join (type (k).__name__ for k in self.ops)
        print(f'base.{type(self).__name__}.normalize: not implemented: {sops}')
        raise
        return self
    
    def __getitem__(self, item):
        if not isinstance(item, tuple):
            item = item,
        def index_or_slice(obj):
            if isinstance(obj, slice):
                return self.slice_type(obj)
            return self.index_type(obj)
        item = map(index_or_slice, item)
        return self.component_type(self, *item).normalize ()

    def get_precedence(self, target='python'):
        if target=='repr':
            return precedence['call']
        if target=='tree':
            return 0
        if target=='python':
            return precedence['call']
        raise NotImplementedError(f'base.{type(self).__name__}.get_precedence({target!r})')

    def tostr(self, target='python', parent=None, level=0):
        if target == 'repr':
            return '{}({!r})'.format(type(self).__name__, self.ops)
        if target == 'tree':
            tab = level*'  '
            l = [tab + type(self).__name__+':']
            for op in self.ops:
                if isinstance(op, tuple):
                    l2 = [tab + '  ' + type(op).__name__ + ':']
                    for _op in op:
                        if isinstance (_op, BaseCalculus):
                            l2.append(_op.tostr(target=target, level=level + 2))
                        else:
                            l2.append (tab + '    ' + repr (_op))
                    sop = '\n'.join(l2)
                elif isinstance(op, BaseCalculus):
                    sop = op.tostr(target=target, level=level+1)
                else:
                    sop = tab + '  ' + repr(op)
                l.append(sop)
            return '\n'.join(l)
        if target == 'python':
            l = []
            for op in self.ops:
                if isinstance(op, str):
                    l.append(op)
                elif isinstance(op, tuple):
                    l2 = []
                    for _op in op:
                        if isinstance (_op, BaseCalculus):
                            l2.append(_op.tostr(target=target, parent=op, level=level+2))
                        else:
                            l2.append(str(_op))
                    l.append('(' + ', '.join(l2) + ')')
                else:
                    l.append(op.tostr(target=target, parent=self, level=level+1))
            return '{}({})'.format(type(self).__name__, ', '.join(l))
        raise NotImplementedError('{}.tostr({!r})'.format(type(self).__name__, target))

    def power (self, other):
        return NotImplemented


class BaseAtom(BaseCalculus):
    """Base class for atoms.

    Atom is a symbolic field instance. Field instances can represent
    scalar, vector, tensor fields.

    """
    
    def __init__ (self, op):
        if isinstance (op, Fraction):
            n, d = op.numerator, op.denominator
            if n == d:
                op = n
            if n == 0:
                op = n
        BaseCalculus.__init__ (self, (op,))

    def _get_hashable(self):
        return self.ops[0]

    def get_precedence(self, target='python'):
        if target=='tree':
            return 0
        if target == 'python':
            x = self.ops[0]
            if isinstance (x, str):
                return precedence['atom']
            if isinstance (x, self.number_types):
                if x < 0:
                    return precedence['unary']
                return precedence['atom']
        return BaseCalculus.get_precedence(self, target)

    def tostr(self, target='python', parent=None, level=0):
        if target == 'python':
            return str (self.ops[0])
        if target == 'repr':
            return '{}({!r})'.format(type(self).__name__, self.ops[0])
        return BaseCalculus.tostr(self, target=target, parent=parent, level=level)

    def normalize(self):
        return self

class BasePairs(BaseCalculus):

    def _check (self):
        BaseCalculus._check(self)
        scalar_type = self.scalar_type
        algebra_type = self.algebra_type
        number_type = self.number_type
        for l, r in self.ops.items ():
            assert isinstance (l, (algebra_type, tuple)),repr((type (l), algebra_type))
            if self.is_scalar_algebra:
                assert isinstance (r, (scalar_type, algebra_type)),repr((type (r), scalar_type))

    def tostr(self, target='python', parent=None, level=0):
        if target == 'tree':
            tab = level*'  '
            l = [tab + type(self).__name__+':']
            for left, right in self.ops.items():
                if isinstance(left, tuple):
                    l2 = [tab + '  ' + type(left).__name__ + ':']
                    for op in left:
                        if isinstance(op, int):
                            sop = tab + '    ' + str(op)
                        else:
                            sop = op.tostr(target=target, level = level + 2)
                        l2.append(sop)
                    st = '\n'.join(l2)
                else:
                    st = left.tostr(target=target, level=level+1)
                sc = right.tostr(target=target, level=level+1)
                l.append(st)
                l.append(sc)
            return '\n'.join(l)
        return BaseCalculus.tostr(self, target=target, parent=parent, level=level)

    @classmethod
    def _add_pair(cls, d, l, r, zero):
        c = d.get (l)
        if c is None:
            d[l] = r
        else:
            c = c+r
            if c==zero:
                del d[l]
            else:
                d[l] = c

    @classmethod
    def _make_pair (cls, l, r, zero):
        d = {}
        cls._add_pair (d, l, r, zero)
        return cls(d).normalize()

class BaseTerms(BasePairs):

    @check_rtype
    def normalize(self):
        terms = {}
        cls = type (self)
        zero = self.scalar_zero
        one = self.scalar_one
        number_type = self.number_type
        for l, r in self.ops.items ():
            if l==self.algebra_zero:
                continue
            if r==self.scalar_zero:
                continue
            if isinstance(l, cls):
                for l1, r1 in l.ops.items ():
                    self._add_pair(terms, l1, r1 * r, zero = zero)
            else:
                self._add_pair(terms, l, r, zero = zero)
        if len (terms) == 0:
            return self.algebra_zero
        if len (terms) == 1:
            l, r = list(terms.items ())[0]
            if self.is_scalar_algebra:
                if l == one:
                    return r
            if r==one:
                return l
        return cls (terms)

    def tostr(self, target='python', parent=None, level=0):
        if target not in ['python']:
            return BasePairs.tostr(self, target=target, parent=parent, level=level)
        prec = self.get_precedence (target)
        if target == 'python':
            mulsym = ' * '
        if len (self.ops) == 0:
            return self.algebra_zero.tostr (target, parent=self)        
        if len (self.ops) > 0:
            l = []
            for t, c in sorted(self.ops.items ()):
                st = t.tostr(target=target, parent=self)
                sc = c.tostr(target=target, parent=self)
                tprec = t.get_precedence(target)
                cprec = c.get_precedence(target)
                if t == self.algebra_one:
                    if cprec < precedence['add']:
                        sc = parens(sc, target)
                    if cprec == precedence['unary']:
                        l.append(sc)
                    else:
                        l.append(' @+@ '+sc)
                elif c == self.scalar_one:
                    if tprec < precedence['add']:
                        st = parens(st, target)
                    if tprec == precedence['unary']:
                        l.append (st)
                    else:
                        l.append (' @+@ {}'.format(st))
                elif c == -self.scalar_one:
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
            if target == 'latex':
                return r.replace(' @+@ ', ' \\allowbreak + ').replace(' @-@ ', ' \\allowbreak - ')
            return r.replace(' @+@ ', ' + ').replace(' @-@ ', ' - ')
        return self.algebra_zero.tostr(target=target, parent=self)

    def get_precedence (self, target='python'):
        if target=='tree':
            return 0
        if len (self.ops) > 1:
            return precedence['add']
        if len (self.ops) ==0:
            return precedence['atom']
        t, c = list(self.ops.items ())[0]
        if t==self.algebra_one:
            return c.get_precedence(target)
        return precedence['mul']    


class BaseFactors(BasePairs):
    
    def get_precedence(self, target='python'):
        if target=='tree':
            return 0
        if len (self.ops) > 1:
            return precedence['mul']
        if len (self.ops) ==0:
            return precedence['atom']
        b, e = list(self.ops.items ())[0]
        if e==self.scalar_one:
            return b.get_precedence(target)
        return precedence['exp']
    
    def tostr(self, target='python', parent=None, level=0):
        if target not in ['python']:
            return BasePairs.tostr(self, target=target, parent=parent, level=level)
        if target == 'python':
            expsym = ' ** '
            mulsym = ' * '
            l, r = '', ''
        if len (self.ops) == 0:
            return self.algebra_one.tostr (target, parent=self)
        if len (self.ops) > 1:
            lst = []
            for b, e in self.ops.items ():
                sb = b.tostr(target=target, parent=self)
                se = e.tostr(target=target, parent=self)
                bprec = b.get_precedence(target)
                eprec = e.get_precedence(target)
                if target == 'python' and eprec <= precedence['exp']:
                    se = parens(se, target)
                if e == self.scalar_one:
                    if bprec <= precedence['mul']:
                        sb = parens(sb, target)                
                    lst.append ('{}{}'.format(mulsym, sb))
                else:
                    if bprec == precedence['frac']:
                        sb = parens(sb, target)
                    elif bprec <= precedence['exp']:
                        sb = parens(sb, target)
                    lst.append (''.join((mulsym, l, sb,r, expsym,l,se,r)))
            lst = sorted(lst, key=cmp_to_key(pair_cmp))
            r = ''.join(lst)
            if r.startswith (' * '):
                r = r[3:]
            return r
        b, e = list(self.ops.items ())[0]
        sb = b.tostr(target=target, parent=self)
        se = e.tostr(target=target, parent=self)
        bprec = b.get_precedence(target)
        eprec = e.get_precedence(target)
        if target == 'python' and eprec <= precedence['exp']:
            se = parens(se, target)
        if e == self.scalar_one:
            return sb
        if bprec == precedence['frac']:
            sb = parens(sb, target)
        elif bprec <= precedence['exp']:
            sb = parens(sb, target)
        return ''.join ((l,sb,r, expsym, l,se,r))

    def power (self, other):
        number_type = self.number_type
        zero = self.scalar_zero
        if isinstance(other, number_type):
            n = other.ops[0]
            d = {}
            if isinstance(n, int):
                for b, e in self.ops.items():
                    if isinstance(e, number_type):
                        _e = e.ops[0]
                        if not isinstance(_e, int):
                            return NotImplemented
                        ne = other * e
                        self._add_pair(d, b, ne, zero)
                    else:
                        return NotImplemented
            else:
                return NotImplemented # is_positive is not impl here
                for b, e in self.ops.items():
                    if not b.is_positive:
                        return NotImplemented
                    self._add_pair(d, b, e * other, zero)
            if len(d)==0:
                return self.algebra_one
            if len(d)==1:
                b, e = list (d.items())[0]
                if e == self.scalar_one:
                    return b
            return self.factors_type(d)
        return NotImplemented

    @check_rtype
    def normalize(self):

        terms = {}
        cls = type (self)
        zero = self.scalar_zero
        ZERO = self.algebra_zero
        one = self.scalar_one
        ONE = self.algebra_one
        number_type = self.number_type
        factors_type = self.factors_type
        terms_type = self.terms_type

        if not self.ops:
            return ONE

        factors = {}
        terms = {ONE:one}
        for b, e in self.ops.items ():
            if b==ONE or e==zero:
                continue

            p = b.power(e)
            if p is not NotImplemented:
                b, e = p, one
            
            if isinstance (e, number_type): ne = e.ops[0]
            else: ne = None
            
            if b==ZERO:
                assert ne > 0,repr((e, ne))
                return b

            if isinstance (ne, int) and isinstance (b, terms_type) and len(b.ops)==1:
                t, c = list(b.ops.items())[0]
                b, e = t ** e * c ** e, one
                ne = 1
                
            if isinstance (ne, int) and isinstance (b, factors_type):
                for b1, e1 in b.ops.items ():
                    #assert not isinstance (b1, terms_type), `b1, e1`
                    _e = e1 * e
                    if isinstance (_e, number_type): _ne = _e.ops[0]
                    else: _ne = None
                    if isinstance(_ne, int) and _ne > 0 and isinstance(b1, terms_type):
                        for i in range(_ne):
                            d = {}
                            for t1, c1 in terms.items():
                                for t2, c2 in b1.ops.items():
                                    t = t1 * t2
                                    c = c1 * c2
                                    if self.is_scalar_algebra and isinstance(t, number_type):
                                        t, c = ONE, t * c
                                    self._add_pair(d, t, c, zero)
                            terms = d
                    else:
                        if str(_e) == '1':
                            assert not isinstance(b1, terms_type),repr((b1, _e))
                        self._add_pair (factors, b1, _e, zero)
            elif isinstance (ne, int) and ne > 0 and isinstance (b, terms_type):
                for i in range (ne):
                    d = {}
                    for t1, c1 in terms.items ():
                        for t2, c2 in b.ops.items():
                            t = t1 * t2
                            c = c1 * c2
                            if self.is_scalar_algebra and isinstance(t, number_type):
                                t, c = ONE, t * c
                            self._add_pair(d, t, c, zero)
                    terms = d
            else:
                if str(e) == '1':
                    assert not isinstance(b, terms_type),repr((b, e))
                self._add_pair(factors, b, e, zero)

        d = {}
        f = self.algebra_one
        for b, e in factors.items ():
            if isinstance (e, number_type): ne = e.ops[0]
            else: ne = None
            r = b.power(e)
            if r is not NotImplemented:
                if isinstance(r, terms_type):
                    d1 = {}
                    for t1, c1 in terms.items ():
                        for t2, c2 in r.ops.items():
                            t = t1 * t2
                            c = c1 * c2
                            if self.is_scalar_algebra and isinstance(t, number_type): # I*I -> -1
                                t, c = ONE, t * c
                            self._add_pair(d1, t, c, zero)
                    terms = d1
                elif isinstance (r, self.scalar_type):
                    d1 = {}
                    for t1, c1 in terms.items ():
                        c = c1 * r
                        self._add_pair(d1, t1, c, zero)
                    terms = d1
                elif isinstance(r, factors_type):
                    for _b, _e in r.ops.items():
                        self._add_pair(d, _b, _e, zero)
                else:
                    assert not isinstance(r, BaseTerms),repr(r)
                    self._add_pair(d, r, one, zero)
            elif isinstance(ne, int) and ne > 0 and isinstance(b, terms_type):
                for i in range(ne):
                    d1 = {}
                    for t1, c1 in terms.items():
                        for t2, c2 in b.ops.items():
                            t = t1 * t2
                            c = c1 * c2
                            if self.is_scalar_algebra and isinstance(t, number_type):
                                t, c = ONE, t * c
                            self._add_pair(d1, t, c, zero)
                    terms = d1
            else:
                if str(e)=='1':
                    assert not isinstance(b, BaseTerms),repr((b,e))
                #assert not isinstance(b, BaseFactors) and isinstance(ne, int),`type(b), b, e`
                if b==self.algebra_one:
                    pass
                else:
                    self._add_pair(d, b, e, zero)
                
        factors = d
        
        if len(factors)==2:
            for _b, _e in factors.items():
                if isinstance(_b, BaseTerms) and str(_e) == '1':
                    print ('self=',self)
                    for b,e in factors.items():
                        print (b, repr(e))
                    raise
        
        if len (factors)==0:
            return terms_type(terms).normalize()

        if terms == {ONE: one}:
            if len (factors)==1:
                b, e = list(factors.items ())[0]
                if e == one:
                    return b
                return factors_type (factors)
            return factors_type(factors)
        if len(factors)==1:
            b, e = list(factors.items ())[0]
            if e == one:
                factors = b
            else:
                factors = factors_type(factors)
        else:
            factors = factors_type(factors)
        d = {}
        for t, c in terms.items ():
            t1 = t*factors
            if isinstance(t1, number_type):
                self._add_pair(d, one, t1*c, zero)
            else:
                self._add_pair(d, t1, c, zero)

                
        return terms_type(d).normalize()


class BaseComposite (BaseCalculus):
    
    def __init__ (self, func, *arguments):
        lst = []
        for a in arguments:
            if isinstance(a, number_types):
                a = self.number_type(a)
            elif isinstance(a, str):
                a = self.atom_type(a)
            assert isinstance(a, BaseCalculus),repr(type(a))
            lst.append(a)
        BaseCalculus.__init__ (self, (func,tuple(lst)))

    def _from_ops(self, ops):
        return type(self)(ops[0], *ops[1])
        
    def get_precedence(self, target='python'):
        if target=='tree':
            return 0
        return precedence['call']
        
    def tostr(self, target='python', parent=None, level=0):
        if target not in ['python']:
            return BaseCalculus.tostr(self, target=target, parent=parent, level=level)
        func, arguments = self.ops
        if hasattr(func, 'functostr'):
            return func.functostr(arguments, target=target, parent=parent, level=level)
        
        sfunc = func.tostr (target, parent=self, level = level + 1)
        if func.get_precedence (target) < self.get_precedence (target):
            sfunc = parens (sfunc, target)
        if target == 'python':
            return '{}({})'.format(sfunc, ', '.join([a.tostr(target, parent=self) for a in arguments]))
        return BaseCalculus.tostr(self, target=target, parent=parent, level=level)

    @check_rtype
    def normalize (self):
        func, arguments = self.ops
        if isinstance (func, self.number_type):
            return func
        if isinstance (func, self.terms_type):
            r = self.algebra_zero
            for t, c in func.ops.items ():
                r = r + t (*arguments) * c (*arguments)
            return r
        if isinstance(func, self.factors_type):
            r = self.algebra_one
            for b, e in func.ops.items ():
                r = r * b(*arguments) ** e(*arguments)
            return r
        if isinstance (func, self.composite_type):
            return func.ops[0] (*[g (*arguments) for g in func.ops[1]])
        if isinstance (func, BaseFunction):
            r = func.evaluate(*arguments)
            if r is not NotImplemented:
                return r
            func.set_props(self)
            return self
        if isinstance(func, (BaseAtom, BaseComponent)):
            return self
        return BaseCalculus.normalize(self)        


class BaseComponent(BaseCalculus):

    def __init__ (self, obj, *indices, **props):
        BaseCalculus.__init__ (self, (obj, indices))
        
    def _from_ops(self, ops):
        assert len(ops)==2,repr(len(ops))
        return type(self)(ops[0], *ops[1])
        
    def get_precedence(self, target='python'):
        if target =='python':
            return precedence['item']
        return BaseCalculus.get_precedence(self, target)
    
    def tostr(self, target='python', parent=None, level = 0):
        if target not in ['python']:
            return BaseCalculus.tostr(self, target=target, parent=parent, level=level)            
        A, indices = self.ops
        sA = A.tostr (target, parent=self, level=level + 1)
        if A.get_precedence (target) < self.get_precedence(target):
            sA = parens (sA, target)
        indices = [index.tostr(target, parent=self, level=level+1) for index in indices]
        if target == 'python':
            return '{}[{}]'.format (sA, ', '.join(indices))
        assert 0, repr (target)

    @check_rtype
    def normalize (self):
        A, indices = self.ops
        if isinstance (A, A.atom_type):
            return self
        if isinstance (A, A.terms_type):
            r = self.scalar_zero
            for t, c in A.ops.items ():
                r = r + t[indices] * c
            return r
        if isinstance(A, A.factors_type):
            r = self.scalar_one
            for b,e in A.ops.items ():
                r = r * b[indices] ** e
            return r
        if isinstance (A, A.composite_type):
            func, args = A.ops
            return func[indices] (*args)
        if isinstance (A, A.component_type):
            A1, indices1 = A.ops
            print (A1, indices, indices1)
            return A1[indices1 + indices]

        return BaseCalculus.normalize(self)


class BaseIndex(BaseAtom):

    pass

class BaseSlice(BaseAtom):

    def tostr(self, target='python', parent=None, level=0):
        if target == 'python':
            s = self.ops[0]
            r = ''
            if s.start is not None:
                r += str(s.start)
            if s.stop is not None:
                r += ':' + str(s.stop)
                if s.step is not None:
                    r += ':' + str(s.step)
            elif s.step is not None:
                r += '::' + str(s.step)
            return r
        return BaseAtom.tostr(self, target=target, parent=parent, level=level)


class BaseFloorDiv(BaseCalculus):

    def __init__ (self, op1, op2):
        BaseCalculus.__init__ (self, (op1, op2))

    def get_precedence (self, target='python'):
        if target=='tree':
            return 0
        return precedence['call']

        
    def tostr(self, target='python', parent=None, level = 0):
        if target in ['python']:
            snumer, sdenom = self.ops[0].tostr(target, parent=self, level=level+1), self.ops[1].tostr(target, parent=self, level=level+1)
            return f'floor({snumer}, {sdenom})'
        return BaseCalculus.tostr(self, target, parent=parent, level = level)
        
    @check_rtype
    def normalize(self):
        n, d = self.ops
        if n==d:
            return self.algebra_one
        if d==self.scalar_one:
            return n
        if isinstance(n, (self.atom_type, self.terms_type)):
            return self
        return BaseCalculus.normalize(self)
    
    @check_rtype
    def normalize (self):
        numer, denom = self.ops
        if numer == self.algebra_zero or denom==self.scalar_one:
            return numer
        if numer == denom:
            return self.algebra_one
        if numer == -denom:
            return -self.algebra_one
        if isinstance(numer, self.number_type):
            if isinstance(denom, self.number_type):
                return numer // denom
        return self
