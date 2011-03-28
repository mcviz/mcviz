
# The Tool types
# Special members: _type, _short_opt, _short_help, _merge_classes
from .tools import Tool, Arg

class Annotation(Tool):
    _type = "annotation"
    _short_opt = "a"
    _short_help = "Add an annotation specifying a property to the label "
    _args = (Arg("position", str, "position of the label", default="super", 
                 choices=("super", "sub", "over", "under")),)

    def annotate_particles(self, particles, annotate_function):
        """
        Add a subscript for all particles. annotate_function(particle) should
        return a value to be added.
        """
        for particle in particles:
            subscript = annotate_function(particle)
            if subscript:
                particle.subscripts.append((subscript, self.options["position"]))

class Transform(Tool):
    _type = "transform"
    _short_opt = "t"
    _short_help = ("Select a transform that is applied to the graph."
                   "Can be applied multiple times.")

class Layout(Tool):
    _type = "layout"
    _short_opt = "l"
    _short_help = ("Select layout classes that are used to layout the graph."
                   "Can also be applied multiple times.")
    _merge_classes = True

class LayoutEngine(Tool):
    _type = "layout-engine"
    _short_opt = "e"
    _short_help = ("If specified, pipes output through specified "
                   "graphviz engine")


class Style(Tool):
    _type = "style"
    _short_opt = "s"
    _short_help = "Select styles that are applied to the graph"


class Painter(Tool):
    _type = "painter"
    _short_opt = "p"
    _short_help = "Set the painter"
    _merge_classes = True


class OptionSet(Tool):
    _type = "optionset"
    _short_opt = False
    _short_help = "option set (hidden since we do not specify short_opt)"
