
class Summary(object):
    def undo_summary(self):
        self.graph.p_map.update(self.orig_p_map)
        self.graph.v_map.update(self.orig_v_map)

class ViewObject(object):
    """
    Inherited by ViewParticle and ViewVertex
    """
    
    def __init__(self, graph):
        self.graph = graph
        self.subscripts = []
        self.tags = set()
        self.layout_objects = []

    def tag(self, tag):
        """
        Tag a view object with some information. Can be arbitrary hashable 
        information. Usually used to test if the object should be styled or 
        layed out in a specific fashion.
        """
        self.tags.add(tag)

    @classmethod
    def tagger(self, what):
        """
        Return a function which tags particles with `what`
        """
        def tag(obj, depth):
            obj.tags.add(what)
        return tag
    
    @classmethod
    def attr_setter(self, what, f):
        def dosetattr(obj, depth):
            setattr(obj, what, f(obj))
        return dosetattr

    def __lt__(self, rhs):
        "Define p1 < p2 so that we can sort particles (by id in this case)"
        return self.order_number < rhs.order_number
