from .texglyph import TexGlyph

from xml.dom.minidom import getDOMImplementation, Document
dom_impl = getDOMImplementation()

class SVGDocument(Document):
    def __init__(self, wx, wy, scale = 1):

        self.doc = dom_impl.createDocument("http://www.w3.org/2000/svg", "svg", None)

        self.svg = self.doc.documentElement
        self.svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")
        self.svg.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink")
        self.svg.setAttribute("viewBox", "0 0 %.1f %.1f" % (wx * scale, 
                                                            wy * scale))
        self.svg.setAttribute("version", "1.1")

        if scale != 1:
            g = self.doc.createElement("g")
            g.setAttribute("transform","scale(%.5f)" % scale)
            self.svg.appendChild(g)
            self.svg = g

        self.defs = self.doc.createElement("defs")
        self.svg.appendChild(self.defs)

    def add_glyph(self, pdgid, x, y, font_size):
        glyph = TexGlyph.from_pdgid(pdgid)
        glyph_scale = glyph.default_scale * font_size
        #glyph.dom.setAttribute("transform", "scale(%.5f)" % (glyph_scale))
        if not glyph.dom in self.defs.childNodes:
            self.defs.appendChild(glyph.dom)


        wx, wy = glyph.dimensions
        wx *= glyph_scale
        wy *= glyph_scale

        box = self.doc.createElement("rect")
        box.setAttribute("x", "%.2f" % (x - wx/2))
        box.setAttribute("y", "%.2f" % (y - wy/2))
        box.setAttribute("width", "%.2f" % wx)
        box.setAttribute("height", "%.2f" % wy)
        box.setAttribute("fill", "red")
        self.svg.appendChild(box)

        x -= (glyph.xmin + glyph.xmax) * glyph_scale
        y -= (glyph.ymin + glyph.ymax) * glyph_scale

        use = self.doc.createElement("use")
        use.setAttribute("x", "%.2f" % x)
        use.setAttribute("y", "%.2f" % y)
        use.setAttribute("x", "0")
        use.setAttribute("y", "0")
        use.setAttribute("transform", "scale(%.5f) translate(%.2f,%.2f)" % (glyph_scale, x/glyph_scale, y/glyph_scale))
        use.setAttribute("xlink:href", "#pdg%i"%pdgid)
        self.svg.appendChild(use)

    def add_object(self, element):
        self.svg.appendChild(element)

    def toprettyxml(self):
        return self.doc.toprettyxml()

