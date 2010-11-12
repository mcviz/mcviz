class Vertex(object):
    """
    Each vertex is identified by either:
    
    * An id (vno)
    * The frozenset of particles going into that vertex
    """
    
    def __init__(self, vno, incoming=(), outgoing=()):
        self.vno = vno
        self.incoming = set(incoming)
        self.outgoing = set(outgoing)
    
    @classmethod
    def from_hepmc(self, hvertex, outgoing):
        v = Vertex(int(hvertex.barcode), outgoing=outgoing)
        v.hvertex = hvertex
        return v
    
    def __repr__(self):
        args = self.vno, sorted(self.incoming), sorted(self.outgoing)
        return "<Vertex id=%i in=set(%r) out=set(%r)>" % args
    
    def __lt__(self, rhs):
        """
        Sort vertices in order of vno
        """
        return self.vno < rhs.vno
