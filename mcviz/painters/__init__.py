from os.path import basename

from logging import getLogger; log = getLogger("mcviz.painters")

from painters import DOTPainter
from svg import SVGPainter

# Map file extensions to their default painters
gv_extensions = ["bmp", "dot", "xdot", "eps", "fig", "gif", "jpg", "jpeg", 
                 "jpe", "pdf", "png", "ps", "svg", "svgz", "tif", "tiff"
                 "vml", "vmlz", "vrml"]
extensions = dict(zip(gv_extensions, ["graphviz"]*len(gv_extensions)))
extensions["svg"] = "svg"
extensions["-"] = "dot" # this means stdout

