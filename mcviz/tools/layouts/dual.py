from mcviz.tools import FundamentalTool, Arg

from .layouts import BaseLayout, LayoutEdge, LayoutNode


class DualLayout(BaseLayout, FundamentalTool):
    """
    The Dual layout, so named because it is the "Dual" in the graph sense of
    Feynman diagrams, shows particles as nodes.
    """
    _name = "Dual"
    _global_args = ("label_size",)
    _args = [Arg("helper_vertices",Arg.bool,"add helper vertices if there are many-to-many vertices", default=True)]

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
        items = []

        need_help = False
        if self.options["helper_vertices"]:
            if len(vertex.incoming) > 1 and len(vertex.outgoing) > 1:
                need_help = True
            elif vertex.initial and len(vertex.outgoing) > 1:
                need_help = True

        if need_help:
            helper_node = LayoutNode(vertex)
            helper_node.width = 0.5
            helper_node.height = 0.5
            items.append(helper_node)
            
            for particle in vertex.incoming:
                items.append(LayoutEdge(vertex, particle, vertex))
            for particle in vertex.outgoing:
                items.append(LayoutEdge(vertex, vertex, particle))
            return items
            
        for particle in vertex.outgoing:
            for mother in particle.mothers:
                items.append(LayoutEdge(vertex, mother, particle))
        
        return items

class DualDecongestedHad(DualLayout):
    """
    UNDOCUMENTED
    Takes the all-to-all connections at the hadronization step and replaces it
    with a all-to-one-to-all vertex labelled "A miracle occurs"
    """
    _name = "DualDecongestedHad"
    _args = [Arg("label",str,"label for the hadronization vertex",
                 default="A miracle occurs")]

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
