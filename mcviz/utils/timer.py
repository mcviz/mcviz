from .. import log; log = log.getChild(__name__)

import logging

from contextlib import contextmanager
from time import time


timer_depth = 0

class Timer(object):
    def __init__(self, logger, level=logging.DEBUG, child=True):
        """
        Create a new timer object
        
        logger: log to write messages to
        level (default DEBUG): default level to write messages at
        child (defaul True): Create a child logger named "T".
        """
        self.logger = logger
        self.level = level
        if child and hasattr(logger, "getChild"):
            self.logger = logger.getChild("T")
    
    def __call__(self, what, level_override=None):
        level = level_override if level_override is not None else self.level
        log = self.logger.log
        
        @contextmanager
        def thunk():
            global timer_depth
            timer_depth += 1
            start = time()
            try:
                yield
            finally:
                elapsed = time() - start
                timer_depth -= 1
                log(level, "{depth} Took {0:.3f}s to {1}".format(
                           elapsed, what, depth="-" * timer_depth))
        
        return thunk()
