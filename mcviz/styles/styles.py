from __future__ import division

from math import log as ln

from logging import getLogger; log = getLogger("mcviz.styles")

from ..view_particle import ViewParticle
from ..view_vertex import ViewVertex

from ..tool import Style, tool

@tool
class Default(Style):
    _name = "Default"
    def __call__(self, layout):
        edge_args = {}
        edge_args["energy"] = 0.2
        edge_args["stroke"] = "black"
        edge_args["fill"] = "black"
        edge_args["stroke-width"] = 0.05
        edge_args["scale"] = 0.1

        for edge in layout.edges:
            edge.style_line_type = "identity"
            edge.style_args.update(edge_args)

        node_args = {"stroke":"black", "fill":"none", "stroke-width" : "0.05"}
        for node in layout.nodes:
            node.style_args.update(node_args)


def particle_color(particle):
    if particle.gluon:
        return "green"
    elif particle.photon:
        return "orange"
    elif particle.colored:
        if particle.color:
            return "red"
        else:
            return "blue"
    else:
        return "black"


@tool
class SimpleColors(Style):
    _name = "SimpleColors"
    def __call__(self, layout):
        """ just do some simple coloring of lines """
        for edge in layout.edges:
            if isinstance(edge.item, ViewParticle):
                edge.style_args["stroke"] = edge.style_args["fill"] = particle_color(edge.item)
            else:
                pass
                # no coloring for vertices-as-lines

        initial_color = "cyan"
        for node in layout.nodes:
            if isinstance(node.item, ViewVertex):
                if node.item.initial:
                    node.style_args["fill"] = initial_color
            else:
                # label in Inline; particle in Dual
                # fill will be ignored in inline
                node.style_args["stroke"] = node.style_args["fill"] = particle_color(node.item)
                node.style_args["fill"] = node.style_args["fill"].replace("black", "white")
                if node.item.initial_state:
                    node.style_args["fill"] = initial_color

@tool
class FancyLines(Style):
    _name = "FancyLines"
    def __call__(self, layout):
        """ set fancy line types, curly gluons, wavy photons etc."""
        for edge in layout.edges:
            particle = edge.item
            # colouring
            if "cluster" in particle.tags:
                edge.style_line_type = "hadron"
                edge.style_args["scale"] = 0.8
                edge.style_args["stroke-width"] = 0.4
            elif particle.gluon:
                edge.style_line_type = "gluon"
            elif particle.photon:
                if particle.final_state:
                    edge.style_line_type = "final_photon"
                else:
                    edge.style_line_type = "photon"
            elif particle.colored:
                edge.style_line_type = "fermion"
            elif particle.lepton:
                edge.style_line_type = "fermion"
            elif particle.boson:
                edge.style_line_type = "boson"
            else:
                edge.style_line_type = "hadron"
                
@tool
class LineWidthPt(Style):
    _name = "LineWidthPt"
    def __call__(self, layout):
        for edge in layout.edges:
            particle = edge.item

            edge.style_args["stroke-width"] = ln(particle.pt+1)*0.1 + 0.01
            
@tool
class ThickenColor(Style):
    _name = "ThickenColor"
    _args = [("color_id", int)]
    def __call__(self, layout):
        color_id = self.options["color_id"]
        for edge in layout.edges:
            particle = edge.item
            if color_id in (particle.color, particle.anticolor):
                edge.style_args["stroke-width"] = 0.5

@tool
class StatusColor(Style):
    _name = "StatusColor"
    def __call__(self, layout):
        from mcviz.styles import rainbow_color
        
        colors = [rainbow_color(i/10, 0.25 + 0.5*(i%2)) for i in xrange(10)]
        log.warning("Colors are: %r", colors)
        
        from mcviz.layouts import FeynmanLayout, DualLayout
        if isinstance(layout, FeynmanLayout):
            for edge in layout.edges:
                particle = edge.item
                edge.style_args["stroke"] = colors[abs(particle.status) // 10]
                
        elif isinstance(layout, DualLayout):
            for node in layout.nodes:
                particle = node.item
                if hasattr(particle, "status"):
                    node.style_args["fill"] = colors[abs(particle.status) // 10]
            
