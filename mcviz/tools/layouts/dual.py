from mcviz.tool import FundamentalTool

from .layouts import BaseLayout, LayoutEdge, LayoutNode


class DualLayout(BaseLayout, FundamentalTool):
    _name = "Dual"
    _global_args = ("label_size",)

    def get_subgraph(self, particle):
        if particle.initial_state:
            return "initial"

    def get_particle(self, particle):
        lo = LayoutNode(particle)
        lo.subgraph = self.get_subgraph(particle)

        lo.label = particle.pdgid
        lo.label_size = self.options["label_size"]
         
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


class DualDecongestedHad(DualLayout):
    """
    Takes the all-to-all connections at the hadronization step and replaces it
    with a all-to-one-to-all vertex labelled "A miracle occurs"
    """
    _name = "DualDecongestedHad"
    _args = [("label",str)]
    _defaults = {"label": "A miracle occurs"}

    def get_vertex(self, vertex, node_style=None):
        if vertex.hadronization:
            items = []
            had_node = LayoutNode(vertex, label=self.options["label"])
            had_node.width = 5.0
            had_node.height = 1.0
            items.append(had_node)
            
            for particle in vertex.incoming:
                items.append(LayoutEdge(vertex, particle, vertex))
            for particle in vertex.outgoing:
                items.append(LayoutEdge(vertex, vertex, particle))
                
            return items
        else:
            return super(DualDecongestedHad, self).get_vertex(vertex, node_style)
