from __future__ import division

from ..svg import TexGlyph

from ..graphviz import make_node, make_edge
from ..utils import latexize_particle_name, make_unicode_name

from math import log10

class BaseLayout(object):

    def __init__(self, options):
        self.options = options

    def get_label_string(self, pdgid)
        if TexGlyph.exists(pdgid):
            w, h = TexGlyph.from_pdgid(pdgid).dimensions
            w *= self.options.label_size
            h *= self.options.label_size
            table = '<<table border="1" cellborder="0"><tr>%s</tr></table>>'
            td = '<td height="%.2f" width="%.2f"></td>' % (h, w)
            label = table % td
        else:
            # a pure number here leads graphviz to ignore the edge
            label = "|%i|" % pdgid

class LayoutEdge(object):
    def __init__(self, spline, label_pos=None):
        self.spline = spline
        self.label_pos = label_pos

class LayoutVertex(object):
    def __init__(self, x=None, y=None, r=None):
        self.x = x
        self.y = y
        self.r = r


