
class LayoutEdge(object):
    def __init__(self, spline, label = None):
        self.spline = spline
        self.label = label

class LayoutVertex(object):
    def __init__(self, x = None, y = None, r = None):
        self.x = x
        self.y = y
        self.r = r
