from __future__ import division

from math import sqrt, hypot
from bisect import bisect_left

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
        assert 0 <= s <= 1
        s *= self.length
        i = bisect_left(self.cumulative, s)
        if i == 0: 
            i = 1
        part = (s - self.cumulative[i]) / self.distances[i - 1]
        return (i + part) / self.N

    def transform(self, ix, iy):
        """transform a point according to the spline trafo
        x is in [0,1] and is along the spline
        y is across and in the same units as x"""
        t = self.get_t(ix)
        x, y, px, py = self.get_point_perp(t)
        #return x + px*iy/self.length, y + py*iy/self.length
        print x, px, py, iy
        return x + px*iy*self.length, y + py*iy*self.length


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


