import platform
import sys

collect_ignore = ['build_docs.py', '__main__.py']


def pytest_cmdline_preparse(args):
    """
    # run tests on multiple processes if pytest-xdist plugin is available
    # unfortunately it does not work with codecov, and does not collect any tests
    import sys
    if "xdist" in sys.modules:  # pytest-xdist plugin
        import multiprocessing

        num = int(max(multiprocessing.cpu_count() / 2, 1))
        args[:] = ["-n", str(num)] + args
    """

    # add mypy option if not pypy - so mypy will be called with setup.py install test
    # add mypy only on 3.x versions
    # mypy does not find some functions on python 3.6
    if platform.python_implementation() != "PyPy" and sys.version_info >= (3, 5) and sys.version_info != (3, 6):
        args[:] = ["--mypy"] + args

    # for python 3.x use --pycodestyle, for python 2.7 use --pep8
    if sys.version_info <= (3, 5):
        args[:] = ["--pep8"] + args
    else:
        args[:] = ["--pycodestyle"] + args
