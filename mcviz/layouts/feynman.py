from __future__ import division

from math import log10
from layouts import BaseLayout, LayoutEdge, LayoutNode

class FeynmanLayout(BaseLayout):

    def get_subgraph(self, vertex):
        if vertex.initial:
            return "initial"
        elif vertex.connecting:
            return "connecting"

    def process(self):

        # sort the edges
        def ordering(edge): 
            order = (1 if edge.item.gluon else 
                     0 if edge.item.color else 
                     2 if edge.item.anticolor else None)
            return edge.going.reference, order, edge.item.reference

        self.edges.sort(key=ordering)

    def get_vertex(self, vertex, node_style=None):

        lo = LayoutNode(vertex, width = 0.1, height = 0.1)
        lo.label = None
        lo.label_size = self.options.label_size
        lo.subgraph = self.get_subgraph(vertex)

        if node_style:
            lo.dot_args.update(node_style)
       
        if vertex.final:
            # Don't show final particle vertices
            lo.show = False
        elif "summary" in vertex.tags:
            lo.width = 1.0
            lo.height = 1.0
        elif vertex.hadronization:
            # Big white hardronization vertices
            if self.options.layout_engine == "dot":
                n_gluons_in = sum(1 for p in vertex.incoming if p.gluon)
                lo.width = 2 + n_gluons_in*0.5
                lo.height = 1
                lo.dot_args["shape"] = "record"
                lo.dot_args["label"] = " <leftedge>|<left>|<middle>|<right>|<rightedge>"
            else:
                lo.width = lo.height = 1.0
            
        elif vertex.initial:
            # Big red initial vertices
            lo.width = lo.height = 1.0
        else:
            nr_particles = len(vertex.incoming) + len(vertex.outgoing)
            lo.width = lo.height = nr_particles * 0.04

        return lo
   
    def get_particle(self, particle):

        lo = LayoutEdge(particle, particle.start_vertex, particle.end_vertex)
        lo.label_size = self.options.label_size

        if "jet" in particle.tags:
            lo.label = "jet (%.1f GeV)" % particle.pt
        elif particle.gluon or particle.photon:
            lo.label = None
        else:
            lo.label = particle.pdgid

        lo.dot_args["weight"] = log10(particle.e+1)*0.1 + 1

        if self.options.layout_engine == "dot":
            if particle.end_vertex.hadronization:
                if particle.gluon:
                    lo.port_going = "middle"
                elif particle.color:
                    lo.port_going = "left"
                elif particle.anticolor:
                    lo.port_going = "right"
       
        return lo


class InlineLabelsLayout(FeynmanLayout):
    
    def get_particle(self, particle):
            
        down = super(InlineLabelsLayout, self).get_particle(particle)
        if down.item.gluon or down.item.photon:
            return down
       
        middle = LayoutNode(down.item, label=down.label)
        middle.show = False
        middle.dot_args["margin"] = "0,0"
        #middle.dot_args["shape"] = "square"
        middle.dot_args["group"] = "particlelabels"
        
        up = LayoutEdge(down.item, down.coming, middle.item, **down.args)
        down.coming = middle.item
        up.label = down.label = None
        up.port_going = None
        
        return [up, middle, down] 
