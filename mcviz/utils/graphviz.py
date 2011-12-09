from .. import log; log = log.getChild(__name__)

from csv import reader as csv_reader
from subprocess import Popen, PIPE

from .. import FatalError
from . import Spline, SplineLine, Point2D


REF_PREFIX = "MCVIZ_REF_"

def run_graphviz(layout_engine, input_dot, options=[]):
    args = [layout_engine] + options
    try:
        p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    except OSError as e:
        if e.errno == 2:
            log.fatal("Couldn't run graphviz, is it installed? (try 'which dot')")
            raise FatalError
        else:
            raise
    
    gv_output, gv_errors = p.communicate(input_dot)
    p.wait()
    
    return gv_output, gv_errors

def pretty_value(value):
    "If the type is a string, quote it, if it is a float, strip to 3 sig. fig."
    if isinstance(value, basestring):
        # TODO: This is evil. let's fix this
        if value and value[0] == "<" and value[-1] == ">":
            return value
        else:
            return '"%s"' % value
    elif isinstance(value, float):
        return "%.3f" % value
    return value

def splitup(somestring):
    gen = iter(somestring.split('"'))
    for unquoted in gen:
        for part in unquoted.split():
            yield part
        yield gen.next().join('""')

def make_properties_string(**properties):
    if not properties:
        return ""

    propgen = ("%s=%s" % (prop, pretty_value(value)) 
               for prop, value in sorted(properties.iteritems()))

    return " [%s]" % ", ".join(propgen)

def make_node(name, comment="", **properties):
    properties = make_properties_string(**properties)
    if comment: comment = " // %s" % comment 
    return "%s%s%s" % (name, properties, comment)
    
def make_edge(from_, to_, comment="", directed=True, **properties):
    properties = make_properties_string(**properties)
    if comment: comment = " // %s" % comment 
    if directed: link = "->"
    else: link = "--"
    return "%s %s %s%s%s" % (from_, link, to_, properties, comment)

class PlainOutput(object):
    def __init__(self, plain):

        self.scale = None
        self.width, self.height = None, None
        self.nodes = {}
        self.edge_lines = {}
        self.edge_label = {}

        for line in plain.split("\n"):
            tokens = list(splitup(line.strip()))
            if not tokens:
                continue
            command = tokens[0]
            if command == "graph":
                self.handle_graph(tokens[1:])
            elif command == "node":
                self.handle_node(tokens[1:])
            elif command == "edge":
                self.handle_edge(tokens[1:])
            elif command == "stop":
                break
        assert self.scale, "No graph command in plain graphviz output!"

    def handle_graph(self, parameters):
        self.scale, self.width, self.height = map(float, parameters)

    def handle_node(self, parameters):
        node_ref = parameters[0][len(REF_PREFIX):]
        x, y = float(parameters[1]), self.height - float(parameters[2])
        w, h = float(parameters[3]), float(parameters[4])
        self.nodes[node_ref] = Point2D(x, y), (w, h)

    def handle_edge(self, parameters):
        """
        Reads an edge from graphviz plain output and updates LayoutEdges with 
        this information.
        """
        ref_in, ref_out = parameters[0], parameters[1]

        n_control_points = int(parameters[2])
        spline_parameters = parameters[3:(3 + 2 * n_control_points)]
        remaining = parameters[3 + 2 * n_control_points:]
        control_points = map(float, spline_parameters)
        # flip y coordinate
        for i in range(len(control_points)):
            if i % 2 == 1:
                control_points[i] = self.height - control_points[i]
        splines = self.get_splines(control_points)
        if len(splines) == 0:
            # TODO: Warn of degenerate particle
            return
        elif len(splines) == 1:
            splineline = splines[0]
        else:
            splineline = SplineLine(self.get_splines(control_points))

        if remaining[0].startswith(REF_PREFIX):
            label_position = None
        else:
            label = remaining[0].strip('"')
            label_position = (float(remaining[1]), self.height - float(remaining[2]))
            remaining = remaining[3:]

        edge_ref = remaining[0][len(REF_PREFIX):]

        self.edge_lines[edge_ref] = splineline
        self.edge_label[edge_ref] = label_position

    def get_splines(self, points):
        if len(points) == 2:
            return []
        pairs = (points[0:2], points[2:4], points[4:6], points[6:8])
        start, c1, c2, end = map(tuple, pairs)
        if start == c1 == c2 == end:
            return []
        return [Spline(start, c1, c2, end)] + self.get_splines(points[6:])
