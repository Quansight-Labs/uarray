import sys


def pytest_cmdline_preparse(args):
    try:
        import pytest_black  # type: ignore
    except ImportError:
        pass
    else:
        args.append("--black")
        print("uarray: Enabling pytest-black")

    try:
        import pytest_mypy  # type: ignore
    except ImportError:
        pass
    else:
        args.append("--mypy")
        print("uarray: Enabling pytest-mypy")
