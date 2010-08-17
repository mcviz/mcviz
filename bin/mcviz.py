#! /usr/bin/env python2.6

from mcviz import EventGraph, parse_options
from mcviz.graphviz import run_graphviz
from mcviz.utils import replace_stdout
from mcviz.layout import get_layout
from mcviz.style import get_style
from mcviz.svg_painter import paint_svg
from sys import argv, stdout, stderr

def main():
    options, args = parse_options(argv)
    
    if options.debug:
        from IPython.Shell import IPShellEmbed
        ip = IPShellEmbed(["-pdb"], rc_override=dict(quiet=True))

    if len(args) <= 1:
        print "Specify a pythia log file to run on"
        return -1

    # step 1: get event graph representation
    event = EventGraph.from_pythia_log(args[1], options)
   
    # step 2: layout event graph into a dot file
    layout = get_layout(options.layout)(options)
    with replace_stdout() as our_stdout:
        layout.layout(event)
        result = our_stdout.getvalue()

    # [step 3]: process layouted dot file with graphviz
    if options.layout_engine:
        gv_output, gv_errors = run_graphviz(options.layout_engine, result,
                                            options.extra_gv_options)
        result = gv_output
        # TODO: check gv_errors
    
    # [step 4]: create styled svg file from event graph + graphviz position
    style = get_style(options.style)(options)
    if options.svg:
        result = paint_svg(result, event, style)

    # step 5: print whatever result we get to stdout
    try:
        print result
    except IOError, e:
        if e.errno == 32:
            # Ignore broken pipes, just means we used head or somesuch tool
            pass
        else:
            raise

if __name__ == "__main__":
    """
    try:
        import 
    """
    main()
