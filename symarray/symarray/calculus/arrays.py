
from . import base, integers

scalars = integers # temporary

def check_shape(func):
    def wrapper (self, *arguments, **parameters):
        r = func(self, *arguments, **parameters)
        if r is NotImplemented:
            return r
        if isinstance(r, base.BasePairs):
            shape = None
            for k in r.ops:
                if shape is None:
                    shape = k.shape
                if shape is None or k.shape is None or shape == k.shape:
                    continue
                raise TypeError(f'mismatch of shapes: {shape} vs {k.shape}')
        return r
    wrapper.__name__ = 'check_shape@' + func.__name__
    return wrapper


class ArrayCalculus(base.BaseCalculus):
    
    @property
    def algebra_type (self):
        return ArrayCalculus
    @property
    def scalar_type (self):
        return scalars.IntegerCalculus # temporary
        #return scalars.ScalarCalculus
    @property
    def number_type (self):
        return integers.Int # temporary
    @property
    def index_type(self):
        return ArrayIndex
    @property
    def slice_type(self):
        return ArraySlice
    @property
    def exponent_type (self):
        return integers.IntegerCalculus
    @property
    def terms_type (self):
        return ArrayTerms
    @property
    def factors_type (self):
        return ArrayFactors
    @property
    def component_type(self):
        return ArrayComponent
    @property
    def algebra_zero(self):
        return AZERO
    @property
    def scalar_zero(self):
        return scalars.ZERO
    @property
    def number_zero(self):
        return integers.ZERO
    @property
    def algebra_one(self):
        return AONE
    @property
    def scalar_one(self):
        return scalars.ONE
    @property
    def number_one(self):
        return integers.ONE
    @property
    def is_scalar_algebra(self):
        return False
    @property
    def is_number_scalar(self):
        return False
    @property
    def atom_type(self):
        return ArrayAtom

    @property
    def shape(self):
        raise NotImplementedError(repr(type(self)))

    def __str__ (self):
        r = self.tostr(target = 'python')
        if 0 and self.shape is not None:
            s = str(self.shape)
            r = r + ' $ ' + s
        return r

    def power(self, other):
        if isinstance(other, integers.Int):
            n = other.ops[0]
            if n==0:
                return AONE
            if n==1:
                return self
        return NotImplemented
    
class ArrayAtom(ArrayCalculus, base.BaseAtom):

    def __init__(self, name, shape = None):
        """
        Parameters
        ----------
        name : str
          Specify name of a symbolic array.
        shape : {None, Shape}
          Specify shape of the array. When None, any shape is assumed.
        """
        self.ops = (name, shape)

    @property
    def shape(self):
        return self.ops[1]

    def tostr(self, target='python', parent=None, level = 0):
        r = base.BaseAtom.tostr(self, target=target, parent=parent, level=level)
        if self.shape is not None:
            r += self.shape.rank * "'"
        return r
    
class ArrayConstant(ArrayAtom):

    pass


class Array(ArrayAtom):

    pass


AZERO = ArrayConstant('<<0>>')
AONE = ArrayConstant('<<1>>')

class ArrayPairs(ArrayCalculus):

    def __getitem__(self, item):
        d = {}
        for k, v in self.ops.items():
            d[k[item]] = v
        return type(self)(d)
    
    @property
    def shape(self):
        for k in self.ops:
            if k.shape is not None:
                return k.shape


            
class ArrayTerms (base.BaseTerms, ArrayPairs):

    @check_shape
    @base.check_rtype
    def normalize(self):
        return base.BaseTerms.normalize(self)



class ArrayFactors(base.BaseFactors, ArrayPairs):

    @check_shape
    @base.check_rtype
    def normalize(self):
        return base.BaseFactors.normalize(self)

class ArrayComponent(ArrayCalculus, base.BaseComponent):

    @base.check_rtype
    def normalize(self):
        A, item = self.ops
        if isinstance(A, ArrayAtom) and A.shape is not None:
            item = tuple(map(lambda x: x.ops[0], item))
            shape = A.shape[item]
            return type(A)(A.ops[0], shape)
        return base.BaseComponent.normalize(self)

    @property
    def shape(self):
        return

class ArrayIndex(base.BaseIndex):

    pass

class ArraySlice(base.BaseSlice):

    pass
