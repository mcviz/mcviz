from __future__ import division

from .. import log; log = log.getChild(__name__)

import re

from os.path import basename

from mcviz.tools import Painter, FundamentalTool, Arg

class StdPainter(Painter):
    _global_args = ("output_file",)
    _args = (Arg("output_file", str, "output filename", default="mcviz.svg"),)
    _base = True

    def write_data(self, data_string):
        output_file = self.options["output_file"]
        # Dump the data to stdout if required
        log.debug("data hash: 0x%0X", hash(data_string))
        if output_file == "-":
            print data_string
        elif hasattr(output_file, "write"):
            output_file.write(data_string.encode("UTF-8"))
        else:
            # Write the data to file otherwise
            log.info('writing "%s"' % output_file)
            with open(output_file, "w") as f:
                f.write(data_string.encode("UTF-8"))

    def recalculate_boundingbox(self):
        # if we do not know the scale; (i.e. bounding box) calculate it
        x_min, y_min, x_max, y_max = 0, 0, 0, 0
        def get_minmax(x,y):
            return min(x, x_min), min(y, y_min), max(x, x_max), max(y, y_max)

        for edge in self.layout.edges:
            if edge.spline:
                x0, x1, y0, y1 = edge.spline.boundingbox
                x_min, y_min, x_max, y_max = get_minmax(x0, y0)
                x_min, y_min, x_max, y_max = get_minmax(x1, y0)
                x_min, y_min, x_max, y_max = get_minmax(x0, y1)
                x_min, y_min, x_max, y_max = get_minmax(x1, y1)

        for node in self.layout.nodes:
            if node.center:
                x_min, y_min, x_max, y_max = get_minmax(node.center.x, node.center.y)
        wx = x_max - x_min
        wy = y_max - y_min
        if not self.layout.width:
            self.layout.width = 100
            self.layout.height = 100
            self.layout.scale = 1
        else:
            self.layout.scale = min(self.width/wx, self.height/wy)


class DOTPainter(StdPainter, FundamentalTool):
    """
    Writes out the graph in dot format
    """
    _name = "dot"
    def __call__(self, workspace, layout):
        self.write_data("graph {\n%s\n}" % layout.dot.encode("UTF-8"))

class ThreePainter(StdPainter, FundamentalTool):
    _name = "3"
    def __call__(self, workspace, layout):
        
        assert getattr(layout, "is3D", False), (
            "You must use a layout engine with 3D co-ordinates.")
        
        from webcolors import name_to_hex
        def get_color(color):
            if not color.startswith("#"):
                color = name_to_hex(color)
            return "0x" + color[1:]
                
        object_to_layoutobject = {}
        for e in list(layout.edges) + list(layout.nodes):
            assert not e.item in object_to_layoutobject
            object_to_layoutobject[e.item] = e
        
        BIGDEPTH = 0
        def mark(item, depth):
            current_depth = getattr(item, "distance_to_final_vertex", BIGDEPTH)
            item.distance_to_final_vertex = max(depth, current_depth)
        
        graph = layout.graph
        final_state = [p for p in graph.particles if p.final_state]
        for p in final_state: 
            graph.walk(p, vertex_action=mark, particle_action=mark, ascend=True)
        
        maxdistance = max(getattr(p, "distance_to_final_vertex", 0) for p in graph.particles)
        
        data = []; A = data.append
        A("maxdistance = {0}; data = [".format(maxdistance))
        
        
        lines = [edge.spline for edge in layout.edges]
        from pprint import pprint
        #pprint(lines)
        lines = [edge.spline for edge in layout.edges if edge.spline and edge.spline[0] and edge.spline[1]]
        
        assert lines, "Something wrong with the layout?"
        
        p1s, p2s = zip(*lines)
        ps = p1s + p2s
        ps = xs, ys, zs = zip(*ps)
        cmins = xmin, ymin, zmin = map(min, ps)
        cmaxs = xmax, ymax, zmax = map(max, ps)
        diffs = xd, yd, zd = [mi - ma for mi, ma in zip(cmins, cmaxs)]
        corrections = [d / 2 for d in diffs]
        
        def point_correction(p):
            return [(coord - mi + correction)*2
                     for coord, correction, mi in zip(p, corrections, cmins)]
        
        def correction(spline):
            p1, p2 = spline
            return point_correction(p1), point_correction(p2)
        
        for edge in layout.edges:
            if not edge.spline: continue
            edge.spline = correction(edge.spline)
        
        for edge in layout.edges:
            if not edge.spline: continue
            
            sa = edge.style_args
            A("[{0}, {1}, {2}],".format(
                ", ".join(map(str, edge.spline[0] + edge.spline[1])),
                get_color(sa.get("fill", "white")),
                sa.get("stroke-width", 1),
            ))
        
        for p in []: # graph.particles:
            lo = object_to_layoutobject[p]
            sa = lo.style_args
            color = sa.get("fill", "white")
            from math import log10
            #linewidth = sa.get("stroke-width", 1)
            linewidth = log10(1+p.e)
            #A("{p.p} {p.e} {p.pdgid} {0.style_args}".format(, p=p))
            A("[{p.p[0]}, {p.p[1]}, {p.p[2]}, {p.e}, {linewidth}, {color}, {depth}],".format(
                p=p, color=color, linewidth=round(linewidth, 2), 
                depth=getattr(p, "distance_to_final_vertex", 0)))
        
        A("]")
        
        self.write_data("\n".join(data))
        
    
    SCRIPT_TAG = re.compile('<script src="([^"]+)"></script>')
    def inject_javascript(self, javascript_text):
        
        def match(m):
            (javascript_filename,) = m.groups()
            args = "mcviz.tools.painters.data", javascript_filename
            if not resource_exists(*args):
                return
            
            # ]]> is not allowed in CDATA and it appears in jquery!
            # Try to prevent that..
            javascript = resource_string(*args).replace("']]>'", "']' + ']>'")
            
            stag = '<script type="text/javascript"><![CDATA[\n{0}\n]]></script>'
            
            return stag.format(javascript.decode("UTF-8"))
        
        return SCRIPT_TAG.sub(match, javascript_text)
