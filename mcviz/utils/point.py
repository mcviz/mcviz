from math import hypot

class Point2D(object):
    """
    Basic point class
    """
    __slots__ = "x", "y"
    
    def __init__(self, x=0.0, y=0.0):
        self.x, self.y = x, y
 
    def dist(self, p):
        return hypot(self.x - p.x, self.y - p.y)

    def tuple(self):
        return self.x, self.y

    def len(self):
        return hypot(self.x, self.y)

    def __add__(self, p):
        return Point2D(self.x+p.x, self.y+p.y)

    def __sub__(self, p):
        return Point2D(self.x-p.x, self.y-p.y)

    def __iadd__(self, p):
        self.x += p.x
        self.y += p.y
        return self

    def __isub__(self, p):
        self.x -= p.x
        self.y -= p.y
        return self

    def __mul__(self, f):
        return Point2D(self.x*f, self.y*f)

    def __div__(self, f):
        return Point2D(self.x/f, self.y/f)

    def __repr__(self):
        return 'Point(%f, %f)' % (self.x, self.y)
