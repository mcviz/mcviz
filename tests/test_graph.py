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
    assert event_graph.particles
    #assert event_graph.vertices

def test_particle_consistency():
    for no in event_graph.particles:
        p = event_graph.particles[no]
        assert p.no == no

        print "PARTICLE: ", p

        print "MOTHERS: ", p.mothers
        for m in p.mothers:
            print m, m.daughters
            assert p in m.daughters

        print "DAUGHTERS: ", p.daughters
        for d in p.daughters:
            print d, d.mothers
            assert p in d.mothers

def test_vertex_consistency():
    for no in event_graph.vertices:
        v = event_graph.vertices[no]
        assert v.vno == no

        print "VERTEX: ", v
        print "INCOMING: ", v.incoming
        for p in v.incoming:
            assert v == p.vertex_out
            assert p.daughters.issubset(v.outgoing)

        print "OUTGOING: ", v.outgoing
        for p in v.outgoing:
            assert v == p.vertex_in
            assert p.mothers.issubset(v.incoming)


def test_graph():
    event_graph.particles
    print event_graph.particles[0]
    #event_graph.vertices
    

