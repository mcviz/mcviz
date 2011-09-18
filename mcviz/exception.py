import sys
import traceback
import string
from inspect import getfile

from os import environ, getcwd, makedirs, symlink, unlink
from os.path import dirname, exists, expanduser, expandvars, isdir, join as pjoin
from sys import stderr


ISSUES_URL = "https://github.com/mcviz/mcviz/issues/new"
XDG_CACHE_HOME = pjoin(expanduser(environ.get("XDG_CACHE_HOME", "~/.cache")), "mcviz")

class FatalError(Exception):
    """
    Raised when a subsystem of MCViz has encountered an error
    it assumes is Fatal for the procedure, but does not warrant
    a full traceback.
    Must be accompanied by a FATAL log message.
    """


def ensure_cachedir():
    "Make sure that the user XDG_CACHE_HOME directory exists"
    if exists(XDG_CACHE_HOME):
        assert isdir(XDG_CACHE_HOME), ("{0} is not a directory! "
            "Please check it and delete it.").format(XDG_CACHE_HOME)
        return
    makedirs(XDG_CACHE_HOME)

def mcviz_excepthook(type, value, tb):
    """
    The MCViz exception hook:
    * Run the normal exception hook
    * Bail out if it's a FatalError or derivative, these are expected
    * Strip out MCViz base path
    * If we didn't strip out an mcviz path, stop - it's not mcviz.
    * Pretty print and save it to the user cache area
    """
    mcviz_excepthook.original_excepthook(type, value, tb)
    if isinstance(value, FatalError):
        return

    class sentinel:
        "A flag to check if we're inside mcviz"
        inside_mcviz = False

    mcviz_prefix = dirname(getfile(sys.modules[__name__])) + "/"
    def strip_prefix(s):
        "Remove the mcviz base path"
        if not s.startswith(mcviz_prefix):
            return s
        sentinel.inside_mcviz = True
        return s[len(mcviz_prefix):]
        
    def fixup_tb(frame):
        "Pretty-print the traceback"
        path, l, f, c = frame
        return "{path}:{line} {func_name} :: {content}".format(
            path=strip_prefix(path), line=l, func_name=f, content=c)
    
    tb = map(fixup_tb, traceback.extract_tb(tb))
    if not sentinel.inside_mcviz:
        # Not an mcviz crash, stop.
        return
    
    complete_tb = [
        "commandline: " + repr(sys.argv),
        "prefix: " + sys.prefix,
        "executable: " + sys.executable,
        "pwd: " + getcwd(),
    ] + tb + [""]
    
    complete_tb = "\n".join(complete_tb)
    
    ensure_cachedir()
    
    tb_ident = hex(abs(hash(tuple(tb[1:]))))[2:]
    except_file = "exception-{0}.txt".format(tb_ident)
    except_file = pjoin(XDG_CACHE_HOME, except_file)
    
    # No `with` statement here to be old python compatible
    fd = open(except_file, "w")
    fd.write(complete_tb)
    fd.close()
    
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
    mcviz_excepthook.original_excepthook = sys.excepthook
    sys.excepthook = mcviz_excepthook

