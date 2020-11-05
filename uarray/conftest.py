import sys
import uarray
import pytest  # type: ignore

from .tests import example_helpers


def pytest_cmdline_preparse(args):
    """
    Preparse pytest function

    Args:
    """
    try:
        import pytest_black  # type: ignore
    except ImportError:
        pass
    else:
        args.append("--black")
        print("uarray: Enabling pytest-black")


@pytest.fixture(autouse=True)
def add_namespaces(doctest_namespace):
    """
    Add the specified namespace to the namespace.

    Args:
        doctest_namespace: (str): write your description
    """
    doctest_namespace["ua"] = uarray
    doctest_namespace["ex"] = example_helpers
