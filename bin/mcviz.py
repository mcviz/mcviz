#! /usr/bin/env python

from mcviz import EventGraph, parse_options
from mcviz.utils import replace_stdout
from mcviz.feynman_artist import FeynmanArtist
from mcviz.dual_artist import DualArtist
from sys import argv, stderr

def main():
    options, args = parse_options(argv)
    
    if options.debug:
        from IPython.Shell import IPShellEmbed
        ip = IPShellEmbed(["-pdb"], rc_override=dict(quiet=True))

    if len(args) <= 1:
        print "Specify a pythia log file to run on"
        return -1

    event = EventGraph.from_pythia_log(args[1], options)
    
    if options.dual:
        artist = DualArtist(options)
    else:
        artist = FeynmanArtist(options)
        
    with replace_stdout() as stdout:
        artist.draw(event)
    
    result = stdout.getvalue()
    print result
    print >>stderr, "Hash of result: 0x%-09x" % hash(result)

if __name__ == "__main__":
    """
    try:
        import 
    """
    main()
