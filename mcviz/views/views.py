#! /usr/bin/env python

from __future__ import with_statement

from sys import argv, stderr
from itertools import takewhile

from ..utils import walk

from logging import getLogger; log = getLogger("event_graph")
import logging as L


class GraphView(object):
    def __init__(self, event_graph):
        self.event = event_graph

        # create central maps (define structure)
        self.v_map, self.p_map = {}, {}
        for v in event_graph.vertices.keys():
            ViewVertexSingle(self, v)
        for p in event_graph.particles.keys():
            ViewParticleSingle(self, p)

        self.init_cache()

    def init_cache(self):
        """ cache input graph topology """
        self._start_vertex, self._end_vertex = {}, {}
        for nr in self.p_map.keys():
            p = self.event.particles[nr]
            if p.vertex_in:
                self._start_vertex[nr] = p.vertex_in.vno if p.vertex_in else None
            if p.vertex_out:
                self._end_vertex[nr] = p.vertex_out.vno if p.vertex_out else None

        self._incoming, self._outgoing = {}, {}
        self._initial_particles = set()
        for nr in self.v_map.keys():
            v = self.event.vertices[nr]
            self._incoming[nr] = set(p.no for p in self.event.vertices[nr].incoming)
            self._outgoing[nr] = set(p.no for p in self.event.vertices[nr].outgoing)
            if not self._incoming[nr]:
                self._initial_particles.update(self._outgoing[nr])

    def numbers_to_particles(self, numbers):
        particles = set(self.p_map[nr] for nr in numbers)
        particles.discard(None)
        return particles

    def numbers_to_vertices(self, numbers):
        vertices = set(self.v_map[nr] for nr in numbers)
        vertices.discard(None)
        return vertices

    def particle_start_vertex(self, particle_number):
        start_vertex = self._start_vertex[particle_number]
        return None if start_vertex is None else self.v_map[start_vertex]

    def particle_end_vertex(self, particle_number):
        end_vertex = self._end_vertex[particle_number]
        return None if end_vertex is None else self.v_map[end_vertex]

    def vertex_incoming_particles(self, vertex_number):
        return self.numbers_to_particles(self._incoming[vertex_number])

    def vertex_outgoing_particles(self, vertex_number):
        return self.numbers_to_particles(self._outgoing[vertex_number])

    @property
    def vertices(self):
        return self.numbers_to_vertices(self.v_map.keys())

    @property
    def particles(self):
        return self.numbers_to_particles(self.p_map.keys())

    @property
    def initial_particles(self):
        return self.numbers_to_particles(self._initial_particles)

    def summarize_particles(self, particles):
        elementary_particles = []
        for p in particles:
            if isinstance(p, ViewParticleSummary):
                elementary_particles.extend(p.particle_numbers)
            else:
                elementary_particles.append(p.particle_number)
        ViewParticleSummary(self, elementary_particles)

    def summarize_vertices(self, vertices):
        elementary_vertices = []
        for p in vertices:
            if isinstance(p, ViewVertexSummary):
                elementary_particles.extend(p.vertex_numbers)
            else:
                elementary_particles.append(p.vertex_number)
        ViewParticleSummary(self, elementary_vertices)

    def walk_descendants(self, obj, 
            walk_action=lambda p, d: None, loop_action=lambda p, d: None):
        if isinstance(obj, ViewParticle):
            step = lambda p : p.daughters
        elif isinstance(obj, ViewVertex):
            step = lambda v : [p.end_vertex for p in v.outgoing]
        return walk(obj, step, walk_action, loop_action)
    
    def walk_ascendants(self, obj, 
            walk_action=lambda p, d: None, loop_action=lambda p, d: None):
        if isinstance(obj, ViewParticle):
            step = lambda p : p.mothers
        elif isinstance(obj, ViewVertex):
            step = lambda v : [p.start_vertex for p in v.incoming]
        return walk(particle, step, walk_action, loop_action)
    
    def tag_descendants(self, obj, tag): 
        return self.walk_descendants(obj, ViewObject.tagger(tag))

    def tag_ascendants(self, obj, tag):
        return self.walk_ascendants(obj, ViewObject.tagger(tag))

    def set_descendants(self, obj, key, f): 
        return self.walk_descendants(obj, ViewObject.attr_setter(key, f))

    def set_ascendants(self, obj, key, f):
        return self.walk_ascendants(obj, ViewObject.attr_setter(key, f))
    
    @property
    def has_loop(self):
        """
        Returns true if loops exist in the graph
        """
        class Store:
            result = False
        
        def found_loop(particle, depth):
            Store.result = True
        
        for particle in self.initial_particles:
            self.walk_descendants(particle, loop_action=found_loop)
        
        return Store.result
        
    @property
    def depth(self):
        """
        Returns the maximum depth of the graph, and sets .depth attributes on 
        all of the particles.
        """
        class Store:
            maxdepth = 0
            
        def walker(particle, depth):
            particle.depth = depth
            Store.maxdepth = max(depth, Store.maxdepth)
        
        for particle in self.initial_particles:
            self.walk_descendants(particle, walker)
        
        return Store.maxdepth
        
class ViewObject(object):
    def __init__(self, graph):
        self.graph = graph
        self.subscripts = []
        self.tags = set()

    @classmethod
    def tagger(self, what):
        """
        Return a function which tags particles with `what`
        """
        def tag(obj, depth):
            obj.tags.add(what)
        return tag
    
    @classmethod
    def attr_setter(self, what, f):
        def dosetattr(obj, depth):
            setattr(obj, what, f(obj))
        return dosetattr

    def __lt__(self, rhs):
        "Define p1 < p2 so that we can sort particles (by id in this case)"
        def get_number(obj):
            if hasattr(obj, "vertex_number"):
                return obj.vertex_number
            elif hasattr(obj, "particle_number"):
                return obj.particle_number
            elif hasattr(obj, "vertex_numbers"):
                return max(obj.vertex_numbers)
            elif hasattr(obj, "particle_numbers"):
                return max(obj.particle_numbers)
        return get_number(self) < get_number(rhs)

class ViewVertex(ViewObject):
    @property
    def interior(self):
        return self.incoming == self.outgoing

    @property
    def edge(self):
        return not self.incoming or not self.outgoing

    @property
    def kink(self):
        return len(self.incoming) == 1 and len(self.outgoing) == 1
        
    @property
    def initial(self):
        return not self.incoming
    
    @property    
    def final(self):
        return not self.outgoing
    
    @property
    def dangling(self):
        return self.initial and self.final

    @property
    def hadronization(self):
        """
        Any vertex which has a colored particle incoming and a non-colored 
        particle outgoing is a hadronization vertex
        """
        return (any(v.colored for v in self.incoming) and 
                any(not v.colored for v in self.outgoing))
                
    @property
    def connecting(self):
        """
        A connecting vertex is one which connects the two initial states 
        together.
        """        
        return (any(p.descends_one  for p in self.incoming) and 
                all(p.descends_both for p in self.outgoing))

class ViewVertexSingle(ViewVertex):
    def __init__(self, graph, vertex_number):
        super(ViewVertex, self).__init__(graph)
        self.vertex_number = vertex_number
        self.graph.v_map[vertex_number] = self

    @property
    def incoming(self):
        return self.graph.vertex_incoming_particles(self.vertex_number)
    
    @property
    def outgoing(self):
        return self.graph.vertex_outgoing_particles(self.vertex_number)

    @property
    def reference(self):
        # replace - for negative vertex numbers
        return ("V%i" % self.vertex_number).replace("-","N")



class ViewVertexSummary(object):
    def __init__(self, vertex_numbers):
        self.vertex_numbers = vertex_numbers
        self._incoming = set()
        self._outgoing = set()
        for v_nr in self.vertex_numbers:
            self.graph.v_map[v_nr] = self
            for p_nr in self.graph._incoming[v_nr]:
                if not self.graph._start_vertex[p_nr] in self.vertex_numbers:
                    self._incoming.add(v_nr)
                else:
                    self.graph.p_map[p_nr] = None
            for p_nr in self.graph._outgoing[v_nr]:
                if not self.graph._end[p_nr] in self.vertex_numbers:
                    self._outgoing.add(v_nr)
                else:
                    self.graph.p_map[p_nr] = None

    def incoming(self):
        return self.graph.numbers_to_particles(self._incoming)

    def outgoing(self):
        return self.graph.numbers_to_particles(self._outgoing)

    @property
    def reference(self):
        ref = "V" + "_".join("%i" % vno for vno in self.vertex_numbers)
        return ref.replace("-","N") # replace for negative vno


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
        return 21 <= abs(self.pdgid) <= 25 or 32 <= abs(self.pdgid) <= 37

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
    def reference(self):
        return "P%i" % self.particle_number

class ViewParticleSummary(ViewParticle):
    """
    Represents a view of a summary of particles ("jet", "gluball")
    """
    def __init__(self, graph, particle_numbers):
        super(ViewParticleSummary, self).__init__(graph)
        self.particle_numbers = particle_numbers

        start_vertices = []
        end_vertices = []
        for p_nr in self.particle_numbers:
            self.graph.p_map[p_nr] = self
            start_vertex = self.graph._start_vertex[p_nr]
            end_vertex = self.graph._end_vertex[p_nr]
            mother_nrs = self.graph._incoming[start_vertex]
            daughter_nrs = self.graph._outgoing[end_vertex]

            if mother_nrs and all(m in self.particle_numbers for m in mother_nrs):
                self.graph.v_map[start_vertex] = None
            else:
                start_vertices.append(start_vertex)

            if daughter_nrs and all(d in self.particle_numbers for d in daughter_nrs):
                self.graph.v_map[end_vertex] = None
            else:
                end_vertices.append(end_vertex)

        self._start_vertices = start_vertices
        self._end_vertices = end_vertices
        # for the assertion:
        self.start_vertex
        self.end_vertex

        #TODO: define p, e, m
        self.m = 0
        self.e = 0
        momentum = [0, 0, 0]
        for v in self._end_vertices:
            for p in self.graph._incoming[v]:
                pp = self.graph.event.particles[p].p
                for i in (0, 1, 2):
                    momentum[i] += pp[i]
                self.e += self.graph.event.particles[p].e
        self.p = tuple(momentum)

        self.pdgid = -666
        self.color, self.anticolor = None, None

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
    def reference(self):
        ref = "P" + "_".join("%i" % no for no in self.particle_numbers)
        return ref.replace("-","N") # replace for negative particle nr
