#! /usr/bin/env python

from __future__ import with_statement

from sys import argv, stderr
from itertools import takewhile

from mcviz import MCVizParseError
from .particle import Particle
from .vertex import Vertex
from .options import parse_options
from .utils import OrderedSet

from logging import getLogger; log = getLogger("event_graph")
import logging as L

class EventGraph(object):
    def __init__(self, vertices, particles, options=None):
        """
        `records`: A list containing many particles
        """
        options = self.options = options if options else parse_options()
        self.vertices = vertices
        self.particles = particles
        self.other_stuff(options)
        
    def other_stuff(self, options):
        self.do_contractions(options)
        
        self.tag_by_progenitors()
        self.tag_by_hadronization_vertex()
        
        #print >>stderr, "Does the graph have loops?", self.has_loop
        
        for i in xrange(options.strip_outer_nodes):
            #print >>stderr, "Iteration", i, "loopy=", self.has_loop, "depth=", self.depth
            self.strip_outer_nodes()
            self.do_contractions(options)
    
        # Graph consistency checks
        from .tests.test_graph import graph_is_consistent
        graph_is_consistent(self)
    
    def do_contractions(self, options):
        
        all_ = "all" in options.contract
        if all_ or "gluballs" in options.contract:
            self.contract_gluons()
            
        if all_ or "kinks" in options.contract:
            self.contract()
    
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
        
    def strip_outer_nodes(self):
        """
        Remove the outermost nodes of the graph
        """
        result = []
        for particle in self.particles.values():
            if particle.final_state:
                result.append(particle)
                self.drop_particle(particle)
        return result
        
    def tag_by_progenitors(self):
        """
        Tag descendants of the initial particles
        """
        for i, p in enumerate(self.initial_particles):
            self.walk(p, Particle.tagger("descendant_of_p%i" % (i+1)))
    
    def tag_by_hadronization_vertex(self):
        had_vertices = [v for v in self.vertices.values() if v.hadronization]
        for i, vertex in enumerate(had_vertices):
            for particle in vertex.outgoing:    
                self.walk(particle, Particle.tagger("after_hadronization"))
                self.walk(particle, Particle.attr_setter("had_idx", i))
    
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
        
    def drop_particle(self, particle):
        """
        Remove a particle from the graph only. 
        (updates mothers and daughters, etc)
        """
        particle.vertex_in.outgoing.discard(particle)
        for p in particle.vertex_in.incoming:
            p.daughters.discard(particle)
        
        particle.vertex_out.incoming.discard(particle)
        for p in particle.vertex_out.outgoing:
            p.mothers.discard(particle)
        
        if particle.vertex_in.is_dangling:
            del self.vertices[particle.vertex_in.vno]
        
        if particle.vertex_out.is_dangling:
            del self.vertices[particle.vertex_out.vno]
            
        del self.particles[particle.no]
        
    
    def contract_particle(self, particle):
        """
        Contracts a particle in the graph.
        It attaches all particles that are attached to the particle start vertex
        to the particle end vertex.
        """

        v_in = particle.vertex_in
        v_out = particle.vertex_out

        # Eliminate vertex_in
        # Attach all of v_in's particles to v_out
        v_in.transplant_particles(v_out)
        del self.vertices[v_in.vno]

        # remove occurred loops:
        removed = v_out.remove_loops()
        for p_no in removed:
            del self.particles[p_no]
        
        # remove the particle being contracted
        v_out.incoming.discard(particle)
        v_out.outgoing.discard(particle)
        
        # update daughter/mother list of the incoming/outgoing particles
        for p in v_out.incoming:
            p.daughters = v_out.outgoing
        for p in v_out.outgoing:
            p.mothers = v_out.incoming

    def contract_incoming_vertices(self, vertex):
        """
        Contracts all incoming vertices around this vertex into this one
        """
        for p in list(vertex.incoming):
            self.contract_particle(p)
    
    def contract(self):
        """
        Remove vertices for the particle representation
        """
        nr_vertices = len(self.vertices) + 1
        while len(self.vertices) < nr_vertices:
            # Repeat whilst the number of vertices changed
            
            nr_vertices = len(self.vertices)
            for no in self.vertices.keys():
                # Continue if this vertex is already removed
                if no not in self.vertices:
                    continue
                vertex = self.vertices[no]
                if vertex.is_kink and vertex.inp_is_outp and not vertex.edge:
                    (incoming,), (outgoing,) = vertex.incoming, vertex.outgoing
                    incoming.contraction_count += outgoing.contraction_count + 1
                    self.contract_particle(outgoing)

    def contract_gluons(self):
        """
        Remove vertices for the particle representation
        """
        # TODO: Pw->Je: 1) Why not for particle in particles? 
        #               2) Isn't "if no in self.particles.keys" redundent?
        for no in list(self.particles):
            if no not in self.particles: continue
            particle = self.particles[no]
            if particle.gluon and all(m.gluon for m in particle.mothers):
                self.contract_particle(self.particles[no])

    def contract_to_final(self):
        """
        JPE. (or delete)
        """
        for no in list(self.particles):
            if no not in self.particles: continue
            particle = self.particles[no]
            if not (particle.initial_state or particle.final_state):
                self.contract_particle(particle)
    
    @property
    def initial_particles(self):
        return sorted(p for p in self.particles.values() if p.initial_state)
    
    @classmethod
    def load(cls, filename, options=None):
        """
        Try to load a monte-carlo event using all available loaders
        """
        parsers = [cls.from_hepmc, cls.from_pythia_log]
        for parser in parsers:
            try:
                return parser(filename, options)
            except MCVizParseError:
                L.debug("Parser %s failed" % parser.__name__)
                
        raise MCVizParseError("No parsers succeeded")
    
    @classmethod
    def from_hepmc(cls, filename, options=None):
        from loaders.hepmc import load_first_event
        vertices, particles = load_first_event(filename)
        return cls(vertices, particles, options)
        
    @classmethod
    def from_pythia_log(cls, filename, options=None):
        from loaders.pythialog import load_event
        vertices, particles = load_event(filename)
        return cls(vertices, particles, options)

