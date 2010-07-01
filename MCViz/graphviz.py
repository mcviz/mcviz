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

def print_node(name, comment="", **properties):
    properties = make_properties_string(**properties)
    if comment: comment = " // %s" % comment 
    print("%s%s%s" % (name, properties, comment))
    
def print_edge(from_, to_, comment="", **properties):
    properties = make_properties_string(**properties)
    if comment: comment = " // %s" % comment 
    print("%s -> %s%s%s" % (from_, to_, properties, comment))

