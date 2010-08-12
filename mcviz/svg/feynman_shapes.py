from __future__ import division

from xml.dom.minidom import getDOMImplementation
svgxml = getDOMImplementation().createDocument(None, "svg", None)

from spline import Spline

def get_photon_splines(length, amplitude, n_waves, power, amp):
    N = n_waves * 2
    wavelength = length / N
    cntrl_strength = wavelength / 2 # TUNING PARAMETER
    
    # scaling envelope 
    if power:
        # TUNING PARAMETER
        #envelope = [1 - abs(2*i/(N - 1) - 1)**power for i in range(N)]
        envelope = [1 - abs(2*i/(2*N - 1) - 1)**power for i in range(N)]
    else:
        envelope = [1 for i in range(N)]

    # x offsets of points:
    px = [0.0] + [wavelength * (0.5 + i) for i in range(N)]
    px.append(px[-1] + wavelength / 2)

    # y offsets of points:
    py = [0.0] + [amplitude * envelope[i] for i in range(N)] + [0.0]
    
    splines = []
    sgn = 1
    for i in range(1, N+1): # STYLE HALF OPEN PHOTONS: Was N+2
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
    loopyness = 0.75 # TUNING PARAMETER
    init_length = 2 # TUNING PARAMETER

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
    data = ["M%.2f %.2f" % splines[0].points[0]]
    for s in splines:
        pts = (s.points[1] + s.points[2] + s.points[3])
        data.append('C%.2f %.2f %.2f %.2f %.2f %.2f' % pts)
    return "".join(data)

# Functions to get SVN path data for objects
# contain some policy

# TUNING DEFAULTS
def photon_data(energy, spline, n_max = 10, n_min = 3, power = 5, amp = 1):
    """Get the SVG path data for a photon. 
    energy must be between 0 and 1"""
    length = spline.length
    # Here are parametrizations:
    energy = min(1, max(0,energy))
    amplitude = (0.5 + 0.5*energy) * amp # TUNING FUNCTION
    n_per_10 = (n_min + energy * (n_max - n_min)) / amp
    n = max(2, int(n_per_10 * length / 10))
    splines = get_photon_splines(length, amplitude, n, power, amp)
    return pathdata_from_splines(splines, trafo_spline = spline)

# TUNING DEFAULTS
def gluon_data(energy, spline, n_max = 11, n_min = 1, amp = 1):
    """Get the SVG path data for a gluon.
    energy must be between 0 and 1"""
    length = spline.length
    # Here are parametrizations:
    energy = min(1, max(0,energy))
    amplitude = (2 - 1*energy) * amp # TUNING FUNCTION
    n_per_10 = (n_min + energy * (n_max - n_min)) / amp
    n = max(1, int(n_per_10 * length / 10))
    splines = get_gluon_splines(length, amplitude, n, amp)
    return pathdata_from_splines(splines, trafo_spline = spline)

# TUNING DEFAULTS
def boson_data(energy, spline, n_max = 2, n_min = 2, amp = 1):
    """Get the SVG path data for a boson.
    energy must be between 0 and 1
    either length or spline must be given."""
    a = amp / 3 # TUNING PARAMETER
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
    data = ["M%.2f %.2f" % tip]
    data.append("L%.2f %.2f" % tail1)
    data.append("C%.2f %.2f %.2f %.2f %.2f %.2f" % (control1 + control2 + tail2))
    data.append("Z")
    return "".join(data)

def pointed_arrow_data(size, spline):
    """Returns the path data for an arrow in the middle of the given spline"""
    width = size*0.3
    x = spline.length - size
    tip = spline.transform_x_point(x, (spline.length, 0))
    tail1 = spline.transform_x_point(x, (x, width))
    tail2 = spline.transform_x_point(x, (x, - width))
    control1 = spline.transform_x_point(x, (x + size*0.1, width*0.5))
    control2 = spline.transform_x_point(x, (x + size*0.1, - width*0.5))
    data = ["M%.2f %.2f" % tip]
    data.append("L%.2f %.2f" % tail1)
    data.append("C%.2f %.2f %.2f %.2f %.2f %.2f" % (control1 + control2 + tail2))
    data.append("Z")
    return "".join(data)

def svg_group(kwds):
    grp = svgxml.createElement("g")
    for kw, val in kwds.iteritems():
        grp.setAttribute(kw, str(val))
    return grp

# Get SVG fragments
def photon(energy, spline, scale = 1, **kwds):
    """Get an SVG fragment for a photon along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    path = svgxml.createElement("path")
    path.setAttribute("fill", "none")
    path.setAttribute("d", photon_data(energy, spline, amp = scale))
    grp = svg_group(kwds)
    grp.appendChild(path)
    return grp

def gluon(energy, spline, scale = 1, **kwds):
    """Get an SVG fragment for a photon along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    path = svgxml.createElement("path")
    path.setAttribute("fill", "none")
    path.setAttribute("d", gluon_data(energy, spline, amp = scale))
    grp = svg_group(kwds)
    grp.appendChild(path)
    return grp

def boson(energy, spline, scale = 1, **kwds):
    """Get an SVG fragment for a photon along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    path = svgxml.createElement("path")
    path.setAttribute("fill", "none")
    path.setAttribute("d", boson_data(energy, spline, amp = scale))
    grp = svg_group(kwds)
    grp.appendChild(path)
    return grp

def fermion(energy, spline, scale = 1, **kwds):
    path = svgxml.createElement("path")
    path.setAttribute("fill", "none")
    path.setAttribute("d", spline.svg_path_data)
    arrowsize = (0.2 + energy) * scale * 2
    arrow = svgxml.createElement("path")
    arrow.setAttribute("stroke", "none")
    arrow.setAttribute("d", fermion_arrow_data(arrowsize, spline))
    grp = svg_group(kwds)
    grp.appendChild(path)
    grp.appendChild(arrow)
    return grp

def hadron(energy, spline, scale = 1, **kwds):
    arrowsize = (0.2 + energy) * scale * 2
    path = svgxml.createElement("path")
    path.setAttribute("fill", "none")
    path.setAttribute("d", spline.get_clipped(arrowsize*0.8).svg_path_data)
    arrow = svgxml.createElement("path")
    arrow.setAttribute("stroke", "none")
    arrow.setAttribute("d", pointed_arrow_data(arrowsize, spline))
    grp = svg_group(kwds)
    grp.appendChild(path)
    grp.appendChild(arrow)
    return grp

def vertex(pt, r, **kwds):
    circle = svgxml.createElement("circle")
    circle.setAttribute("cx", "%.2f" % pt[0])
    circle.setAttribute("cy", "%.2f" % pt[1])
    circle.setAttribute("r", "%.2f" % r)
    for kw, val in kwds.iteritems():
        circle.setAttribute(kw, str(val))
    return circle

if __name__=="__main__":
    from spline import Spline, SplineLine, Line
    
    spline1 = Spline((5.0, -10), (20.000, -10), (15.0, 30.000), (40.0, 10.000))
    spline2 = Spline((40, 10), (65, -10), (60, 30), (80, 20))
    spline = SplineLine((spline1, spline2))
    line = Line((0,0),(spline.length,0))

    doc = svgxml.createElement("svg") 
    doc.setAttribute("xmlns", "http://www.w3.org/2000/svg")
    doc.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink")
    doc.setAttribute("viewBox", "0 0 1000 1000")

    spath = svgxml.createElement("path")
    spath.setAttribute("d", spline.svg_path_data)
    spath.setAttribute("transform", "translate(%i,%i)" % (10, 10))
    spath.setAttribute("fill", "none")
    spath.setAttribute("stroke", "red")
    doc.appendChild(spath)

    args = {"fill":"none", "stroke":"blue", "scale" : 5}
    fargs = {"fill":"blue", "stroke":"blue", "scale" : 5}

    n = 10
    for i in range(n+1):
        x = 10
        y = 40 + i*25
        e = i/n
        doc.appendChild(photon(e, line, transform="translate(%i,%i)" % (x, y),**args)).toprettyxml() 
        doc.appendChild(photon(e, spline, transform="translate(%i,%i)" % (x+100, y),**args)).toprettyxml()
        doc.appendChild(gluon(e, line, transform="translate(%i,%i)" % (x+200, y),**args)).toprettyxml()    
        doc.appendChild(gluon(e, spline, transform="translate(%i,%i)" % (x+300, y),**args)).toprettyxml()
        doc.appendChild(boson(e, line, transform="translate(%i,%i)" % (x+400, y),**args)).toprettyxml()    
        doc.appendChild(boson(e, spline, transform="translate(%i,%i)" % (x+500, y),**args)).toprettyxml()
        doc.appendChild(fermion(e, line, transform="translate(%i,%i)" % (x+600, y),**fargs)).toprettyxml()    
        doc.appendChild(fermion(e, spline, transform="translate(%i,%i)" % (x+700, y),**fargs)).toprettyxml()

    for i in range(n+1):
        x = 10
        y = 400 + i*25
        e = 0.6
        l = Line((0,0),((i + 0.5) / n * 180, 10))
        doc.appendChild(photon(e, l, transform="translate(%i,%i)" % (x, y),**args)).toprettyxml()
        doc.appendChild(gluon(e, l, transform="translate(%i,%i)" % (x+250, y),**args)).toprettyxml()
        doc.appendChild(boson(e, l, transform="translate(%i,%i)" % (x+500, y),**args)).toprettyxml()
        doc.appendChild(fermion(e, l, transform="translate(%i,%i)" % (x+750, y),**fargs)).toprettyxml()

    #s.append('<path transform="translate(10,10)" fill="none" stroke="red" id="u" d="%s" />\n' % (gluon(0.5, 200)))

    f = file("feynman_shapes.svg","w")
    f.write(doc.toprettyxml())
    f.close()

    print "Written feynman_shapes.svg."
