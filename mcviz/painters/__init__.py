from os.path import basename

from logging import getLogger; log = getLogger("mcviz.painters")

from painters import GraphvizPainter, DOTPainter
from svg import SVGPainter

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

def instantiate_painter(options, graph_view):
    
    # Determine which Painter gets to paint this graph
    outfile_extension = basename(options.output_file).split(".")[-1]
    painter_class = get_painter(options.painter, outfile_extension)
    log.debug("file extension '%s', using painter class '%s'" % 
                (outfile_extension, painter_class.__name__ ))
                
    if painter_class is None:
        log.error("Unknown output file extension: %s" % outfile_extension)
        return -1

    log.debug('creating painter class')
    return painter_class(graph_view, options.output_file, options)
