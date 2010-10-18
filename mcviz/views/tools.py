from views import ViewParticleSummary, Summary
from sys import stderr

def contract(graph_view):
    pass

def remove_kinks(graph_view):
    for vertex in graph_view.vertices:
        if len(vertex.incoming) == 1 and len(vertex.outgoing) == 1:
            if list(vertex.incoming)[0].pdgid == list(vertex.outgoing)[0].pdgid:
                to_summarize = vertex.incoming | vertex.outgoing
                summary = graph_view.summarize_particles(vertex.incoming | vertex.outgoing)
                summary.tag("kink")
                summary.kink_number = sum(getattr(x, "kink_number", 0) for x in to_summarize) + 1
            else:
                print >> stderr, "%s changing to %s" % (list(vertex.incoming)[0].pdgid, list(vertex.outgoing)[0].pdgid)
            

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
                if len(vertices) > 1:
                    summary = graph_view.summarize_vertices(vertices)
                    summary.tag("gluball")
                    nv = sum(getattr(x, "gluball_nvertices", 1) for x in vertices)
                    summary.gluball_nvertices = nv 
                    retry = True
                    break

def chainmail(graph_view):
    from ..tests.test_graph import graph_view_is_consistent
    retry = True
    while retry:
        retry = False
        for particle in graph_view.particles:
            candidates = particle.start_vertex.outgoing
            siblings = set(p for p in candidates 
                           if p.end_vertex == particle.end_vertex and 
                              p.pdgid == particle.pdgid)
            if len(siblings) > 1:
                summary = graph_view.summarize_particles(siblings)
                summary.tag("multiple")
                summary.multiple_count = sum(getattr(x, "multiple_count", 1) for x in siblings)
                retry = True
                break

def contract_jets(graph_view):
    for vertex in graph_view.vertices:
        if vertex.hadronization:
            class Walk:
                particles = set()
                vertices = set()
                failed = False
            def walker(particle, depth):
                if particle.end_vertex.hadronization:
                    Walk.failed = True
                Walk.particles.add(particle)
            graph_view.walk(vertex, particle_action=walker)
            if not Walk.failed:
                vsummary = graph_view.summarize_vertices(set(p.end_vertex for p in Walk.particles if p.final_state))
                vsummary.tag("jet")
                vsummary.jet_nvertices = len(Walk.vertices)
                psummary = graph_view.summarize_particles(Walk.particles)
                psummary.tag("jet")
                psummary.jet_nparticles = len(Walk.particles)

def contract_loops(graph_view):
    for particle in graph_view.particles:
        if particle.start_vertex == particle.end_vertex:
            graph_view.drop(particle)

def unsummarize(graph_view):
    """
    Undo a summarization.
    Useful when used in combination with other tools, 
    e.g. -v{gluballs,pluck,unsummarize}
    """
    retry = True
    while retry:
        retry = False
        for obj in list(graph_view.particles) + list(graph_view.vertices):
            if isinstance(obj, Summary):
                obj.undo_summary()
                retry = True
                # No break needed because we don't remove particles

