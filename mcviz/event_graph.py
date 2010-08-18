#! /usr/bin/env python

from __future__ import with_statement

from sys import argv, stderr
from itertools import takewhile

from .particle import Particle
from .vertex import Vertex
from .options import parse_options
from .utils import OrderedSet

START_COMPLETE = ("--------  "
    "PYTHIA Event Listing  (complete event)  ---------"
    "------------------------------------------------------------------------")
START_COMBINED = ("--------  "
    "PYTHIA Event Listing  (combination of several events)"
    "  ------------------------------------------------------------------")
START_HARD = ("--------  PYTHIA Event Listing  (hard process)  -------------"
    "----------------------------------------------------------------------")
END_LIST = ("--------  End PYTHIA Event Listing  -----------------------------"
    "------------------------------------------------------------------")

class EventGraph(object):
    def __init__(self, records, options=None):
        """
        `records`: A list containing many particles
        """
        options = self.options = options if options else parse_options()
        
        if options.limit is not None:
            # Limit the number of records used to generate the graph
            records = records[:options.limit]
        
        # Make particle objects and {no:Particle} dictionary
        particles = [Particle(*p) for p in records]
        self.particles = dict((p.no, p) for p in particles)
        
        # Convert mothers/daughters to objects
        for particle in particles:
            particle.daughters = set(particles[d] for d in particle.daughters)
            particle.mothers = set(particles[m] for m in particle.mothers)

        # Populate mothers and daughters for particles
        for particle in particles:
            for mother in particle.mothers:
                mother.daughters.add(particle)
            for daughter in particle.daughters:
                daughter.mothers.add(particle)

        # Remove self-connections
        for particle in particles:
            particle.mothers.discard(particle)
            particle.daughters.discard(particle)

        # TODO: Johannes: Please explain!
        self.vertices = dict()
        vno = 0
        for particle in particles:
            found_v = None
            if frozenset(particle.mothers) in self.vertices:
                found_v = self.vertices[frozenset(particle.mothers)]
            else:
                for v in self.vertices.itervalues():
                    for m in particle.mothers:
                        if m in v.incoming:
                            found_v = v
                            #print >> stderr, map(lambda x: x.no, v.incoming), map(lambda x: x.no, particle.mothers)
                            break
                    if found_v:
                        break

            if found_v:
                found_v.outgoing.add(particle)
                for new_mother in found_v.incoming:
                    particle.mothers.add(new_mother)
                    new_mother.daughters.add(particle)
            elif particle.mothers:
                vno += 1
                self.vertices[frozenset(particle.mothers)] = Vertex(vno, particle.mothers, [particle])
                if len(particle.mothers) == 0:
                    # this is the system vertex
                    print >> stderr, "No mothers: ", particle.no, particle
            else: # initial state vertex
                vno += 1
                self.vertices[particle] = Vertex(vno, [], [particle])
                
        for particle in particles:
            if particle.final_state:
                vno += 1
                self.vertices[particle] = Vertex(vno, [particle], [])
            if particle.initial_state:
                print >> stderr, "INITIAL PARTICLE: ", particle.no, particle.name
                
        # Connect particles to their vertices
        for vertex in self.vertices.itervalues():
            for particle in vertex.incoming:
                particle.vertex_out = vertex
                
            for particle in vertex.outgoing:
                particle.vertex_in = vertex

        self.vertices = dict((v.vno,v) for v in self.vertices.values())
        
        self.do_contractions(options)
            
        # Remove system vertex
        del self.particles[0]
        
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
        class Store:
            result = False
        
        def found_loop(particle, depth):
            Store.result = True
        
        for particle in self.initial_particles:
            self.walk(particle, loop_action=found_loop)
        
        return Store.result
        
    def strip_outer_nodes(self):
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
             walk_action=lambda p, d:None, loop_action=lambda p, d:None, 
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
    def from_hepmc(cls, filename):
        "TODO"
        
    @classmethod
    def from_pythia_log(cls, filename, options=None):
        """
        Parse a pythia event record from a log file.
        Numbers are converted to floats where possible.
        """

        with open(filename) as fd:
            lines = [line for line in (line.strip() for line in fd) if line]

        if START_COMPLETE in lines:
            first = lines.index(START_COMPLETE) + 2
            last = first + lines[first:].index(END_LIST) - 1
        elif START_COMBINED in lines:
            first = lines.index(START_COMBINED) + 2
            last = first + lines[first:].index(END_LIST) - 1
        elif START_HARD in lines:
            first = lines.index(START_HARD) + 2
            last = first + lines[first:].index(END_LIST) - 1
        else:
            raise IOError("Failed to read pythia log file: "
                          "no complete event listing found")

        def maybe_num(s):
            try: return float(s)
            except ValueError:
                return s

        records = [map(maybe_num, line.split()) for line in lines[first:last]]
        # insert blank name if name is not specified
        for particle in records:
            if len(particle) == 14: 
                particle.insert(2,"")
        return EventGraph(records, options)

