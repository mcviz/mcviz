#! /usr/bin/env python

from __future__ import with_statement

from math import log10, log, atan2, tan

from sys import argv, stderr
from optparse import OptionParser

FIRST_LINE = ("--------  PYTHIA Event Listing  (complete event)  --------------"
    "-------------------------------------------------------------------")
LAST_LINE = ("--------  End PYTHIA Event Listing  -----------------------------"
    "------------------------------------------------------------------")

class Vertex(object):
    """
    
    """
    def __init__(self, vno, incoming, outgoing):
        self.vno = vno
        self.incoming = set(incoming)
        self.outgoing = set(outgoing)
        
    def draw(self):
        """
        
        """
        size = 5
        args = self.vno, self.vno, size
        #print('%i [label="%i",fontsize=%.0f]' % args)
        # 
        print('%i [label="", height=0.1, width=0.1, color=black]' % self.vno)
            
        # Printing edges
        for out_particle in self.outgoing:
            if out_particle.vertex_out:
                color = out_particle.get_color("black")
                args = (self.vno, out_particle.vertex_out.vno, out_particle.name, 
                        out_particle.no, color, log10(out_particle.pt+1)*10 + 1, log10(out_particle.e+1)*20 + 1)
                print('%i->%i [label="%s (%i)", color=%s, penwidth=%f, weight=%i]' % args)
        
class Particle(object):
    def __init__(self, no, pdgid, name, status, mother1, mother2, 
                 daughter1, daughter2, color1, color2, px, py, pz, e, m):
        self.no = int(no)
        self.pdgid = pdgid
        self.name = name.strip("(").strip(")")
        self.status = status
        self.mothers = [int(m) for m in (mother1, mother2) if m != 0]
        self.daughters = [int(d) for d in (daughter1, daughter2) if d != 0]
        self.colors = int(color1), int(color2)
        self.p = px, py, pz
        self.pt = (px**2 + py**2)**0.5
        #self.eta = -log(tan(atan2(self.pt, pz)/2.))
        self.phi = atan2(px, py)
        self.e = e
        self.m = m
        self.tags = set()
        self.vertex_in = None
        self.vertex_out = None
        
        # States like "drawn"
        self.state = set()
        
    def tag(self, tag):
        """
        Used to record a tag for a particle.
        
        Particles can be selected by tag.
        """
        self.tags.add(tag)
        for daughter in self.daughters:
            daughter.tag(tag)
    
    def get_color(self, default):
        
        color = self.colors[0] != 0
        anticolor = self.colors[1] != 0
        
        if color and not anticolor:
            color = "blue"
        elif color and anticolor:
            color = "green"
        elif not color and anticolor:
            color = "red"
        else:
            color = default
            
        return color
            
    def draw(self):
        color = self.get_color("gray")
        size = (15 + log10(self.pt + 1)*100)
        args = (self.no, self.name, self.no, color, size)
        
        if len(self.daughters) == 0:
            # Printing a leaf node
            print('%i [label="%s (%i)",fillcolor=%s,height,fontsize=%.0f]' % args)
            
        elif len(self.mothers) == 0:
            # Printing a head node
            print('%i [label="%s (%i)",fillcolor=%s,height,fontsize=%.0f]' % args)
            
        else:
            # Printing an internal node
            print('%i [label="%s (%i)",fillcolor=%s,height,fontsize=%.0f]' % args)
        
        # Printing edges
        for mother in self.mothers:
            print('%i->%i // mother' % (mother.no, self.no))
        
        for daughter in self.daughters:
            print('%i->%i // daughter' % (self.no, daughter.no))
            

class EventGraph(object):
    def __init__(self, records):
        """
        `records`: A list containing many particles
        """
        
        # Make particle objects and {no:Particle} dictionary
        particles = [Particle(*particle) for particle in records]
        self.particles = dict((v.no, v) for v in particles)
        
        # Convert mothers/daughters to objects
        for particle in particles:
            #if particle.no == 243:
       	    #    print >> stderr, particle.no, particle.mothers, particle.daughters
            particle.daughters = set(particles[d] for d in particle.daughters)
            particle.mothers = set(particles[m] for m in particle.mothers)
            #if particle.no == 243:
       	    #    print >> stderr, particle.no, map(lambda x:x.no, particle.mothers), map(lambda x:x.no, particle.daughters)

        # Populate daughters for particles
        for particle in particles:
            for mother in particle.mothers:
                mother.daughters.add(particle)
            for daughter in particle.daughters:
                daughter.mothers.add(particle)

        # Remove loops 
        for particle in particles:
            particle.mothers.discard(particle)
            particle.daughters.discard(particle)
            m = list(particle.mothers)
            m.sort()
            particle.mothers = frozenset(m)
                
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
                            print >> stderr, map(lambda x:x.no,v.incoming), map(lambda x : x.no,particle.mothers)
                            break
                    if found_v:
                        break

            if found_v:
                found_v.outgoing.add(particle)
            else:
                vno += 1
                self.vertices[frozenset(particle.mothers)] = Vertex(vno, particle.mothers, [particle])
                if len(particle.mothers) == 0:
                    print >> stderr, particle.no, particle.daughters
                
        for particle in particles:
            if len(particle.daughters) == 0:
                vno += 1
                self.vertices[particle] = Vertex(vno, [particle], [])
            if len(particle.mothers) == 0:
                print >> stderr, particle.no, particle.daughters
                
                
        for vertex in self.vertices.itervalues():
            for particle in vertex.incoming:
                particle.vertex_out = vertex
                
            for particle in vertex.outgoing:
                particle.vertex_in = vertex
                
        self.contract()
                
    def contract(self):
        """
        Remove vertices for the particle representation
        """
        for key in list(self.vertices.keys()):
            vertex = self.vertices[key]
            if len(vertex.incoming) == 1 and len(vertex.outgoing) == 1:
                incoming = list(vertex.incoming)[0]
                outgoing = list(vertex.outgoing)[0]    
                if incoming.pdgid == outgoing.pdgid and incoming.vertex_in and outgoing.vertex_out:
                    # attach outgoing particle to previous vertex
                    outgoing.vertex_in = incoming.vertex_in
                    
                    # fix mothers of outgoing particle
                    outgoing.mothers = set(outgoing.vertex_in.incoming)
                    
                    # in previous vertex, replace particle
                    incoming.vertex_in.outgoing.remove(incoming)
                    incoming.vertex_in.outgoing.add(outgoing)
                    
                    # remove superfluous stuff
                    del self.particles[incoming.no]
                    del self.vertices[key]
                    
            
                    
    def draw_particles(self):        
        print("strict digraph pythia {")
        print("node [style=filled, shape=oval]")
        for particle in self.particles.itervalues():
            particle.draw()
        print("}")
    
    def draw_feynman(self):        
        print("strict digraph pythia {")
        print("node [style=filled, shape=oval]")
        print("edge [labelangle=90, fontsize=12]")
        print("ratio=1")
        
        for vertex in self.vertices.itervalues():
            vertex.draw()
        print("}")
    
    @classmethod
    def from_hepmc(cls, filename):
        "TODO"
        
    @classmethod
    def from_pythia_log(cls, filename):
        print >>stderr, "BLAH!", filename
        with open(filename) as fd:
            lines = [line for line in (line.strip() for line in fd) if line]

        first, last = lines.index(FIRST_LINE)+2, lines.index(LAST_LINE)-1

        def maybe_num(s):
            try: return float(s)
            except ValueError:
                return s

        records = [map(maybe_num, line.split()) for line in lines[first:last]]
        return EventGraph(records)
        
def main():
    p = OptionParser()
    o = p.add_option
    o("-m", "--method", choices=["pt", "eta", "generations"], default="pt",
      help="Specify a method")

    o("-d", "--dual", action="store_true",
      help="Draw the dual of the Feynman graph")

    options, args = p.parse_args(argv)
    
    if not args:
        p.error("Specify a pythia log file to run on")

    event = EventGraph.from_pythia_log(args[1])
    
    event.draw_feynman()
    #event.draw_particles()
    

if __name__ == "__main__":
    """
    try:
        import 
    """

    main()
