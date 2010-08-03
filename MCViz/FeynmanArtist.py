from .graphviz import print_node, print_edge
from .utils import latexize_particle_name

from math import log10

class FeynmanArtist(object):

    def __init__(self, options):
        self.options = options

    def draw(self, graph):
        print("strict digraph pythia {")
        print("node [style=filled, shape=oval]")
        print("edge [labelangle=90, fontsize=12]")
        print("ratio=1")

        for vertex in sorted(graph.vertices.itervalues()):
            self.draw_vertex(vertex)

        print("}")

    def draw_vertex(self, vertex):
        style = "filled"
        size = 0.1
        fillcolor = "black"
        
        if vertex.hadronization:
            # Big white hardronization vertices
            size, fillcolor = 1.0, "white"
            
        elif vertex.is_initial:
            # Big red initial vertices
            size, fillcolor = 1.0, "red"
            
        elif vertex.is_final:
            # Don't show final particle vertices
            style = "invis"

        print_node(vertex.vno, height=size, width=size, 
                   color="black", fillcolor=fillcolor, label="", style=style)
            
        # Printing edges
        for out_particle in sorted(vertex.outgoing):
            if out_particle.vertex_out:
                color = out_particle.get_color("black")
                
                # Halfsize arrows for final vertices
                arrowsize = 1.0 if not out_particle.final_state else 0.5
                
                # Greek-character-ize names.
                name = latexize_particle_name(out_particle.name)
                if self.options and self.options.show_id:
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

                going, coming = vertex.vno, out_particle.vertex_out.vno
                print_edge(going, coming, label=label, color=color,
                           penwidth=log10(out_particle.pt+1)*1 + 1,
                           weight=log10(out_particle.e+1)*0.1 + 1,
                           arrowsize=arrowsize,
                           style=style,
                           dir=dir)
        
