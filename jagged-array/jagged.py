import numbers


class Jagged(object):
    def __init__(self, jagged_array):
        if isinstance(jagged_array, Jagged):
            self.shape_array = [list(s) for s in jagged_array.shape_array]
            self.data_array = list(jagged_array.data_array)
            return

        self.shape_array, self.data_array = _convert(jagged_array)

    def __getitem__(self, item):
        if not isinstance(item, tuple):
            item = (item,)

        if not all(isinstance(i, numbers.Integral) for i in item):
            raise NotImplementedError("Right now, only integer indexing is supported.")

        if not all(i >= 0 for i in item):
            raise NotImplementedError("Right now, all indices must be positive.")

        if not len(item) == len(self.shape_array):
            raise NotImplementedError("Can only get scalar elements, not sub-arrays.")

        offset = 0
        for i, (idx, shape_ar) in enumerate(zip(item, self.shape_array)):
            if not idx < shape_ar[offset + 1] - shape_ar[offset]:
                raise IndexError("Invalid index.")
            offset = shape_ar[offset] + idx

        return self.data_array[offset]


def _convert(jagged_array):
    shape_array = []
    data_array = []

    _convert_to_canonical(jagged_array, shape_array, data_array)

    return shape_array, data_array


def _convert_to_canonical(jagged_array, shape_array, data_array, enforce_stacklevel=None, stacklevel=0):
    if not isinstance(jagged_array, list) and enforce_stacklevel is None:
        enforce_stacklevel = stacklevel

    if bool(stacklevel == enforce_stacklevel) == isinstance(jagged_array, list):
        raise ValueError("Inconsistent depth encountered.")

    if isinstance(jagged_array, list):
        if stacklevel >= len(shape_array):
            shape_array.append([0])

        shape_array[stacklevel].append(shape_array[stacklevel][-1] + len(jagged_array))

        for sub_array in jagged_array:
            _convert_to_canonical(
                sub_array, shape_array, data_array,
                enforce_stacklevel=enforce_stacklevel, stacklevel=stacklevel + 1
            )
    else:
        data_array.append(jagged_array)
