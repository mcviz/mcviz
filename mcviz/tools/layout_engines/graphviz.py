from logging import getLogger; log = getLogger("mcviz.utils.graphviz")

from mcviz.tools import LayoutEngine, Arg
from mcviz.utils.graphviz import run_graphviz
from mcviz.utils import timer

from new import classobj

class GraphvizEngine(LayoutEngine):
    _global_args = [("extra_gv_options")]
    _args = [Arg("dump", bool, "dump raw graphviz input", default=False),
             Arg("extra", str, "extra graphviz options", default="")]
    _base = True

    def graphviz_pass(self, engine, graphviz_options, dot_data):
        log.debug("dot_data hash: 0x%0X", hash(dot_data))

        # Dump the whole dot file before passing it to graphviz if requested
        if self.options["dump"]:
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

    def __call__(self, layout):
        engine = self._name
        opts = self.options["extra"].split()
        if not any(opt.startswith("-T") for opt in opts):
            opts.append("-Tplain")
        plain = self.graphviz_pass(engine, opts, self.dot(layout))
        layout.update_from_plain(plain)

    def dot(self, layout):
        out = ["digraph pythia {"]
        out.append('dpi=1;')
        if layout.width and layout.height:
            out.append('size="%s,%s!";' % (layout.width, layout.height))
        if layout.ratio:
            out.append("ratio=%s;" % layout.ratio)
        out.append(layout.dot)
        out.append("}")
        return "\n".join(out)

class DotEngine(GraphvizEngine):
    _name = "dot"
    _args = [Arg("orientation", str, "orientation of the graph", "TB", choices=["LR","RL", "TB", "BT"])]

    def dot(self, layout):
        """ tuning parameters specific to dot:
          * rankdir (G) - direction of layout LR, RL, TB, BT 

          * nodesep (G, 0.25) - minimum in-rank separation
          * ranksep (G, 0.5) - minimum separation between ranks

          * aspect (G, unset) - if set can narrow layouts
          * compound (G, false) - allow edges between clusters

          * ordering (G) - force ordering of in/out particles per vertex

          * remincross (G) - reminimize cluster (??)
          * mclimit (G, 1) - tweak number of iterations
          * searchsize (G, 30) - optimization parameter, bigger better

          * rank (S) -  same, min, max, source or sink (force to that rank)
          * group (N) - if same at start and end, try to connect straight
          * constraint (E, true) - edge used for ranking 
          * minlen (E, 1) - minumum edge length in rank difference
          * weight (E, 1) - heavier is shorter, 0 is minimum
          """

        out = ["digraph pythia {"]
        #out.append(layout.options["extra_dot"])
        out.append('rankdir="%s";' % self.options["orientation"])
        #out.append('ranksep=10;')
        out.append('dpi=1;')
        if layout.width and layout.height:
            out.append('size="%s,%s!";' % (layout.width, layout.height))
        if layout.ratio:
            out.append("ratio=%s;" % layout.ratio)

        out.append("edge [labelangle=90]")

        out.append(layout.dot)

        out.append("}")
        return "\n".join(out)

class FDPEngine(GraphvizEngine):
    _name = "fdp"
    
    def dot(self, layout):
        """ tuning parameters specific to FDP:
         * K (GC, 0.3) - ideal edge length, overruled by edge len
         * sep (G, +4) - minimal (additive) margin. no plus -> multiplicative
         * esep (G, +3) - spline routing margin (as sep)

         * overlap (G, 9:portho) - scale, false (voronoi), scalexy, compress,
                vpsc
         * maxiter (G, 600) - # iterations
         * pack, packmode (G) - for packing disconnected graphs
         * start (G) - random seed for initial position placementi (?)
         * voro_margin (G, 0.05) -  Factor to scale up drawing to allow margin
                    for expansion in Voronoi technique. dim' = (1+2*margin)*dim
         * dim, dimen (G, 2) - dimensionality

         * weight (E, 1.0) - must be >1; 
         * len (E, 0.3) - preferred edge length

         * pin (N) - if true, fix the position of that node
         * pos (N) - set initial position (or fixed position)
        """

        out = ["digraph pythia {"]
        out.append('K=1.0;')
        out.append('sep="+30";')
        out.append('overlap="6:";') # tradeoff between speed and overlap quality
        out.append('dpi=1;')

        if layout.width and layout.height:
            out.append('size="%s,%s!";' % (layout.width, layout.height))
        if layout.ratio:
            out.append("ratio=%s;" % layout.ratio)

        out.append("edge [labelangle=90]")

        out.append(layout.dot)

        out.append("}")
        return "\n".join(out)


for le in ["neato", "sfdp", "circo", "twopi"]:
    # create class and apply "tool" decorator
    classobj(le, (GraphvizEngine,), {"_name" : le})



