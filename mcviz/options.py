from __future__ import division

from optparse import OptionParser, OptionGroup
import sys

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

    g = OptionGroup(p, "Presentation", "Options that modify the presentation")
    p.add_option_group(g)
    o = g.add_option

    o("--stretch", default=0.2, type=float,
      help="for -lFixIni: Ranges from 0 to 1; 0 pulls the initial particles apart the furthest.")

    o("--label-size", type=float, default=1.,
      help="scale of the labels in the output SVG file")
    
    o("--extra-dot", default="",
      help="Additional information to be inserted into the graph properties")
      
    g = OptionGroup(p, "Output", "Options that modify the presentation")
    p.add_option_group(g)
    o = g.add_option
    #
    # Control the output file options
    #
    o("-o", "--output-file", type=str, default="mcviz.svg",
      help="Output file for graph. "
           "Note: Currently output as SVG is best by far")

    o("--ratio", type=float, help="aspect ratio of output canvas")
      
    o("--width", default=100, type=int, help="Width of the output file in pixels")

    o("--resolution", metavar="800x400",
            type=str, help="Resolution of the output file in pixels")

      
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
    
def parse_options(argv=None):
    p = get_option_parser()

    if argv is None:
        argv = sys.argv

    if "--" in argv:
        extraopts_index = argv.index("--")
        extra_gv_options = argv[extraopts_index+1:]
        argv = argv[:extraopts_index]
    else:
        extra_gv_options = []

    result = options, args = p.parse_args(argv)

    options.extra_gv_options = extra_gv_options

    # resolve resolutions
    res_x, res_y = None, None
    if options.resolution:
        try:
            res_x, res_y = map(int, options.resolution.split("x"))
        except ValueError:
            log.fatal("resolution must be given as AxB, i.e. 800x400")
            raise Exception()
        options.ratio = res_y / res_x
    elif options.width:
        res_x = options.width
        if options.ratio:
            res_y = int(options.ratio*res_x)
    options.resolution = (res_x, res_y)

    return result
