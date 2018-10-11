
def _inttuple(obj):
    if isinstance(obj, (int, slice)):
        return (obj,)
    return tuple(obj)

def _allint(obj):
    for _o in obj:
        if not isinstance(_o, int):
            return False
    return True

class Stride(object):

    def __init__(self, start, step, size):
        self.start = start
        self.step = step
        self.size = size

    def __getitem__(self, item):
        if isinstance(item, slice):
            start, stop, step = item.start, item.stop, item.step

            new_start = self.start + self.step * start
            new_step = self.step * step
            last = self.start + self.step * (stop - 1)

class Shape(object):

    def __init__(self):
        pass

    def __getitem__(self, item):
        """Indexing operation

        Parameters
        ----------
        item : {int, slice, index}
          Specify index.

        Returns
        -------
        shape : Shape
          Shape of subarray.
        """
        return Item(self, item)
    
    def __call__(self, index):
        """Index-pointer mapping

        Parameters
        ----------
        index : tuple
          Specify index.
        Returns
        -------
        pointer: int
          Pointer value for given index.
        """
        return Apply(self, index)


class NDShape(Shape):
    """ Represents a shape of an N-dimensional array.
    """

    def __init__(self,
                 # Shape parameters
                 dims,
                 strides=None,
                 offset=0,
                 itemsize=1,
                 # Optional parameters used for calculating the default strides
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
        self.ndim = len(dims)
        self.dims = dims
        self.strides = strides
        self.offset = offset
        self.itemsize = itemsize

    def __repr__(self):
        return f'{type(self).__name__}({self.dims}, {self.strides}, {self.offset}, {self.itemsize})'

    def __getitem__(self, item):
        item = _inttuple(item)
        ndim = len(item)
        if ndim == self.ndim and _allint(item):
            # 0-dimensional array
            return type(cls)((), offset=self(item), itemsize=self.itemsize)
        elif ndim <= self.ndim:
            # a subarray
            pass
        else:
            # a broadcasted array
            pass
        raise NotImplementedError(repr(item))

    def __call__(self, index):
        """
        By definition, for N-dimensional array we have:
          pointer = offset + itemsize * sum(index[i] * strides[i], i=0..ndims-1)
        """
        index = _inttuple(index)
        ndim = len(index)
        if ndim == self.ndim:
            return self.offset + self.itemsize * sum(i*s for i,s in zip(index, self.strides))
        raise ValueError(f'incomplete index for {self.ndim}-dimensional array: {index}')
