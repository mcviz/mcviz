from __future__ import division

from math import log10
from itertools import chain

from ..svg import TexGlyph

from ..graphviz import make_node, make_edge, PlainOutput
from ..utils import latexize_particle_name, make_unicode_name, Point2D


class BaseLayout(object):
    """
    Class that encapsulates the layout and styling information of the graph
    """

    def __init__(self, graph, options):
        self.options = options
        self.subgraphs = {None: []}
        self.subgraph_options = {}
        self.edges = []
        self.width, self.height, self.scale = None, None, 1.0
            
        # Label particles by id if --show-id is on the command line.
        if "id" in self.options.subscript:
            def label_particle_no(particle):
                if not particle.gluon:
                    return particle.reference
            self.annotate_particles(graph.particles, label_particle_no)

        if "color" in self.options.subscript:
            self.annotate_particles(graph.particles, lambda p: p.color)
            self.annotate_particles(graph.particles, lambda p: -p.anticolor)

        # create node and edge objects from the graph
        self.fill_objects(graph)

        # do custom processing of the layout objects here
        self.process()

    def fill_objects(self, graph):

        for vertex in graph.vertices:
            self.add_object(self.get_vertex(vertex))

        for particle in graph.particles:
            self.add_object(self.get_particle(particle))

    def add_object(self, obj):
        if obj is None:
            return
        elif hasattr(obj, "__iter__"):
            for o in obj:
                self.add_object(o)
            return
            
        obj.item.layout_objects.append(obj)
        if isinstance(obj, LayoutNode):
            self.subgraphs.setdefault(obj.subgraph, []).append(obj)
        elif isinstance(obj, LayoutEdge):
            self.edges.append(obj)
        else:
            raise NotImplementedError()

    def process(self):
        pass

    @property
    def nodes(self):
        return chain(*self.subgraphs.values())

    @property
    def subgraph_names(self):
        names = sorted(self.subgraphs.keys())
        # move "None" (sorted always first) to the back
        return names[1:] + [None]

    @property
    def dot(self):
        out = ["digraph pythia {"]
        out.append(self.options.extra_dot)
        if self.options.fix_initial:
            width = self.options.width
            height = width * float(self.options.ratio)
            stretch = self.options.stretch
            out.append('size="%s,%s!";' % (width, height))
        out.append("ratio=%s;" % self.options.ratio)
        out.append("edge [labelangle=90, fontsize=%.2f]" % (72*self.options.label_size))

        for name in self.subgraph_names:
            nodelist = self.subgraphs.get(name, [])
            subgraph = self.subgraph_options.get(name, [])
            subgraph.extend(node.dot for node in nodelist)
            if name:
                subgraph.insert(0, "subgraph %s {" % name)
                subgraph.append("}")
            out.extend(subgraph)

        for edge in self.edges:
            out.append(edge.dot)

        out.append("}")
        return "\n".join(out)

    def update_from_plain(self, plain):
        data = PlainOutput(plain)
        self.width, self.height = data.width, data.height
        self.scale = data.scale

        for edge in self.edges:
            edge.spline = data.edge_lines.get(edge.reference, None)
            edge.label_center = data.edge_label.get(edge.reference, None)

        for node in self.nodes:
            if node.item.reference in data.nodes:
                node.center, size = data.nodes[node.item.reference]
                node.width, node.height = size
    
    def get_label_string(self, pdgid):
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
        return label

    def annotate_particles(self, particles, annotate_function):
        """
        Add a subscript for all particles. annotate_function(particle) should
        return a value to be added.
        """
        for particle in particles:
            subscript = annotate_function(particle)
            if subscript:
                particle.subscripts.append(subscript)

class LayoutObject(object):
    def __init__(self, item):
        self.item = item
        self.show = True
        self.label = True
        self.dot_label = False # special dot_only label
        self.style_args = {}

class LayoutEdge(LayoutObject):
    def __init__(self, item, coming, going, **args):
        super(LayoutEdge, self).__init__(item)
        self.coming, self.going = coming, going
        self.port_coming, self.port_going = None, None
        self.dot_args = {}
        self.spline = None
        self.label = ""
        self.label_center = None
        self.args = args
        self.style_line_type = None
        for key, val in args.iteritems():
            setattr(self, key, val)

    @property
    def reference(self):
        parts = self.item.reference, self.coming.reference, self.going.reference
        return "_".join(parts)

    @property
    def dot(self):
        def join_port(to, port):
            return ":".join((to, port)) if port else to 
        coming = join_port(self.coming.reference, self.port_coming)
        going = join_port(self.going.reference, self.port_going)
        
        return make_edge(coming, going,
            label=self.label,
            style=self.reference,
            arrowhead="none",
            **self.dot_args
            # consider this for the future
            #constraint=not particle.decends_one)
        )


class LayoutNode(LayoutObject):
    def __init__(self, item, **args):
        super(LayoutNode, self).__init__(item)
        self.dot_args = {}
        self.label = ""
        self.subgraph = None
        self.center = None
        self.width = self.height = None
        for key, val in args.iteritems():
            setattr(self, key, val)

    @property
    def dot(self):
        kwargs = ({"width":self.width, "height":self.height} 
                  if self.width and self.height else {})
        kwargs.update(self.dot_args)
        if self.dot_label:
            label = self.dot_label
        elif self.label:
            label = self.label
        else:
            label = ""
        return make_node(self.item.reference, label=label, 
            style="" if self.show else "invis", **kwargs)
