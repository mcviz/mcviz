#! /usr/bin/env python2.6
"""
MCViz - Visualize Monte Carlo Events
Copyright (C) 2011 : See http://mcviz.net/AUTHORS

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from textwrap import dedent

from mcviz.logger import LOG, get_logger_level, log_level
LOG = LOG.getChild(__name__)

from mcviz.exception import FatalError, EventParseError
from mcviz.graph.graph import EventGraph
from mcviz.workspace import GraphWorkspace
from mcviz.options import parse_options

# from .utils import Units
from mcviz.utils.timer import Timer
TIMER = Timer(LOG, LOG.VERBOSE)
from mcviz.help import run_help

def run(args, argv):
    """Load event and apply tools to resulting Workspace"""
    # Activate the python debugger if requested
    if args.debug:
        import IPython
        IPython.embed()

    if not args.filename:
        LOG.fatal("Please specify an HepMC, LHE or Pythia log file to run on. "
                  "Use --help for help.")
        raise FatalError

    LOG.info("MCViz Copyright (C) 2011 : See http://mcviz.net/AUTHORS")
    LOG.info("Licensed under GNU AGPL version 3. "
             "Please see http://mcviz.net/license.txt")

    filename = args.filename
    LOG.verbose('trying to read event from "%s"' % filename)
    with TIMER('read event from "%s"' % filename):
        try:
            event_graph = EventGraph.load(args)
        except EventParseError:
            LOG.fatal("No success in reading events from %s!" % filename)
            raise FatalError
    LOG.info('drawing event from "%s"' % (filename))

    workspace = GraphWorkspace("local", event_graph, cmdline=" ".join(argv))
    workspace.load_tools(args)
    workspace.run()

def real_main(argv):
    """Parse arguments then call run"""
    parser, args = parse_options()
    if args.help:
        with log_level(LOG.ERROR):
            return run_help(parser, args)

    try:
        with log_level(get_logger_level(args.quiet, args.verbose)):
            with TIMER("complete run"):
                run(args, argv)
        return 0
    except FatalError:
        return -1

def main():
    """Wrap real_main in profiler if requested"""
    from sys import argv

    if "--profile" in argv:
        try:
            from profilestats import profile
            to_run = profile(real_main)
        except:
            print dedent("""
            #######
            Profilestats had a problem. Did you install it?
            Are you in the right environment?
            See the mcviz/utils/bootstrap_extenv.sh and source
            mcviz/utils/extenv/bin/activate
            #######""").strip()
            raise
    else:
        to_run = real_main

    return to_run(argv)
