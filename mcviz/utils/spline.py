from __future__ import division

from copy import deepcopy
from math import sqrt, hypot
from bisect import bisect_left, bisect_right
from ..utils import Point2D

class Spline(object):
    def __init__(self, p0, p1, p2, p3, N = 100):
        """ Create a spline given the start point, 
        two control points and the end point"""
        assert not (p0 == p1 == p2 == p3)
        def make_point(p):
            return Point2D(*p) if isinstance(p, tuple) else p
        self.points = map(make_point, [p0, p1, p2, p3])
        self.N = N
        self.sampled = False
        self._functionals = None
        self.fidelity = 2

    def calculate_functionals(self):
        # calculate functional parameters of the spline
        p = self.points
        A = p[3].x - 3*p[2].x + 3*p[1].x - p[0].x
        B = 3*p[2].x - 6*p[1].x + 3*p[0].x
        C = 3*p[1].x - 3*p[0].x
        D = p[0].x
        E = p[3].y - 3*p[2].y + 3*p[1].y - p[0].y
        F = 3*p[2].y - 6*p[1].y + 3*p[0].y
        G = 3*p[1].y - 3*p[0].y
        H = p[0].y
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
        return Point2D(x, y)

    def perturb(self, begin, amount):
        """
        Move the beginning or end of a line perpendicularly to its point.
        TODO: maybe calculate amount to move by in splinelines.
        """
        t = 0 if begin else 1
        p, dp = self.get_point_perp(t)
        newpoint = Point2D(p.x + dp.x*amount, p.y + dp.y*amount)
        points = list(self.points)
        points[0 if begin else 3] = newpoint
        self.points = tuple(points)

    def get_point_perp(self, t):
        A, B, C, D, E, F, G, H = self.functionals
        p = self.get_point(t)
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
        return p, Point2D(-dy/d, dx/d)

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
        return Point2D(x, y), Point2D(dx/d, dy/d), Point2D(-dy/d, dx/d)

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
        self.distances = [p1.dist(p2)
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
        t = self.get_t(ip.x/self.length)
        p, dp = self.get_point_perp(t)
        return Point2D(p.x + dp.x*ip.y, p.y + dp.y*ip.y)

    def transform_x_point(self, ix, pt):
        """transform a point pt according to the spline trafo at splinepoint x"""
        t = self.get_t(ix/self.length)
        p, dp, perp = self.get_point_tan_perp(t)
        return Point2D(p.x + dp.x*(pt.x - ix) + perp.x*pt.y, p.y + dp.y*(pt.x - ix) + perp.y*pt.y)

    def transform_spline(self, spline):
        s0T = self.transform_point(spline.points[0])
        s3T = self.transform_point(spline.points[3])
        s1T = self.transform_x_point(spline.points[0].x,spline.points[1])
        s2T = self.transform_x_point(spline.points[3].x,spline.points[2])
        return Spline(s0T, s1T, s2T, s3T)
    
    def transform_splineline(self, splineline):
        new_splines = [self.transform_spline(s) for s in splineline.splines]
        return SplineLine(new_splines)

    def shift_by(self, spline, t0 = 0, t1 = None):
        """
        Take this spline and transform it using 'spline'
        spline should be in a relative coordinate system to this spline
        """
        if t1 is None:
            t1 = self.length
        p0 = spline.get_point(spline.get_t(t0))
        p0.x = 0
        p1 = spline.get_point(spline.get_t(t1))
        p1.x = self.length

        tp0 = self.transform_point(p0)
        tp1 = self.transform_point(p1)

        tp0 -= self.points[0]
        tp1 -= self.points[3]

        #print "> ", tp0
        #print "> ", tp1
        #print self.points[0], self.points[0] + tp0
        #print self.points[1], self.points[1] + tp0
        #print self.points[2], self.points[2] + tp1
        #print self.points[3], self.points[3] + tp1
        #print "---------"
        self.points[0] += tp0
        self.points[1] += tp0
        v01 = self.points[1] - self.points[0]
        if v01.len() > 0:
            self.points[1] = self.points[1] - v01 * (1 / v01.len()) * tp0.len() * p0.y
        self.points[2] += tp1
        v32 = self.points[3] - self.points[2]
        if v32.len() > 0:
            self.points[2] = self.points[2] - v32 * (1 / v32.len()) * tp1.len() * p0.y
        self.points[3] += tp1
    
    def get_clipped(self, clip_length):
        x = self.length - clip_length
        p0, p1 = self.points[0], self.points[1]
        p3 = self.transform_point(Point2D(x, 0))
        p2 = self.points[2] + p3 - self.points[3]
        return Spline(p0, p1, p2, p3, self.N)

    def bifurcate(self, amount=1.0, start_amount=None):
        if start_amount is None: start_amount=amount
        s1 = deepcopy(self)
        s1.shift_by(Line(Point2D(0, start_amount), Point2D(self.length, amount)))
        s2 = deepcopy(self)
        s2.shift_by(Line(Point2D(0, -start_amount), Point2D(self.length, -amount)))
        return s1, s2

    def trifurcate(self, amount=1.0, start_amount=None):
        if start_amount is None: start_amount=amount
        s1 = deepcopy(self)
        s1.shift_by(Line(Point2D(0, start_amount), Point2D(self.length, amount)))
        s2 = deepcopy(self)
        s3 = deepcopy(self)
        s3.shift_by(Line(Point2D(0, -start_amount), Point2D(self.length, -amount)))
        return s1, s2, s3
    
    @property
    def svg_path_data(self):
        f = self.fidelity
        start_form = "M{0:.%df} {1:.%df}" % (f, f)
        point_form = 'C{0:.%df} {1:.%df} {2:.%df} {3:.%df} {4:.%df} {5:.%df}' % (f,f,f,f,f,f)
        data = [start_form.format(*self.points[0].tuple())]
        pts = (self.points[1].tuple() + self.points[2].tuple() + self.points[3].tuple())
        data.append(point_form.format(*pts))
        return "".join(data)
        #return "".join(self.raw_svg_path_data)

    #@property
    #def raw_svg_path_data(self):
    #    data = ["M%.2f %.2f" % self.points[0]]
    #    data.append("c")
    #    for i in (1,2,3):
    #        x = self.points[i][0] - self.points[0][0]
    #        y = self.points[i][1] - self.points[0][1]
    #        data.append("%.3f,%.3f " % (x, y))
    #    return data
    @property 
    def boundingbox(self):
        x0 = min(p.x for p in self.points)
        x1 = max(p.x for p in self.points)
        y0 = min(p.y for p in self.points)
        y1 = max(p.y for p in self.points)
        return x0, x1, y0, y1

    def __str__(self):
        return "spline; start %s; control points %s; %s; end %s" % tuple(self.points)


class SplineLine(object):
    def __init__(self, splines):
        self.splines = splines
        self.cumulative = None
        self.fidelity = 2

    def shift_by(self, spline):
        if not self.cumulative:
            self.cumulate()
        t = 0
        for s, l in zip(self.splines, self.cumulative):
            s.shift_by(spline, t, t + s.length)
            t += s.length

    def bifurcate(self, amount=1.0, start_amount=None):
        if start_amount is None: start_amount=amount
        s1 = deepcopy(self)
        s1.shift_by(Line(Point2D(0, start_amount), Point2D(self.length, amount)))
        s2 = deepcopy(self)
        s2.shift_by(Line(Point2D(0, -start_amount), Point2D(self.length, -amount)))
        return s1, s2
        if len(self.splines) == 1:
            # TODO. Somehow mess with the handles? Insert an inner control point
            # and perturb that?
            return self, self
        spline1 = deepcopy(self).perturb("inward", amount)
        spline2 = deepcopy(self).perturb("outward", amount)
        return spline1, spline2

    def trifurcate(self, amount=1.0, start_amount=None):
        if start_amount is None: start_amount=amount
        s1 = deepcopy(self)
        s1.shift_by(Line(Point2D(0, start_amount), Point2D(self.length, amount)))
        s2 = deepcopy(self)
        s3 = deepcopy(self)
        s3.shift_by(Line(Point2D(0, -start_amount), Point2D(self.length, -amount)))
        return s1, s2, s3
    
    def perturb(self, direction, amount):
        "Perturb the middle of a line inward or outward."
        amount = amount if direction == "inward" else -amount
        
        #self.splines[0].perturb(False, amount)
        for spline in self.splines: #[1:-1]:
            spline.perturb(True, amount)
            spline.perturb(False, amount)        
        #self.splines[-1].perturb(True, amount)
        return self

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
        spline, x, xleft = self.find_spline_at(ip.x)
        return spline.transform_point(Point2D(x, ip.y))

    def transform_x_point(self, ix, pt):
        spline, x, xleft = self.find_spline_at(ix)
        return spline.transform_x_point(x, Point2D(pt.x - xleft, pt.y))

    def transform_spline(self, spline):
        s0T = self.transform_point(spline.points[0])
        s3T = self.transform_point(spline.points[3])
        s1T = self.transform_x_point(spline.points[0].x,spline.points[1])
        s2T = self.transform_x_point(spline.points[3].x,spline.points[2])
        return Spline(s0T, s1T, s2T, s3T)

    def transform_splineline(self, splineline):
        new_splines = [self.transform_spline(s) for s in splineline.splines]
        return SplineLine(new_splines)

    @property
    def length(self):
        return sum(s.length for s in self.splines)

    @property
    def svg_path_data(self):
        f = self.fidelity
        start_form = "M{0:.%df} {1:.%df}" % (f, f)
        point_form = 'C{0:.%df} {1:.%df} {2:.%df} {3:.%df} {4:.%df} {5:.%df}' % (f,f,f,f,f,f)
        data = [start_form.format(*self.splines[0].points[0].tuple())]
        for s in self.splines:
            pts = (s.points[1].tuple() + s.points[2].tuple() + s.points[3].tuple())
            data.append(point_form.format(*pts))
        return " ".join(data)

        #return " ".join(s.svg_path_data for s in self.splines)
        #data = [self.splines[0].svg_path_data]
        #for i in range(1, len(self.splines)):
        #    s = self.splines[i]
        #    if s.points[0] == self.splines[i-1].points[3]:
        #        data.append("".join(s.raw_svg_path_data[1:]))
        #    else:
        #        data.append(s.svg_path_data)
        #return " ".join(data)
    @property
    def boundingbox(self):
        x0, x1, y0, y1 = self.splines[0].boundingbox
        for s in self.splines[1:]:
            sx0, sx1, sy0, sy1 = self.splines[0].boundingbox
            x0, x1, y0, y1 = min(x0, sx0), max(x1, sx1), min(y0, sy0), max(y1, sy1)
        return x0, x1, y0, y1 

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
        #print t, x,y, px, py, hypot(x - lx, y - ly)
        lx, ly = x, y


