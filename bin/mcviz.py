#! /usr/bin/env python2.6

import logging as L

from mcviz import EventGraph, parse_options, MCVizParseError
from mcviz.graphviz import run_graphviz
from mcviz.layout import get_layout
from mcviz.style import get_style
from mcviz.views import apply_view_tool, GraphView, tag
from sys import argv, stdout, stderr, exit

from textwrap import dedent

def main():
    options, args = parse_options(argv)
    
    if options.debug:
        from IPython.Shell import IPShellEmbed
        ip = IPShellEmbed(["-pdb"], rc_override=dict(quiet=True))

    if len(args) <= 1:
        print "Specify a pythia log file to run on"
        return -1
    
    event_graph = EventGraph.load(args[1], options)

    # step 1a: make a view and apply view tools on it
    graph_view = GraphView(event_graph)
    if options.view_tools:
        for tool in options.view_tools:
            apply_view_tool(tool, graph_view)
    tag(graph_view)
   
    # step 2: layout event graph into a dot file
    layout_class = get_layout(options.layout)
    layout = layout_class(graph_view, options)
    result = layout.dot

    # [step 3]: process layouted dot file with graphviz
    if options.layout_engine:
        gv_output, gv_errors = run_graphviz(options.layout_engine, result,
                                            options.extra_gv_options)
        errors = map(str.strip, gv_errors.split("\n"))
        errors = filter(lambda e : e and not "Warning: gvrender" in e, errors)
        if errors:
            print >> stderr, "********* GraphViz ERRORS **********"
            print >> stderr, "\n".join(errors)
            print >> stderr, "************************************"
        if not gv_output.strip():
            print >> stderr, "ERROR: No output from %s " % options.layout_engine
            print >> stderr, "There may be too many constraints on the graph."
            return -1

        result = gv_output

        if "-Tplain" in options.extra_gv_options:
            layout.update_from_plain(result)
 
    # [step 4]: create styled svg file from event graph + graphviz position

    if options.svg:
        style_class = get_style(options.style)
        style = style_class(layout, options)
        result = style.paint()
        #result = paint_svg(result, event, style)

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
    L.basicConfig(level=L.DEBUG)
    
    from sys import argv
    if "--profile" in argv:
        try:
            from profilestats import profile
            main = profile(main)
        except:
            print dedent("""
            #######
            Profilestats had a problem. Did you install it?
            Are you in the right environment?
            See the mcviz/utils/bootstrap_extenv.sh and source 
            mcviz/utils/extenv/bin/activate
            #######""").strip()
            raise

    exit(main())
