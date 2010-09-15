from __future__ import division

from ..svg import photon, final_photon, gluon, boson, fermion, hadron, vertex, multigluon

from .svg import SVGStyle

class StrongStyle(SVGStyle):

    def paint(self):
        colors = [e.item.color for e in self.layout.edges]
        anticolors = [e.item.anticolor for e in self.layout.edges]
        unique_colors = sorted(list(set(colors + anticolors)))
        self.cmap = dict(zip(unique_colors, ["red", "lime", "blue"]*(len(unique_colors)//3+1)))
        self.amap = dict(zip(unique_colors, ["cyan", "magenta", "yellow"]*(len(unique_colors)//3+1)))
        return super(StrongStyle, self).paint()

    def paint_particle(self, edge):
        
        particle = edge.item

        # set garish defaults args to make oversights obvious
        display_func = hadron
        args = {}
        args["energy"] = 0.5
        args["stroke"] = "pink"
        args["fill"] = "pink"
        args["stroke-width"] = 0.05
        args["scale"] = 0.1

        ao = self.doc.add_object 
        # colouring
        if particle.gluon:
            display_func = multigluon
            args["color"] = self.cmap[particle.color]
            args["anticolor"] = self.amap[particle.anticolor]
        elif particle.photon:
            if particle.final_state:
                display_func = final_photon
            else:
                display_func = photon
            args["stroke"] = "orange"
        elif particle.colored:
            display_func = fermion
            if particle.color:
                args["stroke"] = self.cmap[particle.color]
                args["fill"] = self.cmap[particle.color]
            else:
                args["stroke"] = self.amap[particle.anticolor]
                args["fill"] = self.amap[particle.anticolor]
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
        self.label_edge(edge)

