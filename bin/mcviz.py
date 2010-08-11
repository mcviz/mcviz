#! /usr/bin/env python2.6

from mcviz import EventGraph, parse_options
from mcviz.graphviz import run_graphviz
from mcviz.utils import replace_stdout
from mcviz.feynman_artist import FeynmanArtist
from mcviz.dual_artist import DualArtist
from sys import argv, stdout, stderr

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
    
    with replace_stdout() as our_stdout:
        artist.draw(event)
        dot = our_stdout.getvalue()
        if options.layout_engine:
            gv_output, gv_errors = run_graphviz(options.layout_engine, dot,
                                                options.extra_gv_options)
            result = gv_output
        else:
            result = dot
    
    try:
        print result
    except IOError, e:
        if e.errno == 32:
            # Ignore broken pipes, just means we used head or somesuch tool
            pass
        else:
            raise

if __name__ == "__main__":
    """
    try:
        import 
    """
    main()
