import pytest
import ulinalg as ula
import ulinalg.torch_backend


torch = pytest.importorskip('torch')


def test_svd():
    arr = torch.eye(5)
    assert all(isinstance(obj, torch.Tensor) for obj in ula.svd(arr))


def test_svd2():
    arr = torch.eye(5)
    assert isinstance(ula.svd(arr, compute_uv=False), torch.Tensor)
