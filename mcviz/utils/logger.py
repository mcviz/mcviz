import logging

log_level = logging.INFO
VERBOSE_LEVEL = 15

#The background is set with 40 plus the number of the color, and the foreground with 30
RED, YELLOW, BLUE, WHITE = 1, 3, 4, 7

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    'DEBUG'   : BLUE,
    'VERBOSE' : WHITE,
    'INFO'    : WHITE,
    'WARNING' : YELLOW,
    'ERROR'   : RED,
    'FATAL'   : RED,
}

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color# Custom logger class with multiple destinations
        return logging.Formatter.format(self, record)

class ColoredLogger(logging.Logger):
    #FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
    FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s]  %(message)s"
    COLOR_FORMAT = formatter_message(FORMAT, True)

    def __init__(self, name, level):
        logging.Logger.__init__(self, name, level)
        color_formatter = ColoredFormatter(self.COLOR_FORMAT)
        console = logging.StreamHandler()
        console.setFormatter(color_formatter)
        self.addHandler(console)

    def verbose(self, message):
        self.log(VERBOSE_LEVEL, message)

    def fatal(self, message):
        self.critical(message)

all_loggers = []

def set_logger_level(quiet, verbose):
    global log_level
    logging.addLevelName(VERBOSE_LEVEL, "VERBOSE")
    logging.addLevelName(logging.CRITICAL, "FATAL")
    if quiet:
        log_level = logging.WARNING
    elif not verbose:
        log_level = logging.INFO
    elif verbose == 1:
        log_level = VERBOSE_LEVEL
    elif verbose > 1:
        log_level = logging.DEBUG

    for log in all_loggers:
        log.setLevel(log_level)

def get_logger(name):
    log = ColoredLogger(name, log_level)
    log.setLevel(log_level)
    all_loggers.append(log)
    return log
