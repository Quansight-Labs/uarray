from uarray.backend import wrap_dispatcher

__all__ = ['svd']


def svd_rd(args, kwargs, arrays):
    return svd.dispatcher(arrays[0], *args, **kwargs)


@wrap_dispatcher(svd_rd)
def svd(a, full_matrices=True, compute_uv=True, overwrite_a=False, check_finite=True, lapack_driver='gesdd'):
    return (a,)
