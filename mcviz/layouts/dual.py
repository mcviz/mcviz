from layouts import BaseLayout, LayoutEdge, LayoutNode

class DualLayout(BaseLayout):

    def get_subgraph(self, particle):
        if particle.initial_state:
            return "initial"

    def get_particle(self, particle):
        lo = LayoutNode(particle)
        lo.subgraph = self.get_subgraph(particle)

        lo.label = particle.pdgid
        lo.label_size = self.options.label_size
         
        if particle.initial_state:
            # Big red initial vertices
            lo.width = lo.height = 1.0
        elif "cluster" in particle.tags:
            lo.label = "cluster (%.1f GeV)" % particle.pt
        
        return lo
   
    def get_vertex(self, vertex, node_style=None):

        edges = []
        for particle in vertex.outgoing:
            for mother in particle.mothers:
                edges.append(LayoutEdge(vertex, mother, particle))
        
        return edges
