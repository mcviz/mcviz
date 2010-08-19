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

    def layout(self, graph):
    
        # Label particles by id if --show-id is on the command line.
        if self.options.show_id:
            def label_particle_no(particle):
                if not particle.gluon:
                    return particle.no
                    
            self.annotate_particles(graph.particles.values(), label_particle_no)
    
        print("digraph pythia {")
        print(self.options.extra_dot)
        if self.options.fix_initial:
            width = self.options.width
            height = width * float(self.options.ratio)
            stretch = self.options.stretch
            print('size="%s,%s!";' % (width, height))
        print("ratio=%s;" % self.options.ratio)
        print("edge [labelangle=90, fontsize=%.2f]" % (72*self.options.label_size))

        self.print_graph(graph)

        print("}")
    
    def annotate_particles(self, particles, annotate_function):
        """
        Add a subscript for all particles. annotate_function(particle) should
        return a value to be added.
        """
        for particle in particles:
            subscript = annotate_function(particle)
            if subscript:
                particle.subscripts.append(subscript)
                
    def print_graph(self):
        pass

class LayoutEdge(object):
    def __init__(self, spline, label_pos=None):
        self.spline = spline
        self.label_pos = label_pos

class LayoutVertex(object):
    def __init__(self, x=None, y=None, w=None, h=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


