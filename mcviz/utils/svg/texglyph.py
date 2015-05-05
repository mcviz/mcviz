"""
texglyph.py
functions for converting LaTeX equation string into SVG path
This extension need, to work properly:
    - a TeX/LaTeX distribution (MiKTeX ...)
    - pstoedit software: <http://www.pstoedit.net/pstoedit>

Parts of this file Copyright (C) 2006 Julien Vitard <julienvitard@gmail.com>
Copyright (C) 2011 Johannes Ebke <ebke@cern.ch>; Peter Waller

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""

import os
import tempfile
import re
import unicodedata as UD
import sys
from xml.dom import minidom
from shutil import rmtree
from textwrap import dedent
from cPickle import dumps, loads
from pkg_resources import resource_string, resource_exists, resource_filename

def fixup_unicodedata_name(x):
    "Oh dear. unicodedata misspelt lambda."
    if x == "lamda": return "lambda"
    return x

GREEK_RANGE = xrange(0x3b1, 0x3ca)
GREEK_LETTERS = (unichr(x) for x in GREEK_RANGE)
GREEK_NAME = lambda l: fixup_unicodedata_name(UD.name(l).split()[-1].lower())
GREEK_NAMECHARS = [(GREEK_NAME(l), l) for l in GREEK_LETTERS]
GREEK_ALTERNATES = "(%s)" % "|".join("[%c%c]%s" % (g[0].upper(), g[0], g[1:])
                                     for g, c in GREEK_NAMECHARS)
GREEK_FINDER = re.compile(GREEK_ALTERNATES)

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

def read_pythia_particle_db():
    particles = {}
    try:
        xml_data = resource_string("mcviz.utils.svg.data", "ParticleData.xml")
    except ImportError:
        xml_data = "".join(file("ParticleData.xml").readlines())
    particle_data = minidom.parseString(xml_data)
    for particle in particle_data.getElementsByTagName("particle"):
        name = particle.getAttribute("name")
        antiName = particle.getAttribute("antiName")
        pdgid = int(particle.getAttribute("id"))
        if name:
            groupdict = PARTICLE_MATCH.match(name).groupdict()
            particles[pdgid] = (pdgid, name, groupdict)
        if antiName:
            groupdict = PARTICLE_MATCH.match(antiName).groupdict()
            particles[-pdgid] = (-pdgid, antiName, groupdict)
    return particles

def test_particle_data():
    db = read_pythia_particle_db()
    keys = ['star', 'extra', 'sub', 'techni', 'hv', 'susy', 'alt', 'prime', 'bar', 'name', 'state', 'charge', 'mass']
    s = []
    for key in keys:
        s.append("-"*80)
        s.append("    " + key)
        s.append("-"*80)
        for pdgid, label, gd in sorted(db.values()):
            if gd[key]:
                s.append("%20s | %s" % (label, gd[key]))
    return "\n".join(s)

def particle_to_latex(gd, bastardize=False):
    """
    Generate latex from particle
    
    `bastardize`: Generate ROOT latex from particle
    """
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
    name = GREEK_FINDER.sub(lambda g: greek_prefix + g.group(0), name)
    return name

def test_particle_display():
    res = []
    db = read_pythia_particle_db()
    for pdgid, label, gd in sorted(db.values()):
        res.append(particle_to_latex(gd))
    return "\\\\\n".join(res)

def process_path_data(d, tf_x, tf_y):
    x_positions = []
    y_positions = []


    # treat Polygon data here
    if d[0] != "M":
        new_points = []
        for pt in d.split():
            x, y = map(float, pt.split(","))
            x = tf_x(x)
            y = tf_y(y)
            x_positions.append(x)
            y_positions.append(y)
            new_points.append("%.2f,%.2f" % (x, y))
        return (" ".join(new_points), min(x_positions), max(x_positions), 
                                      min(y_positions), max(y_positions))

    # split and preprocess command strings
    cmds = []
    for cmdstr in d.strip().split(" "):
        if cmdstr[0] == "Z":
            numbers = []
        else:
            numbers = map(float, cmdstr[1:].split(","))
        cmds.append((cmdstr[0], numbers))

    # Trace the pen and relativize svg
    x0, y0 = cmds[0][1][0], cmds[0][1][1]
    x0, y0 = tf_x(x0), tf_y(y0)
    x_positions.append(x0)
    y_positions.append(y0)

    out = ["M%.2f,%.2f" % (x0, y0)]
    for cmd, numbers in cmds[1:]:
        if cmd == "H":
            numbers[0] = tf_x(numbers[0])
            x_positions.append(numbers[0])
            numbers[0] -= x0
            x0 += numbers[0]
        elif cmd == "V":
            numbers[0] = tf_y(numbers[0])
            y_positions.append(numbers[0])
            numbers[0] -= y0
            y0 += numbers[0]
        else:
            for i in range(len(numbers)/2):
                numbers[2*i] = tf_x(numbers[2*i]) - x0
                numbers[2*i+1] = tf_y(numbers[2*i + 1]) - y0
            if numbers:
                x_positions.append(numbers[-2] + x0)
                y_positions.append(numbers[-1] + y0)
                x0 += numbers[-2]
                y0 += numbers[-1]
        nstr = (",".join(["%.2f"]*len(numbers))) % tuple(numbers)
        out.append("%s%s" % (cmd.lower(),nstr))
    return " ".join(out), min(x_positions), max(x_positions), min(y_positions), max(y_positions)

class TexGlyph(object):
    library = None

    @classmethod
    def make_library(cls):
        print >> sys.stderr, "Creating TexGlyph library..."
        cls.library = {}
        db = read_pythia_particle_db()
        for pdgid, label, gd in sorted(db.values()):
            print >> sys.stderr, "Processing %s (PDG ID %i)" % (label, pdgid)
            glyph = TexGlyph(particle_to_latex(gd), pdgid)
            print >> sys.stderr, (" box: X %.1f to %.1f / Y %.1f to %.1f" % 
                                  (glyph.xmin, glyph.xmax, glyph.ymin, glyph.ymax))
            cls.library[pdgid] = glyph
        avg_height = cls.get_average_dimensions()[1]
        for glyph in cls.library.values():
            glyph.default_scale = 1.0 / avg_height
            glyph.dom.setAttribute("transform", "scale(%.6f)" % (glyph.default_scale))
            glyph.dom2xml()

    @classmethod
    def get_library(cls):
        if cls.library:
            return cls.library
        
        if resource_exists("mcviz.utils.svg.data", "texglyph.cache.bz2"):
            cls.library = loads(resource_string("mcviz.utils.svg.data", "texglyph.cache.bz2").decode("bz2"))
        elif resource_exists("mcviz.utils.svg.data", "texglyph.cache"):
            cls.library = loads(resource_string("mcviz.utils.svg.data", "texglyph.cache"))
        else:
            cls.make_library()
            with file(resource_filename("mcviz.utils.svg", "texglyph.cache"), "w") as f:
                f.write(dumps(cls.library, 2))
                
        return cls.library

    @classmethod
    def from_pdgid(cls, pdgid):
        glyph = cls.get_library()[pdgid]
        if hasattr(glyph, "_with_bounding_box") and glyph._with_bounding_box:
            return glyph

        wx, wy = glyph.dimensions
        
        doc = minidom.parseString(glyph.xml)
        grp = doc.childNodes[0]
        box = doc.createElement("g")
        
        grp.appendChild(box)
        
        glyph._with_bounding_box = True
        glyph.dom = grp
        glyph.dom2xml()
        return glyph

    @classmethod
    def exists(cls, pdgid):
        return pdgid in cls.get_library()

    @classmethod
    def pdgids(cls):
        cls.get_library().keys()

    def __init__(self, formula, pdgid):
        self.formula = formula
        self.pdgid = pdgid
        self.xmin, self.xmax = None, None
        self.ymin, self.ymax = None, None
        self.dom = None
        self.default_scale = 1
        self._with_bounding_box = False
        self.build_svg()

    def build_svg(self, use_pdf = True):
        base_dir = tempfile.mkdtemp("", "texglyph-");
        latex_file = os.path.join(base_dir, "eq.tex")
        aux_file = os.path.join(base_dir, "eq.aux")
        log_file = os.path.join(base_dir, "eq.log")
        if use_pdf:
            texout_file = os.path.join(base_dir, "eq.pdf")
            ps_file = os.path.join(base_dir, "eq.ps")
            pdf_file = texout_file
        else:
            texout_file = os.path.join(base_dir, "eq.dvi")
            ps_file = os.path.join(base_dir, "eq.ps")
        svg_file = os.path.join(base_dir, "eq.svg")
        out_file = os.path.join(base_dir, "eq.out")
        err_file = os.path.join(base_dir, "eq.err")

        def clean():
            rmtree(base_dir)

        self.write_tex_file(latex_file)
        os.system('%slatex "-output-directory=%s" -halt-on-error "%s" > "%s"'
                  % ("pdf" if use_pdf else "", base_dir, latex_file, out_file))
                  
        try:
            os.stat(texout_file)
        except OSError:
            print >>sys.stderr, "invalid LaTeX input:"
            print >>sys.stderr, self.formula
            print >>sys.stderr, "temporary files were left in:", base_dir
            raise

        if not use_pdf:
            os.system('dvips -q -f -E -D 600 -y 5000 -o "%s" "%s"' % (ps_file, texout_file))
        else:
            os.system('pdftops "%s" "%s"' % (pdf_file, ps_file))

        # cd to base_dir is necessary, because pstoedit writes
        # temporary files to cwd and needs write permissions
        separator = ';'
        if os.name == 'nt':
            separator = '&&'
        os.system('cd "%s" %s pstoedit -f plot-svg -dt -ssp "%s" "%s" > "%s" 2> "%s"'
                  % (base_dir, separator, ps_file, svg_file, out_file, err_file))

        # forward errors to stderr but skip pstoedit header
        if os.path.exists(err_file):
            err_stream = open(err_file, 'r')
            for line in err_stream:
                if not line.startswith('pstoedit: version'):
                    sys.stderr.write(line + '\n')
            err_stream.close()
 
        self.process_svg_file(svg_file)

        clean()

    def write_tex_file(self, filename):
        with open(filename, "w") as fd:
            fd.write(dedent(r"""
                %% processed with eqtexsvg.py
                \documentclass{article}
                \usepackage{amsmath}
                \usepackage{amssymb}
                \usepackage{amsfonts}

                \thispagestyle{empty}
                \begin{document}
                \begin{center}%s\end{center}
                \end{document}
            """ % self.formula).strip())

    def process_svg_file(self, filename):
        # scale set to 10 to avoid resolution effects with %.2f
        scale = 10
        # constants derived from experience
        shift_x = -305.22
        shift_y = 709.75

        def tf_x(x):
            return (  x + shift_x) * scale
        def tf_y(y):
            # This minus sign is here on purpose, the input svg is flipped
            return (- y + shift_y) * scale

        def report_x(x):
            if self.xmin is None:
                self.xmin = x
            if self.xmax is None:
                self.xmax = x
            self.xmin, self.xmax = min(x, self.xmin), max(x, self.xmax)

        def report_y(y):
            if self.ymin is None:
                self.ymin = y
            if self.ymax is None:
                self.ymax = y
            self.ymin, self.ymax = min(y, self.ymin), max(y, self.ymax)

        def clone_and_rewrite(self, node_in):
            in_tag = node_in.nodeName
            if in_tag != 'svg':
                node_out = minidom.Element(in_tag)
                for name, value in node_in.attributes.items():
                    node_out.setAttribute(name, value)
            else:
                node_out = minidom.Element("svg")

            for c in node_in.childNodes:
                if c.nodeName not in ('g', 'path', 'polyline', 'polygon', 'line'):
                    continue
                    
                child = clone_and_rewrite(self, c)
                
                if c.nodeName == 'g':
                    child.removeAttribute("transform")
                    child.setAttribute('id', "pdg%i" % self.pdgid)
                elif c.nodeName == 'path' or c.nodeName == 'polygon':
                    if c.nodeName == 'path':
                        data_attr = "d"
                    else:
                        data_attr = "points"
                    data = c.getAttribute(data_attr)
                    d, x0, x1, y0, y1 = process_path_data(data, tf_x, tf_y)
                    child.setAttribute(data_attr, d)
                    report_x(x0)
                    report_x(x1)
                    report_y(y0)
                    report_y(y1)
                elif c.nodeName == 'line':
                    width = float(child.getAttribute("stroke-width")) * scale
                    for attr in ("x1", "x2"):
                        x = tf_x(float(child.getAttribute(attr)))
                        report_x(x)
                        child.setAttribute(attr, "%.2f" % x)
                    for attr in ("y1", "y2"):
                        y = tf_y(float(child.getAttribute(attr)))
                        report_y(y)
                        child.setAttribute(attr, "%.2f" % y)
                    child.setAttribute("stroke-width", "%.2f" % width)

                node_out.appendChild(child)
                
            return node_out

        doc = minidom.parse(filename)
        svg = [cn for cn in doc.childNodes if cn.childNodes][0]
        self.dom = clone_and_rewrite(self, svg).childNodes[0]
    
    @property
    def dimensions(self):
        """Returns width and height of glyph"""
        xwidth = self.xmax - self.xmin
        ywidth = self.ymax - self.ymin
        return xwidth, ywidth

    def dom2xml(self):
        self.xml = self.dom.toxml()
        self.dom = None

    @classmethod
    def get_average_dimensions(cls):
        w_sum, h_sum = 0, 0
        dimensions = [glyph.dimensions for glyph in cls.get_library().values()]
        w = sum(d[0] for d in dimensions)/len(dimensions)
        h = sum(d[1] for d in dimensions)/len(dimensions)
        return w, h

if __name__ == '__main__':
    #print test_particle_data()
    #print test_particle_display()

    if True:
        db = read_pythia_particle_db()
        scale = 0.001
        paperw, margin = 10/scale, 100
        lmargin = 200
        lineskip = 200
        curx, cury, maxy = lmargin, 200, 0
        
        with file("test.svg", "w") as f:
            f.write('<?xml version="1.0" standalone="no"?>\n')
            f.write('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox = "0 0 100 100" version = "1.1">\n')

            for pdgid, label, gd in sorted(db.values()):
                print >> sys.stderr, "Processing ", label, " (PDG ID ", pdgid , ")..."
                glyph = TexGlyph(particle_to_latex(gd), pdgid)
                #glyph.write_tex_file('test.tex')
                wx, wy = glyph.dimensions
                maxy = max(wy, maxy)


                f.write('<g transform="translate(%.3f,%.3f) scale(%.4f)">\n' % ((curx - glyph.xmin)*scale, cury*scale, scale))
                from xml.dom.minidom import getDOMImplementation
                svgxml = getDOMImplementation().createDocument(None, "svg", None)
                box = svgxml.createElement("rect")
                box.setAttribute("x", "%.3f" % (glyph.xmin))
                box.setAttribute("y", "%.3f" % (glyph.ymin))
                box.setAttribute("width", "%.3f" % wx)
                box.setAttribute("height", "%.3f" % wy)
                box.setAttribute("fill", "red")
                f.write(box.toprettyxml())
                f.write(glyph.dom.toprettyxml())
                f.write("</g>\n")

                curx += wx + margin
                if curx > paperw:
                    curx = lmargin
                    cury += 2*maxy + lineskip
                    maxy = 0

            f.write('</svg>')

    else:
        for pdgid in sorted(TexGlyph.pdgids()):
            with file("pdg%i.svg"%pdgid, "w") as f:
                f.write('<?xml version="1.0" standalone="no"?>\n')
                f.write('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox = "0 0 100 100" version = "1.1">\n')
                f.write(' <defs>\n')
                f.write(TexGlyph.from_pdgid(pdgid).dom.toxml())
                f.write(' </defs>\n')
                f.write('<use x = "50" y = "50" xlink:href = "#pdg%s" />\n' % pdgid)
                baseline = 50
                midpoint = 50
                f.write('<circle cx = "%.3f" cy = "%.3f" r = "1" fill = "red" stroke ="none" />\n' % (midpoint, baseline))
                f.write('<path d="M 0 %s H 100" fill = "none" stroke ="red" />\n' % baseline)
                f.write('</svg>')

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
