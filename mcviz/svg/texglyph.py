#!/usr/bin/env python
# -*- coding: cp1252 -*-
"""
eqtexsvg.py
functions for converting LaTeX equation string into SVG path
This extension need, to work properly:
    - a TeX/LaTeX distribution (MiKTeX ...)
    - pstoedit software: <http://www.pstoedit.net/pstoedit>

Copyright (C) 2006 Julien Vitard <julienvitard@gmail.com>
Heavily modified 2010 Johannes Ebke <ebke@cern.ch>

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

def fixup_unicodedata_name(x):
    "Oh dear. unicodedata misspelt lambda."
    if x == "lamda": return "lambda"
    return x

GREEK_RANGE = xrange(0x3b1, 0x3ca)
GREEK_LETTERS = (unichr(x) for x in GREEK_RANGE)
GREEK_NAME = lambda l: fixup_unicodedata_name(UD.name(l).split()[-1].lower())
GREEK_NAMECHARS = [(GREEK_NAME(l), l) for l in GREEK_LETTERS]
GREEK_UNAMECHARS = [(g.capitalize(), l.upper()) for g, l in GREEK_NAMECHARS]
GREEK_ALTERNATES = "(%s)" % "|".join("[%c%c]%s" % (g[0].upper(), g[0], g[1:])
                                     for g, c in GREEK_NAMECHARS)
GREEK_FINDER = re.compile(GREEK_ALTERNATES)
BAR_FINDER = re.compile(r"([^\s]+?)(?<!\\)bar(.*)")


#PARTICLES_GREEK = re.compile(r"(\~?)" + GREEK_ALTERNATES + r"(\*?)(_[A-Za-z]*|_[0-9]*)?(bar)?(\+\+|--|\+|-|0)?(\([0-9]*\))?([^\s]+?)")
#PARTICLES_GREEK = re.compile(r"(\~?)([A-Za-z]*)(\*)?(_[A-Za-z]*|_[0-9]*)?(bar)?(++|--|+|-|0)?(\([0-9]*\))?([^\s]+?)")

grp_susy = r"(?P<susy>\~)?"
grp_name = r"(?P<name>[A-Za-z8/]+?)"
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
re_groups = [grp_susy, grp_name, grp_star, grp_prime, grp_sub, grp_mass, grp_bar, grp_charge, grp_techni, grp_2s, grp_extra, grp_alt, grp_end]
PARTICLE_MATCH = re.compile(r"".join(re_groups))

glyph_library = None


def get_particle_db():
    particles = {}
    particle_data = minidom.parse("mcviz/svg/ParticleData.xml")
    for particle in particle_data.getElementsByTagName("particle"):
        name = particle.getAttribute("name")
        antiName = particle.getAttribute("antiName")
        pdgid = int(particle.getAttribute("id"))
        if name:
            particles[pdgid] = (pdgid, name, PARTICLE_MATCH.match(name).groupdict())
        if antiName:
            particles[-pdgid] = (-pdgid, antiName, PARTICLE_MATCH.match(antiName).groupdict())
    return particles

def test_particle_data():
    db = get_particle_db()
    keys = ['star', 'extra', 'sub', 'techni', 'susy', 'alt', 'prime', 'bar', 'name', 'state', 'charge', 'mass']
    s = []
    for key in keys:
        s.append("-"*80)
        s.append("    " + key)
        s.append("-"*80)
        for pdgid, label, gd in sorted(db.values()):
            if gd[key]:
                s.append("%20s | %s" % (label, gd[key]))
    return "\n".join(s)

def particle_to_latex(gd):
    rep = []
    rep.append(r"$\mathbf{")
    if gd["mass"]:
        rep.append(r"\underset{\mbox{\tiny (%s)}}{" % gd["mass"])
    if gd["bar"]:
        rep.append(r"\overline{")
    if gd["susy"]:
        rep.append(r"\tilde{")
    rep.append(gd["name"])
    if gd["susy"]:
        rep.append(r"}")
    if gd["bar"]:
        rep.append(r"}")

    if gd["sub"] or gd["techni"]:
        rep.append(r"_{")
        subs = []
        if gd["sub"]:
            subs.extend(gd["sub"].strip("_").split("_"))
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

    rep.append(r"}$")
    name = "".join(rep)
    name = GREEK_FINDER.sub(lambda g: "\\" + g.group(0) + " ", name)
    return name

def test_particle_display():
    res = []
    db = get_particle_db()
    for pdgid, label, gd in sorted(db.values()):
        res.append(particle_to_latex(gd))
    return "\\\\\n".join(res)

def make_glyph_library():
    print >> sys.stderr, "Creating glyph library..."
    res = {}
    db = get_particle_db()
    for pdgid, label, gd in sorted(db.values()):
        print >> sys.stderr, "Processing ", label, " (PDG ID ", pdgid , ")..."
        res[pdgid] = TexGlyph(particle_to_latex(gd), "pdg%i"%pdgid).get_def()
    return res

def get_glyph_library():
    global glyph_library
    if not glyph_library:
        try:
            glyph_library = loads(file("mcviz/svg/texglyph.cache.bz2").read().decode("bz2"))
        except IOError:
            glyph_library = make_glyph_library()
            with file("mcviz/svg/texglyph.cache.bz2", "w") as f:
                f.write(dumps(glyph_library).encode("bz2"))
    return glyph_library

def get_glyph_dom(pdgid):
    return get_glyph_library()[pdgid]

def get_glyph_xml(pdgid):
    return get_glyph_library()[pdgid].toprettyxml()

def glyph_ids():
    return get_glyph_library().keys()

class TexGlyph(object):
    def __init__(self, formula, name):
        self.formula = formula
        self.name = name

    def get_svg(self):
        base_dir = tempfile.mkdtemp("", "glyphsvg-");
        latex_file = os.path.join(base_dir, "eq.tex")
        aux_file = os.path.join(base_dir, "eq.aux")
        log_file = os.path.join(base_dir, "eq.log")
        ps_file = os.path.join(base_dir, "eq.ps")
        dvi_file = os.path.join(base_dir, "eq.dvi")
        svg_file = os.path.join(base_dir, "eq.svg")
        out_file = os.path.join(base_dir, "eq.out")
        err_file = os.path.join(base_dir, "eq.err")

        def clean():
            rmtree(base_dir)

        self.create_equation_tex(latex_file)
        os.system('latex "-output-directory=%s" -halt-on-error "%s" > "%s"' \
                  % (base_dir, latex_file, out_file))
                  
        try:
            os.stat(dvi_file)
        except OSError:
            print >>sys.stderr, "invalid LaTeX input:"
            print >>sys.stderr, self.formula
            print >>sys.stderr, "temporary files were left in:", base_dir
            raise

        os.system('dvips -q -f -E -D 600 -y 5000 -o "%s" "%s"' % (ps_file, dvi_file))

        # cd to base_dir is necessary, because pstoedit writes
        # temporary files to cwd and needs write permissions
        separator = ';'
        if os.name == 'nt':
            separator = '&&'
        os.system('cd "%s" %s pstoedit -f plot-svg -dt -ssp "%s" "%s" > "%s" 2> "%s"' \
                  % (base_dir, separator, ps_file, svg_file, out_file, err_file))

        # forward errors to stderr but skip pstoedit header
        if os.path.exists(err_file):
            err_stream = open(err_file, 'r')
            for line in err_stream:
                if not line.startswith('pstoedit: version'):
                    sys.stderr.write(line + '\n')
            err_stream.close()
 
        res = self.svg_open(svg_file)

        clean()

        return res

    def get_def(self):
        dom = self.get_svg()
        return dom.childNodes[0]

    def create_equation_tex(self, filename):
        with open(filename, "w") as fd:
            fd.write(dedent(r"""
                %% processed with eqtexsvg.py
                \documentclass{article}
                \usepackage{amsmath}
                \usepackage{amssymb}
                \usepackage{amsfonts}

                \thispagestyle{empty}
                \begin{document}
                \begin{center}
                %s
                \end{center}
                \end{document}
            """ % self.formula).strip())

    def svg_open(self, filename):
        doc_sizeH = 100
        doc_sizeW = 100

        def clone_and_rewrite(self, node_in):
            in_tag = node_in.nodeName
            if in_tag != 'svg':
                node_out = minidom.Element(in_tag)
                for name, value in node_in.attributes.items():
                    node_out.setAttribute(name, value)
                    
            else:
                node_out = minidom.Element("svg")
                node_out.setAttribute("viewBox","0 0 %s %s" % (doc_sizeH, doc_sizeW))
                node_out.setAttribute("xmlns", "http://www.w3.org/2000/svg")
                node_out.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink")
                node_out.setAttribute("version", "1.1")

            for c in node_in.childNodes:
                c_tag = c.nodeName
                if c_tag not in ('g', 'path', 'polyline', 'polygon'):
                    continue
                    
                child = clone_and_rewrite(self, c)
                if c_tag == 'g':
                    matrix = 'matrix(%s,0,0,%s,%s,%s)' % ( doc_sizeH/700., -doc_sizeH/700., 
                                                          -doc_sizeH*0.25,  doc_sizeW*0.75)
                    child.setAttribute('transform', matrix)
                    child.setAttribute('id', self.name)
                    
                node_out.appendChild(child)
                
            return node_out

        doc = minidom.parse(filename)
        svg = [cn for cn in doc.childNodes if cn.childNodes][0]
        group = clone_and_rewrite(self, svg)
        return group

if __name__ == '__main__':
    #e = TexGlyph(r"$\bar{K}^{++}$", "barKpp")
    #print e.get_svg().toprettyxml()
    #print e.get_def().toprettyxml()
    #print test_particle_data()
    #formula = test_particle_display()
    #e = TexGlyph(formula, "test")
    #e.create_equation_tex('test.tex')
    #e.get_svg().toprettyxml()
    #lib = get_glyph_library()
    for pdgid in sorted(glyph_ids()):
        with file("pdg%i.svg"%pdgid, "w") as f:
            f.write('<?xml version="1.0" standalone="no"?>\n')
            f.write('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox = "0 0 100 100" version = "1.1">\n')
            f.write(' <defs>\n')
            f.write(get_glyph_xml(pdgid))
            f.write(' </defs>\n')
            f.write('<use x = "0" y = "0" xlink:href = "#pdg%s" />\n' % pdgid)
            baseline = 20
            midpoint = 42.5
            f.write('<circle cx = "%.3f" cy = "%.3f" r = "1" fill = "red" stroke ="none" />\n' % (midpoint, baseline))
            f.write('<path d="M 0 %s H 100" fill = "none" stroke ="red" />\n' % baseline)
            f.write('</svg>')

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 encoding=utf-8 textwidth=99
