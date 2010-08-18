from __future__ import division

from ..graphviz import make_node, make_edge

from math import log10


from base import BaseLayout, LayoutEdge, LayoutVertex

class FeynmanLayout(BaseLayout):

    def print_graph(self, graph):
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
        width = height = 0.1
        
        if vertex.hadronization:
            # Big white hardronization vertices
            width = 20
            height = 1

            
        elif vertex.is_initial:
            # Big red initial vertices
            width = height = 1.0

        elif vertex.is_final:
            # Don't show final particle vertices
            style = "invis"
        
        else:
            nr_particles = len(vertex.incoming) + len(vertex.outgoing)
            width = height = nr_particles * 0.04

        vertex.layout = LayoutVertex(w = width/2, h = height/2)


        node = make_node(vertex.vno, height=height, width=width, label="", 
                         style=style,
                         **node_style)
        
        print node
            
        edges = set()
        # Printing edges
        for out_particle in sorted(vertex.outgoing):
            if out_particle.vertex_out:

                edge_text = self.get_particle_text(out_particle)
                
                order = (1 if out_particle.gluon else 
                         0 if out_particle.color else 
                         2 if out_particle.anticolor else None)
                
                edge = out_particle.vertex_out.vno, order, edge_text
                
                edges.add(edge)
                
        return edges        
   
    def get_particle_text(self, particle):
        label = self.get_label_string(particle.pdgid)
        if particle.gluon or particle.photon:
            label = ""

        weight = log10(particle.e+1)*0.1 + 1

        style = str(particle.no)
        coming, going = particle.vertex_in.vno, particle.vertex_out.vno
        edge_text = make_edge(coming, going, label=label,
            weight=weight,
            style=style,
            arrowhead="none",
            # consider this for the future
            #constraint=not particle.decends_one)
        )
        return edge_text
