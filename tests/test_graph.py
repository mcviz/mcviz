#! /usr/bin/env python

from mcviz import EventGraph
from copy import deepcopy
import sys
sys.setrecursionlimit(10000)

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

def graph_view_is_consistent(graph):
    for v in graph.vertices:
        if hasattr(v, "vertex_number"):
            graph.v_map[v.vertex_number] == v
        if hasattr(v, "vertex_numbers"):
            for vertex_number in v.vertex_numbers:
                graph.v_map[vertex_number] == v

        #print "VERTEX: ", v
        #print "INCOMING: ", v.incoming
        for p in v.incoming:
            assert p in graph.particles
            assert v == p.end_vertex
            #print p, p.daughters, v.outgoing
            assert set(p.daughters).issubset(v.outgoing)

        #print "OUTGOING: ", v.outgoing
        for p in v.outgoing:
            assert p in graph.particles
            assert v == p.start_vertex
            assert set(p.mothers).issubset(v.incoming)

    for p in graph.particles:
        candidates = p.start_vertex.outgoing

        #print "PARTICLE: ", p
        assert p.start_vertex in graph.vertices
        assert p.end_vertex in graph.vertices

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
    from mcviz.options import parse_options
    options, args = parse_options([])
    global event_graph
    event_graph = EventGraph.from_pythia_log(test_file, options)

def get_bottom_nodes(top):
    #if top.
    pass 

def test_graph():
    graph = deepcopy(event_graph)
    N = len(event_graph.particles)
    assert graph.particles
    graph_is_consistent(graph)
    print "removing one vertex"
    for no in graph.particles.keys():
        if graph.particles[no].vertex_in and graph.particles[no].vertex_out:
            graph.contract_particle(graph.particles[no])
            break
    graph_is_consistent(graph)
    print "removing all vertices"
    for no in graph.particles.keys():
        if no in graph.particles and not graph.particles[no].initial_state and not graph.particles[no].final_state:
            graph.contract_particle(graph.particles[no])
    assert N == len(event_graph.particles)

def test_momentum():
    for i in (0,1,2):
        psum = sum (particle.p[i] for particle in event_graph.particles.values() if particle.final_state)
        print "Outgoing momentum sum ", i, psum
        assert abs(psum) < 0.05

    connection_to_system = set()
    for vertex in event_graph.vertices.values():
        if not vertex.edge:
            for i in (0,1,2):
                p_in = sum(particle.p[i] for particle in vertex.incoming)
                p_out = sum(particle.p[i] for particle in vertex.outgoing)
                if abs(p_in - p_out) > 0.05:
                    #assert not (all(not p.colored for p in vertex.incoming) and all(not p.colored for p in vertex.outgoing))
                    connection_to_system.add(vertex)
            p_in = sum(particle.e for particle in vertex.incoming)
            p_out = sum(particle.e for particle in vertex.outgoing)
            if abs(p_in - p_out) > 0.05:
                #assert not (all(not p.colored for p in vertex.incoming) and all(not p.colored for p in vertex.outgoing))
                connection_to_system.add(vertex)
    
    for i in (0,1,2):
        pdiff = 0
        for vertex in connection_to_system:
            p_in = sum(particle.p[i] for particle in vertex.incoming)
            p_out = sum(particle.p[i] for particle in vertex.outgoing)
            pdiff += p_in - p_out
        print i, pdiff
        assert pdiff < 1
    ediff = 0
    for vertex in connection_to_system:
        e_in = sum(particle.e for particle in vertex.incoming)
        e_out = sum(particle.e for particle in vertex.outgoing)
        ediff += e_in - e_out
    print ediff
    assert ediff < 1


def test_color():
    for vertex in event_graph.vertices.values():
        color_in = set(particle.color for particle in vertex.incoming)
        color_in.update(particle.anticolor for particle in vertex.outgoing)
        color_out = set(particle.color for particle in vertex.incoming)
        color_out.update(particle.anticolor for particle in vertex.outgoing)

        color_in.discard(0)
        color_out.discard(0)
        print vertex
        print color_in, color_out
        assert len(color_in) == len(color_out)
        #assert color_in == color_out # not valid
