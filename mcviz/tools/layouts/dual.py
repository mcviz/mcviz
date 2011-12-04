from mcviz.tools import FundamentalTool, Arg

from .layouts import BaseLayout, LayoutEdge, LayoutNode

class DualLayout(BaseLayout, FundamentalTool):
    """
    The Dual layout, so named because it is the "Dual" in the graph sense of
    Feynman diagrams, shows particles as nodes.
    """
    _name = "Dual"
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
            lo.label = "cluster (%.4g %seV)" % self.graph.units.pick_mag(particle.pt)
        elif "cut_summary" in particle.tags:
            pass #lo.label = None
        elif "jet" in particle.tags:
            jet_id = 0
            for tag in particle.tags:
               if tag != 'jet' and tag[:4] == 'jet_':
                    jet_id = int(tag[4:]) + 1
            lo.label = "jet {0:d} ({1:.4g} {2:s}eV)".format(jet_id, *self.graph.units.pick_mag(particle.pt))
        
        return lo
   
    def get_vertex(self, vertex, node_style=None):
        items = []

        if "cut_summary" in vertex.tags and len(vertex.incoming) > 1:
            return None

        need_help = False
        if self.options["helper_vertices"]:
            if len(vertex.incoming) > 1 and len(vertex.outgoing) > 1:
                need_help = True
            elif vertex.vacuum:
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
