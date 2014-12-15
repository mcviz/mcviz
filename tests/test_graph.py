#! /usr/bin/env python

from mcviz.graph import EventGraph, GraphView
from copy import deepcopy
import sys
sys.setrecursionlimit(10000)

def graph_is_consistent(graph):
    for vertex in graph.vertices:
        #print "VERTEX: ", v
        #print "INCOMING: ", v.incoming
        for p in vertex.incoming:
            assert vertex == p.end_vertex
            #print p, p.daughters, v.outgoing
            assert all(daughter in vertex.outgoing for daughter in p.daughters)

        #print "OUTGOING: ", v.outgoing
        for p in vertex.outgoing:
            assert vertex == p.start_vertex
            assert all(mother in vertex.incoming for mother in p.mothers)

    for particle in graph.particles:
        #print "PARTICLE: ", p

        #print "MOTHERS: ", p.mothers
        for m in particle.mothers:
            #print m, m.daughters
            assert particle in m.daughters

        #print "DAUGHTERS: ", p.daughters
        for d in particle.daughters:
            #print d, d.mothers
            assert particle in d.mothers

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
    test_file = "examples/pythia/LHC/out01"
    from mcviz.options import parse_options
    parser, args = parse_options([])
    args.filename = test_file
    global event_graph, view_graph
    event_graph = EventGraph.from_pythia_log(args)
    view_graph = GraphView(event_graph)

def get_bottom_nodes(top):
    #if top.
    pass 

def test_graph():
    graph = deepcopy(view_graph)
    N = len(event_graph.particles)
    assert graph.particles
    graph_is_consistent(graph)
    print "removing one vertex"
    for particle in graph.particles:
        if particle.start_vertex and particle.end_vertex:
            graph.summarize_particles([particle])
            break
    graph_is_consistent(graph)
    print "removing all vertices"
    for particle in graph.particles:
        if particle in graph.particles and not particle.initial_state and not particle.final_state:
            graph.summarize_particles([particle])
    assert N == len(event_graph.particles)

def test_momentum():
    for i in (0,1,2):
        psum = sum (particle.p[i] for particle in event_graph.particles.values() if particle.final_state)
        print "Outgoing momentum sum ", i, psum
        assert abs(psum) < 0.05

    connection_to_system = set()
    for vertex in view_graph.vertices:
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
