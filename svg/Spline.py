from __future__ import division

from math import sqrt, hypot
from bisect import bisect_left, bisect_right

class Splines(object):
    def __init__(self, splines):
        self.splines = splines
        cum = self.cumulative = [0]
        for spline in self.splines:
            cum.append(cum[-1] + spline.length)

    @property
    def length(self):
        return sum(s.length for s in self.splines)

    def getSplineAt(self, s):
        i = bisect_left(self.cumulative, s) - 1
        i = max(0, min(len(self.splines) - 1, i))
        return self.splines[i], s - self.cumulative[i], self.cumulative[i]

    def transform(self, ip):
        spline, x, xleft = self.getSplineAt(ip[0])
        return spline.transform((x, ip[1]))

    def transform_to(self, ix, pt):
        spline, x, xleft = self.getSplineAt(ix)
        return spline.transform_to(x, (pt[0] - xleft, pt[1]))

class Spline(object):
    def __init__(self, x0, y0, x1, y1, x2, y2, x3, y3, N=100):
        A = x3 - 3*x2 + 3*x1 - x0
        B = 3*x2 - 6*x1 + 3*x0
        C = 3*x1 - 3*x0
        D = x0
        E = y3 - 3*y2 + 3*y1 - y0
        F = 3*y2 - 6*y1 + 3*y0
        G = 3*y1 - 3*y0
        H = y0
        self.x = (x0, x1, x2, x3)
        self.y = (y0, y1, y2, y3)
        self.Ax = (A, B, C, D)
        self.Ay = (E, F, G, H)
        self.sample_path(N)
    
    def get_point_perp(self, t):
        A, B, C, D = self.Ax
        E, F, G, H = self.Ay
        x = (((A*t) + B)*t + C)*t + D
        y = (((E*t) + F)*t + G)*t + H
        dx = 3*A*t**2 + 2*B*t + C
        dy = 3*E*t**2 + 2*F*t + G
        d = sqrt(dx**2 + dy**2)
        return x, y, -dy/d, dx/d

    def get_point_tan_perp(self, t):
        A, B, C, D = self.Ax
        E, F, G, H = self.Ay
        x = (((A*t) + B)*t + C)*t + D
        y = (((E*t) + F)*t + G)*t + H
        dx = 3*A*t**2 + 2*B*t + C
        dy = 3*E*t**2 + 2*F*t + G
        d = sqrt(dx**2 + dy**2)
        return x, y, dx/d, dy/d, -dy/d, dx/d

    def get_point(self, t):
        A, B, C, D = self.Ax
        E, F, G, H = self.Ay
        x = (((A*t) + B)*t + C)*t + D
        y = (((E*t) + F)*t + G)*t + H
        return x, y

    def sample_path(self, N):
        self.N = N
        self.points = [self.get_point(x / N) for x in range(N + 1)]
        self.distances = [hypot(p1[0] - p2[0], p1[1] - p2[1])
                          for p1, p2 in zip(self.points[:-1], self.points[1:])]
        self.length = sum(self.distances)
        cum = self.cumulative = [0]
        for dist in self.distances:
            cum.append(cum[-1] + dist)

    def get_t(self, s):
        s = min(1, max(0, s))
        s *= self.length
        i = bisect_left(self.cumulative, s)
        if i == 0: 
            i = 1
        part = (s - self.cumulative[i]) / self.distances[i-1]
        return (i*1.0 + part)/self.N

    def transform(self, ip):
        """transform a point according to the spline trafo
        x is length along the spline
        y is across and in the same units as x"""
        ix, iy = ip
        t = self.get_t(ix/self.length)
        x, y, px, py = self.get_point_perp(t)
        return x + px*iy, y + py*iy

    def transform_to(self, ix, pt):
        """transform a point pt according to the spline trafo at splinepoint x"""
        t = self.get_t(ix/self.length)
        x, y, dx, dy, px, py = self.get_point_tan_perp(t)
        return x + dx*(pt[0]-ix) + px*pt[1], y + dy*(pt[0]-ix) + py*pt[1]

if __name__=="__main__":
    #s = Spline(55.000, -9.722, 60.000, -9.722, 60.000, 10.000, 65.000, 10.000)
    s = Spline(5.0, -10, 20.000, -10, 20.0, 10.000, 40.0, 10.000)
    lx, ly = 0, 0
    for i in range(500):
        t = s.get_t(i / 500)
        x, y, px, py = s.get_point_perp(t)
        if lx == 0 and ly == 0: 
            lx, ly = x, y        
        print t, x,y, px, py, hypot(x - lx, y - ly)
        lx, ly = x, y


