from subprocess import Popen, PIPE
from svg import Spline, SplineLine 

def run_graphviz(layout_engine, input_dot, options=[]):
    p = Popen([layout_engine] + options, 
              stdin=PIPE, stdout=PIPE, stderr=PIPE)
    gv_output, gv_errors = p.communicate(input_dot)
    #print >>stderr, repr(gv_stdout)
    #gv_output, gv_errors = gv_stdout.read(), gv_stderr.read()
    #gv_output = gv_stdout.read()
    #gv_errors = gv_stderr.read()
    p.wait()
    
    return gv_output, gv_errors

def pretty_value(value):
    "If the type is a string, quote it, if it is a float, strip to 3 sig. fig."
    if isinstance(value, basestring):
        if value and value[0] == "<" and value[-1] == ">":
            return value
        else:
            return '"%s"' % value
    elif isinstance(value, float):
        return "%.3f" % value
    return value

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
            tokens = line.strip().split()
            command = tokens[0]
            if command == "graph":
                self.handle_graph(tokens[1:])
            elif command == "node":
                self.handle_node(tokens[1:])
            elif command == "edge":
                self.handle_edge(tokens[1:])
            elif command == "stop":
                break

    def handle_graph(self, parameters):
        self.scale, self.width, self.height = map(float, parameters)

    def handle_node(self, parameters):
        no = int(parameters[0])
        x, y = float(parameters[1]), self.height - float(parameters[2])
        self.nodes[no] = (x,y)

    def handle_edge(self, parameters):
        no_in, no_out = int(parameters[0]), int(parameters[1])

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

        if '"' in remaining[0]:
            left, label, right = " ".join(remaining).split('"', 2)
            remaining = right.strip().split()
            label_position = (float(remaining[0]), self.height - float(remaining[1]))
            remaining = remaining[2:]
        else:
            label_position = None

        no = int(remaining[0])

        self.edge_lines[no] = splineline
        self.edge_label[no] = label_position

    def get_splines(self, points):
        if len(points) == 2:
            return []
        pairs = (points[0:2], points[2:4], points[4:6], points[6:8])
        start, c1, c2, end = map(tuple, pairs)
        if start == c1 == c2 == end:
            return []
        return [Spline(start, c1, c2, end)] + self.get_splines(points[6:])
