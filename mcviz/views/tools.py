from views import ViewParticleSummary

def contract(graph_view):
    pass

def remove_kinks(graph_view):
    for vertex in graph_view.vertices:
        if len(vertex.incoming) == 1 and len(vertex.outgoing) == 1:
            graph_view.summarize_particles(vertex.incoming | vertex.outgoing)


def gluballs(graph_view):
    retry = True
    while retry:
        retry = False
        for vertex in graph_view.vertices:
            if all(p.gluon for p in vertex.incoming | vertex.outgoing):
                vertices = set()
                def walker(vertex, depth):
                    if all(p.gluon for p in vertex.incoming | vertex.outgoing):
                        vertices.add(vertex)
                    else:
                        return () # empty tuple means: do not continue here
                graph_view.walk(vertex, vertex_action=walker)
                #graph_view.walk(vertex, vertex_action=walker, ascend=True)
                if len(vertices) > 1:
                    graph_view.summarize_vertices(vertices)
                    retry = True
                    break


