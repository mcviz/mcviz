from logging import getLogger; log = getLogger("mcviz.transforms.tagging")

from math import hypot

def tag(graph_view):
    tag_by_progenitors(graph_view)
    tag_by_hadronization_vertex(graph_view)
    tag_by_jet(graph_view)

def tag_by_progenitors(graph_view):
    """
    Tag descendants of the initial particles
    """
    for i, p in enumerate(graph_view.initial_particles):
        graph_view.tag(p, "descendant_of_p%i" % (i + 1), particles=True)

def tag_by_hadronization_vertex(graph_view):
    had_vertices = [v for v in graph_view.vertices if v.hadronization]
    for i, vertex in enumerate(had_vertices):
        graph_view.tag(vertex, "after_cluster", particles=True, vertices=True)
        graph_view.set(vertex, "cluster_index", lambda x: i, particles=True, vertices=True)
        
def tag_by_jet(graph_view):
    from mcviz.jet import cluster_jets, JetAlgorithms
    jets = cluster_jets([p for p in graph_view.particles if p.final_state], JetAlgorithms.antikt)
    tagged = []
    def pt(jet):
        return hypot(*jet.p[:2])
    for i, jet in enumerate(sorted(jets, key=pt, reverse=True)):
        if i >= 5:
            break
        log.info("Created jet: np=%2i, %r, %r", len(jet.particles), jet.p, jet.e)
        for particle in jet.particles:
            particle.tags.add("jet%i" % i)
            tagged.append(particle)
    log.info("Tagged %i particles in %i jets" % (len(tagged), min(5, len(jets))))
