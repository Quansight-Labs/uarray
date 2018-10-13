
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
    def terms_type (self):
        return ArrayTerms
    @property
    def factors_type (self):
        return ArrayFactors

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
        if self.shape is not None:
            s = str(self.shape)
            r = r + ' $ ' + s
        return r
    
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

    def __getitem__(self, item):
        if self.shape is None:
            return self
        shape = self.shape[item]
        return type(self)(self.ops[0], shape)


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
