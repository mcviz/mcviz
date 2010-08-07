class Vertex(object):
    """
    Each vertex is identified by either:
    
    * An id (vno)
    * The frozenset of particles going into that vertex
    """
    
    def __init__(self, vno, incoming, outgoing):
        self.vno = vno
        self.incoming = set(incoming)
        self.outgoing = set(outgoing)
    
    def __repr__(self):
        args = self.vno, sorted(self.incoming), sorted(self.outgoing)
        return "<Vertex id=%i in=set(%r) out=set(%r)>" % args
    
    def __lt__(self, rhs):
        """
        Sort vertices in order of vno
        """
        return self.vno < rhs.vno
        
    def transplant_particles(self, to_vertex):
        
        to_vertex.incoming.update(self.incoming)
        to_vertex.outgoing.update(self.outgoing)
        for p in self.incoming:
            p.vertex_out = to_vertex
        for p in self.outgoing:
            p.vertex_in = to_vertex
    
    def remove_loops(self):
        
        loops = self.incoming.intersection(self.outgoing) #- set([particle])
        for p in loops:
            self.incoming.discard(p)
            self.outgoing.discard(p)
        return [p.no for p in loops]

    @property
    def edge(self):
        return not self.incoming or not self.outgoing

    @property
    def is_initial(self):
        return not self.incoming
    
    @property    
    def is_final(self):
        return not self.outgoing

    @property
    def hadronization(self):
        """
        Any vertex which has a colored particle incoming and a non-colored 
        particle outgoing is a hadronization vertex
        """
        return (any(v.colored for v in self.incoming) and 
                any(not v.colored for v in self.outgoing))
