from views import ViewParticleSummary

def contract(graph_view):
    pass

def remove_kinks(graph_view):
    for vertex in graph_view.vertices:
        if len(vertex.incoming) == 1 and len(vertex.outgoing) == 1:
            graph_view.summarize_particles(vertex.incoming | vertex.outgoing)
