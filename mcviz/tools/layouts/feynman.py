from __future__ import division

from math import log10

from mcviz.tools import FundamentalTool, Arg
from mcviz.graph import ViewVertex, ViewParticle

from .layouts import BaseLayout, LayoutEdge, LayoutNode

class FeynmanLayout(BaseLayout, FundamentalTool):
    """
    Produces something analagous to the familiar Feynman diagram. Beware though,
    event records are not really like feynman diagrams.
    """
    _name = "Feynman"

    _args = [Arg("gluid", Arg.bool, "label gluons")]

    dummy_number = -1000
    
    def get_subgraph(self, vertex):
        if vertex.initial:
            return "initial"
        elif vertex.connecting:
            return "connecting"

    def process(self):

        # TODO: do something with the edge ordering. It is currently nonsensical
        def ordering(edge): 
            order = (1 if edge.item.gluon else 
                     0 if edge.item.color else 
                     2 if edge.item.anticolor else None)
            return edge.going.reference, order, edge.item.reference

        self.edges.sort(key=ordering)

    def get_vertex(self, vertex, node_style=None):

        lo = LayoutNode(vertex, width=0.1, height=0.1)
        lo.label = None
        lo.label_size = self.options["label_size"]
        lo.subgraph = self.get_subgraph(vertex)

        if node_style:
            lo.dot_args.update(node_style)
        
        # Put clusters in the same graphviz "group".
        if "after_cluster" in vertex.tags:
            lo.dot_args["group"] = "cluster_%i" % vertex.cluster_index
        elif (all("after_cluster" in p.tags for p in vertex.outgoing) and 
              vertex.outgoing):
            cluster_particle = (p for p in vertex.outgoing if "after_cluster" in p.tags).next()
            lo.dot_args["group"] = "cluster_%i" % cluster_particle.cluster_index

        if vertex.initial:
            # Big red initial vertices
            lo.width = lo.height = 1.0
        elif vertex.final:
            # Don't show final particle vertices
            lo.show = False
            
        elif "cut_summary" in vertex.tags:
            return None
            
        elif "summary" in vertex.tags:
            lo.width = lo.height = 1.0
            
        elif vertex.hadronization:
            # Big white hardronization vertices
            lo.width = lo.height = 1.0
            
        else:
            nr_particles = len(vertex.incoming) + len(vertex.outgoing)
            lo.width = lo.height = nr_particles * 0.04

        return lo
   
    def get_particle(self, particle):

        if "cut_summary" in particle.tags:
            dummy = ViewVertex(self.graph)
            dummy.order_number = self.dummy_number
            self.dummy_number -= 1
            lo = LayoutEdge(particle, particle.start_vertex, dummy)
        else:
            lo = LayoutEdge(particle, particle.start_vertex, particle.end_vertex)
        lo.label_size = self.options["label_size"]

        if "cluster" in particle.tags:
            lo.label = "cluster (%.4g %seV)" % self.graph.units.pick_mag(particle.pt)
        elif (particle.gluon or particle.photon) and not self.options["gluid"]:
            lo.label = None
        elif "cut_summary" in particle.tags:
            lo.label = None
        elif "jet" in particle.tags:
            jet_id = 0
            for tag in particle.tags:
               if tag != 'jet' and tag[:4] == 'jet_':
                    jet_id = int(tag[4:]) + 1
            if not jet_id: print(particle.tags)
            lo.label = "jet {0:d} ({1:.4g} {2:s}eV)".format(jet_id, *self.graph.units.pick_mag(particle.pt))
        else:
            lo.label = particle.pdgid

        #lo.dot_args["weight"] = log10(particle.e+1)*0.1 + 1
        
        return lo


class InlineLabelsLayout(FeynmanLayout):
    """
    Causes particle labels to "interrupt" particle edges, rather than be shown
    by the side of them.
    """
    _name = "InlineLabels"
    
    def get_particle(self, particle):
            
        down = super(InlineLabelsLayout, self).get_particle(particle)
        if not down.label:# or "jet" in particle.tags:
            return down
       
        middle = LayoutNode(down.item, label=down.label)
        middle.show = False
        middle.dot_args["margin"] = "0,0"
        #middle.dot_args["shape"] = "square"
        middle.dot_args["group"] = "particlelabels"
        
        if 'jet' in down.item.tags: #Make a dummy item for the upstream particle
            item = ViewParticle(self.graph)
            item.pdgid = 0
            item.color = item.anticolor = None
            item.order_number = -1000
        else:
            item = down.item

        up = LayoutEdge(item, down.coming, middle.item, **down.args)
        down.coming = middle.item
        up.label = down.label = None
        up.port_going = None
        
        return [up, middle, down]


class StringClustersLayout(FeynmanLayout):
    """
    Causes strings to try and arrange the edges so that gluons go into 
    the middle, coloured particles come in on the left, and anti-colours arrive 
    on the right.
    """
    _name = "StringClusters"

    def __init__(self, *args, **kwargs):
        super(StringClustersLayout, self).__init__(*args, **kwargs)
        
        #assert self.options.layout_engine == "dot", (
        #    "StringClustersLayout is only meaningful with dot.")

    def get_vertex(self, vertex, node_style=None):
        lo = super(StringClustersLayout, self).get_vertex(vertex, node_style)
        if vertex.hadronization:
            n_gluons_in = sum(1 for p in vertex.incoming if p.gluon)
            lo.width = 2 + n_gluons_in*0.5
            lo.height = 1
            lo.dot_args["shape"] = "record"
            record_shape = " <leftedge>|<left>|<middle>|<right>|<rightedge>"
            lo.dot_args["label"] = record_shape
        
        return lo
        
    def get_particle(self, particle):
        lo = super(StringClustersLayout, self).get_particle(particle)
        if particle.end_vertex.hadronization:
            if isinstance(lo, list):
                # If it's a list, take the last one, assuming that that is the
                # one which is going somewhere
                this_particle = lo[-1]
            else:
                this_particle = lo
            if particle.gluon:
                this_particle.port_going = "middle"
            elif particle.color:
                this_particle.port_going = "left"
            elif particle.anticolor:
                this_particle.port_going = "right"
                
        return lo
