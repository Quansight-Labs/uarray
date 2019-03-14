from uarray.backend import Method

__all__ = ['svd']


def svd_fd(a, full_matrices=True, compute_uv=True, overwrite_a=False, check_finite=True, lapack_driver='gesdd'):
    return (a,)


def svd_rd(args, kwargs, arrays):
    def impl(a, **kwargs):
        return arrays, kwargs

    return impl(arrays[0], *args, **kwargs)


svd = Method(dispatcher=svd_fd, reverse_dispatcher=svd_rd)
