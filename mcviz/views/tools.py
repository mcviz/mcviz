from views import ViewParticleSummary

def contract(graph_view):
    pass

def remove_kinks(graph_view):
    for vertex in graph_view.vertices:
        if len(vertex.incoming) == 1 and len(vertex.outgoing) == 1:
            graph_view.summarize_particles(vertex.incoming + vertex.outgoing)
            

def gluballs(graph_view):
    retry = True
    while retry:
        retry = False
        for vertex in graph_view.vertices:
            if all(p.gluon for p in vertex.incoming + vertex.outgoing):
                vertices = set()
                def walker(vertex, depth):
                    if all(p.gluon for p in vertex.incoming + vertex.outgoing):
                        vertices.add(vertex)
                    else:
                        return () # empty tuple means: do not continue here
                graph_view.walk(vertex, vertex_action=walker)
                #graph_view.walk(vertex, vertex_action=walker, ascend=True)
                if len(vertices) > 1:
                    graph_view.summarize_vertices(vertices)
                    retry = True
                    break

def chainmail(graph_view):
    from ..tests.test_graph import graph_view_is_consistent
    retry = True
    while retry:
        retry = False
        for particle in graph_view.particles:
            candidates = particle.start_vertex.outgoing
            siblings = set(p for p in candidates if p.end_vertex == particle.end_vertex)
            if len(siblings) > 1:
                graph_view.summarize_particles(siblings)
                retry = True
                break

