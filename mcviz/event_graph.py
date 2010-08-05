#! /usr/bin/env python

from __future__ import with_statement

from sys import argv, stderr

from .particle import Particle
from .vertex import Vertex

FIRST_LINE = ("--------  PYTHIA Event Listing  (complete event)  --------------"
    "-------------------------------------------------------------------")
LAST_LINE = ("--------  End PYTHIA Event Listing  -----------------------------"
    "------------------------------------------------------------------")            

class EventGraph(object):
    def __init__(self, records, options=None):
        """
        `records`: A list containing many particles
        """
        self.options = options
        
        if options and options.limit is not None:
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
        
        if options and "gluballs" in options.contract:
            self.contract_gluons()
            
        if options and "kinks" in options.contract:
            self.contract()
     

    def contract_particle(self, particle):
        """Contracts a particle in the graph, 
        it attaches all particles that are attached to the particle start vertex
        to the particle end vertex"""

        v_in = particle.vertex_in
        v_out = particle.vertex_out

        v_out.incoming.update(v_in.incoming)
        for p in v_in.incoming:
            p.vertex_out = v_out
        v_out.outgoing.update(v_in.outgoing)
        for p in v_in.outgoing:
            p.vertex_in = v_out

        # remove occurred loops:
        loops = v_out.incoming.intersection(v_out.outgoing)
        for p in loops:
            if not p == particle:
                v_out.incoming.discard(p)
                v_out.outgoing.discard(p)
                del self.particles[p.no]

        # remove the particle itself
        v_out.incoming.discard(particle)
        v_out.outgoing.discard(particle)

        # update mother/daughter list of 
        for p in v_out.incoming:
            p.daughters = set(v_out.outgoing)
        for p in v_out.outgoing:
            p.mothers = set(v_out.incoming)

        # now there should be no more reference to v_in
        del self.vertices[v_in.vno]
        del self.particles[particle.no]

    def contract_incoming_vertices(self, vertex):
        """Contracts all incoming vertices around this vertex into this one"""
        for p in list(vertex.incoming):
            self.contract_particle(p)
    
    def contract(self):
        """
        Remove vertices for the particle representation
        """
        nr_vertices = len(self.vertices) + 1
        while len(self.vertices) < nr_vertices:
            nr_vertices = len(self.vertices)
            for no in self.vertices.keys():
                # Continue if this vertex is already removed
                if not no in self.vertices:
                    continue
                vertex = self.vertices[no]
                if len(vertex.incoming) == 1 and len(vertex.outgoing) == 1:
                    incoming = list(vertex.incoming)[0]
                    outgoing = list(vertex.outgoing)[0]    
                    if (incoming.pdgid == outgoing.pdgid and 
                        incoming.vertex_in and outgoing.vertex_out):
                        self.contract_particle(outgoing)

    def contract_gluons(self):
        """
        Remove vertices for the particle representation
        """
        # TODO: Pw->Je: 1) Why not for particle in particles? 
        #               2) Isn't "if no in self.particles.keys" redundent?
        for no in self.particles.keys():
            if no in self.particles.keys() and self.particles[no].pdgid == 21 and all(m.pdgid == 21 for m in self.particles[no].mothers):
                self.contract_particle(self.particles[no])

    def contract_to_final(self):
        for no in self.particles.keys():
            if no in self.particles.keys() and not self.particles[no].initial_state and not self.particles[no].final_state:
                self.contract_particle(self.particles[no])
                    
    
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

        first, last = lines.index(FIRST_LINE)+2, lines.index(LAST_LINE)-1

        def maybe_num(s):
            try: return float(s)
            except ValueError:
                return s

        records = [map(maybe_num, line.split()) for line in lines[first:last]]
        return EventGraph(records, options)

