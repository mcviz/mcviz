from __future__ import division
max_amp = 5

def set_width(width):
    global max_amp
    max_amp = width

def get_photon_splines(length, amplitude, n_waves, power = 5):
    N = n_waves * 2
    wavelength = length / N
    cntrl_strength = wavelength / 2
    
    # scaling envelope 
    envelope = [1 - abs(2*i/(N-1) - 1)**power for i in range(N)]

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
        splines.append([op, cp1, cp2, dp])
        sgn = -sgn
    return splines

def get_gluon_splines(length, amplitude, n_waves):
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
        splines.append([op, cp1, cp2, dp])
        sgn = -sgn
    return splines
    
def pathdata_from_splines(splines, trafo_spline = None):
    if trafo_spline:
        splines = [map(trafo_spline.transform, s) for s in splines]
    data = ["M %.5f %.5f\n" % splines[0][0]]
    for s in splines:
        data.append('C %.5f %.5f %.5f %.5f %.5f %.5f\n' % (s[1] + s[2] + s[3]))
    return "".join(data)

def pathdata_from_splines_smooth(splines, trafo_spline = None):
    if trafo_spline:
        new_splines = []
        for s in splines:
            s0T = trafo_spline.transform(s[0])
            s3T = trafo_spline.transform(s[3])
            s1T = trafo_spline.transform_to(s[0][0],s[1])
            s2T = trafo_spline.transform_to(s[3][0],s[2])
            new_splines.append([s0T, s1T, s2T, s3T])        
        splines = new_splines
    data = ["M %.5f %.5f\n" % splines[0][0]]
    for s in splines:
        data.append('C %.5f %.5f %.5f %.5f %.5f %.5f\n' % (s[1] + s[2] + s[3]))
    return "".join(data)


def photon(energy, length = None, spline = None, n_max = 10, n_min = 3):
    """Get the SVG path data for a photon.
    energy must be between 0 and 1
    either length or spline must be given."""
    assert length or spline
    assert not (length and spline)
    if not length:
        length = spline.length
    energy = min(1, max(0,energy))
    amplitude = (0.5 + 0.5*energy) * max_amp
    n_per_50 = n_min + energy * (n_max - n_min)
    n = max(2, int(n_per_50 * length / 50))
    if spline:
        return pathdata_from_splines_smooth(get_photon_splines(spline.length, amplitude, n), trafo_spline = spline)
    else:
        return pathdata_from_splines(get_photon_splines(length, amplitude, n))

def gluon(energy, length = None, spline = None, n_max = 11, n_min = 1):
    """Get the SVG path data for a gluon.
    energy must be between 0 and 1
    either length or spline must be given."""
    assert length or spline
    assert not (length and spline)
    if not length:
        length = spline.length
    energy = min(1, max(0,energy))
    amplitude = (1 - 0.3*energy) * max_amp
    n_per_50 = n_min + energy * (n_max - n_min)
    n = max(1, int(n_per_50 * length / 50))
    if spline:
        return pathdata_from_splines_smooth(get_gluon_splines(spline.length, amplitude, n), trafo_spline = spline)
    else:
        return pathdata_from_splines(get_gluon_splines(length, amplitude, n))

if __name__=="__main__":
    from spline import Spline, Splines
    
    spline1 = Spline(5.0, -10, 20.000, -10, 15.0, 30.000, 40.0, 10.000)
    spline2 = Spline(40, 10, 65, -10, 60, 30, 80, 20)
    dat1 = ("M %.5f %.5f C " + "%.f "*6) % (5.0, -10, 20.000, -10, 15.0, 30.000, 40.0, 10.000)
    dat2 = ("M %.5f %.5f C " + "%.f "*6) % (40, 10, 65, -10, 60, 30, 80, 20)
    spline = Splines((spline1, spline2))
    print spline.length


    s = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 500 700">\n']

    s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (10, 10, dat1))
    s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (10, 10, dat2))


    n = 10
    for i in range(n+1):
        x = 10
        y = 40 + i*25
        e = i/n
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (x, y, photon(e, spline.length)))
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (100+x, y, photon(e, spline = spline)))
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (200+x, y, gluon(e, spline.length)))
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (300+x, y, gluon(e, spline = spline)))

    for i in range(n+1):
        x = 10
        y = 400 + i*25
        e = 0.6
        l = (i + 0.5) / n * 180
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (x, y, photon(e, l)))
        s.append('<path transform="translate(%i,%i)" fill="none" stroke="red" id="u" d="%s" />\n' % (200+x, y, gluon(e, l)))

    #s.append('<path transform="translate(10,10)" fill="none" stroke="red" id="u" d="%s" />\n' % (gluon(0.5, 200)))

    s.append('" />\n')
    s.append('</svg>\n')

    f = file("photon.svg","w")
    f.write("".join(s))
    f.close()

    print "Written photon.svg."
