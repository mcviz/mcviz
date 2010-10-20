from contextlib import contextmanager
from time import time

from .logger import get_logger; log = get_logger("timing")

@contextmanager
def timer(what, level=None):
    start = time()
    try: yield
    finally:
        elapsed = time() - start
        msg = "it took %.3f seconds to %s" % (elapsed, what)
        log.debug(msg) if level is None else log.log(level, msg)

