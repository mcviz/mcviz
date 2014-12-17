
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
        self.hvertex = None

    @classmethod
    def from_hepmc(cls, hvertex, outgoing):
        vertex = cls(int(hvertex.barcode), outgoing=outgoing)
        vertex.hvertex = hvertex
        return vertex

    @property
    def position(self):
        vertex = self.hvertex
        if vertex is None:
            return vertex
        return vertex.x, vertex.y, vertex.z, vertex.ctau

    def __repr__(self):
        args = self.vno, sorted(self.incoming), sorted(self.outgoing)
        return "<Vertex id=%i in=set(%r) out=set(%r)>" % args

    def __lt__(self, rhs):
        """
        Sort vertices in order of vno
        """
        return self.vno < rhs.vno
