from logging import getLogger; log = getLogger("mcviz.layouts.extra")

from .layouts import BaseLayout, LayoutNode
from ..view_vertex import ViewVertex


class FixedHadronsLayout(BaseLayout):
    """
    Place all of the hadronization vertices on the same rank.
    """
    def process(self):
        sg_options = self.subgraph_options.setdefault("hadronization", [])
        sg_options.append('rank="same"')
        return super(FixedHadronsLayout, self).process()
        
    def process_node(self, obj):
        if isinstance(obj.item, ViewVertex):
            if obj.item.hadronization:
                obj.subgraph = "hadronization"
        elif obj.item.start_vertex.hadronization:
            if obj.dot_args.get("group","") != "particlelabels":
                obj.subgraph = "hadronization"
        return super(FixedHadronsLayout, self).process_node(obj)


class FixedInitialLayout(BaseLayout):
    """
    Place all of the hadronization vertices on the same rank.
    """
    def process(self):
        sg_options = self.subgraph_options.setdefault("initial", [])
        sg_options.append('rank="source"')

        super(FixedInitialLayout, self).process()

        initial = self.subgraphs["initial"]
        initial_pairs = len(initial) // 2
        for i, p in enumerate(initial):
            pair = i // 2
            if self.width and self.height:
                stretch = self.options.stretch * self.width / 2.0
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
                log.info("Making hardproc graph")
                obj.subgraph = "cluster_hardproc"
            else:
                log.info("Not making hardproc graph %r", [p.status for p in obj.item.through])
        elif 21 <= abs(obj.item.status) <= 29:
            obj.subgraph = "cluster_hardproc"
        return super(HardProcessSubgraph, self).process_node(obj)
