import unumpy as np
import torch
import unumpy.pytorch_backend


def test_add():
    assert isinstance(np.add(torch.Tensor([5]), torch.Tensor([6])), torch.Tensor)


def test_asin():
    assert isinstance(np.arcsin(torch.Tensor([0.1])), torch.Tensor)
