from .graphviz import make_node, make_edge
from .utils import latexize_particle_name

from math import log10

class FeynmanArtist(object):

    def __init__(self, options):
        self.options = options

    def draw(self, graph):
        print("strict digraph pythia {")
        print(self.options.extra_dot)
        print("node [style=filled, shape=oval]")
        print("edge [labelangle=90, fontsize=12]")
        print("ratio=1")

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
        
        edges.update(self.draw_vertices_cluster("initial", initial, "rank=source;"))
        edges.update(self.draw_vertices_cluster("connecting", connecting, 'rank=same;style=filled;fillcolor=grey;'))
        edges.update(self.draw_vertices(other))
        
        for edge in sorted(edges):
            print edge

        print("}")
    
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

    def draw_vertex(self, vertex):
        style = "filled"
        size = 0.1
        fillcolor = "black"
        color_mechanism = self.options.color_mechanism
        thickness = self.options.line_thickness
        
        if vertex.hadronization:
            # Big white hardronization vertices
            size, fillcolor = 1.0, "white"
            
        elif vertex.is_initial:
            # Big red initial vertices
            size, fillcolor = 1.0, "red"
            
        elif vertex.is_final:
            # Don't show final particle vertices
            style = "invis"

        node = make_node(vertex.vno, height=size, width=size, label="", 
                         color="black", fillcolor=fillcolor, style=style)
        
        print node
            
        edges = set()
        # Printing edges
        for out_particle in sorted(vertex.outgoing):
            if out_particle.vertex_out:
                color = out_particle.get_color("black", color_mechanism)
                
                # Halfsize arrows for final vertices
                arrowsize = 1.0 if not out_particle.final_state else 0.5
                
                # Greek-character-ize names.
                name = latexize_particle_name(out_particle.name)
                if self.options.show_id:
                    label = "%s (%i)" % (name, out_particle.no)
                else:
                    label = name

                style = ""
                dir = "forward"
                if out_particle.gluon:
                    label = ""
                    style = "decorate, draw=green, decoration={coil,amplitude=4pt, segment length=5pt}"
                elif out_particle.photon:
                    label = ""
                    style = "decorate, decoration=snake, draw=red"
                    dir = "none"

                penwidth = log10(out_particle.pt+1)*thickness + 1

                going, coming = vertex.vno, out_particle.vertex_out.vno
                edge = make_edge(going, coming, label=label, color=color,
                                 penwidth=penwidth,
                                 weight=log10(out_particle.e+1)*0.1 + 1,
                                 arrowsize=arrowsize,
                                 style=style,
                                 dir=dir,
                                 )#constraint=not out_particle.decends_one)
                                 
                edges.add(edge)
                
        return edges
        
