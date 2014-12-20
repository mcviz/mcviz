from .. import log; log = log.getChild(__name__)

from functools import wraps
from collections import defaultdict
from new import classobj

from mcviz.tools import Transform, Arg
from mcviz.graph import Summary


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
    

class NoKinks(Transform):
    """
    Remove vertices in the graph which have the same particle going in and out.
    
    These are, for example, recoil vertices in pythia events which are the
    particle recoiling against the whole event.
    """
    _name = "NoKinks"
    def __call__(self, graph_view):
        pdgid_changes = defaultdict(int)
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
                pdgid_changes[arg] += 1
                
        for change, count in sorted(pdgid_changes.iteritems()):
            arg = change + (count,)
            log.debug("kink removal: observed pdgid %s change to %s %i time(s)" % arg)

@Transform.decorate("Gluballs")
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

@Transform.decorate("Categorize")
def categorize(graph_view):
    """
    Categorize all final state particles with the same pdgid into one particle
    """
    for vertex in graph_view.vertices:
        final_state_particles = [p for p in vertex.outgoing if p.final_state]
        by_pdgid = {}
        for p in final_state_particles:
            by_pdgid.setdefault(p.pdgid, []).append(p)
        for k, particles in by_pdgid.iteritems():
            if len(particles) > 1:
                graph_view.summarize_vertices(p.end_vertex for p in particles).tag("category")
                summary = graph_view.summarize_particles(particles)
                summary.tag("category")
                summary.subscripts.append(("x%i" % len(particles), "under"))

@Transform.decorate("Chainmail")
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

_jet_algos = ("kt", "cambridge", "antikt", "genkt", "cambridge_for_passive", "genkt_for_passive", "ee_kt", "ee_genkt")
class Jets(Transform):
    _name = "Jets"
    _args = [Arg("algorithm", str, "Jet Algorithm", default="antikt", choices=_jet_algos),
             Arg("r", float, "Delta R for the Jet Algorithm", default=0.4),
             Arg("n_max", int, "Maximum number of jets to form", default=5),
             Arg("tracks", Arg.bool, "Only cluster charged particles", default=False)]
    def __call__(self, graph_view):
        from mcviz.jet import cluster_jets, JetAlgorithms
        from math import hypot
        track_jets = self.options["tracks"]
        if track_jets:
            raise Exception("Unimplemented!")
        def pselect(p):
            return p.final_state and not p.invisible and (p.charge != 0 if track_jets else True)
        final_state_particles = [p for p in graph_view.particles if pselect(p)]
        jets = cluster_jets(final_state_particles, getattr(JetAlgorithms, self.options["algorithm"]))
        print "Converted %i final state particles into %i jets" % (len(final_state_particles), len(jets))

        def pt(jet):
            return hypot(*jet.p[:2])
        for i, jet in enumerate(sorted(jets, key=pt, reverse=True)):
            print "Created jet: np=%2i, %r, %r" % (len(jet.particles), jet.p, jet.e)
            if i >= self.options["n_max"]:
                break
            jet_start_vertices = set(p.start_vertex for p in jet.particles)
            jet_end_vertices = set(p.end_vertex for p in jet.particles)
            vs_summary = graph_view.summarize_vertices(jet_start_vertices)
            ve_summary = graph_view.summarize_vertices(jet_end_vertices)
            p_summary = graph_view.summarize_particles(jet.particles)
            vs_summary.tag("jet")
            ve_summary.tag("jet")
            p_summary.tag("jet")
            p_summary.tag("jet_{0:d}".format(i))

@Transform.decorate("Clusters")
def contract_clusters(graph_view):
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
            
        cluster_ends = set(p.end_vertex for p in Walk.particles if p.final_state)
        vsummary = graph_view.summarize_vertices(cluster_ends)
        vsummary.tag("cluster")
        vsummary.cluster_nvertices = len(Walk.vertices)
        psummary = graph_view.summarize_particles(Walk.particles)
        psummary.tag("cluster")
        psummary.cluster_nparticles = len(Walk.particles)

@Transform.decorate("NoLoops")
def contract_loops(graph_view):
    """
    Drop loops from the graph
    """
    for particle in graph_view.particles:
        if particle.start_vertex == particle.end_vertex:
            graph_view.drop(particle)

@Transform.decorate("Pluck", args=[Arg("start", float, "start of range to keep", default=6),
                                   Arg("end", float, "end of range", default=0),
                                   Arg("param", str, "parameter of interest", default="pdgid"),
                                   Arg("keep_down", int, "max depth to descend from vertex", default=8),
                                   Arg("keep_up", int, "max depth to ascend from vertex", default=20)])
def pluck(graph_view, start, end, param, keep_down, keep_up):
    """
    Keep a specific vertex and particles travelling through it
    """
    
    if not end:
        end = start

    keep_particles = [] #particle for particle in graph_view.particles if abs(particle.pdgid) in keep]
    for particle in graph_view.particles:
        if particle.pdgid == -6: print(abs(getattr(particle, param)))
        if hasattr(particle, param):
            if start <= abs(getattr(particle, param)) <= end:
                keep_particles.append(particle)

    keep_objects = set()
    max_depth = keep_down
    def walker(vertex, depth):
        keep_objects.add(vertex)
        log.debug("vertex depth = %d" %depth)
        if depth > max_depth:
            return ()

    for p in keep_particles:
        max_depth = keep_down
        graph_view.walk(p.start_vertex, vertex_action=walker, particle_action=walker)
        max_depth = keep_up
        graph_view.walk(p.start_vertex, vertex_action=walker, particle_action=walker, ascend=True)
    
    for obj in list(graph_view.particles) + list(graph_view.vertices):
        if obj not in keep_objects:
            graph_view.drop(obj)

class Unsummarize(Transform):
    """
    Undo a summarization.
    Useful when used in combination with other transforms, 
    e.g. -v{gluballs,pluck,unsummarize}
    """
    _name = "Unsummarize"
    _args = [Arg("pno", int, "id of particle to unsummarize", default=None),
             Arg("vno", int, "id of vertex to unsummarize", default=None)]
    def __call__(self, graph_view):
        if self.options["pno"] is None and self.options["vno"] is None:
            retry = False
            for obj in list(graph_view.particles) + list(graph_view.vertices):
                if isinstance(obj, Summary):
                    obj.undo_summary()
        else:
            if not self.options["pno"] is None:
                for obj in list(graph_view.particles):
                    if isinstance(obj, Summary):
                        if self.options["pno"] in obj.particle_numbers:
                            vs, ve = obj.start_vertex, obj.end_vertex
                            if isinstance(vs, Summary):
                                vs.undo_summary()
                            if isinstance(ve, Summary):
                                ve.undo_summary()
                            obj.undo_summary()
            if not self.options["vno"] is None:
                for obj in list(graph_view.vertices):
                    if isinstance(obj, Summary):
                        if self.options["vno"] in obj.vertex_number:
                            obj.undo_summary()
    

@Transform.decorate("Shallow")
def shallow(graph_view, drop_depth=10):
    """
    Take only the first `drop_depth`
    """
    keep_objects = set()
    
    def walker(obj, depth):
        if depth <= drop_depth:
            keep_objects.add(obj)
    
    for vertex in graph_view.vertices:
        if vertex.initial:
            graph_view.walk(vertex, vertex_action=walker, particle_action=walker)
    
    for obj in list(graph_view.particles) + list(graph_view.vertices):
        if obj not in keep_objects:
            graph_view.drop(obj)
            
@Transform.decorate("MergeVertices")
def merge_vertices(graph_view):
    """
    Merge vertices by position. Required by some generators which don't connect 
    particles together.
    """
    vertices_by_position = defaultdict(list)
    for vertex in graph_view.vertices:
        if vertex.event_vertex.position:
            pos = tuple(float(v) for v in vertex.event_vertex.position)
            if pos != (0,0,0,0):
                vertices_by_position[pos].append(vertex)

    for pos, vertices in sorted(vertices_by_position.iteritems()):
        if len(vertices) >= 2:
            summary = graph_view.summarize_vertices(vertices)


class Cut(Transform):
    """
    Cut away particles from the 'outside' of the graph (default). When
    'final_state' is set to force, also cut on 'inner' particles.

    Instead of taking the value of the parameter of a particle
    directly, it can be checked against the value of its mother or
    daugther when the corresponding boolean flags are true. E.g. to
    draw all particles with at least one mother with pt > 5 GeV, do:

    '-tCut:cut=5:param=pt:mothers=True'

    'final_state' is automatically set to 'False' if 'mothers' or
    'daugthers' is True.

    """
    _name = "Cut"
    _args = [Arg("cut", float, "cut value", default=5),
             Arg("param", str, "parameter to cut on", default="pt"),
             Arg("abs", Arg.bool, "take abs value of param", default=True),
             Arg("reverse", Arg.bool, "reverse cut", default=False),
             Arg("exact", Arg.bool, "exact cut", default=False),
             Arg("mothers", Arg.bool, "cut on mother parameters", default=False),
             Arg("daughters", Arg.bool, "cut on daughter parameters", default=False),
             Arg("final_state", Arg.bool, "cut on final state particles only", default=True),
             ]

    def __call__(self, graph_view):
        cut = self.options["cut"]
        param = self.options["param"]
        take_abs = self.options["abs"]
        reverse = self.options["reverse"]
        exact = self.options["exact"]
        mothers = self.options["mothers"]
        daughters = self.options["daughters"]

        # when cutting on daugthers don't restrict on final state particles
        final_state = self.options["final_state"] if not daughters else False

        if final_state:
            particles = [p for p in graph_view.particles if p.final_state]
        else:
            particles = graph_view.particles

        passed_tag = "passed_cut"
        def cutter(p):

            reject = True

            if hasattr(p, param):
                value = getattr(p, param)
                if take_abs: value = abs(value)

                if exact:
                    reject = (value != cut)
                else:
                    reject = (value <= cut)

            return (reject if not reverse else not reject)

        keep = set()
        def mark(item, depth):
            keep.add(item)
            item.tag(passed_tag)

        particles_to_walk = set()

        for particle in particles:

            if mothers:
                loop_over = particle.mothers
            elif daughters:
                loop_over = particle.daughters
            else:
                loop_over = [particle]

            for p in loop_over:
                if not cutter(p):
                    particles_to_walk.add(p)
                    # also display the particle whose mother or daughter passed the cut
                    if mothers or daughters:
                        particles_to_walk.add(particle)

        for p in particles_to_walk:
            graph_view.walk(p, vertex_action=mark, particle_action=mark, ascend=True)

        def pruner(item, depth):
            if passed_tag in item.tags:
                return ()

        for vertex in graph_view.vertices:
            if passed_tag in vertex.tags:
                cut_daughters = [p for p in vertex.outgoing if passed_tag not in p.tags]
                #print vertex, cut_daughters
                if len(cut_daughters) > 0:
                    vsummary = graph_view.summarize_vertices(set(d.end_vertex for d in cut_daughters))
                    vsummary.tag("cut_summary")
                    psummary = graph_view.summarize_particles(set(cut_daughters))
                    psummary.tag("cut_summary")

        for p in graph_view.particles:
            if p in keep:
                continue

            if p.start_vertex in keep: # and not p.start_vertex.hadronization:
                # Don't discard
                continue

            graph_view.drop(p)

        #Clean out 'dangling' vertices
        for vertex in graph_view.vertices:
            if not vertex.incoming and not vertex.outgoing:
                graph_view.drop(vertex)
