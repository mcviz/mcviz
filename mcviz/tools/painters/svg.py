from logging import getLogger; log = getLogger("mcviz.painters.svg")

from mcviz.tools import FundamentalTool

from mcviz.utils import timer
from mcviz.utils.svg.svg_document import (
    SVGDocument, NavigableSVGDocument, MCVizWebNavigableSVGDocument)
from mcviz.utils.svg import (identity, photon, final_photon, gluon, multigluon,
                             boson, fermion, hadron, vertex)

from painters import StdPainter


class SVGPainter(StdPainter, FundamentalTool):
    """
    Write out the result to plain SVG.
    """
    _name = "svg"

    document_creator = SVGDocument

    type_map = {"identity": identity,
                "photon": photon, 
                "final_photon": final_photon,
                "gluon": gluon, 
                "multigluon": multigluon, 
                "boson": boson, 
                "fermion": fermion, 
                "hadron": hadron, 
                "vertex": vertex
                }

    def __call__(self, layout):
        with timer("create the SVG document"):
            args = layout.width, layout.height, layout.scale
            self.label_size = layout.label_size
            self.doc = self.document_creator(*args)
            for edge in layout.edges:
                if not edge.spline:
                    # Nothing to paint!
                    continue
                self.paint_edge(edge)
            for node in layout.nodes:
                self.paint_vertex(node)

            if hasattr(self, "paint_additional"):
                self.paint_additional(layout)

        self.write_data(self.doc.toprettyxml())

    def paint_edge(self, edge):
        """
        In the dual layout, paint a connection between particles
        """

        if edge.show and edge.spline:
            display_func = self.type_map.get(edge.style_line_type, hadron)
            display = display_func(spline=edge.spline, **edge.style_args)
            self.doc.add_object(edge.reference, display)

        if edge.label and edge.label_center:
            self.doc.add_glyph(edge.reference, edge.label, edge.label_center,
                           self.label_size, edge.item.subscripts)


    def paint_vertex(self, node):
        if node.show and node.center:
            vx = vertex(node.center, node.width/2, node.height/2,
                        **node.style_args)
            self.doc.add_object(node.reference, vx)
           
        if not node.label is None and node.center:
            self.doc.add_glyph(node.reference, node.label, node.center.tuple(),
                               self.label_size,
                               node.item.subscripts)


class NavigableSVGPainter(SVGPainter):
    """
    Write out additional javascript into the SVG, making it easy to navigate
    from a recent web browser, through click-drag and scrollwheel.
    """
    _name = "navisvg"
    document_creator = NavigableSVGDocument
    
    
class MCVizWebNavigableSVGPainter(SVGPainter):
    """
    UNDOCUMENTED
    Used for the web
    """
    _name = "webnavisvg"
    document_creator = MCVizWebNavigableSVGDocument
    
    def paint_additional(self, layout):
        for particle in layout.graph.particles:
            self.doc.add_particle(particle)
