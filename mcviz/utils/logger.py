import os
import logging
from contextlib import contextmanager


VERBOSE_LEVEL = 15
logging.addLevelName(VERBOSE_LEVEL, "VERBOSE")

# Rename critical to FATAL.
logging.addLevelName(logging.CRITICAL, "FATAL")

# The background is set with 40 plus the number of the color, and the foreground with 30
RED, YELLOW, BLUE, WHITE = 1, 3, 4, 7

# These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def insert_seqs(message):
    return message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)

COLORS = {
    'DEBUG'   : BLUE,
    'VERBOSE' : WHITE,
    'INFO'    : YELLOW,
    'WARNING' : YELLOW,
    'ERROR'   : RED,
    'FATAL'   : RED,
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            color_seq = COLOR_SEQ % (30 + COLORS[levelname])
            record.levelname = color_seq + levelname + RESET_SEQ
        return logging.Formatter.format(self, record)


LoggerClass = logging.getLoggerClass()
@logging.setLoggerClass
class ExtendedLogger(LoggerClass):
    def __init__(self, name):
        LoggerClass.__init__(self, name)
        self.__dict__.update(logging._levelNames)

    def verbose(self, *args):
        self.log(VERBOSE_LEVEL, *args)

    def fatal(self, *args):
        self.critical(*args)


def get_log_handler(singleton={}):
    """
    Return the STDOUT handler singleton used for all mcviz logging.
    """
    if "value" in singleton:
        return singleton["value"]
        
    handler = logging.StreamHandler()
    if os.isatty(handler.stream.fileno()):
        FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s"
        handler.setFormatter(ColoredFormatter(insert_seqs(FORMAT)))
    
    # Make the top level logger and make it as verbose as possible.
    # The log messages which make it to the screen are controlled by the handler
    log = logging.getLogger("mcviz")
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)

    singleton["value"] = handler
    return handler

@contextmanager
def log_level(level):
    """
    A log level context manager. Changes the log level for the duration.
    """
    handler = get_log_handler()
    old_level = handler.level
    try:
        handler.setLevel(level)
        yield
    finally:
        handler.setLevel(old_level)

def get_logger_level(quiet, verbose):
    if quiet:
        log_level = logging.WARNING
    elif not verbose:
        log_level = logging.INFO
    elif verbose == 1:
        log_level = VERBOSE_LEVEL
    elif verbose > 1:
        log_level = logging.DEBUG
        
    return log_level
