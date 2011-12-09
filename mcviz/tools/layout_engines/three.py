"""
Layout engines designed for three.js
"""

from .graphviz import FDPEngine
from mcviz.utils.graphviz import REF_PREFIX

class SFDPThreeDEngine(FDPEngine):
    _name = "sfdp3"
    
    def get_graphviz_options(self):
        """
        Return (binary, option list)
        """
        options = self.options["extra"].split()
        assert not any(options.startswith("-T") for opt in options)
        options.append("-Tdot")
        binary = "sfdp"
        return binary, options

    def dot(self, layout):
        extra = [
            "dimen = 3;"
        ]
        return super(SFDPThreeDEngine, self).dot(layout, extra)
    
    def update(self, layout, data):
        
        import re
        regex = r'^\s+{0}([A-Z0-9_]+)\s+\[.*?pos="(?P<pos>[\-0-9\.,]+)".*?\];\s*$'.format(REF_PREFIX)
        nodeexpr = re.compile(regex, re.M)
        regex = r'^\s+{0}([A-Z0-9_]+)\s+->\s+{0}([A-Z0-9_]+).*{0}([^\s,]+).*$'.format(REF_PREFIX)
        edgeexpr = re.compile(regex, re.M)
        
        node_positions = dict((ref, map(float, coord.split(",")))
                              for ref, coord in nodeexpr.findall(data))
                              
        edges = edgeexpr.findall(data)
        
        for r1, r2, r3 in edges:
            if r1 not in node_positions:
                log.warning("Missing node: {0}".format(r1))
                        
        lines = dict((r3, (node_positions[r1], node_positions[r2]))
                     for r1, r2, r3 in edges 
                     if r1 in node_positions and r2 in node_positions)
        
        layout.is3D = True
                
        for edge in layout.edges:
            edge.spline = lines.get(edge.reference, None)
            

