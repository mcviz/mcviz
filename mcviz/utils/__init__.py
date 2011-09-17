# -*- coding: UTF-8 -*-
from .. import log; log = log.getChild(__name__)

import re
import unicodedata as UD
import sys

from cStringIO import StringIO
from contextlib import contextmanager

from .orderedset import OrderedSet
from .point import Point2D
from .colors import rainbow_color
from .spline import Spline, SplineLine, Line
from .units import Units

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

SUPER_ZERO = u"⁰"
SUPER_PLUS = u"⁺"
SUPER_MINUS = u"⁻"
BAR = u"̅"

def latexize_particle_name(name, n=0):
    r"""
    pi+ => pi^+
    pi0 => pi^0
    Kbar0 => \bar{K}^0
    K_L0 => K_L0
    greekletter0 => {\greekletter}0
    """
    start_name = name
    
    if not n:
        # only do this on the first pass
        name = GREEK_FINDER.sub(lambda g: "\\\\" + g.group(0), name)
        replacements = [
            ("0", "^0"),
            ("+", "^+"),
            ("-", "^-"),
            ("^-^-", "^{--}"),
            ("^+^+", "^{++}"),
            ("_^", "_")]
        for what, replacement in replacements:
            name = name.replace(what, replacement)
    
    name = BAR_FINDER.sub(lambda g: "\\\\bar{%s}%s" % g.groups(), name)
    
    if name != start_name:
        # Keep going until we didn't make any changes
        return latexize_particle_name(name, n+1)
    
    return "$\\\\mathbf{" + name + "}$"

def make_unicode_name(name):
    replacements = [
        ("0", SUPER_ZERO),
        ("+", SUPER_PLUS),
        ("-", SUPER_MINUS),
        ("bar", BAR),
    ] + GREEK_NAMECHARS + GREEK_UNAMECHARS
    
    for what, replacement in replacements:
        name = name.replace(what, replacement)
        
    return name.encode("UTF-8")

@contextmanager
def replace_stdout(what=None):
    old_stdout = sys.stdout
    sys.stdout = what if what else StringIO()
    try:
        yield sys.stdout
    finally:
        sys.stdout = old_stdout

def test():
    print latexize_particle_name(r"I am the alpha0 and the Zeta etabar")

if __name__ == "__main__":
    test()
