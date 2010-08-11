from subprocess import Popen, PIPE

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

