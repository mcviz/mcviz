from base import BaseLayout, LayoutEdge, LayoutNode

class DualLayout(BaseLayout):

    def get_subgraph(self, particle):
        if particle.initial_state:
            return "initial"

    @property
    def subgraph_names(self):
        return ["initial", None]

    def get_particle(self, particle):
        lo = LayoutNode(particle)
        lo.subgraph = self.get_subgraph(particle)
        lo.label = self.get_label_string(particle.pdgid)
         
        if particle.initial_state:
            # Big red initial vertices
            lo.width = lo.height = 1.0
        
        return lo
   
    def get_vertex(self, vertex, node_style=None):

        edges = []
        for particle in vertex.outgoing:
            for mother in particle.mothers:
                edges.append(LayoutEdge(vertex, mother, particle))
        
        return edges
