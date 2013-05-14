import re

from pkg_resources import resource_string, resource_exists
from textwrap import dedent

from .texglyph import TexGlyph
from ..nanodom import XMLNode, RawNode

SCRIPT_TAG = re.compile('<script type="text/ecmascript" xlink:href="([^"]+)"/>')

def mkattrs(**kwargs):
    return " ".join('{0}="{1}"'.format(*i) 
                     for i in sorted(kwargs.iteritems()))

class SVGDocument(object):
    def __init__(self, wx, wy, scale=1):

        self.scale = scale
        viewbox = "0 0 %.1f %.1f" % (wx * scale, wy * scale)
        self.svg = XMLNode("svg", 
            'version="1.1" viewBox="%s" '
            'xmlns="http://www.w3.org/2000/svg" '
            'xmlns:mcviz="http://mcviz.net" '
            'xmlns:xlink="http://www.w3.org/1999/xlink"' % viewbox)
        
        # Adds a big white background rect
        self.svg.appendChild(RawNode('<rect id="background" x="0" y="0" width="%.1f" '
                                     'height="%.1f" style="fill:white;" />'
                                      % ((wx * scale), (wy * scale))))
        
        self.defs = XMLNode("defs")
        self.defined_pdgids = []
        self.svg.appendChild(self.defs)

    def add_glyph(self, reference, pdgid, center, font_size, subscript=None):

        if not TexGlyph.exists(pdgid):
            return self.add_text_glyph(str(pdgid), center, font_size, subscript)

        x, y = center
        # Apply total scale
        font_size *= self.scale
        x *= self.scale
        y *= self.scale

        glyph = TexGlyph.from_pdgid(pdgid)
        if not pdgid in self.defined_pdgids:
            self.defs.appendChild(RawNode(glyph.xml))
            self.defined_pdgids.append(pdgid)

        if False: #options.debug_labels:
            wx, wy = glyph.dimensions
            wx *= font_size * glyph.default_scale
            wy *= font_size * glyph.default_scale

            box = XMLNode("rect")
            box.setAttribute("mcviz:r", reference)
            box.setAttribute("x", "%.3f" % (x - wx/2))
            box.setAttribute("y", "%.3f" % (y - wy/2))
            box.setAttribute("width", "%.3f" % wx)
            box.setAttribute("height", "%.3f" % wy)
            box.setAttribute("fill", "red")
            self.svg.appendChild(box)

        x -= 0.5 * (glyph.xmin + glyph.xmax) * font_size * glyph.default_scale
        y -= 0.5 * (glyph.ymin + glyph.ymax) * font_size * glyph.default_scale

        use = XMLNode("use")
        use.setAttribute("mcviz:r", reference)
        use.setAttribute("x", "%.3f" % (x/font_size))
        use.setAttribute("y", "%.3f" % (y/font_size))
        use.setAttribute("transform", "scale(%.3f)" % (font_size))
        use.setAttribute("xlink:href", "#pdg%i"%pdgid)
        self.svg.appendChild(use)

        xw = glyph.xmax * glyph.default_scale * font_size
        yw = glyph.ymax * glyph.default_scale * font_size
        self.add_subscripts(subscript, (x, y), (xw, yw), font_size)

    def add_text_glyph(self, label, center, font_size, subscript = None):

        x, y = center

        # Apply total scale
        font_size *= self.scale
        x *= self.scale
        y *= self.scale

        width_est = len(label) * font_size * 0.5 # 0.5 is a fudge factor

        if False: #options.debug_labels:
            wx, wy = width_est, font_size
            box = XMLNode("rect")
            box.setAttribute("x", "%.3f" % (x - wx/2))
            box.setAttribute("y", "%.3f" % (y - wy/2))
            box.setAttribute("width", "%.3f" % wx)
            box.setAttribute("height", "%.3f" % wy)
            box.setAttribute("fill", "red")
            self.svg.appendChild(box)
        txt = XMLNode("text")
        txt.setAttribute("x", "%.3f" % (x - width_est / 2))
        txt.setAttribute("y", "%.3f" % (y + font_size / 3)) # 3 is a fudge factor
        txt.setAttribute("font-size", "%.2f" % (font_size))
        txt.appendChild(RawNode(label))
        self.svg.appendChild(txt)

        self.add_subscripts(subscript, (x, y), (width_est/2, font_size/3), font_size)

    def add_subscripts(self, subscripts, center, dimensions, font_size):
        subscripts_by_pos = {}
        for subscript, pos in subscripts:
            subscripts_by_pos.setdefault(pos, []).append(subscript)
    
        for pos, subscripts in sorted(subscripts_by_pos.iteritems()):
            subscript = ", ".join(map(str, subscripts))
            x, y  = center
            xw, yw = dimensions
            if pos == "sub":
                x, y = x + xw, y + yw + font_size*0.1
            elif pos == "super":
                x, y = x + xw, y - font_size*0.1
            elif pos == "under":
                x, y = x - xw/2, y + yw + font_size*0.4
            elif pos == "over":
                x, y = x - xw/2, y - font_size*0.4
            elif pos == "left":
                x, y = x - len(subscript)/5., y

            txt = XMLNode("text")
            txt.setAttribute("x", "%.3f" % (x))
            txt.setAttribute("y", "%.3f" % (y))
            txt.setAttribute("font-size", "%.2f" % (font_size*0.3))
            txt.appendChild(subscript)
            self.svg.appendChild(txt)

    def add_object(self, reference, element):
        element.setAttribute("mcviz:r", reference)
        assert not element.getAttribute("transform")
        element.setAttribute("transform", "scale(%.3f)" % (self.scale))
        self.svg.appendChild(RawNode(element.toxml()))

    def toprettyxml(self):
        return "".join(['<?xml version="1.0" encoding="UTF-8"?>', unicode(self.svg)])


class NavigableSVGDocument(SVGDocument):
    """
    An SVG document which has the capability to clik and scroll to navigate the
    document, implemented in javascript.
    """

    def __init__(self, *args, **kwargs):
        super(NavigableSVGDocument, self).__init__(*args, **kwargs)
        
        # No viewbox for a NavigableSVGDocument
        self.svg.attrs = ['version="1.1" '
                          'xmlns="http://www.w3.org/2000/svg" '
                          'xmlns:xlink="http://www.w3.org/1999/xlink" '
                          'xmlns:mcviz="http://mcviz.net" '
                          'id="whole_document"',
                          'onload="mcviz_init(evt)"']
        self.full_svg_document = self.svg
        self.svg = XMLNode("g", 'id="everything"')
        self.full_svg_document.appendChild(self.svg)
    
    def inject_javascript(self, javascript_text):
        
        def match(m):
            (javascript_filename,) = m.groups()
            if not resource_exists("mcviz.utils.svg.data", javascript_filename):
                return
                
            args = "mcviz.utils.svg.data", javascript_filename
            
            # ]]> is not allowed in CDATA and it appears in jquery!
            # Try to prevent that..
            javascript = resource_string(*args).replace("']]>'", "']' + ']>'")
            
            stag = '<script type="text/javascript"><![CDATA[\n%s\n]]></script>'
            
            return stag % javascript.decode("UTF-8")
        
        return SCRIPT_TAG.sub(match, javascript_text)
    
    def toprettyxml(self):
        script_fragments = resource_string("mcviz.utils.svg.data", 
                                           "navigable_svg_fragment.xml")
        
        script_fragments = self.inject_javascript(script_fragments)
                         
        #self.full_svg_document.appendChild(self.svg)
        self.full_svg_document.appendChild(RawNode(script_fragments))
        self.svg = self.full_svg_document
        result = super(NavigableSVGDocument, self).toprettyxml()
        return result
        
        
class MCVizWebNavigableSVGDocument(NavigableSVGDocument):
    """
    Overrides inject_javascript in the case that we're running within mcviz.web
    so that the URLs are correct
    """
    def inject_javascript_(self, javascript_text):
        
        def match(m):
            (javascript_filename,) = m.groups()
            
            #from mcviz.web import get_mcviz_data_url
            #data_url = get_mcviz_data_url()
            from pkg_resources import resource_filename
            data_url = "file://" + resource_filename("mcviz.utils.svg.data", "/")
            javascript_path = data_url + javascript_filename
            
            stag = '<script type="text/javascript" xlink:href="%s"></script>'
            return stag % javascript_path
        
        return SCRIPT_TAG.sub(match, javascript_text)
    
    def add_event_data(self, graph):
    
        element = XMLNode("mcviz:eventdata", attrs='xmlns="http://mcviz.net"')
        self.full_svg_document.appendChild(element)
        
        event = graph.event
        
        graph.particles
        
        for i, p in sorted(event.particles.iteritems()):
            element.appendChild(XMLNode("particle", mkattrs(
                id=p.no,
                status=p.status,
                pdgid=p.pdgid,
                color=p.color,
                anticolor=p.anticolor,
                e=p.e,
                pt=p.pt,
                eta=p.eta,
                phi=p.phi,
                m=p.m,
                daughters=" ".join("{0.no}".format(d) for d in sorted(p.daughters)),
            )))
            
    
        element = XMLNode("mcviz:viewdata", attrs='xmlns="http://mcviz.net"')
        self.full_svg_document.appendChild(element)
        
        for p in graph.particles:            
            element.appendChild(XMLNode("particle", mkattrs(
                id=p.reference,
                vin=p.start_vertex.reference,
                vout=p.end_vertex.reference,
                event=" ".join("{0}".format(i) for i in sorted(p.represented_numbers)),
            )))
        
        for vertex in graph.vertices:
            element.appendChild(XMLNode("vertex", mkattrs(
                id=vertex.reference,
                event=" ".join("{0}".format(i) for i in sorted(vertex.represented_numbers)),
                pin=" ".join(p.reference for p in vertex.incoming),
                pout=" ".join(p.reference for p in vertex.outgoing),
            )))
        
        info = RawNode(dedent("""
            <foreignObject x="5" y="5" width="300" height="400">
                <html xmlns="http://www.w3.org/1999/xhtml">
                <body style="margin: 0px;" id="interface">
                    <!-- 
                        Webkit hack. Works because the border is correctly drawn over the SVG.
                    -->
                    <span style="border: 400px solid rgba(180, 180, 250, .9);">.</span>
                    
                    <div id="particle_info" style="padding: 0px; margin-left: 0.3em; margin-top: -0.7em;">
                    
                        <button id="hidelowpt">Hide low pt</button>
                        <button id="hidehieta">Hide eta > 2</button>
                        <button id="reset">Show all</button>
                    
                        <div>Particle <span id="id"></span> in:<span id="vin"></span> out:<span id="vout"></span></div>
                        <div id="contents">
                        </div>
                        <div id="template" style="display: none">
                            <div id="pdgid"></div>
                            <div id="pt"></div>
                            <div id="eta"></div>
                            <div id="phi"></div>
                            <div id="e"></div>
                            <div id="m"></div>
                        </div>
                    </div>
                    
                </body>
                </html>
            </foreignObject>

            <rect stroke="black" stroke-width="2px" x="5" y="5" width="300" height="400" fill="none"/>
        """))
        
        self.svg.appendChild(RawNode(dedent("""
            <circle cx="-100" cy="-100" r="0.8px" stroke-width="0.1px" stroke="red" id="selected-particle" fill="none"/>
        """)))
        
        self.full_svg_document.appendChild(info)
        
        
