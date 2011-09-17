from __future__ import division

from sys import stderr
from math import sqrt, sin, cos, atan2, tan, log as ln

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
             Arg("view", str, "view on the event", choices=["front", "side", "eta_pt"], default="side"),
             Arg("phi", float, "rotate the view in phi [radian]", default=0.0),
             Arg("pt", float, "minimum pT for a particle to be fixed [GeV]", default=0.0),
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
        min_fix_pt = self.options["pt"]
        D = self.options["scale"]

        def rotate_phi_proj(momentum, dims):
            p0 = cos(rotate_phi)*momentum[0] + sin(rotate_phi)*momentum[1]
            p1 = -sin(rotate_phi)*momentum[0] + cos(rotate_phi)*momentum[1]
            p = p0, p1, momentum[2]
            return Point2D(p[dims[0]], p[dims[1]])

        if self.options["view"] == "front":
            pfunc = lambda m : rotate_phi_proj(m, (0,1))
            mfunc = lambda m : rotate_phi_proj(m, (0,1))
        elif self.options["view"] == "side":
            pfunc = lambda m : rotate_phi_proj(m, (2,1))
            mfunc = lambda m : rotate_phi_proj(m, (2,1))
        elif self.options["view"] == "eta_pt":
            mfunc = lambda m : rotate_phi_proj(m, (2,1))
            def pfunc(momentum):
                p0, p1 = rotate_phi_proj(momentum, (0, 1)).tuple()
                pt = sqrt(p0**2 + p1**2)
                y = pt * (1 if p0 > 0 else -1)
                if all(momentum[i] == 0 for i in (0,1,2)):
                    return 0, 0
                if pt == 0:
                    x = - momentum[2] / abs(momentum[2]) * 5
                else:
                    x = -ln(tan(atan2(pt, momentum[2])/2.))
                return Point2D(x, y)

        for node in self.nodes:
            recursive_fix = all(p.final_state and p.pt < min_fix_pt for p in node.item.outgoing)
            nofix = node.item.final and list(node.item.incoming)[0].pt < min_fix_pt
            if not nofix and (node.item.final or recursive_fix):
                p = list(node.item.incoming)[0]
                phi, pt, e = p.phi, p.pt, p.e

                scale = pt
                if scale < 1:
                    scale = 1
                elif scale > 100:
                    scale = 100
                scale *= self.options["scale"]

                momentum = mfunc(p.p) * scale

                sv = p.start_vertex
                sv_p = [sum(par.p[i] for par in sv.outgoing) for i in (0,1,2)]
                svn = item_nodes[sv]

                dlvl = get_max_descendant_levels(sv) + 1 - (1 if recursive_fix else 0)

                if sv_p[0] == 0 and sv_p[1] == 0:
                    continue

                stretch = 1.0
                assert 0 < stretch <= 1
                pos = pfunc(sv_p) * (D / sqrt(dlvl))
                pos.y = pos.y / (abs(pos.y)/D)**(stretch) * 10 # signum modified by stretch
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
                node.center = pfunc(p.p) * 1.2 * D
                node.dot_args["pos"] = "%s,%s!" % node.center.tuple()
                node.dot_args["pin"] = "true"
                nodes_remaining.remove(node)

                sv = p.end_vertex
                sv_p = [sum(par.p[i] for par in sv.incoming) for i in (0,1,2)]
                svn = item_nodes[sv]
                pos = pfunc(sv_p) * D
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


