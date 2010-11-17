

class FatalError(Exception):
    """
    Raised when a subsystem of MCViz has encountered an error
    it assumes is Fatal for the procedure, but does not warrant
    a full traceback.
    Must be accompanied by a FATAL log message.
    """

from utils import logger
from graph import EventGraph
from tools import Tool
from workspace import GraphWorkspace
from options import parse_options
from main import main

