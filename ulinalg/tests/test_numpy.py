import pytest
import ulinalg as ula

np = pytest.importorskip('numpy')


def test_svd():
    arr = np.eye(5)
    assert all(isinstance(obj, np.ndarray) for obj in ula.svd(arr))


def test_svd2():
    arr = np.eye(5)
    assert isinstance(ula.svd(arr, compute_uv=False), np.ndarray)
