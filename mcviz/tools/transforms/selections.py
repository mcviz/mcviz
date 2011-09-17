from .. import log; log = log.getChild(__name__)

from mcviz.tools import Transform, Arg
from mcviz.graph import Summary


@Transform.decorate("OnlyHard")
def only_hard(graph_view):
    """
    Select only the hard interaction
    """
    def is_hard(p):
        return 20 <= abs(p.status) < 30

    # first summarize all particles which are not hard
    # and also have no hard mothers
    for particle in graph_view.particles:
        if not is_hard(particle):
            if not any(is_hard(p) for p in particle.mothers):
                graph_view.summarize_vertices((particle.start_vertex, particle.end_vertex))

    # really drop all particles
    for vertex in graph_view.vertices:
        if vertex.final and not any(is_hard(p) for p in vertex.incoming):
            graph_view.drop(vertex)

    # re-summarize the leftovers
    for particle in graph_view.particles:
        if not is_hard(particle):
            graph_view.summarize_vertices((particle.start_vertex, particle.end_vertex))
