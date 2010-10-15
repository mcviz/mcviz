
def tag(graph_view):
    tag_by_progenitors(graph_view)
    tag_by_hadronization_vertex(graph_view)

def tag_by_progenitors(graph_view):
    """
    Tag descendants of the initial particles
    """
    for i, p in enumerate(graph_view.initial_particles):
        graph_view.tag(p, "descendant_of_p%i" % (i+1), particles=True)

def tag_by_hadronization_vertex(graph_view):
    had_vertices = [v for v in graph_view.vertices if v.hadronization]
    for i, vertex in enumerate(had_vertices):
        graph_view.tag(vertex, "after_hadronization", particles=True, vertices=True)
        graph_view.set(vertex, "had_idx", lambda x : i, particles=True)
