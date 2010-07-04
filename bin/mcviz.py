#! /usr/bin/env python

from MCViz import EventGraph, parse_options
from sys import argv

def main():
    options, args = parse_options(argv)
    
    if options.debug:
        from IPython.Shell import IPShellEmbed
        ip = IPShellEmbed(["-pdb"], rc_override=dict(quiet=True))
    
    if not args:
        p.error("Specify a pythia log file to run on")
    
    event = EventGraph.from_pythia_log(args[1], options)
    
    if options.dual:
        event.draw_particles()
    else:
        event.draw_feynman()

if __name__ == "__main__":
    """
    try:
        import 
    """

    main()
