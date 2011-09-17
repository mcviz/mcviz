class FatalError(Exception):
    """
    Raised when a subsystem of MCViz has encountered an error
    it assumes is Fatal for the procedure, but does not warrant
    a full traceback.
    Must be accompanied by a FATAL log message.
    """

import sys

if not sys.version_info >= (2, 6):
    raise ImportError("mcviz is only compatible with python >= 2.6")

# Note: "from .module import" syntax is not used below 
# so that python<2.6 doesn't crash.

from mcviz.logger import log

from mcviz.graph import EventGraph, EventParseError
from mcviz.tools import Tool
from mcviz.workspace import GraphWorkspace
from mcviz.options import parse_options
from mcviz.main import main

