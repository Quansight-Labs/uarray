import sys


def pytest_cmdline_preparse(args):
    if sys.version_info >= (3, 6):
        args.append("--black")
        args.append("--mypy")
