from __future__ import division

import re
from time import time
from sys import stderr

from ..svg import SVGDocument
from ..svg import photon, final_photon, gluon, boson, fermion, hadron, vertex

from ..particle import Particle
from ..vertex import Vertex

from .base import Style

class SVGStyle(Style):

    def paint(self):
        self.doc = SVGDocument(self.width, self.height, self.scale)
        self.vertex_args = {"stroke":"black", "fill":"none", "stroke-width" : "0.05"}

        for edge in self.layout.edges:
            if isinstance(edge.item, Particle):
                self.paint_particle(edge)
            else:
                raise NotImplementedError("Cannot draw vertices as edges :(")

        for node in self.layout.nodes:

            if isinstance(node.item, Vertex):
                self.paint_vertex(node)
            else:
                raise NotImplementedError("Cannot draw particles as nodes :(")

        return self.doc.toprettyxml()

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
            display_func = gluon
            args["stroke"] = "green"
        elif particle.photon:
            if particle.final_state:
                display_func = final_photon
            else:
                display_func = photon
            args["stroke"] = "orange"
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
            display_func = boson
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


    def paint_vertex(self, node):
        if not node.style == "invis":
            vx = vertex(node.center, node.width/2, node.height/2, 
                        **self.vertex_args)
            self.doc.add_object(vx)
