
from .. import log; log = log.getChild(__name__)

from mcviz.graph import ViewVertex, ViewParticleSummary
from mcviz.tools import Arg

from .layouts import BaseLayout, LayoutNode

class FixedHadronsLayout(BaseLayout):
    """
    Place all of the hadronization vertices on the same rank.
    """
    _name = "FixHad"

    def process(self):
        sg_options = self.subgraph_options.setdefault("hadronization", [])
        # rank=same means that the objects in this group should be laid out
        # on the same line
        sg_options.append('rank="same"')
        return super(FixedHadronsLayout, self).process()
        
    def process_node(self, obj):
        if isinstance(obj.item, ViewVertex):
            if obj.item.hadronization:
                obj.subgraph = "hadronization"
        elif (obj.item.start_vertex.hadronization and 
              not isinstance(obj.item, ViewParticleSummary)):
            if obj.dot_args.get("group", "") != "particlelabels":
                obj.subgraph = "hadronization"
        return super(FixedHadronsLayout, self).process_node(obj)

class FixedJetsLayout(BaseLayout):
    """
    Place all of the hadronization vertices on the same rank.
    """
    def __init__(self, *args, **kwargs):
        super(FixedJetsLayout, self).__init__(*args, **kwargs)
        self.jetnodes = {}
    
    def get_jetnode(self, tag, particle):
        if tag in self.jetnodes: return self.jetnodes[tag]
        result = LayoutNode(particle.item, label="CLUSTER")
        self.jetnodes[tag] = result
        return result
        
    def get_particle(self, particle):
        part = super(FixedJetsLayout, self).get_particle(particle)
        if particle.final:
            for t in particle.tags:
                if "jet" in t:
                    cluster = self.get_jetnode(t, part)
                    
                    # I have no idea what I'm doing here.
                    
                    up = LayoutEdge(down.item, down.coming, middle.item, **down.args)
                    
                    break
        
        return part
class FixedInitialLayout(BaseLayout):
    """
    Place all of the initial vertices on the same rank.
    """
    _name = "FixIni"
    _args = [Arg("stretch", float, "pull initial vertices apart, 1 is max", 
                 default=0.8)]
    
    def process(self):
        sg_options = self.subgraph_options.setdefault("initial", [])
        # rank=source means "put these on the first rank" to graphviz
        sg_options.append('rank="source"')
        super(FixedInitialLayout, self).process()

        initial = self.subgraphs["initial"]
        initial_pairs = len(initial) // 2
        for i, p in enumerate(initial):
            pair = i // 2
            if self.width and self.height:
                # Attempt to fix the initial particles on the left and right
                # of the graph.
                stretch = self.options["stretch"] * self.width / 2.0
                xposition = stretch + (i % 2) * (self.width - 2 * stretch)
                yposition = (1 + pair) * self.height / (initial_pairs + 1)
                p.dot_args["pos"] = "%s,%s!" % (xposition, yposition)
        
    def process_node(self, obj):
        if isinstance(obj.item, ViewVertex):
            if obj.item.initial:
                obj.subgraph = "initial"
        elif obj.item.start_vertex.initial:
            if obj.dot_args.get("group","") != "particlelabels":
                obj.subgraph = "initial"
        return super(FixedInitialLayout, self).process_node(obj)


class HardProcessSubgraph(BaseLayout):
    """
    Place all of the hadronization vertices on the same rank.
    """
    _name = "HardProcessSubgraph"
    
    def process(self):
        sg_options = self.subgraph_options.setdefault("cluster_hardproc", [])
        sg_options.append("bgcolor=red;")
        sg_options.append("clusterrank=local;")
        super(HardProcessSubgraph, self).process()
        
    def process_node(self, obj):
        # TODO:
        # We need also to include any particles between two hard process vertices
        if isinstance(obj.item, ViewVertex):
            if any(21 <= abs(p.status) <= 29 for p in obj.item.through):
                log.verbose("Making hardproc graph")
                obj.subgraph = "cluster_hardproc"
            else:
                log.verbose("Not making hardproc graph %r", [p.status for p in obj.item.through])
        elif 21 <= abs(obj.item.status) <= 29:
            obj.subgraph = "cluster_hardproc"
        return super(HardProcessSubgraph, self).process_node(obj)
        

class UnconstrainedPhotons(BaseLayout):
    """
    UNDOCUMENTED
    """
    _name = "UnconstrainedPhotons"
        
    def process_edge(self, obj):
        #if any(p.photon for p in obj.item.outgoing):
            #obj.dot_args["constraint"] = "false"
        return super(UnconstrainedPhotons, self).process_edge(obj)
    
