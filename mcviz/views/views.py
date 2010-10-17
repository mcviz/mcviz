#! /usr/bin/env python

from __future__ import with_statement

from sys import argv, stderr
from itertools import chain

from ..utils import walk, OrderedSet

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
        self._incoming, self._outgoing = {}, {}
        self._initial_particles = []
        self._particles = sorted(self.p_map.keys())
        self._vertices = sorted(self.v_map.keys())
        for nr in self._particles:
            p = self.event.particles[nr]
            if p.vertex_in:
                self._start_vertex[nr] = p.vertex_in.vno if p.vertex_in else None
            if p.vertex_out:
                self._end_vertex[nr] = p.vertex_out.vno if p.vertex_out else None

        for nr in self._vertices:
            v = self.event.vertices[nr]
            self._incoming[nr] = sorted([p.no for p in self.event.vertices[nr].incoming])
            self._outgoing[nr] = sorted([p.no for p in self.event.vertices[nr].outgoing])
            if not self._incoming[nr]:
                self._initial_particles.extend(self._outgoing[nr])

    def numbers_to_particles(self, numbers):
        return OrderedSet(p for p in (self.p_map[nr] for nr in numbers) if p)

    def numbers_to_vertices(self, numbers):
        return OrderedSet(v for v in (self.v_map[nr] for nr in numbers) if v)

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
        return self.numbers_to_vertices(self._vertices)

    @property
    def particles(self):
        return self.numbers_to_particles(self._particles)

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

    def check_connected(self, vertex_numbers):
        # check for connectedness
        unconnected = list(vertex_numbers)
        connected = [unconnected.pop()]
        while len(unconnected) > 0:
            for v in unconnected:
                for p in self._incoming[v] + self._outgoing[v]:
                    if self._start_vertex[p] in connected or self._end_vertex[p] in connected:
                        connected.append(v)
                        unconnected.remove(v)
                        break
                if not v in unconnected:
                    break

    def summarize_vertices(self, vertices):
        elementary_vertices = []
        for p in vertices:
            if isinstance(p, ViewVertexSummary):
                elementary_vertices.extend(p.vertex_numbers)
            else:
                elementary_vertices.append(p.vertex_number)
        ViewVertexSummary(self, elementary_vertices)

    def walk(self, obj, 
        particle_action=lambda p, d: None, vertex_action=lambda p, d: None,
        loop_action=lambda p, d: None, ascend=False):
        def walk_action(obj, depth):
            if isinstance(obj, ViewParticle):
                next_vertices = particle_action(obj, depth) if particle_action else None
                if next_vertices is None:
                    next_vertices = (obj.start_vertex,) if ascend else (obj.end_vertex,)
                return next_vertices
            elif isinstance(obj, ViewVertex):
                next_particles = vertex_action(obj, depth) if vertex_action else None
                if next_particles is None:
                    next_particles = obj.incoming if ascend else obj.outgoing
                return next_particles
            else:
                raise NotImplementedError("Unknown object in graph: %s" % obj.__class__.__name__)
        return walk(obj, walk_action, loop_action)
    
    def tag(self, obj, tag, particles=False, vertices=False, ascend=False): 
        particle_action = ViewObject.tagger(tag) if particles else None
        vertex_action = ViewObject.tagger(tag) if vertices else None
        return self.walk(obj, particle_action, vertex_action, ascend=ascend)

    def set(self, obj, key, f, particles=False, vertices=False, ascend=False): 
        particle_action = ViewObject.attr_setter(key, f) if particles else None
        vertex_action = ViewObject.attr_setter(key, f) if vertices else None
        return self.walk(obj, particle_action, vertex_action, ascend=ascend)
    
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
            self.walk(particle, loop_action=found_loop)
        
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
        return self.order_number < rhs.order_number

class ViewVertex(ViewObject):
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
    
    @property
    def reference(self):
        # replace - for negative vertex numbers
        return ("V%i" % self.order_number).replace("-","N")

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
    def order_number(self):
        # replace - for negative vertex numbers
        return self.vertex_number

    @property
    def represented_numbers(self):
        return [self.vertex_number]

class ViewVertexSummary(ViewVertex):
    def __init__(self, graph, vertex_numbers):
        super(ViewVertexSummary, self).__init__(graph)
        self.vertex_numbers = vertex_numbers
        self._incoming = []
        self._outgoing = []
        for v_nr in self.vertex_numbers:
            self.graph.v_map[v_nr] = self
            for p_nr in self.graph._incoming[v_nr]:
                if self.graph._start_vertex[p_nr] in self.vertex_numbers:
                    self.graph.p_map[p_nr] = None
                else:
                    self._incoming.append(p_nr)
            for p_nr in self.graph._outgoing[v_nr]:
                if self.graph._end_vertex[p_nr] in self.vertex_numbers:
                    self.graph.p_map[p_nr] = None
                else:
                    self._outgoing.append(p_nr)
        self.tags.add("summary")

    @property
    def incoming(self):
        return self.graph.numbers_to_particles(self._incoming)

    @property
    def outgoing(self):
        return self.graph.numbers_to_particles(self._outgoing)

    @property
    def order_number(self):
        #ref = "V" + "_".join("%i" % vno for vno in self.vertex_numbers)
        #return ref.replace("-","N") # replace for negative vno
        return min(self.vertex_numbers)

    @property
    def represented_numbers(self):
        return self.vertex_numbers

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

class ViewParticleSummary(ViewParticle):
    """
    Represents a view of a summary of particles ("jet", "gluball")
    """
    def __init__(self, graph, summarized_particle_numbers):
        super(ViewParticleSummary, self).__init__(graph)
        self.particle_numbers = summarized_particle_numbers

        # represent all particles
        for p in self.particle_numbers:
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
