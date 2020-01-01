import sys


def pytest_cmdline_preparse(args):
    try:
        import pytest_black
    except ImportError:
        pass
    else:
        args.append("--black")
        print("uarray: Enabling pytest-black")

    try:
        import pytest_mypy
    except ImportError:
        pass
    else:
        args.append("--mypy")
        print("uarray: Enabling pytest-mypy")
