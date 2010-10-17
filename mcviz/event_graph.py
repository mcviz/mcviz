#! /usr/bin/env python

from mcviz import MCVizParseError

from logging import getLogger; log = getLogger("event_graph")

class EventGraph(object):
    def __init__(self, vertices, particles):
        """
        `records`: A list containing many particles
        """
        self.vertices = vertices
        self.particles = particles
        # Graph consistency checks
        from .tests.test_graph import graph_is_consistent
        graph_is_consistent(self)

    @property
    def initial_particles(self):
        return sorted(p for p in self.particles.values() if p.initial_state)
    
    @classmethod
    def load(cls, filename):
        """
        Try to load a monte-carlo event using all available loaders
        """
        loaders = [cls.from_hepmc, cls.from_pythia_log]
        for loader in loaders:
            try:
                return loader(filename)
            except MCVizParseError:
                log.debug("loader %s failed" % loader.__name__)
                
        raise MCVizParseError("No loaders succeeded")
    
    @classmethod
    def from_hepmc(cls, filename):
        from loaders.hepmc import load_first_event
        vertices, particles = load_first_event(filename)
        return cls(vertices, particles)

        
    @classmethod
    def from_pythia_log(cls, filename):
        from loaders.pythialog import load_event
        vertices, particles = load_event(filename)
        return cls(vertices, particles)

