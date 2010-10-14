#! /usr/bin/env python

from __future__ import with_statement

from sys import argv, stderr
from itertools import takewhile

from ..utils import OrderedSet

from logging import getLogger; log = getLogger("event_graph")
import logging as L

class GraphView(object):
    def __init__(self, event_graph):
        self.g = event_graph
        g_vertices_no = list(v.vno for v in event_graph.vertices.values())
        g_particles_no = list(p.no for p in event_graph.particles.values())
        self.v_map = dict((v, ViewVertex(self, v)) for v in g_vertices_no)
        self.p_map = dict((p, ViewParticle(self, p)) for p in g_particles_no)
        self.next_particle_no = max(g_particles_no) + 1
        self.next_vertex_no = max(g_vertices_no) + 1

    def vertex_in(self, g_no):
        original_v = self.g.particles[g_no].vertex_in
        if original_v:
            return self.v_map[original_v.vno]

    def vertex_out(self, g_no):
        original_v = self.g.particles[g_no].vertex_out
        if original_v:
            return self.v_map[original_v.vno]

    def incoming(self, g_vno):
        return set(self.p_map[p.no] for p in self.g.vertices[g_vno].incoming)

    def outgoing(self, g_vno):
        return set(self.p_map[p.no] for p in self.g.vertices[g_vno].outgoing)

    @property
    def vertices(self):
        return sorted(set(p for p in self.v_map.values()))

    @property
    def particles(self):
        return sorted(set(p for p in self.p_map.values()))

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
        
    def walk(self, particle, 
             walk_action=lambda p, d: None, loop_action=lambda p, d: None, 
             completed_walks=None, uncompleted_walks=None, depth=0):
        """
        Walk the particle graph.
        
        Shamelessly stolen algorithm from:
        http://www.electricmonk.nl/log/2008/08/07/dependency-resolving-algorithm
        
        Enhanced for our purposes to provide loop marking.
        """
        if completed_walks is None: completed_walks = OrderedSet()
        if uncompleted_walks is None: uncompleted_walks = OrderedSet()
        
        walk_action(particle, depth)
        
        uncompleted_walks.add(particle)
        
        for daughter in particle.daughters:
            if daughter not in completed_walks:
                # we haven't yet seen this particle, walk it.
                if daughter in uncompleted_walks:
                    # We have a loop, because we have seen it but not walked it.
                    # All particles from the end up to this daughter are 
                    # participating in the loop
                    if not loop_action:
                        continue
                     
                    lps = takewhile(lambda x: x != daughter, 
                                    reversed(uncompleted_walks))
                                     
                    looping_particles = list(lps) + [daughter]
                    
                    # -1 because a single particle loop should be at the same
                    # depth as the self.walk() call.
                    n_lp = len(looping_particles) - 1
                    for i, looping_particle in enumerate(looping_particles):
                        loop_action(looping_particle, depth - n_lp + i + 1)
                         
                else:
                    # Not circular, so walk it.
                    self.walk(daughter, walk_action, loop_action, 
                              completed_walks, uncompleted_walks, depth+1)
        
        completed_walks.add(particle)
        uncompleted_walks.discard(particle)
        return completed_walks
    
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
            self.walk(particle, walker)
        
        return Store.maxdepth
        
    @property
    def initial_particles(self):
        return sorted(set(p for p in self.p_map.values() if p.initial_state))
    
        
class ViewObject(object):
    def __init__(self, graph):
        self.graph = graph
        self.subscripts = []
        self.tags = set()


class ViewVertex(ViewObject):
    def __init__(self, graph, g_vno):
        super(ViewVertex, self).__init__(graph)
        self.g_vno = g_vno
        self.vno = g_vno

    @property
    def incoming(self):
        return self.graph.incoming(self.g_vno)
    
    @property
    def outgoing(self):
        return self.graph.outgoing(self.g_vno)

    @property
    def edge(self):
        return not self.incoming or not self.outgoing

    @property
    def is_kink(self):
        return len(self.incoming) == 1 and len(self.outgoing) == 1
        
    @property
    def inp_is_outp(self):
        assert self.is_kink, "This function is only intended for kinks"
        incoming, = self.incoming
        outgoing, = self.outgoing
        return incoming.pdgid == outgoing.pdgid

    @property
    def is_initial(self):
        return not self.incoming
    
    @property    
    def is_final(self):
        return not self.outgoing
    
    @property
    def is_dangling(self):
        return self.is_initial and self.is_final

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
        return ("V%i" % self.vno).replace("-","_")


class ViewVertexSummary(object):
    def __init__(self, vertex_numbers):
        pass

class ViewParticleSummary(ViewObject):
    """
    Represents a view of a summary of particles ("jet", "gluball")
    """
    def __init__(self, graph, particles, vertex_in, vertex_out):
        super(ViewParticleSummary, self).__init__(graph)
        self.particles = particles
        self.vertex_in = vertex_in
        self.vertex_out = vertex_out

class ViewParticle(ViewObject):
    """
    Represents a view of a single particle
    """
    def __init__(self, graph, g_particle_no):
        super(ViewParticle, self).__init__(graph)
        self.g_no = g_particle_no
        self.no = self.g_no

    @property
    def p(self):
        return self.graph.g.particles[self.g_no]

    @property
    def pdgid(self):
        return self.p.pdgid

    @property
    def e(self):
        return self.p.e
    
    @property
    def color(self):
        return self.p.color

    @property
    def anticolor(self):
        return self.p.anticolor

    @property
    def vertex_in(self):
        return self.graph.vertex_in(self.g_no)

    @property
    def vertex_out(self):
        return self.graph.vertex_out(self.g_no)

    @property
    def mothers(self):
        return self.vertex_in.incoming

    @property
    def daughters(self):
        return self.vertex_out.outgoing

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
    def reference(self):
        return "P%i" % self.no
    
    @classmethod
    def tagger(self, what):
        """
        Return a function which tags particles with `what`
        """
        def tag(particle, depth):
            particle.tags.add(what)
        return tag
    
    @classmethod
    def attr_setter(self, what, value):
        def dosetattr(particle, depth):
            setattr(particle, what, value)
        return dosetattr

    @property
    def initial_state(self):
        "No mothers"
        return not bool(self.mothers)
    
    @property
    def final_state(self):
        "No daughters"
        return not bool(self.daughters)

        
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
        return "P%i" % self.no



