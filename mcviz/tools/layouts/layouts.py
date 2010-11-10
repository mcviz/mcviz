from __future__ import division

from math import log10
from itertools import chain

from mcviz.tool import Layout
from mcviz.svg import TexGlyph

from mcviz.graphviz import make_node, make_edge, PlainOutput
from mcviz.utils import latexize_particle_name, make_unicode_name, Point2D

label_scale_factor = 72.0

class BaseLayout(Layout):
    """
    Class that encapsulates the layout and styling information of the graph
    """
    _global_args = ("resolution", "ratio", "extra_dot")
    _defaults = {"resolution" : (800, 600), "ratio" : None}

    def __call__(self, graph):

        self.width, self.height = self.options["resolution"]
        self.ratio = self.options["ratio"]
        self.scale = 1.0

        self.subgraphs = {None: []}
        self.subgraph_options = {}
        self.edges = []

        # create node and edge objects from the graph
        self.fill_objects(graph)

        # do custom processing of the layout objects here
        self.process()

        return self

    def fill_objects(self, graph):

        for vertex in graph.vertices:
            self.add_object(self.get_vertex(vertex))

        for particle in graph.particles:
            self.add_object(self.get_particle(particle))

    def process_node(self, node):
        return node

    def process_edge(self, edge):
        return edge

    def add_object(self, obj):
        if obj is None:
            return
        elif hasattr(obj, "__iter__"):
            for o in obj:
                self.add_object(o)
            return
            
        obj.item.layout_objects.append(obj)
        if isinstance(obj, LayoutNode):
            obj = self.process_node(obj)
            if obj:
                self.subgraphs.setdefault(obj.subgraph, []).append(obj)
        elif isinstance(obj, LayoutEdge):
            obj = self.process_edge(obj)
            if obj:
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
        out.append(self.options["extra_dot"])
        out.append('dpi=1;')
        if self.width and self.height:
            out.append('size="%s,%s!";' % (self.width, self.height))
        if self.ratio:
            out.append("ratio=%s;" % self.ratio)

        out.append("edge [labelangle=90]")

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
    


class LayoutObject(object):
    def __init__(self, item):
        self.item = item
        self.show = True
        self.label = None
        self.label_size = 1.0
        self.style_args = {}

    def get_label_string(self):
        if self.label is None:
            return ""
        elif isinstance(self.label, str):
            return self.label
        elif isinstance(self.label, int):
            if TexGlyph.exists(self.label):
                w, h = TexGlyph.from_pdgid(self.label).dimensions
                w *= self.label_size
                h *= self.label_size
                table = '<<table border="1" cellborder="0"><tr>%s</tr></table>>'
                td = '<td height="%.2f" width="%.2f"></td>' % (h, w)
                return table % td
            else:
                # a pure number here leads graphviz to ignore the edge
                return "|%i|" % self.label
        else:
            return str(self.label) # WTF?
        

class LayoutEdge(LayoutObject):
    def __init__(self, item, coming, going, **args):
        super(LayoutEdge, self).__init__(item)
        self.coming, self.going = coming, going
        self.port_coming, self.port_going = None, None
        self.dot_args = {}
        self.spline = None
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

        kwargs = {}
        if self.label_size is not None:
            if self.label:# or ("label" in self.dot_args):
                kwargs["fontsize"] = self.label_size * label_scale_factor
        kwargs["label"] = self.get_label_string()
        kwargs.update(self.dot_args)

        return make_edge(coming, going,
            style=self.reference,
            arrowhead="none",
            **kwargs
            # consider this for the future
            #constraint=not particle.decends_one)
        )


class LayoutNode(LayoutObject):
    def __init__(self, item, **args):
        super(LayoutNode, self).__init__(item)
        self.dot_args = {}
        self.subgraph = None
        self.center = None
        self.width = self.height = None
        for key, val in args.iteritems():
            setattr(self, key, val)

    @property
    def dot(self):
        kwargs = {}
        if self.width and self.height:
            kwargs["width"] = self.width
            kwargs["height"] = self.height
        kwargs["style"] = "" if self.show else "invis"
        if self.label_size is not None:
            if self.label:# or ("label" in self.dot_args):
                kwargs["fontsize"] = self.label_size * label_scale_factor

            kwargs["label"] = self.get_label_string()
        kwargs.update(self.dot_args)

        return make_node(self.item.reference, **kwargs)
