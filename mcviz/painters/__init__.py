
from painters import GraphvizPainter, DOTPainter, SVGPainter

# List of known painters
painters = {}
painters["svg"] = SVGPainter
painters["dot"] = DOTPainter
painters["graphviz"] = GraphvizPainter

# Map file extensions to their default painters
gv_extensions = ["bmp", "dot", "xdot", "eps", "fig", "gif", "jpg", "jpeg", 
                 "jpe", "pdf", "png", "ps", "svg", "svgz", "tif", "tiff"
                 "vml", "vmlz", "vrml"]
extensions = dict(zip(gv_extensions, ["graphviz"]*len(gv_extensions)))
extensions["svg"] = "svg"
extensions["-"] = "dot" # this means stdout

def list_painters():
    return sorted(painters.keys())

def list_extensions():
    return sorted(extensions.keys())

def get_painter(name, extension):
    if name is None:
        if extension is None:
            return painters[default]
        elif extension in extensions:
            painter = extensions[extension]
            return painters[painter]
        else:
            return None
    return painters[name]

