import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_load_initial_conftests(early_config, parser, args):
    try:
        import pytest_black
    except ImportError:
        pass
    else:
        args.append("--black")
        print("uarray: Enabling pytest-black")
