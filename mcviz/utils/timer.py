from contextlib import contextmanager
from time import time

from .logger import get_logger; log = get_logger("timing")

@contextmanager
def timer(what):
    start = time()
    try: yield
    finally:
        elapsed = time() - start
        log.verbose("Took %.3f to %s" % (elapsed, what))



