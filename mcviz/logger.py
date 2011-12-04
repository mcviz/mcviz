
import os
import logging

from contextlib import contextmanager

FORCE_COLOR = "FORCE_COLOR" in os.environ
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

def remove_seqs(message):
    return message.replace("$RESET", "").replace("$BOLD", "")

COLORS = {
    'DEBUG'   : BLUE,
    'VERBOSE' : WHITE,
    'INFO'    : YELLOW,
    'WARNING' : YELLOW,
    'ERROR'   : RED,
    'FATAL'   : RED,
}


class MCVizFormatter(logging.Formatter):

    def mcviz_strip(self, record):
        if record.name.startswith("mcviz."):
            # If we're running as mcviz, omit the "mcviz" name, which doesn't
            # introduce any additional information
            record.name = record.name[len("mcviz."):]

    def format(self, record):
        self.mcviz_strip(record)
        return logging.Formatter.format(self, record)
        
class ColoredFormatter(MCVizFormatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        self.mcviz_strip(record)
            
        if self.use_color and levelname in COLORS:
            color_seq = COLOR_SEQ % (30 + COLORS[levelname])
            record.levelname = color_seq + levelname + RESET_SEQ
        return logging.Formatter.format(self, record)


LoggerClass = logging.getLoggerClass()
class ExtendedLogger(LoggerClass):
    """
    The ExtendedLogger only gets used by loggers created as children of the 
    mcviz logger, `log`, at module level in logger.py.
    """
    
    def __init__(self, name):
        LoggerClass.__init__(self, name)

    def getChild(self, suffix):
        """
        Taken from CPython 2.7, modified to remove duplicate prefix and suffixes
        """
        if self.root is not self:
            if suffix.startswith(self.name + "."):
                # Remove duplicate prefix
                suffix = suffix[len(self.name + "."):]
                
                suf_parts = suffix.split(".")
                if len(suf_parts) > 1 and suf_parts[-1] == suf_parts[-2]:
                    # If we have a submodule's name equal to the parent's name,
                    # omit it.
                    suffix = ".".join(suf_parts[:-1])
                    
            suffix = '.'.join((self.name, suffix))
            
        return self.manager.getLogger(suffix)

    def verbose(self, *args):
        self.log(VERBOSE_LEVEL, *args)

    def fatal(self, *args):
        self.critical(*args)
        
    def __repr__(self):
        return "<MCViz logger {0}>".format(self.name)

# Give the ExtendedLogger class the log level constants
for key, value in logging._levelNames.iteritems():
    if not isinstance(key, basestring): continue
    setattr(ExtendedLogger, key, value)

class MCVizLogManager(logging.Manager):
    """
    Workaround for CPython 2.6
    """
    def getLogger(self, name):
        """
        Fetch an ordinary logger and switch out its class
        """
        logger = logging.Manager.getLogger(self, name)
        logger.__class__ = ExtendedLogger
        return logger

# Reference: 
# http://hg.python.org/cpython/file/5395f96588d4/Lib/logging/__init__.py#l979

log_manager = MCVizLogManager(logging.getLogger())
log = log_manager.getLogger("mcviz")

def get_log_handler(singleton={}):
    """
    Return the STDOUT handler singleton used for all mcviz logging.
    """
    if "value" in singleton:
        return singleton["value"]
        
    handler = logging.StreamHandler()
    FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s"
    if os.isatty(handler.stream.fileno()) or FORCE_COLOR:
        handler.setFormatter(ColoredFormatter(insert_seqs(FORMAT)))
    else:
        handler.setFormatter(MCVizFormatter(remove_seqs(FORMAT)))
    
    # Make the top level logger and make it as verbose as possible.
    # The log messages which make it to the screen are controlled by the handler
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
