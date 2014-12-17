
from math import atan2, log as ln, tan

class Particle(object):

    def __init__(self, px, py, pz, e, m):

        self.p = px, py, pz
        self.e = e
        self.m = m
        self.pt = (px**2 + py**2)**0.5
        self.eta = -ln(tan(atan2(self.pt, pz)/2.)) if self.pt else +999
        self.phi = atan2(px, py)
        self.e = e
        self.m = m
        self.other_flow = {}

        self.vertex_in = None
        self.vertex_out = None

        self.mothers = self.daughters = None

    @classmethod
    def from_pythia(cls, record):
        (no, pdgid, name, status, mother1, mother2, daughter1, daughter2,
         color1, color2, px, py, pz, energy, mass) = record

        particle = cls(px, py, pz, energy, mass)
        particle.no = int(no)
        particle.pdgid = pdgid
        particle.name = name.strip("(").strip(")")
        particle.status = int(status)
        particle.mothers = [int(m) for m in (mother1, mother2) if m != 0]
        particle.daughters = [int(d) for d in (daughter1, daughter2) if d != 0]
        particle.color, particle.anticolor = int(color1), int(color2)

        return particle

    @classmethod
    def from_lhe(cls, no, part):
        #IDUP(I), ISTUP(I), MOTHUP(1,I), MOTHUP(2,I), ICOLUP(1,I), ICOLUP(2,I), PUP(1,I), PUP(2,I), PUP(3,I), PUP(4,I), PUP(5,I), VTIMUP(I), SPINUP(I)
        # p, e & m values are in GeV
        # lifetime is invarient lifetime in mm
        # spin=9 particles are unpolarized or unknown

        particle = cls(part.PUP1, part.PUP2, part.PUP3, part.PUP4, part.PUP5)
        particle.no = no
        particle.pdgid = part.IDUP
        particle.name = ""
        particle.status = part.ISTUP
        particle.mothers = [m for m in (part.MOTHUP1, part.MOTHUP2) if m != 0]
        particle.daughters = []
        particle.color, particle.anticolor = part.ICOLUP1, part.ICOLUP2

        return particle

    @classmethod
    def from_hepmc(cls, hparticle):
        hp = hparticle
        particle = cls(*map(float, (hp.px, hp.py, hp.pz, hp.energy, hp.mass)))
        particle.hparticle = hp
        particle.no = int(hp.barcode)
        particle.pdgid = int(hp.pdgid)
        particle.name = ""
        particle.status = int(hp.status)
        particle.color, particle.anticolor = hp.flow.pop(1, 0), hp.flow.pop(2, 0)
        particle.other_flow = hp.flow
        return particle

    def __repr__(self):
        return "<Particle id=%i name=%s>" % (self.no, self.name)

    def __lt__(self, rhs):
        "Define p1 < p2 so that we can sort particles (by id in this case)"
        return self.no < rhs.no

    @property
    def initial_state(self):
        "No mothers"
        return not bool(self.mothers)

    @property
    def final_state(self):
        "No daughters"
        return not bool(self.daughters)
