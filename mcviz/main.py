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

from mcviz import EventGraph, GraphWorkspace, FatalError, parse_options
from mcviz.utils import get_logger_level, log_level, timer


def run(options, n_argv, args):

    # Activate the python debugger if requested
    if options.debug:
        from IPython.Shell import IPShellEmbed
        ip = IPShellEmbed(["-pdb"], rc_override=dict(quiet=True))

    if len(args) <= 1:
        log.fatal("Please specify an HepMC file or Pythia log file to run on. "
                  "Use --help for help.")
        raise FatalError

    log.info("MCViz Copyright (C) 2010 Peter Waller & Johannes Ebke")
    log.info("Licensed under GNU AGPL version 3. "
             "Please see http://mcviz.net/license.txt")
    
    filename = args[1]
    log.verbose('trying to read the first event from "%s"' % filename)
    with timer('read one event from "%s"' % filename):
        event_graph = EventGraph.load(filename)
    log.info('drawing the first event from "%s"' % (filename))

    gw = GraphWorkspace("mcviz.graph", event_graph)
    gw.load_tools(options)
    gw.run()

def real_main(argv):
    options, args = parse_options(argv)
    n_argv = len(argv[1:])
    try:
        with log_level(get_logger_level(options.quiet, options.verbose)):
            with timer("complete run"):
                run(options, n_argv, args)
        return 0
    except FatalError:
        return -1
            
def main():
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

