from math import atan2, log

class Particle(object):
    def __init__(self, no, pdgid, name, status, mother1, mother2, 
                 daughter1, daughter2, color1, color2, px, py, pz, e, m):
        self.no = int(no)
        self.pdgid = pdgid
        self.name = name.strip("(").strip(")")
        self.status = status
        self.mothers = [int(m) for m in (mother1, mother2) if m != 0]
        self.daughters = [int(d) for d in (daughter1, daughter2) if d != 0]
        self.color, self.anticolor = int(color1), int(color2)
        self.p = px, py, pz
        self.pt = (px**2 + py**2)**0.5
        #self.eta = -log(tan(atan2(self.pt, pz)/2.))
        self.phi = atan2(px, py)
        self.e = e
        self.m = m
        self.tags = set()
        self.vertex_in = None
        self.vertex_out = None
    
    def __repr__(self):
        return "<Particle id=%i name=%s>" % (self.no, self.name)
    
    def __lt__(self, rhs):
        "Define p1 < p2 so that we can sort particles (by id in this case)"
        return self.no < rhs.no
        
    @property
    def decends_both(self):
        return self.decends(1) and self.decends(2)
        
    def decends(self, n):
        assert n == 1 or n == 2, "Only supported for initial particles"
        return "decendent_of_p%i" % n in self.tags
    
    @classmethod
    def tagger(self, what):
        """
        Return a function which tags particles with `what`
        """
        def tag(particle):
            particle.tags.add(what)
        return tag
    
    def get_color(self, default, mechanism="colour_charge"):
        
        if mechanism == "colour_charge":
            if self.color and self.anticolor:
                return "green"
            elif self.color:
                return "blue"
            elif self.anticolor:
                return "red"
            return default
            
        elif mechanism == "ascendents":
            if self.decends_both:
                return "purple"
            elif self.decends(1):
                return "red"
            elif self.decends(2):
                return "blue"
            return default
        
        else:
            raise NotImplementedError("Mechanism == '%s'" % mechanism)
            
    @property
    def initial_state(self):
        "No mothers"
        return not bool(self.mothers)
    
    @property
    def final_state(self):
        "No daughters"
        return not bool(self.daughters)

    @property
    def colored(self):
        return self.color or self.anticolor

    @property
    def gluon(self):
        return self.pdgid == 21

    @property
    def photon(self):
        return self.pdgid == 22

    @property
    def quark(self):
        return 1 <= abs(self.pdgid) <= 8
    
    @property
    def lepton(self):
        return 11 <= abs(self.pdgid) <= 18
