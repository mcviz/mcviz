from ... import log; log = log.getChild(__name__)
from mcviz.tools import Annotation, Arg

class Index(Annotation):
    """
    Particle index in the event record
    """
    _name = "index"
    def __call__(self, graph):
        def label_particle_no(particle):
            #if particle.gluon:
            #    if not "gluid" in self.options.subscript:
            #        # Don't label gluons unless 'gluid' subscript specified
            #        return
            return particle.reference
        self.annotate_particles(graph.particles, label_particle_no)


class Color(Annotation):
    """
    Colour indices that the particle has
    """
    _name = "color"
    def __call__(self, graph):
        self.annotate_particles(graph.particles, lambda p: int(p.color))
        self.annotate_particles(graph.particles, lambda p: int(-p.anticolor))


class Status(Annotation):
    """
    Monte-Carlo status code for the particle
    """
    _name = "status"
    def __call__(self, graph):
        self.annotate_particles(graph.particles, lambda p: p.status)
            

class E(Annotation):
    """
    Particle energy (in Monte-Carlo units)
    """
    _name = "e"
    def __call__(self, graph):
        self.annotate_particles(graph.particles,
            lambda p: "{0:.4g}{1:s}eV".format(*graph.units.pick_mag(p.e)))


class Pt(Annotation):
    """
    Particle transverse momentum (in Monte-Carlo units)
    """
    _name = "pt"
    def __call__(self, graph):
        self.annotate_particles(graph.particles,
            lambda p: "{0:.4g}{1:s}eV".format(*graph.units.pick_mag(p.pt)))
        
        
class PDGID(Annotation):
    """
    Particle transverse momentum (in Monte-Carlo units)
    """
    _name = "pdg"
    def __call__(self, graph):
        self.annotate_particles(graph.particles, lambda p: str(p.pdgid))

class PDFInfo(Annotation):
    """
    Annotate beam particles with pdf information
    """
    _name = "pdfinfo"
    def __call__(self, graph):
        for ip in graph.initial_particles:
            if ip.reference == "P1":
                pdfinfo = graph.event.pdfinfo
                ip.subscripts.append(("id: %s" % pdfinfo.id1, "left"))
                ip.subscripts.append(("x: %f" % float(pdfinfo.x1), "left"))
            elif ip.reference == "P2":
                pdfinfo = graph.event.pdfinfo
                ip.subscripts.append(("id: %s" % pdfinfo.id2, "left"))
                ip.subscripts.append(("x: %f" % float(pdfinfo.x2), "left"))
