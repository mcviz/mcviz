from __future__ import division

from optparse import OptionParser, OptionGroup
import sys

from mcviz import FatalError
from mcviz.tools import tool_type_options

def get_option_parser():
    usage = "usage: %prog [options] {hepmc_file|pythia_log}"

    p = OptionParser(usage=usage)
    o = p.add_option
    #
    # Program control
    #
    o("-q", "--quiet", action="store_true", help="Do not print out anything except warnings and errors")

    o("-v", "--verbose", action="count", help="Be more verbose. Specify -vv for debug output")

    o("--demo", action="store_true", 
      help="Create many demo svgs in the current directory (takes a while)")

    g = OptionGroup(p, "The MCViz Toolbox", "")
    p.add_option_group(g)
    o = g.add_option

    for shortopt, longopt, helptext in tool_type_options():
        o(shortopt, longopt, action="append", default=[], help=helptext)

    o("", "--optionset", action="append", default=["cl"], help="Select a set of default settings to use. Currently only 'cl'")

    g = OptionGroup(p, "Debug", "These options may help in finding problems")
    p.add_option_group(g)
    o = g.add_option

    o("-d", "--debug", action="store_true",
      help="Drop to ipython shell on exception")
    
    o("--profile", action="store_true", 
      help="Turn on profiling (requires bootstrap_extenv to have been run)")

    o("--dump-dot", action="store_true",
      help="Print the DOT data passed into graphviz.")
    return p
    
def parse_options(argv=sys.argv):
    return get_option_parser().parse_args(argv)
