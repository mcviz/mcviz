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

    options, args = p.parse_args(argv)
    
    if not args:
        p.error("Specify a pythia log file to run on")
    
    event = EventGraph.from_pythia_log(args[1])
    
    event.draw_feynman()
    #event.draw_particles()
    

if __name__ == "__main__":
    """
    try:
        import 
    """

    main()
