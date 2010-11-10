
from ..tool import Tool, tooltype, tool

@tooltype
class Annotation(Tool):
    _type = "annotation"
    _short_opt = "a"
    _short_help = "Add an annotation specifying a property to the label "

    _args = [("position", str)]
    _defaults = {"position" : "sub"}
    _choices = {"position" : ("sub", "super", "under", "over")}

    def annotate_particles(self, particles, annotate_function):
        """
        Add a subscript for all particles. annotate_function(particle) should
        return a value to be added.
        """
        for particle in particles:
            subscript = annotate_function(particle)
            if subscript:
                particle.subscripts.append((subscript, self.options["position"]))

@tool
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

@tool
class Color(Annotation):
    _name = "color"
    def __call__(self, graph):
        self.annotate_particles(graph.particles, lambda p: p.color)
        self.annotate_particles(graph.particles, lambda p: -p.anticolor)

@tool
class Status(Annotation):
    _name = "status"
    def __call__(self, graph):
        self.annotate_particles(graph.particles, lambda p: p.status)
            
@tool
class Pt(Annotation):
    _name = "pt"
    def __call__(self, graph):
        self.annotate_particles(graph.particles, lambda p: "%.2f"%p.pt)
        
