from __future__ import division

from ..graphviz import make_node, make_edge
from ..utils import latexize_particle_name, make_unicode_name

from math import log10


from base import BaseLayout, LayoutEdge, LayoutVertex

class FeynmanLayout(BaseLayout):

    def layout(self, graph):
        print("digraph pythia {")
        print("ordering=in;")
        print(self.options.extra_dot)
        if self.options.fix_initial:
            width = self.options.width
            height = width * float(self.options.ratio)
            stretch = self.options.stretch
            print('size="%s,%s!";' % (width, height))
        print("ratio=%s;" % self.options.ratio)
        print("edge [labelangle=90, fontsize=%.2f]" % (72*self.options.label_size))

        subgraphs = dict(one=[], two=[], both=[])
        other, connecting, initial = [], [], []
        for vertex in graph.vertices.values():
            if vertex.is_initial:
                initial.append(vertex)
            elif vertex.connecting:
                connecting.append(vertex)
            else:
                other.append(vertex)                
        
        edges = set()
        
        #edges.update(self.draw_vertices_cluster("initial", initial, "rank=source;"))
        
        print("subgraph initial_nodes {")
        initial_pairs = len(initial) // 2
        for i, p in enumerate(initial):
            if self.options.fix_initial:
                print('rank="source"')
                pair = i // 2
                yposition = (1 + pair) * height / (initial_pairs + 1)
                xposition = stretch + (i % 2) * (width - 2 * stretch)
                p_options = dict(pos="%s,%s!" % (xposition, yposition))
            else:
                p_options = {}
            edges.update(self.draw_vertex(p, p_options))
        print("}")
        
        #edges.update(self.draw_vertices_cluster("connecting", connecting, 'rank=same;'))
        edges.update(self.draw_vertices_cluster("connecting", connecting, ''))
        edges.update(self.draw_vertices(other))
        
        self.print_edges(edges)

        print("}")
    
    def print_edges(self, edges):
        
        # Original ordering
        # ordering = lambda (out_vertex_no, order, edge): edge
        # Ordering by color
        ordering = lambda x: x
        
        for out_vertex_no, order, edge in sorted(edges, key=ordering):
            print edge
    
    def draw_vertices_cluster(self, subgraph, vertices, style=""):
        print("subgraph %s {" % subgraph)
        print(style)
        edges = self.draw_vertices(vertices)
        print("}")
        return edges
    
    def draw_vertices(self, vertices):
        edges = set()
        for vertex in sorted(vertices):
            edges.update(self.draw_vertex(vertex))
        return edges

    def draw_vertex(self, vertex, node_style=None):
        if node_style is None:
            node_style = {}
        style = ""
        size = 0.1
        
        if vertex.hadronization:
            # Big white hardronization vertices
            size = 1.0
            
        elif vertex.is_initial:
            # Big red initial vertices
            size = 1.0
            
        elif vertex.is_final:
            # Don't show final particle vertices
            style = "invis"
        
        else:
            nr_particles = len(vertex.incoming) + len(vertex.outgoing)
            size = nr_particles * 0.04

        vertex.layout = LayoutVertex(r = size/2)

        node = make_node(vertex.vno, height=size, width=size, label="", 
                         style=style,
                         **node_style)
        
        print node
            
        edges = set()
        # Printing edges
        for out_particle in sorted(vertex.outgoing):
            if out_particle.vertex_out:
                label = self.get_label_string(out_particle.pdgid)

                if out_particle.gluon or out_particle.photon:
                    label = ""

                style = str(out_particle.no)
                coming, going = vertex.vno, out_particle.vertex_out.vno
                edge_text = make_edge(coming, going, label=label,
                    weight=log10(out_particle.e+1)*0.1 + 1,
                    style=style,
                    arrowhead="none",
                    #constraint=not out_particle.decends_one)
                )
                
                order = (1 if out_particle.gluon else 
                         0 if out_particle.color else 
                         2 if out_particle.anticolor else None)
                
                edge = going, order, edge_text
                
                edges.add(edge)
                
        return edges        
    
