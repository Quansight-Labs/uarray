from uarray import argument_extractor, all_of_type
from unumpy import ndarray

__all__ = ['svd']


def svd_rd(args, kwargs, arrays):
    out_args = arrays + args[1:]
    return out_args, kwargs


@argument_extractor(svd_rd)
@all_of_type(ndarray)
def svd(a, full_matrices=True, compute_uv=True, overwrite_a=False, check_finite=True, lapack_driver='gesdd'):
    return (a,)
