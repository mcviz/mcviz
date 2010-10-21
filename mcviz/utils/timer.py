from contextlib import contextmanager
from time import time

from .logger import get_logger; log = get_logger("timing")

timer_depth = 0

@contextmanager
def timer(what, level=None):
    global timer_depth
    timer_depth += 1
    start = time()
    try: yield
    finally:
        timer_depth -= 1
        elapsed = time() - start
        depth = "-" * timer_depth
        msg = "%sit took %.3f seconds to %s" % (depth, elapsed, what)
        log.debug(msg) if level is None else log.log(level, msg)

