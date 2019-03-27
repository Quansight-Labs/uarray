import unumpy as np
import torch


def test_add():
    assert isinstance(np.add(torch.Tensor([5]), torch.Tensor([6])), torch.Tensor)
