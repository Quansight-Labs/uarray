import sys
import uarray
import pytest  # type: ignore

from .tests import example_helpers


def pytest_cmdline_preparse(args):
    try:
        import pytest_black  # type: ignore
    except ImportError:
        pass
    else:
        args.append("--black")
        print("uarray: Enabling pytest-black")


@pytest.fixture(autouse=True)
def add_namespaces(doctest_namespace):
    doctest_namespace["ua"] = uarray
    doctest_namespace["ex"] = example_helpers
