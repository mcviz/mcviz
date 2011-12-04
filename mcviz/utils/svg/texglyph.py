import os
import re
import unicodedata as UD
import sys
from xml.dom import minidom
from shutil import rmtree

from cPickle import dumps, loads
from pkg_resources import resource_string, resource_exists, resource_filename

from latex2svg import Latex2SVG

class PythiaParticleDB(object):
    _particles = None
    @classmethod
    def init(cls):
        grp_susy = r"(?P<susy>\~)?"
        grp_name = r"(?P<name>[A-Za-z8/]+?)"
        grp_hv = r"(?P<hv>(E|MU|TAU)?(?<!fla)[v](Up|Dn|Diag)?)?"
        grp_star = r"(?P<star>\*)?"
        grp_prime = r"(?P<prime>'+)?"
        grp_sub = r"(?P<sub>(_([A-Za-z]+?)|_([0-9]+?(s|c|b)?))*?)"
        grp_mass = r"(\((?P<mass>[0-9]*)\))?"
        grp_bar = r"(?P<bar>bar)?"
        grp_charge = r"(?P<charge>\+\+|--|\+|-|0)?"
        grp_techni = r"(?P<techni>_tc)?"
        grp_2s = r"(\((?P<state>2S)\))?"
        grp_extra = r"(\[(?P<extra>.*?)\])?"
        grp_alt = r"(\((?P<alt>.*?)\))?"
        grp_end = r"$"
        re_groups = [grp_susy, grp_name, grp_hv, grp_star, grp_prime, grp_sub, grp_mass, grp_bar, grp_charge, grp_techni, grp_2s, grp_extra, grp_alt, grp_end]
        PARTICLE_MATCH = re.compile(r"".join(re_groups))

        particles = {}
        try:
            xml_data = resource_string("mcviz.utils.svg.data", "ParticleData.xml")
        except ImportError:
            xml_data = "".join(file("data/ParticleData.xml").readlines())
        particle_data = minidom.parseString(xml_data)
        for particle in particle_data.getElementsByTagName("particle"):
            name = particle.getAttribute("name")
            antiName = particle.getAttribute("antiName")
            pdgid = int(particle.getAttribute("id"))
            if name:
                groupdict = PARTICLE_MATCH.match(name).groupdict()
                particles[pdgid] = (name, groupdict)
            if antiName:
                groupdict = PARTICLE_MATCH.match(antiName).groupdict()
                particles[-pdgid] = (antiName, groupdict)
        cls._particles = particles

        GREEK_RANGE = xrange(0x3b1, 0x3ca)
        GREEK_LETTERS = (unichr(x) for x in GREEK_RANGE)
        def fixup_unicodedata_name(x):
            "Oh dear. unicodedata misspelt lambda."
            if x == "lamda": return "lambda"
            return x
        GREEK_NAME = lambda l: fixup_unicodedata_name(UD.name(l).split()[-1].lower())
        GREEK_NAMECHARS = [(GREEK_NAME(l), l) for l in GREEK_LETTERS]
        GREEK_ALTERNATES = "(%s)" % "|".join("[%c%c]%s" % (g[0].upper(), g[0], g[1:])
                            for g, c in GREEK_NAMECHARS)
        cls.GREEK_FINDER = re.compile(GREEK_ALTERNATES)

    @classmethod
    def ensure_init(cls):
        if not cls._particles:
            cls.init()

    @classmethod
    def print_test_particle_data(cls):
        cls.ensure_init()
        keys = ['star', 'extra', 'sub', 'techni', 'hv', 'susy', 'alt', 'prime', 'bar', 'name', 'state', 'charge', 'mass']
        s = []
        for key in keys:
            print "-"*80
            print "    " + key
            print "-"*80
            for pdgid in cls.keys():
                if cls._particles[pdgid][1][key]:
                    print "%20s | %s" % (label, gd[key])

    @classmethod
    def print_test_particle_display(cls):
        cls.ensure_init()
        for pdgid in cls.keys():
            print cls.latex(pdgid)

    @classmethod
    def keys(cls):
        cls.ensure_init()
        return cls._particles.keys()

    @classmethod
    def label(cls, pdgid):
        cls.ensure_init()
        return cls._particles[pdgid][0]

    @classmethod
    def latex(cls, pdgid, bastardize=False):
        """
        Generate latex from particle
        
        `bastardize`: Generate ROOT latex from particle
        """
        cls.ensure_init()
        gd = cls._particles[pdgid][1]
        rep = []
        if not bastardize:
            rep.append(r"$\mathbf{")
        if gd["mass"]:
            rep.append(r"\underset{\mbox{\tiny (%s)}}{" % gd["mass"])
        if gd["bar"]:
            if bastardize:
                rep.append(r"#bar{")
            else:
                rep.append(r"\overline{")
        if gd["susy"]:
            rep.append(r"\tilde{")
        if gd["hv"]: rep.append(gd["name"].lower())
        else: rep.append(gd["name"])
        if gd["susy"]:
            rep.append(r"}")
        if gd["bar"]:
            rep.append(r"}")

        if gd["sub"] or gd["techni"] or gd["hv"]:
            rep.append(r"_{")
            subs = []
            if gd["hv"]:
                tmp = ",v,".join(gd["hv"].split("v")).strip(",")
                tmp = tmp.replace("E", "e", 1)
                tmp = tmp.replace("MU", "mu", 1)
                tmp = tmp.replace("TAU", "tau", 1)
                subs.append(tmp)
            if gd["sub"]:
                tmp = ",R,".join(gd["sub"].strip("_").split("R")).strip(",")
                tmp = ",L,".join(tmp.split("L")).strip(",")
                subs.extend(tmp.split("_"))
            if gd["techni"]:
                subs.append(gd["techni"].strip("_"))
            if gd["state"]:
                subs.append(gd["state"])
            if gd["extra"]:
                subs.append(gd["extra"])
            if gd["alt"]:
                subs.append(gd["alt"])
            rep.append(",".join(subs))
            rep.append(r"}")

        if gd["star"] or gd["charge"] or gd["prime"]:
            rep.append(r"^{")
            if gd["prime"]:
                rep.append("\prime")
            rep.append(r"*" if gd["star"] else "")
            if gd["charge"]:
                rep.append(gd["charge"])
            rep.append(r"}")

        if gd["mass"]:
            rep.append(r"}")
        
        if not bastardize:
            rep.append(r"}$")
            
        greek_prefix = "#" if bastardize else "\\"
            
        name = "".join(rep)
        name = cls.GREEK_FINDER.sub(lambda g: greek_prefix + g.group(0), name)
        return name


class TexGlyphLibrary(object):
    library = None

    @classmethod
    def make_library(cls):
        print >> sys.stderr, "Creating TexGlyph library..."
        cls.library = {}

        ## Add Glyphs for Elements
        try:
            elements = resource_string("mcviz.utils.svg.data", "element_data.txt")
        except ImportError:
            elements = file("data/element_data.txt").read()
        for line in elements.split("\n"):
            if line.startswith("#") or not line:
                continue
            Z, symbol, name = line.split()[:3]
            Z = int(Z)
            pdgid = 1000000000 + 10000*Z + 10*Z
            print >> sys.stderr, "Processing %s (PDG ID %i)" % (name, pdgid)
            glyph = TexGlyph(symbol, pdgid)
            cls.library[pdgid] = glyph

        ## Add PDG IDs from Pythia Library
        for pdgid in sorted(PythiaParticleDB.keys()):
            label = PythiaParticleDB.label(pdgid)
            print >> sys.stderr, "Processing %s (PDG ID %i)" % (label, pdgid)
            glyph = TexGlyph(PythiaParticleDB.latex(pdgid), pdgid)
            print >> sys.stderr, (" box: X %.1f to %.1f / Y %.1f to %.1f" % 
                                  (glyph.xmin, glyph.xmax, glyph.ymin, glyph.ymax))
            cls.library[pdgid] = glyph

        avg_height = cls.get_average_dimensions()[1]
        for glyph in cls.library.values():
            glyph.default_scale = 1.0 / avg_height
            glyph.dom.setAttribute("transform", "scale(%.6f)" % (glyph.default_scale))
            glyph.xmax /= avg_height
            glyph.ymax /= avg_height
            glyph.xmin /= avg_height
            glyph.ymin /= avg_height
            glyph.dom2xml()

    @classmethod
    def get(cls):
        if cls.library:
            return cls.library
        if resource_exists("mcviz.utils.svg.data", "texglyph.cache.bz2"):
            cls.library = loads(resource_string("mcviz.utils.svg.data", "texglyph.cache.bz2").decode("bz2"))
        elif resource_exists("mcviz.utils.svg.data", "texglyph.cache"):
            cls.library = loads(resource_string("mcviz.utils.svg.data", "texglyph.cache"))
        else:
            cls.make_library()
            with file(resource_filename("mcviz.utils.svg.data", "texglyph.cache"), "w") as f:
                f.write(dumps(cls.library, 2))
        return cls.library

    @classmethod
    def is_nucleus(cls, pdgid):
        if 1000000000 <= abs(pdgid) < 1100000000:
            ## Check if base nucleus is in database
            Z = (abs(pdgid)//10**4)%10**3
            return 1000000000 + 10000*Z + 10*Z in cls.get()

    @classmethod
    def interpret_nucleus(cls, pdgid):
        # scheme is +-10LZZZAAAI
        apdgid = abs(pdgid)
        if not cls.is_nucleus(pdgid): return None
        I = (apdgid//10**0)%10**1
        A = (apdgid//10**1)%10**3
        Z = (apdgid//10**4)%10**3
        L = (apdgid//10**7)%10**1
        sign = pdgid/apdgid
        # fake all-proton nucleus needs to stand in for the bare symbol
        base_pdgid = 1000000000 + 10000*Z + 10*Z
        return (sign, L, Z, A, I, base_pdgid)

    @classmethod
    def from_pdgid(cls, pdgid):

        if cls.is_nucleus(pdgid):
            sign, L, Z, A, I, base_pdgid = cls.interpret_nucleus(pdgid)
            glyph = CopiedTexGlyph(cls.get()[base_pdgid])
            glyph.xml = glyph.xml.replace('id="pdg%i"' % base_pdgid, 'id="pdg%i"' % pdgid)
        else:
            glyph = cls.get()[pdgid]

        if hasattr(glyph, "_with_bounding_box") and glyph._with_bounding_box:
            return glyph

        wx, wy = glyph.dimensions
        
        doc = minidom.parseString(glyph.xml)
        grp = doc.childNodes[0]
        box = doc.createElement("ellipse")
        
        box.setAttribute("cx", "%.3f" % (glyph.xmin + wx / 2))
        box.setAttribute("cy", "%.3f" % (glyph.ymin + wy / 2))
        box.setAttribute("rx", "%.3f" % (wx*1.2))
        box.setAttribute("ry", "%.3f" % (wy*1.2))
        box.setAttribute("fill", "red")
        box.setAttribute("opacity", "0")
        grp.appendChild(box)
        
        glyph._with_bounding_box = True
        glyph.dom = grp
        glyph.dom2xml()
        return glyph

    @classmethod
    def exists(cls, pdgid):
        if cls.is_nucleus(pdgid):
            return True
        return pdgid in cls.get()

    @classmethod
    def get_average_dimensions(cls):
        w_sum, h_sum = 0, 0
        dimensions = [glyph.dimensions for glyph in cls.get().values()]
        w = sum(d[0] for d in dimensions)/len(dimensions)
        h = sum(d[1] for d in dimensions)/len(dimensions)
        return w, h

class TexGlyph(Latex2SVG):
    def __init__(self, formula, pdgid):
        self.formula = formula
        self.pdgid = pdgid
        self.default_scale = 1
        self._with_bounding_box = False
        super(TexGlyph, self).__init__("pdg%i" % pdgid, formula)

class CopiedTexGlyph(TexGlyph):
    def __init__(self, tg):
        self.xml = tg.xml
        self.default_scale = tg.default_scale
        self.pdgid = tg.pdgid
        self.formula = tg.formula
        self.xmin = tg.xmin
        self.ymin = tg.ymin
        self.xmax = tg.xmax
        self.ymax = tg.ymax
        self._with_bounding_box = tg._with_bounding_box


if __name__ == '__main__':
    #print test_particle_data()
    #print test_particle_display()
    glyph_size = 1.0
    paperw, margin = 100, glyph_size
    lmargin = 5
    lineskip = 2*glyph_size
    curx, cury, maxy = lmargin, 5, 0

    from xml.dom.minidom import getDOMImplementation
    svgxml = getDOMImplementation().createDocument(None, "svg", None)

    PythiaParticleDB.init()

    with file("test.svg", "w") as f:
        f.write('<?xml version="1.0" standalone="no"?>\n')
        f.write('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox = "0 0 100 100" version = "1.1">\n')

        rerun = False

        if rerun: 
            keys = PythiaParticleDB.keys()[:10]
        else:
            keys = TexGlyphLibrary.get().keys()

        for pdgid in sorted(keys):
            if rerun:
                label = PythiaParticleDB.label(pdgid)
                print >> sys.stderr, "Processing ", label, " (PDG ID ", pdgid , ")..."
                glyph = TexGlyph(PythiaParticleDB.latex(pdgid), pdgid)
            else:
                glyph = TexGlyphLibrary.from_pdgid(pdgid)

            #glyph.write_tex_file('test.tex')
            wx, wy = glyph.dimensions
            maxy = max(wy, maxy)

            f.write('<g transform="translate(%.3f,%.3f) scale(%.4f)">\n' % ((curx - glyph.xmin)*glyph_size, cury*glyph_size, glyph_size))
            box = svgxml.createElement("rect")
            box.setAttribute("x", "%.3f" % (glyph.xmin))
            box.setAttribute("y", "%.3f" % (glyph.ymin))
            box.setAttribute("width", "%.3f" % wx)
            box.setAttribute("height", "%.3f" % wy)
            box.setAttribute("fill", "red")
            f.write(box.toprettyxml())
            if glyph.dom:
                f.write(glyph.dom.toprettyxml())
            else:
                f.write(glyph.xml)
            f.write("</g>\n")

            curx += wx*glyph_size + margin
            if curx > paperw:
                curx = lmargin
                cury += 2*maxy + lineskip
                maxy = 0
        f.write('</svg>')

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
