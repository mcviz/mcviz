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

from .logger import log

from graph import EventGraph, EventParseError
from tools import Tool
from workspace import GraphWorkspace
from options import parse_options
from main import main

