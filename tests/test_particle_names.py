import os

from mcviz.utils.svg import texglyph

def test_particle_names():

    res = texglyph.test_particle_data() + "\n"
    f = file("tests/particles.testing","w")
    f.write(res)
    f.close()
    os.system("diff tests/particles.reference tests/particles.testing > tests/particles.diff")
    diff = file("tests/particles.diff").readlines()
    if "".join(diff).strip():
        print "DIFF:"
        for l in diff:
            print l.strip()
        raise Exception("DIFF")
    os.remove("tests/particles.testing")
    os.remove("tests/particles.diff")


