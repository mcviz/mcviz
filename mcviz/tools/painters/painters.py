from __future__ import division

from .. import log; log = log.getChild(__name__)

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

