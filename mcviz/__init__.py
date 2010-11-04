
class MCVizParseError(Exception):
    """
    Raised when MCViz can't parse
    """
class FatalError(Exception):
    """
    Raised when a subsystem of MCViz has encountered an error
    it assumes is Fatal for the procedure, but does not warrant
    a full traceback.
    Must be accompanied by a FATAL log message.
    """

import transforms
import layouts
import styles
import painters
import annotations

from event_graph import EventGraph
from graph_workspace import GraphWorkspace

from options import parse_options
from main import main



