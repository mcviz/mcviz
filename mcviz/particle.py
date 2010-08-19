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
        self.contraction_count = 0
        self.subscripts = []
    
    def __repr__(self):
        return "<Particle id=%i name=%s>" % (self.no, self.name)
    
    def __lt__(self, rhs):
        "Define p1 < p2 so that we can sort particles (by id in this case)"
        return self.no < rhs.no
        
    @property
    def descends_both(self):
        return self.descends(1) and self.descends(2)
    
    @property
    def descends_one(self):
        return ((self.descends(1) or self.descends(2)) 
                and not (self.descends(1) and self.descends(2)))
        
    def descends(self, n):
        assert n == 1 or n == 2, "Only supported for initial particles"
        return "descendant_of_p%i" % n in self.tags
    
    @classmethod
    def tagger(self, what):
        """
        Return a function which tags particles with `what`
        """
        def tag(particle, depth):
            particle.tags.add(what)
        return tag
    
    @classmethod
    def attr_setter(self, what, value):
        def dosetattr(particle, depth):
            setattr(particle, what, value)
        return dosetattr
    
    def get_color(self, default, mechanism="color_charge"):
        
        if mechanism == "color_charge":
            if self.color and self.anticolor:
                return "green"
            elif self.color:
                return "blue"
            elif self.anticolor:
                return "red"
            return default
            
        elif mechanism == "ascendents":
            if self.descends_both:
                return "purple"
            elif self.descends(1):
                return "red"
            elif self.descends(2):
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
    def boson(self):
        return 21 <= abs(self.pdgid) <= 25 or 32 <= abs(self.pdgid) <= 37

    @property
    def quark(self):
        return 1 <= abs(self.pdgid) <= 8
    
    @property
    def lepton(self):
        return 11 <= abs(self.pdgid) <= 18

    @property
    def reference(self):
        return "P%i" % self.no
