from __future__ import division

from math import log10
from base import BaseLayout, LayoutEdge, LayoutNode

class FeynmanLayout(BaseLayout):

    def get_subgraph(self, vertex):
        if vertex.is_initial:
            return "initial"
        elif vertex.connecting:
            return "connecting"

    @property
    def subgraph_names(self):
        return ["initial", None]

    def process(self):

        if self.options.fix_initial:
            initial = self.subgraphs["initial"]
            initial_pairs = len(initial) // 2
            for i, p in enumerate(initial):
                sg_options = self.subgraph_options.setdefault("initial", [])
                sg_options.append('rank="source"')
                pair = i // 2
                stretch = self.options.stretch
                width = self.options.width
                height = width * float(self.options.ratio)
                xposition = stretch + (i % 2) * (width - 2 * stretch)
                yposition = (1 + pair) * height / (initial_pairs + 1)
                p.dot_args["pos"] = "%s,%s!" % (xposition, yposition)
        
        # sort the edges
        def ordering(edge): 
            order = (1 if edge.item.gluon else 
                     0 if edge.item.color else 
                     2 if edge.item.anticolor else None)
            return edge.going.reference, order, edge.item.reference

        self.edges.sort(key=ordering)

    def get_vertex(self, vertex, node_style=None):

        lo = LayoutNode(vertex, width = 0.1, height = 0.1)
        lo.subgraph = self.get_subgraph(vertex)

        if node_style:
            lo.dot_args.update(node_style)
        
        if vertex.hadronization:
            # Big white hardronization vertices
            if self.options.layout_engine == "dot":
                n_gluons_in = sum(1 for p in vertex.incoming if p.gluon)
                lo.width = 2 + n_gluons_in*0.5
                lo.height = 1
                lo.dot_args["shape"] = "record"
                lo.label = " <left>|<middle>|<right>" 
            else:
                lo.width = lo.height = 1.0
            
        elif vertex.is_initial:
            # Big red initial vertices
            lo.width = lo.height = 1.0

        elif vertex.is_final:
            # Don't show final particle vertices
            lo.style = "invis"
        
        else:
            nr_particles = len(vertex.incoming) + len(vertex.outgoing)
            lo.width = lo.height = nr_particles * 0.04

        return lo
   
    def get_particle(self, particle):

        lo = LayoutEdge(particle, particle.vertex_in, particle.vertex_out)

        lo.label = self.get_label_string(particle.pdgid)
        if particle.gluon or particle.photon:
            lo.label = ""

        lo.dot_args["weight"] = log10(particle.e+1)*0.1 + 1

        if self.options.layout_engine == "dot":
            if particle.vertex_out.hadronization:
                if particle.gluon:
                    lo.port_going = "middle"
                elif particle.color:
                    lo.port_going = "left"
                elif particle.anticolor:
                    lo.port_going = "right"
       
        return lo

