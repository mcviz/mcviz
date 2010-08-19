from __future__ import division

from math import sqrt, hypot
from bisect import bisect_left, bisect_right

class Spline(object):
    def __init__(self, p0, p1, p2, p3, N = 100):
        """ Create a spline given the start point, 
        two control points and the end point"""
        assert not (p0 == p1 == p2 == p3)
        self.points = (p0, p1, p2, p3)
        self.N = N
        self.sampled = False
        self._functionals = None

    def calculate_functionals(self):
        # calculate functional parameters of the spline
        p = self.points
        A = p[3][0] - 3*p[2][0] + 3*p[1][0] - p[0][0]
        B = 3*p[2][0] - 6*p[1][0] + 3*p[0][0]
        C = 3*p[1][0] - 3*p[0][0]
        D = p[0][0]
        E = p[3][1] - 3*p[2][1] + 3*p[1][1] - p[0][1]
        F = 3*p[2][1] - 6*p[1][1] + 3*p[0][1]
        G = 3*p[1][1] - 3*p[0][1]
        H = p[0][1]
        self._functionals = A, B, C, D, E, F, G, H

    @property
    def functionals(self):
        if not self._functionals:
            self.calculate_functionals()
        return self._functionals

    def get_point(self, t):
        A, B, C, D, E, F, G, H = self.functionals
        x = (((A*t) + B)*t + C)*t + D
        y = (((E*t) + F)*t + G)*t + H
        return x, y

    def get_point_perp(self, t):
        A, B, C, D, E, F, G, H = self.functionals
        x = (((A*t) + B)*t + C)*t + D
        y = (((E*t) + F)*t + G)*t + H
        dx = 3*A*t**2 + 2*B*t + C
        dy = 3*E*t**2 + 2*F*t + G
        d = sqrt(dx**2 + dy**2)
        if d/self.length < 1e-8:
            if t < 0.5:
                #print "t = ", t, "increased"
                return self.get_point_perp(t + 0.001)
            else:
                #print "t = ", t, "decreased"
                return self.get_point_perp(t - 0.001)
        return x, y, -dy/d, dx/d

    def get_point_tan_perp(self, t):
        A, B, C, D, E, F, G, H = self.functionals
        x = (((A*t) + B)*t + C)*t + D
        y = (((E*t) + F)*t + G)*t + H
        dx = 3*A*t**2 + 2*B*t + C
        dy = 3*E*t**2 + 2*F*t + G
        d = sqrt(dx**2 + dy**2)
        if d/self.length < 1e-8:
            if t < 0.5:
                #print "t = ", t, "increased"
                return self.get_point_tan_perp(t + 0.001)
            else:
                #print "t = ", t, "decreased"
                return self.get_point_tan_perp(t - 0.001)
        return x, y, dx/d, dy/d, -dy/d, dx/d

    @property
    def length(self):
        if not self.sampled:
            self.sample_path()
        return self._length

    def sample_path(self, N = None):
        if not N:
            N = self.N
        else:
            self.N = N
        self.samples = [self.get_point(x / N) for x in range(N + 1)]
        self.distances = [hypot(p1[0] - p2[0], p1[1] - p2[1])
                          for p1, p2 in zip(self.samples[:-1], self.samples[1:])]
        self._length = sum(self.distances)
        cum = self.cumulative = [0]
        for dist in self.distances:
            cum.append(cum[-1] + dist)
        self.sampled = True

    def get_t(self, s):
        s = min(1, max(0, s))
        s *= self.length
        i = bisect_left(self.cumulative, s)
        if i == 0: 
            i = 1
        part = (s - self.cumulative[i]) / self.distances[i-1]
        return (i*1.0 + part)/self.N

    def transform_point(self, ip):
        """transform a point according to the spline trafo
        x is length along the spline
        y is across and in the same units as x"""
        ix, iy = ip
        t = self.get_t(ix/self.length)
        x, y, px, py = self.get_point_perp(t)
        return x + px*iy, y + py*iy

    def transform_x_point(self, ix, pt):
        """transform a point pt according to the spline trafo at splinepoint x"""
        t = self.get_t(ix/self.length)
        x, y, dx, dy, px, py = self.get_point_tan_perp(t)
        return x + dx*(pt[0]-ix) + px*pt[1], y + dy*(pt[0]-ix) + py*pt[1]

    def transform_spline(self, spline):
        s0T = self.transform_point(spline.points[0])
        s3T = self.transform_point(spline.points[3])
        s1T = self.transform_x_point(spline.points[0][0],spline.points[1])
        s2T = self.transform_x_point(spline.points[3][0],spline.points[2])
        return Spline(s0T, s1T, s2T, s3T)
    
    def transform_splineline(self, splineline):
        new_splines = [self.transform_spline(s) for s in splineline.splines]
        return SplineLine(new_splines)
    
    def get_clipped(self, clip_length):
        x = self.length - clip_length
        p0, p1 = self.points[0], self.points[1]
        p2 = list(self.points[2])
        p3 = self.transform_point((x, 0))
        for i in (0,1):
            p2[i] += p3[i] - self.points[3][i]
        return Spline(p0, p1, tuple(p2), p3, self.N)
        
    @property
    def svg_path_data(self):
        return "".join(self.raw_svg_path_data)

    @property
    def raw_svg_path_data(self):
        data = ["M%.2f %.2f" % self.points[0]]
        data.append("c")
        for i in (1,2,3):
            x = self.points[i][0] - self.points[0][0]
            y = self.points[i][1] - self.points[0][1]
            data.append("%.2f,%.2f " % (x, y))
        return data

    def __str__(self):
        return "spline; start %s; control points %s; %s; end %s" % self.points


class SplineLine(object):
    def __init__(self, splines):
        self.splines = splines
        self.cumulative = None

    def cumulate(self):
        cum = self.cumulative = [0]
        for spline in self.splines:
            cum.append(cum[-1] + spline.length)

    def find_spline_at(self, s):
        if not self.cumulative:
            self.cumulate()
        i = bisect_left(self.cumulative, s) - 1
        i = max(0, min(len(self.splines) - 1, i))
        return self.splines[i], s - self.cumulative[i], self.cumulative[i]

    def transform_point(self, ip):
        spline, x, xleft = self.find_spline_at(ip[0])
        return spline.transform_point((x, ip[1]))

    def transform_x_point(self, ix, pt):
        spline, x, xleft = self.find_spline_at(ix)
        return spline.transform_x_point(x, (pt[0] - xleft, pt[1]))

    def transform_spline(self, spline):
        s0T = self.transform_point(spline.points[0])
        s3T = self.transform_point(spline.points[3])
        s1T = self.transform_x_point(spline.points[0][0],spline.points[1])
        s2T = self.transform_x_point(spline.points[3][0],spline.points[2])
        return Spline(s0T, s1T, s2T, s3T)

    def transform_splineline(self, splineline):
        new_splines = [self.transform_spline(s) for s in splineline.splines]
        return SplineLine(new_splines)

    @property
    def length(self):
        return sum(s.length for s in self.splines)

    @property
    def svg_path_data(self):
        #return " ".join(s.svg_path_data for s in self.splines)
        data = [self.splines[0].svg_path_data]
        for i in range(1, len(self.splines)):
            s = self.splines[i]
            if s.points[0] == self.splines[i-1].points[3]:
                data.append("".join(s.raw_svg_path_data[1:]))
            else:
                data.append(s.svg_path_data)
        return " ".join(data)

    def get_clipped(self, clip_length):
        splines = self.splines[:-1] + [self.splines[-1].get_clipped(clip_length)]
        return SplineLine(splines)

    def __str__(self):
        start, end = self.splines[0].points[0], self.splines[-1].points[-1]
        return "splineline; start %s; end %s" % (start, end)

class Line(Spline):
    def __init__(self, p0, p1):
        super(Line, self).__init__(p0, p0, p1, p1)

if __name__=="__main__":
    s = Spline(5.0, -10, 20.000, -10, 20.0, 10.000, 40.0, 10.000)
    lx, ly = 0, 0
    for i in range(500):
        t = s.get_t(i / 500)
        x, y, px, py = s.get_point_perp(t)
        if lx == 0 and ly == 0: 
            lx, ly = x, y        
        print t, x,y, px, py, hypot(x - lx, y - ly)
        lx, ly = x, y


