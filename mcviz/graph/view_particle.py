from itertools import chain

from .view_object import ViewObject, Summary

class ViewParticle(ViewObject):
    @property
    def mothers(self):
        return self.start_vertex.incoming

    @property
    def daughters(self):
        return self.end_vertex.outgoing

    @property
    def initial_state(self):
        "No mothers"
        return not bool(self.mothers)
    
    @property
    def final_state(self):
        "No daughters"
        return not bool(self.daughters)

    @property
    def pt(self):
        return (self.p[0]**2 + self.p[1]**2)**0.5

    #p.eta = -log(tan(atan2(p.pt, pz)/2.))
    @property
    def phi(self):
        return atan2(self.p[0], self.p[1])

    @property
    def colored(self):
        return self.color or self.anticolor

    @property
    def gluon(self):
        return self.pdgid == 21

    @property
    def photon(self):
        return self.pdgid == 22

    @property
    def boson(self):
        return (21 <= abs(self.pdgid) <= 25 or
                32 <= abs(self.pdgid) <= 37 or
                self.pdgid in [39, 5000039])

    @property
    def quark(self):
        return 1 <= abs(self.pdgid) <= 8
    
    @property
    def lepton(self):
        return 11 <= abs(self.pdgid) <= 18
        
    @property
    def descends_both(self):
        return self.descends(1) and self.descends(2)
    
    @property
    def descends_one(self):
        return ((self.descends(1) or self.descends(2)) 
                and not (self.descends(1) and self.descends(2)))
        
    def descends(self, n):
        assert n == 1 or n == 2, "Only supported for initial particles"
        return "descendant_of_p%i" % n in self.tags

    @property
    def reference(self):
        #ref = "P" + "_".join("%i" % no for no in self.particle_numbers)
        #return ref.replace("-","N") # replace for negative particle nr
        return "P%i" % self.order_number

class ViewParticleSingle(ViewParticle):
    """
    Represents a view of a single particle
    """
    def __init__(self, graph, particle_number):
        super(ViewParticle, self).__init__(graph)
        self.particle_number = particle_number
        self.graph.p_map[particle_number] = self
        self.p = self.event_particle.p
        self.e = self.event_particle.e
        self.m = self.event_particle.m
        self.pdgid = self.event_particle.pdgid
        self.color = self.event_particle.color
        self.anticolor = self.event_particle.anticolor
        self.status = self.event_particle.status
    
    def __repr__(self):
        args = self.pdgid, self.reference
        return "<ViewParticleSingle pdgid=%s ref='%s'>" % args
    
    @property
    def start_vertex(self):
        return self.graph.particle_start_vertex(self.particle_number)

    @property
    def end_vertex(self):
        return self.graph.particle_end_vertex(self.particle_number)

    @property
    def event_particle(self):
        return self.graph.event.particles[self.particle_number]

    @property
    def order_number(self):
        return self.particle_number
        
    @property
    def represented_numbers(self):
        return set([self.particle_number])

class ViewParticleSummary(ViewParticle, Summary):
    """
    Represents a view of a summary of particles ("cluster", "gluball")
    """
    def __init__(self, graph, summarized_particle_numbers):
        super(ViewParticleSummary, self).__init__(graph)
        self.particle_numbers = summarized_particle_numbers
        
        # For storing information before we did the summary (so we can invert it)
        self.orig_p_map, self.orig_v_map = {}, {}

        # represent all particles
        for p in self.particle_numbers:
            self.orig_p_map[p] = self.graph.p_map[p]
            self.graph.p_map[p] = self

        start_vnrs = (self.graph._start_vertex[p_nr] for p_nr in self.particle_numbers)
        end_vnrs = (self.graph._end_vertex[p_nr] for p_nr in self.particle_numbers)
        
        start_vertices = set(self.graph.numbers_to_vertices(start_vnrs))
        end_vertices = set(self.graph.numbers_to_vertices(end_vnrs))
        
        # internal vertex := vertex that has no non-summarized incoming and outgoings
        #                    AND is not final or initial
        def is_internal(vertex):
            me = set((self,))
            return (me == set(vertex.outgoing)) and (me == set(vertex.incoming))

        internal_vertices = [vn for vn in start_vertices & end_vertices if is_internal(vn)]
        start_vertices.difference_update(internal_vertices)
        end_vertices.difference_update(internal_vertices)

        for vertex in internal_vertices:
            for nr in vertex.represented_numbers:
                self.orig_v_map[nr] = self.graph.v_map[nr]
                self.graph.v_map[nr] = None
        
        assert len(start_vertices) == 1
        assert len(end_vertices) == 1

        self._start_vertices = sorted(chain(*[v.represented_numbers for v in start_vertices]))
        self._end_vertices = sorted(chain(*[v.represented_numbers for v in end_vertices]))

        # for the assertion:
        self.start_vertex
        self.end_vertex

        # Extract quantities from particles that go into the end vertex of this summary
        self.m = 0
        self.e = 0
        momentum = [0, 0, 0]
        color, anticolor = set(), set()
        pdgids = set()
        for v in self._end_vertices:
            for p in self.graph._incoming[v]:
                if p in self.particle_numbers:
                    ep = self.graph.event.particles[p]
                    for i in (0, 1, 2):
                        momentum[i] += ep.p[i]
                    self.e += self.graph.event.particles[p].e
                    color.add(ep.color)
                    anticolor.add(ep.anticolor)
                    pdgids.add(ep.pdgid)

        self.p = tuple(momentum)

        self.pdgid = min(pdgids)
        self.color, self.anticolor = max(color), max(anticolor)
        
        particles = [graph.event.particles[p] for p in self.particle_numbers]
        self.status = max(p.status for p in particles)
        
    @property
    def start_vertex(self):
        svs = self.graph.numbers_to_vertices(self._start_vertices)
        assert len(svs) == 1
        return svs.pop()

    @property
    def end_vertex(self):
        evs = self.graph.numbers_to_vertices(self._end_vertices)
        assert len(evs) == 1
        return evs.pop()
    
    @property
    def order_number(self):
        return min(self.particle_numbers)
        
    @property
    def represented_numbers(self):
        return self.particle_numbers
