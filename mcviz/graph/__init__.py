"""
The Graph package of MCViz

Note to developers: Try to keep this package clean of imports
from all other packages except mcviz.utils

This way the loading order of packages will not grow too convoluted.

"""
class EventParseError(Exception):
    """
    Raised when an event file cannot be parsed
    """

from .graph import EventGraph
from .particle import Particle
from .vertex import Vertex

from .view import GraphView
from .view_object import Summary
from .view_particle import ViewParticle, ViewParticleSummary
from .view_vertex import ViewVertex, ViewVertexSummary
