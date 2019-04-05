import pytest
import ulinalg as ula
import uarray as ua
from ulinalg.numpy_backend import NumpyBackend

np = pytest.importorskip('numpy')


def test_svd():
    arr = np.eye(5)
    assert all(isinstance(obj, np.ndarray) for obj in ula.svd(arr))


def test_svd2():
    arr = np.eye(5)
    assert isinstance(ula.svd(arr, compute_uv=False), np.ndarray)


def test_coercion():
    torch = pytest.importorskip('torch')
    arr = torch.eye(5)
    with ua.set_backend(ula.numpy_backend.NumpyBackend, coerce=True):
        assert isinstance(ula.svd(arr, compute_uv=False), np.ndarray)

    assert isinstance(ula.svd(arr, compute_uv=False), torch.Tensor)


def test_coercion_optional():
    my_list = [list(range(5))] * 5

    class A:
        def __getitem__(self, key):
            return my_list[key]

        def __len__(self):
            return len(my_list)

    arr = A()

    with ua.set_backend(NumpyBackend, coerce=None):
        assert isinstance(ula.svd(arr, compute_uv=False), np.ndarray)

    with pytest.raises(TypeError):
        ula.svd(arr, compute_uv=False)
