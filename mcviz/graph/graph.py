#! /usr/bin/env python

from .. import log; log = log.getChild(__name__)

from mcviz import FatalError
from . import EventParseError
#from mcviz.tests.test_graph import graph_is_consistent

class EventGraph(object):
    def __init__(self, vertices, particles, units, pdfinfo=None):
        """
        `records`: A list containing many particles
        """
        self.vertices = vertices
        self.particles = particles
        self.units = units
        self.pdfinfo = pdfinfo
        # Graph consistency checks
        #graph_is_consistent(self)

    @property
    def initial_particles(self):
        return sorted(p for p in self.particles.values() if p.initial_state)
    
    @classmethod
    def load(cls, args):
        """
        Try to load a monte-carlo event using all available loaders
        """
        loaders = [cls.from_hepmc, cls.from_lhe, cls.from_pythia_log]
        for loader in loaders:
            try:
                return loader(args)
            except EventParseError:
                log.debug("loader %s failed" % loader.__name__)
            except IOError as e:
                log.exception('loading file "{0}" failed!'.format(args.filename))
                raise FatalError
                
        raise EventParseError("No loaders succeeded on %s" % args.filename)
    
    @classmethod
    def from_hepmc(cls, args):
        from .loaders.hepmc import load_event
        vertices, particles, units, pdfinfo = load_event(args)
        return cls(vertices, particles, units, pdfinfo)


        
    @classmethod
    def from_pythia_log(cls, args):
        from .loaders.pythialog import load_event
        vertices, particles, units = load_event(args)
        return cls(vertices, particles, units)

    @classmethod
    def from_lhe(cls, args):
        from loaders.leshouchesevent import load_event
	vertices, particles, units = load_event(args)
	return cls(vertices, particles, units)

