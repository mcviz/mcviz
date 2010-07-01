#! /usr/bin/env python

from MCViz import EventGraph
from optparse import OptionParser
from sys import argv

def main():
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

    options, args = p.parse_args(argv)
    
    if options.debug:
        from IPython.Shell import IPShellEmbed
        ip = IPShellEmbed(["-pdb"], rc_override=dict(quiet=True))
    
    if not args:
        p.error("Specify a pythia log file to run on")
    
    event = EventGraph.from_pythia_log(args[1], options)
    
    event.draw_feynman()
    #event.draw_particles()
    

if __name__ == "__main__":
    """
    try:
        import 
    """

    main()
