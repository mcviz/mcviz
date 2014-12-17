#! /usr/bin/env python
"""EventGraph - representation of input event"""

from mcviz.logger import LOG
LOG = LOG.getChild(__name__)

from mcviz.exception import FatalError, EventParseError

class EventGraph(object):
    """Representation of an event, as it is structure in the input file"""
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
        """All particles without mothers"""
        return sorted(p for p in self.particles.values() if p.initial_state)

    @classmethod
    def load(cls, args):
        """Try to load a monte-carlo event using all available loaders"""
        loaders = [cls.from_hepmc, cls.from_lhe, cls.from_pythia_log]
        for loader in loaders:
            try:
                return loader(args)
            except EventParseError:
                LOG.debug("loader %s failed" % loader.__name__)
            except IOError:
                LOG.exception('failed to load "{0}"!'.format(args.filename))
                raise FatalError

        raise EventParseError("No loaders succeeded on %s" % args.filename)

    @classmethod
    def from_hepmc(cls, args):
        """Load event from HepMC file
        (http://lcgapp.cern.ch/project/simu/HepMC)"""
        from mcviz.graph.loaders.hepmc import load_event
        vertices, particles, units, pdfinfo = load_event(args)
        return cls(vertices, particles, units, pdfinfo)

    @classmethod
    def from_pythia_log(cls, args):
        """Load event from Pythia log file
        (http://home.thep.lu.se/~torbjorn/Pythia.html)"""
        from mcviz.graph.loaders.pythialog import load_event
        vertices, particles, units = load_event(args)
        return cls(vertices, particles, units)

    @classmethod
    def from_lhe(cls, args):
        """Load event from Les Houches event file
        (http://arxiv.org/abs/hep-ph/0609017)"""
        from mcviz.graph.loaders.leshouchesevent import load_event
        vertices, particles, units = load_event(args)
        return cls(vertices, particles, units)

