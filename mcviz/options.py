from __future__ import division

from argparse import ArgumentParser, RawDescriptionHelpFormatter, SUPPRESS

import sys

from . import FatalError
from .help import help_topics
from .tools import tool_type_options


def get_option_parser():
    usage = ("usage: %(prog)s [options] {hepmc_file|lhe_file|pythia_log}[:<event index, 0 first>]\n"
             "       for example: %(prog)s --demo pythia_01.log:2")
    epilog = ("\nTo show extensive help, type %(prog)s --help all\n"
             "To show help on a specific tool %(prog)s --help [tool]"
             #"For a list of examples, type %(prog)s --help examples"
             )

    p = ArgumentParser(usage=usage, add_help=False, epilog=epilog, formatter_class=RawDescriptionHelpFormatter)
    o = p.add_argument
    #
    # Program control
    #
    o("-h", "--help", action="store_true", help="Show help. You can specify one of the following topics: {0}. You can also specify the name of any tool.".format(", ".join(help_topics)))

    o("-q", "--quiet", action="store_true", help="Do not print out anything except warnings and errors")

    o("-v", "--verbose", action="count", help="Be more verbose. Specify -vv for debug output")

    o("--demo", action="store_true", 
      help="Use pretty looking default (equivalent to --optionset=demo)")

    o("--units", action="store", dest="units")

    o("--output_file", action="store", help="Filename for output file", default="mcviz.svg")

    o("filename", nargs='?', help="Input file name, optionally followed by event index e.g. pythia_01.log:2", default=None)

    g = p.add_argument_group("The MCViz Toolbox")
    o = g.add_argument

    for shortopt, longopt, helptext in tool_type_options():
        o(shortopt, longopt, action="append", default=[], help=helptext)

    o("--optionset", action="append", default=["cl"], help="Select a set of default settings to use. Currently only 'cl'")

    g = p.add_argument_group("Debug", "These options may help in finding problems")
    o = g.add_argument

    o("-d", "--debug", action="store_true",
      help="Drop to ipython shell on exception")
    
    o("--profile", action="store_true", 
      help="Turn on profiling (requires bootstrap_extenv to have been run)")

    o("--dump-dot", action="store_true",
      help="Print the DOT data passed into graphviz.")

    # Not sure how to make this disappear
    o("--links", action="store_true", help=SUPPRESS)
    return p
    
def parse_options(arguments=None):
    parser = get_option_parser()
    if arguments is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(arguments)

    if args.demo:
        args.optionset = ["demo"]

    return parser, args
