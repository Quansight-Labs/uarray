"""Symbolic shape.

"""
# Author: Pearu Peterson
# Created: October 2018

from .calculus import Integer, Int

integer_types = (int, Int, Integer)

def _inttuple(obj):
    if isinstance(obj, tuple) and len(obj)==1:
        obj = obj[0]
    if isinstance(obj, (slice,)+integer_types):
        return (obj,)
    return tuple(obj)


def _allint(obj):
    for _o in obj:
        if not isinstance(_o, integer_types):
            return False
    return True


class Shape(object):

    def __getitem__(self, item):
        """Get the shape of a subarray.

        Parameters
        ----------
        item : {int, slice, IntegerBase}
          Specify index.

        Returns
        -------
        shape : Shape
          Shape of a subarray.
        """
        raise NotImplementedError(repr(item))
    
    def __call__(self, *index):
        """Index-pointer mapping (the gamma function)

        Parameters
        ----------
        index : tuple
          Specify index as a tuple of (symbolic or numeric) integers.
        Returns
        -------
        pointer: int
          Pointer value for given index.
        """
        #return Apply(self, index)
        raise NotImplementedError(repr(index))

class NDShape(Shape):
    """ Represents a shape of a multi-dimensional array.
    """

    def __init__(self,
                 # Shape parameters
                 dims,
                 strides=None,
                 offset=0,
                 itemsize=1,
                 # Optional parameters used for calculating the
                 # default strides, not stored as attributes:
                 ordering='C'
    ):
        dims = _inttuple(dims)
        if len(dims)==0:
            strides = ()
        elif strides is None:
            strides = (1,)
            if ordering=='C':
                # C or row ordering
                for d in reversed(dims[:-1]):
                    strides = (strides[0]*d,) + strides
            elif ordering=='F':
                # Fortran or column ordering
                for d in dims[1:]:
                    strides = strides + (strides[-1]*d,)
            else:
                # TODO: mixed ordering
                raise NotImplementedError(repr(ordering))
        assert len(dims) == len(strides)
        self.ndim = len(dims)
        self.dims = dims
        self.strides = strides
        self.offset = offset
        self.itemsize = itemsize

    def __repr__(self):
        sdims = ', '.join(map(str, self.dims))
        sstrides = ', '.join(map(str, self.strides))
        return f'{type(self).__name__}(dims=({sdims}), strides=({sstrides}), offset={self.offset}, itemsize={self.itemsize})'

    def __getitem__(self, item):
        item = _inttuple(item)
        ndim = len(item)
        if ndim == self.ndim and _allint(item):
            # 0-dimensional array
            return type(self)((), offset=self(item), itemsize=self.itemsize)
        elif ndim <= self.ndim:
            dims = []
            strides = []
            offset = self.offset
            for i, d in enumerate(item):
                if isinstance(d, slice):
                    start, stop, step = d.start, d.stop, d.step
                    if start is None and stop is None and step is None:
                        dims.append(self.dims[i])
                        strides.append(self.strides[i])
                        continue
                    if start is None: start = 0
                    if step is None: step = 1
                    if stop is None: stop = self.dims[i]
                    dims.append((stop-start)//step)
                    strides.append(self.strides[i] * step)
                elif isinstance(d, integer_types):
                    start, stop, step = d, self.dims[i], 1
                else:
                    raise TypeError(f'expected integer or slice, got {type(d).__name__}')
                offset = offset + self.strides[i] * start * self.itemsize
            for i in range(len(item), self.ndim):
                dims.append(self.dims[i])
                strides.append(self.strides[i])
            return type(self)(dims, strides=strides, offset=offset, itemsize=self.itemsize)
        else:
            # a broadcasted array
            pass
        raise NotImplementedError(repr(item))

    def __call__(self, *index):
        """
        By definition, for N-dimensional array we have:
          pointer = offset + itemsize * sum(index[i] * strides[i], i=0..N-1)
        """
        index = _inttuple(index)
        ndim = len(index)
        if ndim == self.ndim:
            return self.offset + self.itemsize * sum(i*s for i,s in zip(index, self.strides))
        raise ValueError(f'incomplete index for {self.ndim}-dimensional array: {index}')
