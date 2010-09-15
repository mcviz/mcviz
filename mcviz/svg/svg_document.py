from .texglyph import TexGlyph

class XMLNode(object):
    def __init__(self, tag, attrs=None, children=None):
        self.tag = tag
        self.attrs = [] if attrs is None else [attrs]
        self.children = [] if children is None else children

    def appendChild(self, child):
        self.children.append(child)

    def setAttribute(self, attr, val):
        self.attrs.append('%s="%s"' % (attr, val))

    def __str__(self):
        child_data = "".join(str(child) for child in self.children)
        open_tag = "".join(("<"," ".join([self.tag] + self.attrs),">"))
        close_tag = "".join(("</",self.tag,">"))
        return "".join((open_tag, child_data, close_tag))

class RawNode(XMLNode):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return self.data


class SVGDocument(object):
    def __init__(self, wx, wy, scale = 1):

        self.root = XMLNode("svg", 'version="1.1" viewBox="0 0 106.5 53.1" '\
                        'xmlns="http://www.w3.org/2000/svg"'\
                        'xmlns:xlink="http://www.w3.org/1999/xlink"')

        if scale != 1:
            g = XMLNode("g", 'transform="scale(%.5f)"' % scale)
            self.root.appendChild(g)
            self.svg = g
        else:
            self.svg = self.root

        self.defs = XMLNode("defs")
        self.svg.appendChild(self.defs)

    def add_glyph(self, pdgid, center, font_size, subscript = None):
        x, y = center

        if not TexGlyph.exists(pdgid):
            return self.add_text_glyph(pdgid, center, font_size, subscript)

        glyph = TexGlyph.from_pdgid(pdgid)
        if not glyph.xml in self.defs.children:
            self.defs.appendChild(RawNode(glyph.xml))

        if False: #options.debug_labels:
            wx, wy = glyph.dimensions
            wx *= font_size * glyph.default_scale
            wy *= font_size * glyph.default_scale

            box = XMLNode("rect")
            box.setAttribute("x", "%.3f" % (x - wx/2))
            box.setAttribute("y", "%.3f" % (y - wy/2))
            box.setAttribute("width", "%.3f" % wx)
            box.setAttribute("height", "%.3f" % wy)
            box.setAttribute("fill", "red")
            self.svg.appendChild(box)

        x -= 0.5 * (glyph.xmin + glyph.xmax) * font_size * glyph.default_scale
        y -= 0.5 * (glyph.ymin + glyph.ymax) * font_size * glyph.default_scale

        use = XMLNode("use")
        use.setAttribute("x", "%.3f" % (x/font_size))
        use.setAttribute("y", "%.3f" % (y/font_size))
        use.setAttribute("transform", "scale(%.3f)" % (font_size))
        use.setAttribute("xlink:href", "#pdg%i"%pdgid)
        self.svg.appendChild(use)

        if subscript:
            x_sub = x + glyph.xmax * glyph.default_scale * font_size
            y_sub = y + glyph.ymax * glyph.default_scale * font_size
            self.add_subscript(subscript, (x_sub, y_sub), font_size)

    def add_text_glyph(self, pdgid, center, font_size, subscript = None):
        x, y = center
        label = "%i" % pdgid
        width_est = len(label) * font_size * 0.6
        txt = XMLNode("text")
        txt.setAttribute("x", "%.3f" % (x - width_est / 2))
        txt.setAttribute("y", "%.3f" % (y))
        txt.setAttribute("font-size", "%.2f" % (font_size))
        txt.appendChild(RawNode(label))
        self.svg.appendChild(txt)

        if subscript:
            self.add_subscript(subscript, x + width_est/2, y + font_size/3, 
                               font_size)

    def add_subscript(self, subscript, point, font_size):
        txt = XMLNode("text")
        txt.setAttribute("x", "%.3f" % (point[0]))
        txt.setAttribute("y", "%.3f" % (point[1]))
        txt.setAttribute("font-size", "%.2f" % (font_size*0.3))
        txt.appendChild(self.doc.createTextNode(subscript))
        self.svg.appendChild(txt)

    def add_object(self, element):
        self.svg.appendChild(RawNode(element.toxml()))

    def toprettyxml(self):
        return "".join(['<?xml version="1.0" ?>', str(self.root)])

