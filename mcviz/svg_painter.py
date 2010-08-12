from svg import get_glyph, glyph_dimensions
from svg import Spline, SplineLine, Line

def label_pseudohtml(pdgid):
    w, h = glyph_dimensions(pdgid)
    return '<<table border="1" cellborder="0"><tr>\
           <td height="%.2f" width="%.2f">\E</td></tr></table>' % (h, w)

def paint_svg(plain, event):
    data = PlainOutput(plain)


class PlainOutput(object):
    def __init__(self, plain):

        self.scale = None
        self.width, self.height = None, None
        self.nodes = {}
        self.edges = {}

        for line in plain.split("\n"):
            tokens = line.strip().split(" ")
            command = tokens[0]
            if command == "graph":
                self.handle_graph(tokens[1:])
            elif command == "node":
                self.handle_node(tokens[1:])
            elif command == "edge":
                self.handle_edge(tokens[1:])

    def handle_graph(self, parameters):
        self.scale, self.width, self.height = map(float, parameters)

    def handle_node(self, parameters):
        no, x, y = int(parameters[0])
        x, y = float(parameters[1]), float(parameters[2])
        self.nodes[no] = (x,y)

    def handle_edge(self, parameters):
        no_in, no_out = int(parameters[0]), int(parameters[1])
        n_control_points = int(parameters[2])
        control_points = map(float, parameters[3:(3 + 2 * n_cntrl_points)])
        splineline = SplineLine(get_splines(control_points))
        edges[(no_in, no_out)] = splineline

    def get_splines(self, points):
        if len(points) == 2:
            return []
        pairs = (points[0:2], points[2:4], points[4:6], points[6:8])
        start, c1, c2, end = map(tuple, pairs)
        return [Spline(start, c1, c2, end)] + self.get_splines(points[6:])
