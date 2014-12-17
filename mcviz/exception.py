"""Exceptions and handling"""
import sys
import traceback
from inspect import getfile

from os import environ, getcwd, makedirs, symlink, unlink
from os.path import dirname, exists, expanduser, isdir
from os.path import join as pjoin
from sys import stderr


ISSUES_URL = "https://github.com/mcviz/mcviz/issues/new"
XDG_CACHE_HOME = pjoin(expanduser(environ.get("XDG_CACHE_HOME", "~/.cache")),
                       "mcviz")

class FatalError(Exception):
    """
    Raised when a subsystem of MCViz has encountered an error
    it assumes is Fatal for the procedure, but does not warrant
    a full traceback.
    Must be accompanied by a FATAL log message.
    """

class EventParseError(Exception):
    """
    Raised when an event file cannot be parsed
    """

def ensure_cachedir():
    "Make sure that the user XDG_CACHE_HOME directory exists"
    if exists(XDG_CACHE_HOME):
        assert isdir(XDG_CACHE_HOME), ("{0} is not a directory! "
                                       "Please check it and delete it.")\
                                      .format(XDG_CACHE_HOME)
        return
    makedirs(XDG_CACHE_HOME)

def mcviz_excepthook(exception, value, trace):
    """
    The MCViz exception hook:
    * Run the normal exception hook
    * Bail out if it's a FatalError or derivative, these are expected
    * Strip out MCViz base path
    * If we didn't strip out an mcviz path, stop - it's not mcviz.
    * Pretty print and save it to the user cache area
    """
    mcviz_excepthook.original_excepthook(exception, value, trace)
    if isinstance(value, FatalError):
        return

    class Sentinel(object):
        "A flag to check if we're inside mcviz"
        inside_mcviz = False

    mcviz_prefix = dirname(getfile(sys.modules[__name__])) + "/"
    def strip_prefix(name):
        "Remove the mcviz base path"
        if not name.startswith(mcviz_prefix):
            return name
        Sentinel.inside_mcviz = True
        return name[len(mcviz_prefix):]

    def fixup_tb(frame):
        "Pretty-print the traceback"
        path, line, func, content = frame
        return "{path}:{line} {func_name} :: {content}".format(
            path=strip_prefix(path), line=line, func_name=func, content=content)

    trace = [fixup_tb(line) for line in traceback.extract_tb(trace)]
    if not Sentinel.inside_mcviz:
        # Not an mcviz crash, stop.
        return

    complete_tb = [
        "commandline: " + repr(sys.argv),
        "prefix: " + sys.prefix,
        "executable: " + sys.executable,
        "pwd: " + getcwd(),
    ] + trace + [""]

    complete_tb = "\n".join(complete_tb)

    ensure_cachedir()

    tb_ident = hex(abs(hash(tuple(trace[1:]))))[2:]
    except_file = "exception-{0}.txt".format(tb_ident)
    except_file = pjoin(XDG_CACHE_HOME, except_file)

    # No `with` statement here to be old python compatible
    handle = open(except_file, "w")
    handle.write(complete_tb)
    handle.close()

    # Symlink the latest exception
    last_exception = pjoin(XDG_CACHE_HOME, "last-exception.txt")
    if exists(last_exception):
        unlink(last_exception)
    symlink(except_file, last_exception)

    print >>stderr, "Exception in mcviz! Please report this at:"
    print >>stderr, " ", ISSUES_URL
    # TODO: Automated error reporting
    # print >>stderr, "or run {0} --report-exception".format(sys.argv[0])
    print >>stderr, "The content of the traceback is saved in:"
    print >>stderr, " ", except_file

def init_mcviz_exception_hook():
    """Insert hook"""
    mcviz_excepthook.original_excepthook = sys.excepthook
    sys.excepthook = mcviz_excepthook

