#! /usr/bin/env python

from MCViz import EventGraph

event_graph = None
def setup():
    test_file = "inputs/pythia01.out"
    
    global event_graph
    event_graph = EventGraph.from_pythia_log(test_file)

def get_bottom_nodes(top):
    #if top.
    pass 

def test_graph():

    event_graph.particles
