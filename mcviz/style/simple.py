from __future__ import division

from ..svg import identity

from .svg import SVGStyle

class SimpleStyle(SVGStyle):

    def paint_particle(self, edge):

        particle = edge.item

        # set garish defaults args to make oversights obvious
        display_func = identity
        args = {}
        args["energy"] = 0.2
        args["stroke-width"] = 0.05
        args["scale"] = 0.1

        # colouring
        if particle.gluon:
            args["stroke"] = args["fill"] = "green"
        elif particle.photon:
            args["stroke"] = args["fill"] = "orange"
        elif particle.colored:
            display_func = identity
            if particle.color:
                args["stroke"] = args["fill"] = "red"
            else:
                args["stroke"] = args["fill"] = "blue"
        elif particle.lepton:
            display_func = identity
            args["stroke"] = args["fill"] = "black"
        else:
            args["stroke"] = args["fill"] = "black"
        
        self.doc.add_object(display_func(spline = edge.spline, **args))
        self.label_edge(edge)


