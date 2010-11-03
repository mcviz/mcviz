#! /usr/bin/env python2.6

# MCViz - Visualize Monte Carlo Events
# Copyright (C) 2010  Peter Waller & Johannes Ebke

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from textwrap import dedent

from logging import getLogger; log = getLogger("mcviz.main")

from mcviz import EventGraph, GraphView, parse_options
from mcviz.transforms import apply_transforms, tag
from mcviz.painters import instantiate_painter
from mcviz.utils import get_logger_level, log_level, timer


def run(options, n_argv, args):

    # Activate the python debugger if requested
    if options.debug:
        from IPython.Shell import IPShellEmbed
        ip = IPShellEmbed(["-pdb"], rc_override=dict(quiet=True))

    if len(args) <= 1:
        log.fatal("Please specify an HepMC file or Pythia log file to run on. "
                  "Use --help for help.")
        return -1

    log.info("-------------------------------------------------------------")
    log.info("MCViz Copyright (C) 2010 Peter Waller & Johannes Ebke")
    log.info("This program comes with ABSOLUTELY NO WARRANTY - ")
    log.info("including no guarantee for correctness (aka. validation)")
    log.info("This is free software, and you are welcome to redistribute it")
    log.info("under the conditions of the GNU AGPL version 3")
    log.info("-------------------------------------------------------------")
    
    if options.demo:
        from mcviz.utils.demo import run_demo
        if n_argv != len(args) + 1:
            log.warning("For --demo, all arguments are ignored except input "
                        "files")
        for input_file in args[1:]:
            run_demo(input_file)
        return 0
    
    filename = args[1]
    log.verbose('trying to read the first event from "%s"' % filename)
    with timer('read one event from "%s"' % filename):
        event_graph = EventGraph.load(filename)
    log.info('drawing the first event from "%s" to "%s"' % (filename, options.output_file))

    log.debug('Creating a graph view')
    graph_view = GraphView(event_graph)
    
    apply_transforms(options, graph_view)
   
    painter = instantiate_painter(options, graph_view)
    log.verbose('painting the graph')
    with timer('paint the graph', log.VERBOSE):
        painter.paint()

    return 0

def main(argv):
    options, args = parse_options(argv)
    n_argv = len(argv[1:])
    with log_level(get_logger_level(options.quiet, options.verbose)):
        with timer("complete run"):
            run(options, n_argv, args)
            
if __name__ == "__main__":

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

if __name__ == "__main__":
    main()
