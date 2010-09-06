from __future__ import division

import re
from time import time
from sys import stderr

from ..svg import SVGDocument
from ..svg import photon, final_photon, gluon, boson, fermion, hadron, vertex

from ..particle import Particle
from ..vertex import Vertex

from .svg import SVGStyle

class SimpleStyle(SVGStyle):

    def paint_particle(self, edge):

        particle = edge.item

        # set garish defaults args to make oversights obvious
        display_func = hadron
        args = {}
        args["energy"] = 0.2
        args["stroke"] = "pink"
        args["fill"] = "pink"
        args["stroke-width"] = 0.05
        args["scale"] = 0.1

        # colouring
        if particle.gluon:
            display_func = hadron
            args["stroke"] = "green"
            args["fill"] = "green"
        elif particle.photon:
            if particle.final_state:
                display_func = hadron
            else:
                display_func = hadron
            args["stroke"] = "orange"
            args["fill"] = "orange"
        elif particle.colored:
            display_func = fermion
            if particle.color:
                args["stroke"] = "red"
                args["fill"] = "red"
            else:
                args["stroke"] = "blue"
                args["fill"] = "blue"
        elif particle.lepton:
            display_func = fermion
            args["stroke"] = "black"
            args["fill"] = "black"
        elif particle.boson:
            display_func = hadron
            args["stroke"] = "black"
            args["fill"] = "black"
        else:
            display_func = hadron
            args["stroke"] = "black"
            args["fill"] = "black"
        
        self.doc.add_object(display_func(spline = edge.spline, **args))

        if edge.label_center:
            self.doc.add_glyph(particle.pdgid, edge.label_center, 
                               self.options.label_size,
                               ", ".join(map(str, particle.subscripts)))


