from __future__ import division

from ..svg import SVGDocument
from ..svg import photon, final_photon, gluon, boson, fermion, hadron, vertex
from ..particle import Particle
from ..vertex import Vertex

from .base import Style

class SVGStyle(Style):

    def paint(self):
        # if we do not know the scale; (i.e. bounding box) calculate it
        x_min, y_min, x_max, y_max = 0, 0, 0, 0
        def get_minmax(x,y):
            return min(x, x_min), min(y, y_min), max(x, x_max), max(y, y_max)

        for edge in self.layout.edges:
            if edge.spline:
                x0, x1, y0, y1 = edge.spline.boundingbox
                x_min, y_min, x_max, y_max = get_minmax(x0, y0)
                x_min, y_min, x_max, y_max = get_minmax(x1, y0)
                x_min, y_min, x_max, y_max = get_minmax(x0, y1)
                x_min, y_min, x_max, y_max = get_minmax(x1, y1)

        for node in self.layout.nodes:
            if node.center:
                x_min, y_min, x_max, y_max = get_minmax(node.center.x, node.center.y)
        wx = x_max - x_min
        wy = y_max - y_min
        if not self.width:
            self.width = 100
            self.height = 100
            self.scale = 1
        else:
            self.scale = min(self.width/wx, self.height/wy)


        self.doc = SVGDocument(self.width, self.height, self.scale)
        self.vertex_args = {"stroke":"black", "fill":"none", "stroke-width" : "0.05"}

        for edge in self.layout.edges:
            if not edge.spline:
                # Nothing to paint!
                continue
                
            if isinstance(edge.item, Particle):
                self.paint_particle(edge)
            else:
                self.paint_edge(edge)

        for node in self.layout.nodes:
            if isinstance(node.item, Vertex):
                self.paint_vertex(node)
            else:
                self.paint_vertex(node)
                #raise NotImplementedError("Cannot draw particles as nodes :(")

        return self.doc.toprettyxml()

    def paint_edge(self, edge):
        """
        In the dual layout, paint a connection between particles
        """
        display_func = hadron
        args = {}
        args["energy"] = 0.2
        args["stroke"] = "black"
        args["fill"] = "black"
        args["stroke-width"] = 0.05
        args["scale"] = 0.1

        if edge.spline:
            self.doc.add_object(display_func(spline=edge.spline, **args))
            
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
       
        if edge.spline:
            self.doc.add_object(display_func(spline = edge.spline, **args))
        self.label_edge(edge)

    def label_edge(self, edge):
        if edge.label_center:
            self.doc.add_glyph(edge.item.pdgid, edge.label_center,
                               self.options.label_size,
                               ", ".join(map(str, edge.item.subscripts)))

    def paint_vertex(self, node):
        if not node.style == "invis" and node.center:
            vx = vertex(node.center, node.width/2, node.height/2, 
                        **self.vertex_args)
            self.doc.add_object(vx)
            
            # This needs fixing for the Feynman layout, if we want node labels.
            if node.label and isinstance(node.item, Particle):
                self.doc.add_glyph(node.item.pdgid, node.center.tuple(),
                                   self.options.label_size,
                                   ", ".join(map(str, node.item.subscripts)))
