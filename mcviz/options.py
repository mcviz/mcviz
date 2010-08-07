
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
    
    o("-w", "--pen-width", choices=["pt", "off"], default="off")
    o("-W", "--edge-weight", choices=["e", "off"], default="off")
    
    o("-I", "--show-id", action="store_true",
      help="Controls labelling particle ids")
    
    o("-c", "--contract", action="append", type=str, default=[],
      help="Particle graph contraction. Value: 'gluballs', 'kinks'")

    o("-C", "--color-mechanism", default="color_charge",
      help="Changes the way particles are colored. "
           "Possible values: color_charge, ascendents.")

    return p
    
def parse_options(argv=None):
    p = get_option_parser()

    if argv is None:
        argv = sys.argv

    result = options, args = p.parse_args(argv)
    
    return result
