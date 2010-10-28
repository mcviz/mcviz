from __future__ import division

from os.path import basename

from logging import getLogger; log = getLogger("mcviz.painters")

from ..layouts import get_layout
from ..styles import apply_style
from ..graphviz import run_graphviz
from ..utils import timer

class Painter(object):
    def __init__(self, graph_view, output_file, options):
        self.graph = graph_view
        self.output_file = output_file
        self.options = options
        self.extension = basename(output_file).split(".")[-1]

        # resolve resolutions
        self.ratio = options.ratio
        self.res_x, self.res_y = None, None
        if options.resolution:
            try:
                self.res_x, self.res_y = map(int, options.resolution.split("x"))
            except ValueError:
                log.fatal("resolution must be given as AxB, i.e. 800x400")
                raise Exception()
            self.ratio = self.res_y / self.res_x
        elif options.width:
            self.res_x = options.width
            if self.ratio:
                self.res_y = int(self.ratio*self.res_x)

    def layout(self):
        # Get the specified layout class and create a layout of the graph
        log.verbose("applying layout classes %s" % self.options.layout)
        layout_class = get_layout(self.options.layout)
        with timer("layout the graph", log.VERBOSE):
            self.layout = layout_class(self.graph, self.res_x, self.res_y, self.ratio, self.options)

    def style(self):
        # Apply any specified styles onto the layouted graph
        with timer("apply all styles", log.VERBOSE):
            for style in self.options.style:
                log.verbose("applying style: %s" % style)
                with timer("apply %s" % style):
                    apply_style(style, self.layout)

    def write_data(self, data_string):
        # Dump the data to stdout if required
        log.debug("data hash: 0x%0X", hash(data_string))
        if self.output_file == "-":
            print data_string
        else:
            # Write the data to file otherwise
            log.info('writing "%s"' % self.output_file)
            with open(self.output_file, "w") as f:
                f.write(data_string)

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

class GraphvizPainter(Painter):
    def graphviz_pass(self, engine, graphviz_options, dot_data):
        log.debug("dot_data hash: 0x%0X", hash(dot_data))
    
        # Dump the whole dot file before passing it to graphviz if requested
        if self.options.dump_dot:
            log.debug("Data passed to %s:" % engine)
            # TODO: flush log FD
            print dot_data

        # Process the DOT data with graphviz
        log.verbose("Calling '%s' with options %s" % (engine, graphviz_options))
        with timer("run graphviz", log.VERBOSE):
            output, errors = run_graphviz(engine, dot_data, graphviz_options)
        errors = map(str.strip, errors.split("\n"))
        errors = filter(lambda e : e and not "Warning: gvrender" in e, errors)
        if errors:
            log.warning("********* GraphViz Output **********")
            for error in errors:
                log.warning(error)
            log.warning("************************************")
        if not output.strip():
            log.error("No output from %s " % engine)
            log.error("There may be too many constraints on the graph.")
        return output

    def paint(self):
        self.layout()
        self.style()
        engine = self.options.layout_engine
        engine = engine if engine else "dot"
        opts = self.options.extra_gv_options
        if not any(opt.startswith("-T") for opt in opts):
            opts.append("-T%s" % self.extension)
        self.write_data(self.graphviz_pass(engine, opts, self.layout.dot))

class DOTPainter(Painter):
    def paint(self):
        self.layout()
        self.style()
        self.write_data(self.layout.dot)

