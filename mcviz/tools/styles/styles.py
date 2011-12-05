from __future__ import division

from .. import log; log = log.getChild(__name__)

from math import log as ln

from mcviz.tools import Style, Arg
from mcviz.tools.layouts import FeynmanLayout, DualLayout
from mcviz.utils import rainbow_color
from mcviz.graph import ViewParticle, ViewVertex


DEFAULT_NODE_ARGS = {"stroke": "black", "fill": "white", "stroke-width": "0.05"}
DEFAULT_EDGE_ARGS = {"energy": 0.2, "stroke": "black", "fill": "black", 
                     "stroke-width": 0.05, "scale": 1}

class Default(Style):
    "The default style. All lines are black, with no enhancements."
    _name = "Default"
    
    def __call__(self, layout):
        for edge in layout.edges:
            if "cut_summary" in edge.item.tags:
                edge.style_line_type = "cut"
                edge.style_args.update(DEFAULT_EDGE_ARGS)
                try:
                    edge.style_args["n"] = edge.n_represented
                except AttributeError:
                    pass
            else:
                edge.style_line_type = "identity"
                edge.style_args.update(DEFAULT_EDGE_ARGS)
        
        for node in layout.nodes:
            node.style_args.update(DEFAULT_NODE_ARGS)


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
    elif particle.boson:
        return "magenta"
    elif particle.lepton:
        return "#EFDECD" # "Almond"
    else:
        return "black"


class SimpleColors(Style):
    """
    Gluons are drawn green, coloured particles red and anti-coloured blue.
    Photons are orange, bosons magenta and leptons almond.
    """
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
                elif "gluball" in node.item.tags:
                    node.style_args["fill"] = "#22bb44"
            else:
                # label in Inline; particle in Dual
                # fill will be ignored in inline
                node.style_args["fill"] = particle_color(node.item)
                node.style_args["fill"] = node.style_args["fill"].replace("black", "white")
                if node.item.initial_state:
                    node.style_args["fill"] = initial_color


class Highlight(Style):
    """
    Colour particles matching some criteria.
    e.g. -sHighlight:6:color=blue highlights top quarks in blue,
         -sHighlight:param=eta:0:2.5 highlights central particles,
         -sHighlight:1000000:2000015 highlights susy particles
    """
    _name = "Highlight"
    _args = [Arg("start", float, "start pdgid to highlight", default=6),
             Arg("end", float, "end pdgid", default=0),
             Arg("color", str, "highlight color", default="red"),
             Arg("param", str, "parameter", default="pdgid"),]

    def __call__(self, layout):
        """ highlight all particles in rage of interest """
        start = self.options["start"]
        if self.options["end"] == 0:
            end = start
        else:
            end = self.options["end"]
        color = self.options["color"]
        param = self.options["param"]

        for edge in layout.edges:
            try:
                if start <= abs(getattr(edge.item, param)) <= end:
                  edge.style_args["stroke"] = edge.style_args["fill"] = color
            except AttributeError: # looks like the item doesn't have that param
                pass

        for node in layout.nodes:
            try:
                # label in Inline; particle in Dual
                if start <= abs(getattr(node.item, param)) <= end:
                    node.style_args["fill"] = color
            except AttributeError: # looks like the item doesn't have that param
                pass


class FancyLines(Style):
    """
    Draw particle lines with arrows on them, and draw gluons with curls
    """
    _name = "FancyLines"
    _args = [Arg("scale", float, "scale of the line effects", default=1.0),]
    
    def __call__(self, layout):
        """ set fancy line types, curly gluons, wavy photons etc."""
        for edge in layout.edges:
            particle = edge.item
            edge.style_args["scale"] = 0.2 * self.options["scale"]
            if not hasattr(particle, "gluon"):
                return
            # colouring
            if "jet" in particle.tags:
                edge.style_line_type = "jet"
            elif "cluster" in particle.tags:
                edge.style_line_type = "hadron"
                edge.style_args["scale"] = 0.2 * self.options["scale"]
                edge.style_args["stroke-width"] = 0.2
            elif "cut_summary" in particle.tags:
                edge.style_line_type = "cut"
                try:
                    edge.style_args["n"] = edge.n_represented
                except AttributeError:
                    pass # Edge has no n_represented property
            elif particle.gluon:
                edge.style_args["scale"] = 0.2 * self.options["scale"]
                edge.style_line_type = "gluon"
            elif particle.photon:
                if particle.final_state:
                    edge.style_line_type = "final_photon"
                else:
                    edge.style_line_type = "photon"
            elif particle.invisible:
                edge.style_line_type = "invisible"
            elif particle.squark:
                edge.style_line_type = "sfermion"
            elif particle.colored:
                edge.style_line_type = "fermion"
            elif particle.lepton:
                edge.style_line_type = "fermion"
            elif particle.boson:
                edge.style_line_type = "boson"
            elif particle.gluino:
                edge.style_args["scale"] = 0.2 * self.options["scale"]
                edge.style_line_type = "gluino"
            elif particle.chargino:
                edge.style_line_type = "chargino"
            elif particle.slepton:
                edge.style_line_type = "sfermion"
            else:
                edge.style_line_type = "hadron"
                

class LineWidthPt(Style):
    """
    Make the particle line width dependent on the transverse momentum.
    """
    _name = "LineWidthPt"
    _args = [Arg("scale", float, "scale of the line effects", default=1.0),
             Arg("min", float, "minimal width of a line", default=0.1),]
    def __call__(self, layout):
        if isinstance(layout, FeynmanLayout):
            elements = layout.edges
        else:
            elements = layout.nodes
            for edge in layout.edges:
                particle = edge.going
                if hasattr(particle, "pt"):
                    edge.style_args["stroke-width"] = self.options["min"] + self.options["scale"]*ln(particle.pt+1)*0.1

        for element in elements:
            particle = element.item
            if hasattr(particle, "pt"):
                element.style_args["stroke-width"] = self.options["min"] + +self.options["scale"]*ln(particle.pt+1)*0.1


class LabelSizePt(Style):
    """
    Make the label size dependent on the transverse momentum.
    """
    _name = "LabelSizePt"
    _args = [Arg("scale", float, "scale of the line effects", default=1.0),]
    def __call__(self, layout):
        for element in list(layout.edges) + list(layout.nodes):
            particle = element.item
            if not hasattr(particle, "pt"):
                continue
            element.label_size = self.options["scale"]*ln(particle.pt+1)*0.5 + 0.5


class ThickenColor(Style):
    """
    This can be used to make a single (anti)colour line very thick, so that it 
    can be easily seen.
    """

    _name = "ThickenColor"
    _args = [Arg("color_id", int, "id of the color to thicken")]
    
    def __call__(self, layout):
        color_id = self.options["color_id"]
        for edge in layout.edges:
            particle = edge.item
            if color_id in (particle.color, particle.anticolor):
                edge.style_args["stroke-width"] = 0.5


class StatusColor(Style):
    """
    Colour by status codes
    """
    _name = "StatusColor"
    def __call__(self, layout):

        colors = [rainbow_color(i/10, 0.25 + 0.5*(i%2)) for i in xrange(10)]
        log.info("Colors are: %r", colors)
        
        if isinstance(layout, FeynmanLayout):
            for edge in layout.edges:
                particle = edge.item
                edge.style_args["stroke"] = colors[abs(particle.status) // 10]
                
        elif isinstance(layout, DualLayout):
            for node in layout.nodes:
                particle = node.item
                if hasattr(particle, "status"):
                    node.style_args["fill"] = colors[abs(particle.status) // 10]
            

@Style.decorate("ColorPassing")
def color_passing(layout):
	for edge in layout.edges:
		if "pass" in edge.item.tags:
			edge.style_args["stroke"] = "#00ffff"
			
@Style.decorate("ColorFinal")
def color_final(layout):
	for edge in layout.edges:
		if "pass" in edge.item.tags: #edge.item.final_state:
			edge.style_args["stroke"] = "#ff0000"
