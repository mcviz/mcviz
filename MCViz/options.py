
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
    
    o("-L", "--limit", action="store", type=int, default=None,
      help="Limit number of particles made")
    
    o("-w", "--pen-width", choices=["pt", "off"], default="off")
    o("-W", "--edge-weight", choices=["e", "off"], default="off")
    
    return p
    
def parse_options(argv=None):
    p = get_option_parser()

    if argv is None:
        argv = sys.argv

    result = options, args = p.parse_args(argv)
    
    return result
