import re
import unicodedata as UD

GREEK_RANGE = xrange(0x3b1, 0x3ca)
GREEK_LETTERS = [UD.name(unichr(x)).split()[-1].lower() for x in GREEK_RANGE]
GREEK_ALTERNATES = "(%s)" % "|".join("[%c%c]%s" % (g[0].upper(), g[0], g[1:])
                                     for g in GREEK_LETTERS)

GREEK_FINDER = re.compile(GREEK_ALTERNATES)
BAR_FINDER = re.compile(r"([^\s]+?)(?<!\\)bar(.*)")

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
        name = GREEK_FINDER.sub(lambda g: "{\\" + g.group(0) + "}", name)
    
    name = BAR_FINDER.sub(lambda g: "\\bar{%s}%s" % g.groups(), name)
    
    if name != start_name:
        # Keep going until we didn't make any changes
        return latexize_particle_name(name, n+1)
    
    return name
    
def test():
    print latexize_particle_name(r"I am the alpha0 and the Zeta etabar")

if __name__ == "__main__":
    test()
