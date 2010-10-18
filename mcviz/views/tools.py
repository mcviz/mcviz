from views import ViewParticleSummary, Summary
from sys import stderr
from functools import wraps

def retrying(func):
    """
    If the decorated function raises retry, run it again, else, fallthrough.
    The Retry object is passed through as a kwarg.
    """
    class Retry(Exception): pass
    @wraps(func)
    def wrapped(*args, **kwargs):
        kwargs["Retry"] = Retry()
        while True:
            try:
                return func(*args, **kwargs)
            except Retry:
                pass
            else:
                break
    return wrapped

def remove_kinks(graph_view):
    """
    Remove vertices in the graph which have the same particle going in and out.
    
    These are, for example, recoil vertices in pythia events which are the
    particle recoiling against the whole event.
    """
    for vertex in graph_view.vertices:
        if not (len(vertex.incoming) == 1 and len(vertex.outgoing) == 1):
            # Only consider particles with one particle entering and exiting
            continue
            
        if list(vertex.incoming)[0].pdgid == list(vertex.outgoing)[0].pdgid:
            summary = graph_view.summarize_particles(vertex.through)
            kinks = (getattr(x, "kink_number", 0) for x in vertex.through)
            summary.kink_number = sum(kinks) + 1
            summary.tag("kink")
        else:
            # Oops, we have a particle changing pdgid on the way through.. 
            # It could be a graph inconsistency or it could be a K meson. Warn.
            arg = list(vertex.incoming)[0].pdgid, list(vertex.outgoing)[0].pdgid
            print >> stderr, "%s changing to %s" % arg

@retrying
def gluballs(graph_view, Retry):
    """
    Remove gluon self-interaction, replacing them all with one glu-vertex.
    """
    for vertex in graph_view.vertices:
        if not all(p.gluon for p in vertex.through):
            continue
            
        vertices = set()
        def walker(vertex, depth):
            if not all(p.gluon for p in vertex.through):
                return () # empty tuple means: do not continue here
            vertices.add(vertex)
                
        graph_view.walk(vertex, vertex_action=walker)
        if len(vertices) > 1:
            summary = graph_view.summarize_vertices(vertices)
            summary.tag("gluball")
            nv = sum(getattr(x, "gluball_nvertices", 1) for x in vertices)
            summary.gluball_nvertices = nv
            raise Retry

@retrying
def chainmail(graph_view, Retry):
    """
    So named because lots of gluons all going the same way looks like chainmail.
    
    This function removes sibling particles of the same type.
    """
    for particle in graph_view.particles:
        candidates = particle.start_vertex.outgoing
        siblings = set(p for p in candidates 
                       if p.end_vertex == particle.end_vertex and 
                          p.pdgid == particle.pdgid)
        if len(siblings) > 1:
            summary = graph_view.summarize_particles(siblings)
            summary.tag("multiple")
            summary.multiple_count = sum(getattr(x, "multiple_count", 1) for x in siblings)
            raise Retry

def contract_jets(graph_view):
    """
    Summarize all particles and vertices which decend from hadronization 
    vertices and tag them.
    """
    for vertex in graph_view.vertices:
        if not vertex.hadronization:
            continue
        
        class Walk:
            particles = set()
            vertices = set()
            failed = False
            
        def walker(particle, depth):
            if particle.end_vertex.hadronization:
                Walk.failed = True
            Walk.particles.add(particle)
            
        graph_view.walk(vertex, particle_action=walker)
        
        if Walk.failed:
            continue
            
        jet_ends = set(p.end_vertex for p in Walk.particles if p.final_state)
        vsummary = graph_view.summarize_vertices(jet_ends)
        vsummary.tag("jet")
        vsummary.jet_nvertices = len(Walk.vertices)
        psummary = graph_view.summarize_particles(Walk.particles)
        psummary.tag("jet")
        psummary.jet_nparticles = len(Walk.particles)

def contract_loops(graph_view):
    """
    Drop loops from the graph
    """
    for particle in graph_view.particles:
        if particle.start_vertex == particle.end_vertex:
            graph_view.drop(particle)

def pluck(graph_view, vno_keep=3):
    """
    Keep a specific vertex and particles travelling through it
    """
    
    keep_objects = set()
    keep_vertex = graph_view.v_map[vno_keep]
            
    def walker(vertex, depth):
        keep_objects.add(vertex)
        if depth > 3:
            return ()
        
    graph_view.walk(keep_vertex, vertex_action=walker, particle_action=walker)    
    graph_view.walk(keep_vertex, vertex_action=walker, particle_action=walker, ascend=True)
    
    for obj in list(graph_view.particles) + list(graph_view.vertices):
        if obj not in keep_objects:
            graph_view.drop(obj)

@retrying
def unsummarize(graph_view, Retry):
    """
    Undo a summarization.
    Useful when used in combination with other tools, 
    e.g. -v{gluballs,pluck,unsummarize}
    """
    retry = False
    for obj in list(graph_view.particles) + list(graph_view.vertices):
        if isinstance(obj, Summary):
            obj.undo_summary()
            retry = True
    
    if retry:
        raise Retry

