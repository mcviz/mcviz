from __future__ import division

from xml.dom.minidom import getDOMImplementation
svgxml = getDOMImplementation().createDocument(None, "svg", None)

from ..spline import Spline, SplineLine, Point2D

COLOR = {'black' : (0, 0, 0),
         'green' : (0, 127, 0),
         'red'   : (255, 0, 0),
         'blue'  : (0, 0, 255),
         'orange': (255, 166, 0)
}

def get_boson_splines(length, amplitude, n_waves, power, amp):
    N = n_waves * 2
    wavelength = length / N
    cntrl_strength = wavelength # OLD TUNING PARAMETER

    # scaling envelope
    divisor = N - 1
    if power:
        # TUNING PARAMETER
        envelope = [1 - abs(2*i/divisor - 1)**power for i in range(N)]
    else:
        envelope = [1 for i in range(N)]

    # x offsets of points:
    px = [0.0] + [wavelength * (0.5 + i) for i in range(N)]
    px.append(px[-1] + wavelength / 2)

    # y offsets of points:
    py = [0.0] + [amplitude * envelope[i] for i in range(N)] + [0.0]

    splines = []
    sgn = 1
    for i in range(1, N + 2): # STYLE HALF OPEN PHOTONS: Was N+2
        op  = Point2D(px[i-1], -sgn * py[i-1])
        cp1 = Point2D(px[i-1], -sgn * py[i-1])
        cp2 = Point2D(px[i], sgn * py[i])
        dp  = Point2D(px[i], sgn * py[i])
        if i == 1:
            cp1 = op
        elif i == N+1:
            cp2 = dp
        splines.append(Spline(op, cp1, cp2, dp))
        sgn = -sgn
    return SplineLine(splines)

def get_segment_splines(length, n_segments, n, offset):
    N = n_segments*2 - 1
    wavelength = length / N

    # x offsets of points:
    px_start = wavelength*n
    px_mid = wavelength*(n+0.5)
    px_end = wavelength*(n+1)

    if px_start: py_start = offset*px_start
    else: py_start = 0

    splines = [Spline(Point2D(px_start, py_start), Point2D(px_mid, offset*px_mid), Point2D(px_mid, offset*px_mid), Point2D(px_end, offset*px_end))]
    return SplineLine(splines)

def get_photon_splines(length, amplitude, n_waves, power, amp, half_open = False):
    N = n_waves * 2
    wavelength = length / N
    cntrl_strength = wavelength / 2 # TUNING PARAMETER
    
    # scaling envelope
    divisor = 2*N - 1 if half_open else N - 1
    if power:
        # TUNING PARAMETER
        envelope = [1 - abs(2*i/divisor - 1)**power for i in range(N)]
    else:
        envelope = [1 for i in range(N)]

    # x offsets of points:
    px = [0.0] + [wavelength * (0.5 + i) for i in range(N)]
    px.append(px[-1] + wavelength / 2)

    # y offsets of points:
    py = [0.0] + [amplitude * envelope[i] for i in range(N)] + [0.0]
    
    splines = []
    sgn = 1
    for i in range(1, N + (1 if half_open else 2)): # STYLE HALF OPEN PHOTONS: Was N+2
        op  = Point2D(px[i-1], -sgn * py[i-1])
        cp1 = Point2D(px[i-1] + cntrl_strength, -sgn * py[i-1])
        cp2 = Point2D(px[i] - cntrl_strength, sgn * py[i])
        dp  = Point2D(px[i], sgn * py[i])
        if i == 1:
            cp1 = op
        elif i == N+1:
            cp2 = dp
        splines.append(Spline(op, cp1, cp2, dp))
        sgn = -sgn
    return SplineLine(splines)

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
        op  = Point2D(px[i-1], -sgn * py[i-1])
        cp1 = Point2D(px[i-1] - sgn * (2 - sgn) * cntrl_strength, -sgn * py[i-1])
        cp2 = Point2D(px[i] - sgn * (2 + sgn) * cntrl_strength, sgn * py[i])
        dp  = Point2D(px[i], sgn * py[i])
        if i == 1:
            cp1 = op
        elif i == N+1:
            cp2 = dp
        splines.append(Spline(op, cp1, cp2, dp))
        sgn = -sgn
    return SplineLine(splines)

# Functions to get SVN path data for objects
# contain some policy

# TUNING DEFAULTS
def boson_data(energy, spline, n_max=1, n_min=1, amp=1):
    """Get the SVG path data for a boson.
    energy must be between 0 and 1"""
    length = spline.length
    power = None
    amp = amp * 0.5
    # Here are parametrizations:
    energy = min(1, max(0, energy))
    amplitude = (0.5 + 0.5*energy) * amp * 3 # TUNING FUNCTION
    n_per_10 = 1 + (n_min + energy * (n_max - n_min)) / amp
    n = max(1, int(n_per_10 * length / 10))
    splineline = get_boson_splines(length, amplitude, n, power,
                                    amplitude)
    if spline: splineline = spline.transform_splineline(splineline)
    return splineline.svg_path_data

# TUNING DEFAULTS
def segment_data(energy, spline, n_segments, n_segment, offset=0):
    """Get the SVG path data for an particle line segment.
    energy must be between 0 and 1"""
    length = spline.length
    offset /= length*energy
    splineline = get_segment_splines(length, n_segments, n_segment, offset)
    if spline: splineline = spline.transform_splineline(splineline)
    splineline.fidelity = 4
    return splineline.svg_path_data

# TUNING DEFAULTS
def photon_data(energy, spline, n_max=10, n_min=3, power=5, amp=1, half_open=False):
    """Get the SVG path data for a photon. 
    energy must be between 0 and 1"""
    length = spline.length
    # Here are parametrizations:
    energy = min(1, max(0, energy))
    amplitude = (0.5 + 0.5*energy) * amp # TUNING FUNCTION
    n_per_10 = (n_min + energy * (n_max - n_min)) / amp
    n = max(2, int(n_per_10 * length / 10))
    splineline = get_photon_splines(length, amplitude, n, power, 
                                    amplitude, half_open)
    if spline: splineline = spline.transform_splineline(splineline)
    return splineline.svg_path_data

# TUNING DEFAULTS
def gluon_data(energy, spline, n_max = 11, n_min = 1, amp = 1):
    """Get the SVG path data for a gluon.
    energy must be between 0 and 1"""
    length = spline.length
    # Here are parametrizations:
    energy = min(1, max(0,energy))
    amplitude = (1.5 - 1*energy) * amp # TUNING FUNCTION
    n_per_10 = (n_min + energy * (n_max - n_min)) / amp
    n = max(1, int(n_per_10 * length / 10))
    splineline = get_gluon_splines(length, amplitude, n, amplitude)
    if spline: splineline = spline.transform_splineline(splineline)
    return splineline.svg_path_data

def fermion_arrow_data(size, spline):
    """Returns the path data for an arrow in the middle of the given spline"""
    mid = spline.length/2
    width = size*0.3
    tip = spline.transform_x_point(mid, Point2D(mid + size*0.5, 0))
    tail1 = spline.transform_x_point(mid, Point2D(mid - size*0.5, width))
    tail2 = spline.transform_x_point(mid, Point2D(mid - size*0.5, - width))
    control1 = spline.transform_x_point(mid, Point2D(mid - size*0.4, width*0.5))
    control2 = spline.transform_x_point(mid, Point2D(mid - size*0.4, - width*0.5))
    data = ["M%.2f %.2f" % tip.tuple()]
    data.append("L%.2f %.2f" % tail1.tuple())
    data.append("C%.2f %.2f %.2f %.2f %.2f %.2f" % (control1.tuple() + control2.tuple() + tail2.tuple()))
    data.append("Z")
    return "".join(data)

def pointed_arrow_data(size, spline):
    """Returns the path data for an arrow in the middle of the given spline"""
    width = size*0.3
    x = spline.length - size
    tip = spline.transform_x_point(x, Point2D(spline.length, 0))
    tail1 = spline.transform_x_point(x, Point2D(x, width))
    tail2 = spline.transform_x_point(x, Point2D(x, - width))
    control1 = spline.transform_x_point(x, Point2D(x + size*0.1, width*0.5))
    control2 = spline.transform_x_point(x, Point2D(x + size*0.1, - width*0.5))
    data = ["M%.2f %.2f" % tip.tuple()]
    data.append("L%.2f %.2f" % tail1.tuple())
    data.append("C%.2f %.2f %.2f %.2f %.2f %.2f" % (control1.tuple() + control2.tuple() + tail2.tuple()))
    data.append("Z")
    return "".join(data)

def svg_group(kwds):
    grp = svgxml.createElement("g")
    grp.setAttribute("stroke-linecap","round")
    for kw, val in kwds.iteritems():
        grp.setAttribute(kw, str(val))
    return grp

# Get SVG fragments
def final_photon(energy, spline, scale = 1, **kwds):
    """Get an SVG fragment for a photon along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    path = svgxml.createElement("path")
    path.setAttribute("fill", "none")
    path.setAttribute("d", photon_data(energy, spline, amp = scale, half_open = True))
    grp = svg_group(kwds)
    grp.appendChild(path)
    return grp

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
    """Get an SVG fragment for a gluon along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    path = svgxml.createElement("path")
    path.setAttribute("fill", "none")
    path.setAttribute("d", gluon_data(energy, spline, amp = scale))
    grp = svg_group(kwds)
    grp.appendChild(path)
    return grp

def gluino(energy, spline, scale = 1, **kwds):
    """Get an SVG fragment for a gluino along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    grp = gluon(energy, spline, scale = 1, **kwds)
    path2 = svgxml.createElement("path")
    path2.setAttribute("fill", "none")
    path2.setAttribute("d", spline.svg_path_data)
    grp.appendChild(path2)
    return grp

def multigluon(energy, spline, scale=1, **kwds):
    line1, line2 = spline.bifurcate(energy*scale)
    line1 = line1.svg_path_data
    line2 = line2.svg_path_data
    
    path1 = svgxml.createElement("path"); path1.setAttribute("fill", "none"); path1.setAttribute("d", line1)
    path1.setAttribute("stroke", kwds.pop("color"))
    path2 = svgxml.createElement("path"); path2.setAttribute("fill", "none"); path2.setAttribute("d", line2)
    path2.setAttribute("stroke", kwds.pop("anticolor"))
    grp = svg_group(kwds)
    grp.appendChild(path1)
    grp.appendChild(path2)
    return grp

def jet(energy, spline, scale = 8, **kwds):
    """Get an SVG fragment for a jet along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    n_segments = 10
    mag = energy*scale
    offsets = [-mag, 0, mag]
    all_paths = []
    kwds['stroke-width'] = energy*scale*3
    for offset in offsets:
        paths = []
        for i in range(n_segments*2):
            paths.append(svgxml.createElement("path"))
            paths[i].setAttribute("d", segment_data(energy, spline, n_segments, i, offset))
        all_paths.extend(paths)
    grp = svg_group(kwds)
    grp.setAttribute("fill", "none")
    for path in all_paths:
        grp.appendChild(path)
    return grp

def cut(energy, spline, n_represented, scale = 8, **kwds):
    """Get an SVG fragment for a cut along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    n_segments = 10
    mag = energy*scale
    if n_represented > 2: offsets = [-mag, 0, mag] #spline.trifurcate(mag)
    elif n_represented == 2: offsets = [-mag/2, mag/2] #spline.bifurcate(mag)
    else: offsets = [0]
    all_paths = []
    color = kwds.pop('stroke')
    if color[0] == '#':
          rgb = (color[1:3], color[3:5], color[5:7])
          r, g, b = [int(c, 16) for c in rgb]
          color = (r,g,b)
    elif color in COLOR: color = COLOR[color]
    else: color = (0, 0, 0)
    for offset in offsets:
        paths = []
        for i in range(n_segments*2):
            opacity = i/(n_segments*2.0)
            transparency = 1.0 - opacity
            w = 255 * opacity
            t = transparency
            stroke = "rgb({0:d},{1:d},{2:d})".format(int(w + t * color[0]), int(w + t * color[1]), int(w + t * color[2]))
            paths.append(svgxml.createElement("path"))
            paths[i].setAttribute("stroke", stroke)
            paths[i].setAttribute("d", segment_data(energy, spline, n_segments, i, offset))
        all_paths.extend(paths)
    grp = svg_group(kwds)
    grp.setAttribute("fill", "none")
    for path in all_paths:
        grp.appendChild(path)
    return grp
        
#    arrowsize = (0.2 + energy) * scale * 3
#    path = svgxml.createElement("path")
#    path.setAttribute("fill", "none")
#    path.setAttribute("stroke", "url(#fadeout)")
#    #path.setAttribute("style", 'stroke:#00f;fill:none;stroke-width:0.01;')
#    #path.setAttribute("marker-end", "url(#fadeline3)")
#    path.setAttribute("d", spline.get_clipped(arrowsize*0.8).svg_path_data)
#    arrow = svgxml.createElement("path")
#    arrow.setAttribute("stroke", "url(#red_blue)")
#    arrow.setAttribute("fill", "url(#red_blue)")
#    arrow.setAttribute("d", pointed_arrow_data(arrowsize, spline))
#    grp = svg_group(kwds)
#    grp.appendChild(path)
#    #grp.appendChild(arrow)
#    return grp

def boson(energy, spline, scale = 1, **kwds):
    """Get an SVG fragment for a boson along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    path = svgxml.createElement("path")
    path.setAttribute("fill", "none")
    path.setAttribute("d", boson_data(energy, spline, amp=scale))
    grp = svg_group(kwds)
    grp.appendChild(path)
    return grp

def fermion(energy, spline, scale = 1, **kwds):
    path = svgxml.createElement("path")
    path.setAttribute("fill", "none")
    path.setAttribute("d", spline.svg_path_data)
    arrowsize = (0.2 + energy) * scale * 5
    arrow = svgxml.createElement("path")
    arrow.setAttribute("stroke", "none")
    arrow.setAttribute("d", fermion_arrow_data(arrowsize, spline))
    grp = svg_group(kwds)
    grp.appendChild(path)
    grp.appendChild(arrow)
    return grp

def sfermion(energy, spline, scale = 1, **kwds):
    """Get an SVG fragment for a susy particle along a spline
    energy must be between 0 and 1. kwds are added to SVG"""
    grp = boson(energy, spline, scale=0.5*scale, **kwds)
    path = svgxml.createElement("path")
    path.setAttribute("fill", "none")
    path.setAttribute("d", spline.svg_path_data)
    grp.appendChild(path)
    return grp

def chargino(energy, spline, scale = 1, **kwds):
    grp = photon(energy, spline, scale, **kwds)
    path = svgxml.createElement("path")
    path.setAttribute("fill", "none")
    path.setAttribute("d", spline.svg_path_data)
    grp.appendChild(path)
    return grp

def invisible(energy, spline, scale = 1, **kwds):
    n_segments = int(spline.length*2)
    paths = []
    for i in range(n_segments):
        paths.append(svgxml.createElement("path"))
        paths[i].setAttribute("fill", "none")
        paths[i].setAttribute("d", segment_data(energy, spline, n_segments, i*2))
    grp = svg_group(kwds)
    for path in paths:
        grp.appendChild(path)
    return grp

def hadron(energy, spline, scale = 1, **kwds):
    arrowsize = (0.2 + energy) * scale * 5
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

def identity(energy, spline, scale = 1, **kwds):
    
    path = svgxml.createElement("path")
    path.setAttribute("fill", "none")
    path.setAttribute("d", spline.svg_path_data)
    
    grp = svg_group(kwds)
    grp.appendChild(path)
    
    return grp

def vertex(pt, rx, ry, **kwds):
    ellipse = svgxml.createElement("ellipse")
    ellipse.setAttribute("cx", "%.2f" % pt.x)
    ellipse.setAttribute("cy", "%.2f" % pt.y)
    ellipse.setAttribute("rx", "%.2f" % rx)
    ellipse.setAttribute("ry", "%.2f" % ry)
    for kw, val in kwds.iteritems():
        ellipse.setAttribute(kw, str(val))
    return ellipse

#if __name__=="__main__":
def test():
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
    mgargs = {"color":"blue", "anticolor":"red", "scale" : 5}

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
        doc.appendChild(multigluon(e, spline, transform="translate(%i,%i)" % (x+800, y),**mgargs)).toprettyxml()    

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
