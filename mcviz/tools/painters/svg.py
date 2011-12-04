from .. import log; log = log.getChild(__name__)

from ..tools import FundamentalTool, Arg

from mcviz.utils.timer import Timer; timer = Timer(log)
from mcviz.utils.svg.svg_document import (
    XMLNode, RawNode,
    SVGDocument, NavigableSVGDocument, MCVizWebNavigableSVGDocument)
from mcviz.utils.svg import (identity, invisible, photon, final_photon,
                             gluon, multigluon, boson, fermion, hadron,
                             vertex, gluino, sfermion, chargino, cut, jet)

from .painters import StdPainter


class SVGPainter(StdPainter, FundamentalTool):
    """
    Write out the result to plain SVG.
    """
    _name = "svg"
    _args = [
            Arg("debug", Arg.bool, "add debug information into the SVG", default=False),
            ]

    document_creator = SVGDocument

    type_map = {"identity": identity,
                "invisible": invisible,
                "photon": photon, 
                "final_photon": final_photon,
                "gluon": gluon, 
                "gluino": gluino,
                "multigluon": multigluon, 
                "boson": boson, 
                "fermion": fermion, 
                "sfermion": sfermion,
                "chargino": chargino,
                "hadron": hadron, 
                "vertex": vertex,
                "cut":cut,
                "jet":jet
                }

    def __call__(self, workspace, layout):
        with timer("create the SVG document"):
            args = layout.width, layout.height, layout.scale
            self.label_size = layout.label_size
            self.doc = self.document_creator(*args)
            cl = XMLNode("mcviz:cmdline", children=[RawNode(workspace.cmdline)])
            self.doc.svg.children[:0] = [cl]
            for edge in layout.edges:
                if not edge.spline:
                    # Nothing to paint!
                    continue
                self.paint_edge(edge)
            for node in layout.nodes:
                self.paint_vertex(node)

            if hasattr(self, "paint_additional"):
                self.paint_additional(layout)

            if self.options["debug"]:
                w, h = layout.width*layout.scale, layout.height*layout.scale
                def line(x1, y1, x2, y2, w):
                    n = RawNode('<line x1="%.4f" y1="%.4f" x2="%.4f" y2="%.4f" style="stroke:rgb(255,0,0);stroke-width:%.4f"/>' % (x1, y1, x2, y2, w))
                    self.doc.svg.children[:0] = [n]
                def text(x, y, size, txt):
                    n = RawNode('<text x="%.4f" y="%.4f" font-size="%.4f">%s</text>' % (x, y, size, txt))
                    self.doc.svg.children[:0] = [n]
                sz = (w+h)/100.0
                line(0, 0, w, 0, sz)
                line(w, 0, w, h, sz)
                line(w, h, 0, h, sz)
                line(0, h, 0, 0, sz)
                text(2*sz, -3*sz , 0.8*sz, "Scale : %.4f" % layout.scale)
                text(2*sz, -2*sz, 0.8*sz,  "Width : %.4f" % w)
                text(2*sz, -1*sz, 0.8*sz,  "Height: %.4f" % h)


        self.write_data(self.doc.toprettyxml())

    def paint_edge(self, edge):
        """
        In the dual layout, paint a connection between particles
        """

        if edge.show and edge.spline:
            display_func = self.type_map.get(edge.style_line_type, hadron)
            if edge.style_line_type == "cut":
                display = display_func(spline=edge.spline, n_represented=edge.item.n_represented, **edge.style_args)
            else: display = display_func(spline=edge.spline, **edge.style_args)
            self.doc.add_object(edge.reference, display)

        if edge.label and edge.label_center:
            self.doc.add_glyph(edge.reference, edge.label, edge.label_center,
                               edge.label_size, edge.item.subscripts)

    def paint_vertex(self, node):
        if node.show and node.center:
            vx = vertex(node.center, node.width/2, node.height/2,
                        **node.style_args)
            self.doc.add_object(node.reference, vx)
           
        if not node.label is None and node.center:
            self.doc.add_glyph(node.reference, node.label, node.center.tuple(),
                               node.label_size, node.item.subscripts)


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
        self.doc.add_event_data(layout.graph)
