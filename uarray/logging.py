import logging


logger = logging.getLogger(__name__)


class IPythonHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        from IPython.display import display, HTML

        display(HTML(f"<h3>{record.msg}</h3>"), *record.args)


logger.addHandler(IPythonHandler())


def enable_logging():
    logger.setLevel("DEBUG")
