#! /usr/bin/env python2.6
# MCViz - Visualize Monte Carlo Events
# Copyright (C) 2010  Peter Waller & Johannes Ebke

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from os.path import basename
from textwrap import dedent

from logging import getLogger; log = getLogger("mcviz")

from mcviz import EventGraph, parse_options
from mcviz.views import apply_view_tool, GraphView, tag
from mcviz.painter import get_painter

def main(argv):
    options, args = parse_options(argv)
   
    # Activate the python debugger if requested
    if options.debug:
        from IPython.Shell import IPShellEmbed
        ip = IPShellEmbed(["-pdb"], rc_override=dict(quiet=True))

    if len(args) <= 1:
        print "Please specify an HepMC file or Pythia log file to run on. Use --help for help."
        return -1

    log.info("MCViz Copyright (C) 2010 Peter Waller & Johannes Ebke")
    log.info("This program comes with ABSOLUTELY NO WARRANTY - ")
    log.info("including no guarantee for correctness (aka. validation)")
    log.info("This is free software, and you are welcome to redistribute it")
    log.info("under the conditions of the GNU GPL version 3")
    
    # Load the first event from the given file 
    event_graph = EventGraph.load(args[1])

    # Create a view of the graph
    graph_view = GraphView(event_graph)

    # Apply view tools on it
    for tool in options.tool:
        log.debug('applying tool: %s' % tool)
        apply_view_tool(tool, graph_view)

    # Apply all Taggers on the graph
    tag(graph_view)
   
    # Determine which Painter gets to paint this graph
    outfile_extension = basename(options.output_file).split(".")[-1]
    painter_class = get_painter(options.painter, outfile_extension)
    log.info("requested painter '%s' extension '%s' ; got class '%s'" % 
            (options.painter, outfile_extension, painter_class.__name__ ))
    if painter_class is None:
        log.error("Unknown output file extension: %s" % outfile_extension)
        return -1

    # Create a painter and paint
    painter = painter_class(graph_view, options.output_file, options)
    painter.paint()

    return 0

if __name__ == "__main__":

    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    from sys import argv, exit
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

    exit(main(argv))
