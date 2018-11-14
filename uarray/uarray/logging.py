import logging

from IPython.display import display, HTML

logger = logging.getLogger(__name__)


class IPythonHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        display(HTML(f"<h3>{record.msg}</h3>"), *record.args)


logger.addHandler(IPythonHandler())


def enable_logging():
    logger.setLevel("DEBUG")
