from __future__ import division

from spline import Spline

default_amp = 8

def set_width(width):
    global max_amp
    max_amp = width

# Functions to get photon splines

def get_photon_splines(length, amplitude, n_waves, power, amp):
    N = n_waves * 2
    wavelength = length / N
    cntrl_strength = wavelength / 2
    
    # scaling envelope 
    if power:
        envelope = [1 - abs(2*i/(N-1) - 1)**power for i in range(N)]
    else:
        envelope = [1 for i in range(N)]

    # x offsets of points:
    px = [0.0] + [wavelength * (0.5 + i) for i in range(N)]
    px.append(px[-1] + wavelength / 2)

    # y offsets of points:
    py = [0.0] + [amplitude * envelope[i] for i in range(N)] + [0.0]
    
    splines = []
    sgn = 1
    for i in range(1, N+2):
        op  = px[i-1], -sgn * px[i-1]
        cp1 = px[i-1] + cntrl_strength, -sgn * py[i-1]
        cp2 = px[i] - cntrl_strength, sgn * py[i]
        dp  = px[i], sgn * py[i]
        if i == 1:
            cp1 = op
        elif i == N+1:
            cp2 = dp
        splines.append(Spline(op, cp1, cp2, dp))
        sgn = -sgn
    return splines

def get_gluon_splines(length, amplitude, n_waves, amp): 
    loopyness = 0.7
    init_length = 2

    N = n_waves * 2 + 1
    wavelength = length / (N - 1 + 2*init_length)
    cntrl_strength = wavelength * loopyness
    
    # x offsets of points:
    px = [0.0] + [wavelength * (init_length + i) for i in range(N)]
    px.append(px[-1] + init_length * wavelength)

    # y offsets of points:
    py = [0.0] + [amplitude for i in range(N)] + [0.0]
    
    splines = []
    sgn = 1
    for i in range(1, N+2):
        op  = px[i-1], -sgn * px[i-1]
        cp1 = px[i-1] - sgn * (2 - sgn) * cntrl_strength, -sgn * py[i-1]
        cp2 = px[i] - sgn * (2 + sgn) * cntrl_strength, sgn * py[i]
        dp  = px[i], sgn * py[i]
        if i == 1:
            cp1 = op
        elif i == N+1:
            cp2 = dp
        splines.append(Spline(op, cp1, cp2, dp))
        sgn = -sgn
    return splines
    
def pathdata_from_splines(splines, trafo_spline = None):
    if trafo_spline:
        splines = [trafo_spline.transform_spline(s) for s in splines]
    data = ["M %.5f %.5f\n" % splines[0].points[0]]
    for s in splines:
        data.append('C %.5f %.5f %.5f %.5f %.5f %.5f\n' % (s.points[1] + s.points[2] + s.points[3]))
    return "".join(data)


# Functions to get SVN path data for objects
# contain some policy

def photon_data(energy, spline, n_max = 10, n_min = 3,
                power = 10, amp = default_amp):
    """Get the SVG path data for a photon. 
    energy must be between 0 and 1"""
    length = spline.length
    # Here are parametrizations:
    energy = min(1, max(0,energy))
    amplitude = (0.5 + 0.5*energy) * amp
    n_per_50 = n_min + energy * (n_max - n_min)
    n = max(2, int(n_per_50 * length / 50))
    splines = get_photon_splines(length, amplitude, n, power, amp)
    return pathdata_from_splines(splines, trafo_spline = spline)

def gluon_data(energy, spline, n_max = 11, n_min = 1, 
               amp = default_amp):
    """Get the SVG path data for a gluon.
    energy must be between 0 and 1"""
    length = spline.length
    # Here are parametrizations:
    energy = min(1, max(0,energy))
    amplitude = (1 - 0.3*energy) * amp
    n_per_50 = n_min + energy * (n_max - n_min)
    n = max(1, int(n_per_50 * length / 50))
    splines = get_gluon_splines(length, amplitude, n, amp)
    return pathdata_from_splines(splines, trafo_spline = spline)

def boson_data(energy, spline, n_max = 2, n_min = 2):
    """Get the SVG path data for a boson.
    energy must be between 0 and 1
    either length or spline must be given."""
    a = default_amp / 3
    return photon_data(energy, spline, n_max, n_min, power = None, amp = a)

def fermion_arrow_data(size, spline):
    """Returns the path data for an arrow in the middle of the given spline"""
    mid = spline.length/2
    width = size*0.3
    tip = spline.transform_x_point(mid, (mid + size*0.5, 0))
    tail1 = spline.transform_x_point(mid, (mid - size*0.5, width))
    tail2 = spline.transform_x_point(mid, (mid - size*0.5, - width))
    control1 = spline.transform_x_point(mid, (mid - size*0.4, width*0.5))
    control2 = spline.transform_x_point(mid, (mid - size*0.4, - width*0.5))
    data = ["M %.5f %.5f" % tip]
    data.append("L %.5f %.5f" % tail1)
    data.append("C %.5f %.5f %.5f %.5f %.5f %.5f" % (control1 + control2 + tail2))
    data.append("Z")
    return "".join(data)

def svg_group(content, kwds):
    kwdstr = " ".join('%s="%s"' % (k,v) for k,v in kwds.iteritems())
    return "<g %s>\n%s\n </g>\n" % (kwdstr, content)

# Get SVG fragments
def photon(energy, spline, **kwds):
    """Get an SVG fragment for a photon along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    path = '<path d="%s" />\n' % (photon_data(energy, spline))
    return svg_group(path, kwds)

def gluon(energy, spline, **kwds):
    """Get an SVG fragment for a photon along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    path = '<path d="%s" />\n' % (gluon_data(energy, spline))
    return svg_group(path, kwds)

def boson(energy, spline, **kwds):
    """Get an SVG fragment for a photon along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    path = '<path d="%s" />\n' % (boson_data(energy, spline))
    return svg_group(path, kwds)

def fermion(energy, spline, **kwds):
    path = '<path d="%s" fill="none"/>\n' % spline.svg_path_data
    arrowsize = 2 + 10*energy
    arrowdata = fermion_arrow_data(arrowsize, spline)
    arrow = '<path d="%s" stroke="none"/>\n' % arrowdata
    return svg_group("".join((path,arrow)), kwds)

if __name__=="__main__":
    from spline import Spline, SplineLine, Line
    
    spline1 = Spline((5.0, -10), (20.000, -10), (15.0, 30.000), (40.0, 10.000))
    spline2 = Spline((40, 10), (65, -10), (60, 30), (80, 20))
    spline = SplineLine((spline1, spline2))
    line = Line((0,0),(spline.length,0))

    s = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1000 1000">\n']

    s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (10, 10, spline.svg_path_data))

    n = 10
    for i in range(n+1):
        x = 10
        y = 40 + i*25
        e = i/n
        s.append(photon(e, line, transform="translate(%i,%i)" % (x, y), fill="none", stroke="blue"))    
        s.append(photon(e, spline, transform="translate(%i,%i)" % (x+100, y), fill="none", stroke="blue"))
        s.append(gluon(e, line, transform="translate(%i,%i)" % (x+200, y), fill="none", stroke="blue"))    
        s.append(gluon(e, spline, transform="translate(%i,%i)" % (x+300, y), fill="none", stroke="blue"))
        s.append(boson(e, line, transform="translate(%i,%i)" % (x+400, y), fill="none", stroke="blue"))    
        s.append(boson(e, spline, transform="translate(%i,%i)" % (x+500, y), fill="none", stroke="blue"))
        s.append(fermion(e, line, transform="translate(%i,%i)" % (x+600, y), fill="blue", stroke="blue"))    
        s.append(fermion(e, spline, transform="translate(%i,%i)" % (x+700, y), fill="blue", stroke="blue"))

    for i in range(n+1):
        x = 10
        y = 400 + i*25
        e = 0.6
        l = Line((0,0),((i + 0.5) / n * 180, 10))
        s.append(photon(e, l, transform="translate(%i,%i)" % (x, y), fill="none", stroke="blue"))
        s.append(gluon(e, l, transform="translate(%i,%i)" % (x+250, y), fill="none", stroke="blue"))
        s.append(boson(e, l, transform="translate(%i,%i)" % (x+500, y), fill="none", stroke="blue"))
        s.append(fermion(e, l, transform="translate(%i,%i)" % (x+750, y), fill="blue", stroke="blue"))

    #s.append('<path transform="translate(10,10)" fill="none" stroke="red" id="u" d="%s" />\n' % (gluon(0.5, 200)))

    s.append('" />\n')
    s.append('</svg>\n')

    f = file("feynman_shapes.svg","w")
    f.write("".join(s))
    f.close()

    print "Written feynman_shapes.svg."
