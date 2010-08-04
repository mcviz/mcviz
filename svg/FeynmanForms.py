from spline import Spline

#spline = Spline(5.0, -10, 10.000, -9.722, 10.0, 10.000, 15.0, 10.000)
spline = Spline(5.0, -10, 20.000, -10, 15.0, 30.000, 40.0, 10.000)


def getPhotonDataRaw(N, d, amplitude, power=3):
    data = ["M %.5f %.5f\n" % spline.transform(0,0)]

    strength0 = d/2.0

    # scalings of interior points
    scalings = [(1 - abs(i*2.0/(N-1) - 1)**power) for i in range(N)]

    # x offsets of points:
    cpx = [0.0]
    cpx.extend(map(lambda x : d/2.0 + x*d, range(N)))
    cpx.append(cpx[-1] + d/2.0)

    # y offsets of points:
    cpy = [0.0]
    cpy.extend(map(lambda i : amplitude*scalings[i], range(N)))
    cpy.append(0.0)

    sgn = 1
    for i in range(1, N+2):
        cp1 = cpx[i-1]+strength0, -sgn*cpy[i-1]
        cp2 = cpx[i]-strength0, sgn*cpy[i]
        dp  = cpx[i], sgn*cpy[i]
        #print cp1, cp2, dp
        cp1 = spline.transform(*cp1)
        cp2 = spline.transform(*cp2)
        dp = spline.transform(*dp)
        #print cp1, cp2, dp
        data.append('C %.5f %.5f %.5f %.5f %.5f %.5f\n' % (cp1[0], cp1[1], cp2[0], cp2[1], dp[0], dp[1]))
        sgn = -sgn
    return "".join(data)


def getPhotonData(length, energy, base_length = 0.1, N_min = 5, N_max = 20):
    """Get Photon Data depending on energy (clamped from 0 to 1)"""
    energy = min(1, max(0,energy))
    N = int(N_min + energy*(N_max-N_min))
    d = length*1.0/N
    amplitude = d/2.0
    print N, d, amplitude 
    return getPhotonDataRaw(N, d, amplitude)

import sys
from math import sin, cos, pi

#e = float(sys.argv[1])

#amplitude = float(sys.argv[3])
#strength0 = float(sys.argv[4])
#strength0 = d/2.0
e = 0.5
length = 1

s = []
s.append('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 400 400">\n')
s.append('<path transform="translate(10,40)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(length,e,1))
#s.append('<path transform="translate(10,80)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,,2))
#s.append('<path transform="translate(10,120)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,,3))
#s.append('<path transform="translate(10,160)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,,4))

#s.append('<path transform="translate(180,40)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,,1))
#s.append('<path transform="translate(180,80)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,,2))
#s.append('<path transform="translate(180,120)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,,3))
#s.append('<path transform="translate(180,160)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,,4))

#s.append('<path transform="translate(10,240)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,,1))
#s.append('<path transform="translate(10,280)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,,2))
#s.append('<path transform="translate(10,320)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,,3))
#s.append('<path transform="translate(10,360)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,,4))

#s.append('<path transform="translate(120,240)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,/2,1))
#s.append('<path transform="translate(120,280)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,/2,2))
#s.append('<path transform="translate(120,320)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,/2,3))
#s.append('<path transform="translate(120,360)" fill="none" stroke="red" id="u" d="%s" />\n' % getPhotonData(len,e,/2,4))
s.append('" />\n')
#s.append('</symbol>\n')
#s.append("</defs>\n")
#s.append('<use x="60" y="0" transform="scale(2, 4)"  width="200" height="100" fill="none" stroke-width="2" stroke="red" xlink:href="#S"/>\n')
s.append('</svg>\n')

f = file("photon.svg","w")
f.write("".join(s))
f.close()
