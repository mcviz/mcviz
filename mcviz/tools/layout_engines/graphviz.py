from logging import getLogger; log = getLogger("mcviz.utils.graphviz")

from mcviz.tool import LayoutEngine
from mcviz.utils.graphviz import run_graphviz
from mcviz.utils import timer

from new import classobj

class GraphvizEngine(LayoutEngine):
    _global_args = [("extra_gv_options")]
    _args = [("dump", bool)]

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
        opts = self.options["extra_gv_options"]
        if not any(opt.startswith("-T") for opt in opts):
            opts.append("-Tplain")
        plain = self.graphviz_pass(engine, opts, layout.dot)
        layout.update_from_plain(plain)

for le in ["fdp", "neato", "dot", "sfdp", "circo", "twopi"]:
    # create class and apply "tool" decorator
    classobj(le, (GraphvizEngine,), {"_name" : le})



