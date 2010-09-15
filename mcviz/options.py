
from optparse import OptionParser
import sys

from mcviz.layout import list_layouts
from mcviz.style import list_styles

def get_option_parser():
    
    p = OptionParser()
    o = p.add_option
    #
    # Program control
    #
    o("-l", "--layout", choices=list_layouts(),
      help="Select the layout class used to layout the graph (%s)" % ", ".join(list_layouts()))

    o("-s", "--style", choices=list_styles(),
      help="Select the style class used to style the graph (%s)" % ", ".join(list_styles()))

    o("-D", "--debug", action="store_true",
      help="Drop to ipython shell on exception")
    
    o("-H", "--hepmc", action="store_true",
      help="If true, input is hepmc format")
    
    o("-L", "--limit", type=int, default=None,
      help="Limit number of particles made")
    
    o("-w", "--penwidth", choices=["pt", "off"], default="off", help="[not implemented]")
    o("-W", "--edge-weight", choices=["e", "off"], default="off", help="[not implemented]")
    
    o("-t", "--line-thickness", type=float, default=1.,
      help="Controls the thickness of the graph edges")
    
    o("-I", "--show-id", action="store_true",
      help="Controls labelling particle ids")
    o("", "--show-color-id", action="store_true",
      help="Adds a label specifiying the color and anticolor")
    
    o("-c", "--contract", action="append", type=str, default=[],
      help="Particle graph contraction. Value: 'gluballs', 'kinks'")

    o("-C", "--color-mechanism", default="color_charge",
      help="Changes the way particles are colored. "
           "Possible values: color_charge, ascendents.")
           
    o("-S", "--strip-outer-nodes", type=int, default=0, metavar="N",
      help="Performs outer node stripping N times.")


    
    
    #
    # Presentation
    #
    o("-E", "--layout-engine", choices=["fdp", "neato", "dot", "sfdp", "circo", "twopi"],
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
        extra_gv_options = ["-Tplain"]

    result = options, args = p.parse_args(argv)
    options.extra_gv_options = extra_gv_options

    #if options.svg and not options.layout_engine:
    #    options.layout_engine = "dot"
        
    return result
