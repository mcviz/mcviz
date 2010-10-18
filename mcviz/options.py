
from optparse import OptionParser
import sys

from mcviz.layout import list_layouts
from mcviz.style import list_styles
from mcviz.views import list_view_tools
from mcviz.painter import list_painters, list_extensions

def get_option_parser():
    usage = "usage: %prog [options] {hepmc_file|pythia_log}"
    p = OptionParser(usage=usage)
    o = p.add_option
    #
    # Program control
    #
    o("-d", "--debug", action="store_true",
      help="Drop to ipython shell on exception")

    o("-t", "--tool", choices=list_view_tools(), action="append", default=[],
      help="Select a tool that is applied to the graph (%s)" % ", ".join(list_view_tools()))

    o("-l", "--layout", choices=list_layouts(), action="append", default=[],
      help="Select the layout classes used to layout the graph (%s)" % ", ".join(list_layouts()))

    o("-s", "--style", choices=list_styles(), action="append", default=[],
      help="Select a style that is applied to the graph (%s)" % ", ".join(list_styles()))

    o("-o", "--output-file", type="string", default="mcviz.svg",
      help="Output file for graph. Known file extensions: %s" % ", ".join(list_extensions()))

    o("--painter", type="string", default=None,
      help="Override autodetect from outputfile extension (%s)" % ", ".join(list_painters()))

    #
    # Presentation
    #
    o("--subscript", choices=["id","color"], action="append", default=[],
      help="Add a subscript specifying a property to the label (id, color)")
    
    o("-E", "--layout-engine", choices=["fdp", "neato", "dot", "sfdp", "circo", "twopi"],
      default="dot",
      help="If specified, pipes output through specified graphviz engine")

    o("--svg", action="store_true",
      help="create an SVG from the layout using the internal SVG painter")

    o("--label-size", type=float, default=1.,
      help="scale of the labels in the output SVG file")
    
    o("-x", "--extra-dot", default="",
      help="Additional information to be inserted into the graph properties")
    
    o("--ratio", default="0.5", 
      help="Ratio of output graph")
      
    o("-F", "--fix-initial", action="store_true",
      help="Fix the initial vertex positions.")
      
    # These two only have an effect if fix_initial is on.
    o("--width", default=100, type=float, help="Arbitrary units.")
    o("--stretch", default=20, type=float,
      help="Ranges from 0 to width/2. 0 pulls the initial particles apart the "
           "furthest.")
    
    o("-U", "--use-unicode", action="store_true",
      help="Use unicode for labels. (Default False)")
    
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

    #if options.svg and not options.layout_engine:
    #    options.layout_engine = "dot"
        
    return result
