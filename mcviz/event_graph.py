#! /usr/bin/env python

from __future__ import with_statement

from sys import argv, stderr
from itertools import takewhile

from mcviz import MCVizParseError
from .particle import Particle
from .vertex import Vertex
from .options import parse_options
from .utils import OrderedSet

from logging import getLogger; log = getLogger("event_graph")
import logging as L

class EventGraph(object):
    def __init__(self, vertices, particles, options=None):
        """
        `records`: A list containing many particles
        """
        options = self.options = options if options else parse_options()
        self.vertices = vertices
        self.particles = particles
        # Graph consistency checks
        from .tests.test_graph import graph_is_consistent
        graph_is_consistent(self)

    @property
    def initial_particles(self):
        return sorted(p for p in self.particles.values() if p.initial_state)
    
    @classmethod
    def load(cls, filename, options=None):
        """
        Try to load a monte-carlo event using all available loaders
        """
        parsers = [cls.from_hepmc, cls.from_pythia_log]
        for parser in parsers:
            try:
                return parser(filename, options)
            except MCVizParseError:
                L.debug("Parser %s failed" % parser.__name__)
                
        raise MCVizParseError("No parsers succeeded")
    
    @classmethod
    def from_hepmc(cls, filename, options=None):
        from loaders.hepmc import load_first_event
        vertices, particles = load_first_event(filename)
        return cls(vertices, particles, options)
        
    @classmethod
    def from_pythia_log(cls, filename, options=None):
        from loaders.pythialog import load_event
        vertices, particles = load_event(filename)
        return cls(vertices, particles, options)

