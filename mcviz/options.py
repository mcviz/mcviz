
from optparse import OptionParser, OptionGroup
import sys

from mcviz.layouts import list_layouts
from mcviz.styles import list_styles
from mcviz.tools import list_tools
from mcviz.painters import list_painters, list_extensions


def get_option_parser():
    usage = "usage: %prog [options] {hepmc_file|pythia_log}"

    p = OptionParser(usage=usage)
    o = p.add_option
    #
    # Program control
    #
    o("-t", "--tool", choices=list_tools(), action="append", default=[],
      help="Select a that is applied to the graph (%s) "
           "Can be applied multiple times." % ", ".join(list_tools()))

    o("-l", "--layout", choices=list_layouts(), action="append", default=[],
      help="Select layout classes that are used to layout the graph (%s) "
           "Can also be applied multiple times." % ", ".join(list_layouts()))

    o("-s", "--style", choices=list_styles(), action="append", default=[],
      help="Select styles that are applied to the graph (%s)" % ", ".join(list_styles()))

    o("-q", "--quiet", action="store_true", help="Do not print out anything except warnings and errors")

    o("-v", "--verbose", action="count", help="Be more verbose. Specify -vv for debug output")

    o("--demo", action="store_true", 
      help="Create many demo svgs in the current directory (takes a while)")

    g = OptionGroup(p, "Additional Options", "")
    p.add_option_group(g)
    o = g.add_option
    #
    # Presentation
    #
    o("--subscript", choices=["id", "gluid", "color"], action="append", default=[],
      help="Add a subscript specifying a property to the label (id, color)")
    
    o("-E", "--layout-engine", choices=["fdp", "neato", "dot", "sfdp", "circo", "twopi"],
      default="dot",
      help="If specified, pipes output through specified graphviz engine")

    o("--painter", type="string", default=None,
      help="Override autodetect from outputfile extension (%s)" % ", ".join(list_painters()))


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
      help="Output file for graph. (known file extensions: %s) "
           "Note: Currently output as SVG is best by far" % ", ".join(list_extensions()))

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

    return result
