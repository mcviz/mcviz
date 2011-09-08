from mcviz.tools import Annotation, Arg

from mcviz.utils import energy_mag, pick_mag

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
        self.annotate_particles(graph.particles, lambda p: p.color)
        self.annotate_particles(graph.particles, lambda p: -p.anticolor)


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
        self.annotate_particles(graph.particles, lambda p: "%.4g%seV"%energy_mag(p.e))


class Pt(Annotation):
    """
    Particle transverse momentum (in Monte-Carlo units)
    """
    _name = "pt"
    def __call__(self, graph):
        self.annotate_particles(graph.particles, lambda p: "%.4g%seV"%pick_mag(p.pt))
        
        
class PDGID(Annotation):
    """
    Particle transverse momentum (in Monte-Carlo units)
    """
    _name = "pdg"
    def __call__(self, graph):
        self.annotate_particles(graph.particles, lambda p: str(p.pdgid))
        
