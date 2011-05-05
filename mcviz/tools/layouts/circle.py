from __future__ import division

from sys import stderr
from math import sqrt, sin, cos, atan2, log as ln

from mcviz.utils import Point2D
from mcviz.tools import Arg

from .feynman import FeynmanLayout


def get_depth(particle):
    if particle.vertex_out.connecting:
        return 0
    elif particle.descends_both:
        return 1 + min(get_depth(mother) for mother in particle.mothers)
    else:
        if particle.final_state:
            return 0
        return -1 + max(get_depth(daughter) for daughter in particle.daughters)

def get_max_descendant_levels(vertex):
    if vertex.final:
        return 0
    return 1 + max(get_max_descendant_levels(p.end_vertex) for p in vertex.outgoing)# if p.end_vertex != vertex)

class CircleLayout(FeynmanLayout):
    _name = "Circle"
    _args = [Arg("scale", float, "length scale", default=1.0),
             Arg("view", str, "view on the event", choices=["front", "side"], default="side"),
             Arg("phi", float, "rotate the view in phi [radian]", default=0.0),
             ]

    def process(self):
        super(CircleLayout, self).process()

        # create a tree that is used to generate the visuals
        coming = {}
        going = {}
        for edge in self.edges:
            coming.setdefault(edge.coming, []).append(edge)
            going.setdefault(edge.going, []).append(edge)

        nodes_remaining = list(self.nodes)

        item_nodes = {}
        for node in self.nodes:
            item_nodes[node.item] = node

        rotate_phi = self.options["phi"]
        dims = (0,1) if self.options["view"] == "front" else (2,1)

        def pos_func(momentum):
            p0 = cos(rotate_phi)*momentum[0] + sin(rotate_phi)*momentum[1]
            p1 = -sin(rotate_phi)*momentum[0] + cos(rotate_phi)*momentum[1]
            p = p0, p1, momentum[2]
            x, y = p[dims[0]], p[dims[1]]
            if x == 0 and y == 0:
                return Point2D(0, 0)
            return Point2D(x, y) * (1.0/sqrt(x**2+y**2))

        for node in self.nodes:
            if node.item.final:
                p = list(node.item.incoming)[0]
                phi, pt, e = p.phi, p.pt, p.e
                scale = pt
                if scale < 1:
                    scale = 1
                elif scale > 100:
                    scale = 100
                scale *= self.options["scale"]

                momentum = pos_func(p.p) * scale

                sv = p.start_vertex
                sv_p = [sum(par.p[i] for par in sv.outgoing) for i in (0,1,2)]
                svn = item_nodes[sv]

                dlvl = get_max_descendant_levels(sv) + 1

                if sv_p[0] == 0 and sv_p[1] == 0:
                    continue

                pos = pos_func(sv_p) * (100.0 / sqrt(dlvl))
                svn.center = pos
                svn.dot_args["pos"] = "%s,%s!" % svn.center.tuple()
                svn.dot_args["pin"] = "true"
                if svn in nodes_remaining:
                    nodes_remaining.remove(svn)

                node.center = pos + momentum
                node.dot_args["pos"] = "%s,%s!" % node.center.tuple()
                node.dot_args["pin"] = "true"
                nodes_remaining.remove(node)

            elif node.item.initial:
                p = list(node.item.outgoing)[0]
                node.center = pos_func(p.p) * 120
                node.dot_args["pos"] = "%s,%s!" % node.center.tuple()
                node.dot_args["pin"] = "true"
                nodes_remaining.remove(node)

                sv = p.end_vertex
                sv_p = [sum(par.p[i] for par in sv.incoming) for i in (0,1,2)]
                svn = item_nodes[sv]
                pos = pos_func(sv_p) * (100.0)
                svn.center = pos
                svn.dot_args["pos"] = "%s,%s!" % svn.center.tuple()
                svn.dot_args["pin"] = "true"
                if svn in nodes_remaining:
                    nodes_remaining.remove(svn)

        return

        while nodes_remaining:
            for node in list(nodes_remaining):
                pinned = [True for edge in coming[node.item] if item_nodes[edge.going].center]
                if pinned:
                    nongluons = [p for p in pinned if not p.item.gluon]
                    if nongluons:
                        edge = nongluons[0]
                        force_scale = None
                    else:
                        edge = pinned[0]
                        force_scale = 0.1

                    phi = edge.item.phi
                    px, py, pz = edge.item.p
                    pt = edge.item.pt
                    e = edge.item.e
                    signum = 1 if sin(phi)*px + cos(phi)*py > 0 else -1
                    theta = atan2(pz, pt * signum)

                    #phi = 0
                    #phi = theta

                    #scale = ln(edge.item.e)
                    scale = e / 1000.0 + pt * 10
                    if scale < 0.1: 
                        scale = 0.1
                    elif scale > 100:
                        scale = 100
                    if force_scale:
                        scale = force_scale
                    scale *= self.options["scale"]
                    delta = Point2D(DR * sin(phi), DR * cos(phi)) * scale
                    node.center = item_nodes[edge.coming].center + delta
                    node.dot_args["pos"] = "%s,%s!" % node.center.tuple()
                    node.dot_args["pin"] = "true"
                    nodes_remaining.remove(node)
                    break


