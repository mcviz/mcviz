
def tag(graph_view):
    tag_by_progenitors(graph_view)
    tag_by_hadronization_vertex(graph_view)

def tag_by_progenitors(graph_view):
    """
    Tag descendants of the initial particles
    """
    for i, p in enumerate(graph_view.initial_particles):
        graph_view.tag_descendants(p, "descendant_of_p%i" % (i+1))

def tag_by_hadronization_vertex(graph_view):
    had_vertices = [v for v in graph_view.vertices if v.hadronization]
    for i, vertex in enumerate(had_vertices):
        for particle in vertex.outgoing:
            graph_view.tag_descendants(particle, "after_hadronization")
            graph_view.set_descendants(particle, "had_idx", lambda x : i)
