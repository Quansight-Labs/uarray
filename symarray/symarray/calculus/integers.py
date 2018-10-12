
from fractions import Fraction
from . import base

class IntegerCalculus(base.BaseCalculus):

    number_types = (int,)
    
    @property
    def algebra_type (self):
        return IntegerCalculus
    @property
    def scalar_type (self):
        return Int
    @property
    def number_type (self):
        return Int
    @property
    def terms_type (self):
        return IntegerTerms
    @property
    def factors_type (self):
        return IntegerFactors
    @property
    def composite_type (self):
        return IntegerComposite

    @property
    def algebra_zero(self):
        return ZERO
    @property
    def scalar_zero(self):
        return ZERO
    @property
    def number_zero(self):
        return ZERO
    @property
    def algebra_one(self):
        return ONE
    @property
    def scalar_one(self):
        return ONE
    @property
    def number_one(self):
        return ONE
    @property
    def is_scalar_algebra(self):
        return True
    @property
    def is_number_scalar(self):
        return True
    @property
    def atom_type(self):
        return IntegerAtom

class IntegerAtom (IntegerCalculus, base.BaseAtom):

    def normalize(self):
        return self

class Int(IntegerAtom): # constant integer
    
    @property
    def precedence (self):
        if self.ops[0] < 0:
            return 41
        return 100

    def __neg__(self):
        return Int(-self.ops[0])
    def __add__(self, other):
        if isinstance (other, Int):
            return Int (self.ops[0] + other.ops[0])
        if isinstance (other, self.number_types):
            return Int (self.ops[0] + other)
        return NotImplemented
    __radd__ = __add__
    def __sub__(self, other):
        if isinstance (other, Int):
            return Int (self.ops[0] - other.ops[0])
        if isinstance (other, self.number_types):
            return Int (self.ops[0] - other)
        return NotImplemented
    def __mul__(self, other):
        if isinstance (other, Int):
            return Int (self.ops[0] * other.ops[0])
        if isinstance (other, self.number_types):
            return Int (self.ops[0] * other)
        return NotImplemented
    def __rmul__ (self, other):
        if isinstance (other, self.number_types):
            return Int (self.ops[0] * other)
        return NotImplemented
    def __div__(self, other):
        if isinstance (other, Int):
            if isinstance (other.ops[0], int):
                return Int (self.ops[0] * Fraction(1, other.ops[0]))
            return Int (self.ops[0] / other.ops[0])
        if isinstance (other, self.number_types):
            if isinstance (other, int):
                other = Fraction(other, 1)
            return Int (self.ops[0] / other)
        if isinstance (other, self.algebra_type):
            pass
        return NotImplemented
    __truediv__ = __div__

    def __pow__(self, other):
        if isinstance (other, self.number_types):
            other = Int(other)
        r = self.power(other)
        if r is not NotImplemented:
            return r
        if isinstance (other, self.algebra_type):
            return self.factors_type({self: other}).normalize ()
        return NotImplemented

    def power(self, other):
        if isinstance(other, Int):
            b, e = self.ops[0], other.ops[0]
            if b==1:
                return self
            if isinstance(e, int):
                if e>=0 or isinstance(b, Fraction):
                    return Int(b ** e)
                if isinstance(b, int):
                    return Int(Fraction(b, 1) ** e)
            return self.factors_type ({self:other})
        return NotImplemented

class Integer(IntegerAtom): # integer symbol

    pass

class IntegerTerms (base.BaseTerms, IntegerCalculus):

    pass

class IntegerFactors(base.BaseFactors, IntegerCalculus):

    pass


class IntegerComposite (base.BaseComposite, IntegerCalculus):

    pass

ONE = Int(1)
ZERO = Int(0)
