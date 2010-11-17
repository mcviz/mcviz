from mcviz.tools import Annotation

class Index(Annotation):
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
    _name = "color"
    def __call__(self, graph):
        self.annotate_particles(graph.particles, lambda p: p.color)
        self.annotate_particles(graph.particles, lambda p: -p.anticolor)


class Status(Annotation):
    _name = "status"
    def __call__(self, graph):
        self.annotate_particles(graph.particles, lambda p: p.status)
            

class Pt(Annotation):
    _name = "pt"
    def __call__(self, graph):
        self.annotate_particles(graph.particles, lambda p: "%.2f"%p.pt)
        
