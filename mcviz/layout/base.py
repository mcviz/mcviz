from __future__ import division

from ..svg import TexGlyph

from ..graphviz import make_node, make_edge
from ..utils import latexize_particle_name, make_unicode_name

from math import log10

class BaseLayout(object):

    def __init__(self, options):
        self.options = options

    def get_label_string(self, pdgid):
        if self.options.svg and TexGlyph.exists(pdgid):
            w, h = TexGlyph.from_pdgid(pdgid).dimensions
            w *= self.options.label_size
            h *= self.options.label_size
            table = '<<table border="1" cellborder="0"><tr>%s</tr></table>>'
            td = '<td height="%.2f" width="%.2f"></td>' % (h, w)
            label = table % td
        else:
            # a pure number here leads graphviz to ignore the edge
            label = "|%i|" % pdgid
        return label

    def print_header(self):
        print("digraph pythia {")
        print(self.options.extra_dot)
        if self.options.fix_initial:
            width = self.options.width
            height = width * float(self.options.ratio)
            stretch = self.options.stretch
            print('size="%s,%s!";' % (width, height))
        print("ratio=%s;" % self.options.ratio)
        print("edge [labelangle=90, fontsize=%.2f]" % (72*self.options.label_size))

    def print_footer(self):
        print("}")

class LayoutEdge(object):
    def __init__(self, spline, label_pos=None):
        self.spline = spline
        self.label_pos = label_pos

class LayoutVertex(object):
    def __init__(self, x=None, y=None, r=None):
        self.x = x
        self.y = y
        self.r = r


