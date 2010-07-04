#! /usr/bin/env python

from MCViz import EventGraph

def graph_is_consistent(graph):
    for no in graph.vertices:
        v = graph.vertices[no]
        assert v.vno == no

        #print "VERTEX: ", v
        #print "INCOMING: ", v.incoming
        for p in v.incoming:
            assert v == p.vertex_out
            #print p, p.daughters, v.outgoing
            assert p.daughters.issubset(v.outgoing)

        #print "OUTGOING: ", v.outgoing
        for p in v.outgoing:
            assert v == p.vertex_in
            assert p.mothers.issubset(v.incoming)

    for no in graph.particles:
        p = graph.particles[no]
        assert p.no == no

        #print "PARTICLE: ", p

        #print "MOTHERS: ", p.mothers
        for m in p.mothers:
            #print m, m.daughters
            assert p in m.daughters

        #print "DAUGHTERS: ", p.daughters
        for d in p.daughters:
            #print d, d.mothers
            assert p in d.mothers

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
    graph_is_consistent(event_graph)
    print "removing one vertex"
    for no in event_graph.particles.keys():
        if event_graph.particles[no].vertex_in and event_graph.particles[no].vertex_out:
            event_graph.contract_particle(event_graph.particles[no])
            break
    graph_is_consistent(event_graph)
    print "removing all vertices"
    for no in event_graph.particles.keys():
        if no in event_graph.particles and not event_graph.particles[no].initial_state and not event_graph.particles[no].final_state:
            event_graph.contract_particle(event_graph.particles[no])


