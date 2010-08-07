from .graphviz import make_node, make_edge
from .utils import latexize_particle_name

class DualArtist(object):

    def __init__(self, graph, options):
        self.graph = graph
        self.options = options

    def draw(self, graph):
        print("strict digraph pythia {")
        print("node [style=filled, shape=oval]")
        for particle in graph.particles.itervalues():
            self.draw_particle(particle)
        print("}")

    def draw_particle(self, particle):
        color = particle.get_color("gray")
        size = (15 + log10(particle.pt + 1)*100)
        args = (particle.no, particle.name, particle.no, color, size)
        
        # TODO: Do different things for initial/final state
        print(make_node(particle.no, 
                        label="%s (%s)" % (particle.name, particle.no), 
                        fillcolor=color, fontsize=size))
        
        # Printing edges
        for mother in particle.mothers:
            print(make_edge(mother.no, particle.no, comment="mother"))
            
        for daughter in particle.daughters:
            print(make_edge(particle.no, daughter.no, comment="daughter"))
            
