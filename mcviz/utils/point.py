from math import hypot

class Point2D(object):
    """
    Basic point class
    """
    __slots__ = "x", "y"
    
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y
 
    def dist(self, p):
        return hypot(self.x - p.x, self.y - p.y)

    def __add__(self, p):
        return Point2D(self.x+p.x, self.y+p.y)
 
    def __repr__(self):
        return 'Point(%d, %d)' % (self.x, self.y)
