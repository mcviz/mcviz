
from mcviz.logger import LOG
LOG = LOG.getChild(__name__)
from mcviz.tools.types import Annotation

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
        self.annotate_particles(graph.particles, \
                lambda p: graph.units.energy_formatter(p.e))


class Pt(Annotation):
    """
    Particle transverse momentum (in Monte-Carlo units)
    """
    _name = "pt"
    def __call__(self, graph):
        self.annotate_particles(graph.particles, \
                lambda p: graph.units.energy_formatter(p.pt))

class PDGID(Annotation):
    """
    PDG species number
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
        for particle in graph.initial_particles:
            if particle.reference == "P1":
                pdfinfo = graph.event.pdfinfo
                particle.subscripts.append(("id: %s" % pdfinfo.id1, "left"))
                particle.subscripts.append(("x: %f" \
                        % float(pdfinfo.x1), "left"))
            elif particle.reference == "P2":
                pdfinfo = graph.event.pdfinfo
                particle.subscripts.append(("id: %s" % pdfinfo.id2, "left"))
                particle.subscripts.append(("x: %f" \
                        % float(pdfinfo.x2), "left"))
