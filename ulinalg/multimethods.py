from uarray import wrap_dispatcher

__all__ = ['svd']


def svd_rd(args, kwargs, arrays):
    out_args = arrays + args[1:]
    return out_args, kwargs


@wrap_dispatcher(svd_rd)
def svd(a, full_matrices=True, compute_uv=True, overwrite_a=False, check_finite=True, lapack_driver='gesdd'):
    return (a,)
