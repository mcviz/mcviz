
from optparse import OptionParser
import sys

def get_option_parser():
    
    p = OptionParser()
    o = p.add_option
    o("-m", "--method", choices=["pt", "eta", "generations"], default="pt",
      help="Specify a method")

    o("-d", "--dual", action="store_true",
      help="Draw the dual of the Feynman graph")

    o("-D", "--debug", action="store_true",
      help="Drop to ipython shell on exception")
    
    o("-L", "--limit", type=int, default=None,
      help="Limit number of particles made")
    
    o("-w", "--penwidth", choices=["pt", "off"], default="off", help="Not implemented")
    o("-W", "--edge-weight", choices=["e", "off"], default="off", help="Not implemented")
    
    o("-t", "--line-thickness", type=float, default=1.,
      help="Controls the thickness of the graph edges")
    
    o("-I", "--show-id", action="store_true",
      help="Controls labelling particle ids")
    
    o("-c", "--contract", action="append", type=str, default=[],
      help="Particle graph contraction. Value: 'gluballs', 'kinks'")

    o("-C", "--color-mechanism", default="color_charge",
      help="Changes the way particles are colored. "
           "Possible values: color_charge, ascendents.")
           
    o("-S", "--strip-outer-nodes", type=int, default=0, metavar="N",
      help="Removes the outer N nodes from the edge of the graph")
    
    o("-E", "--layout-engine", choices=["fdp", "neato", "dot", "sfdp", "circo", "twopi"])
    
    o("-x", "--extra-dot", default="",
      help="Additional information to be inserted into the graph properties")
    
    
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
        
    return result
