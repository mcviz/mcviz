from .view_object import ViewObject, Summary

class ViewVertex(ViewObject):
    @property
    def edge(self):
        return not self.incoming or not self.outgoing

    @property
    def kink(self):
        return len(self.incoming) == 1 and len(self.outgoing) == 1
        
    @property
    def initial(self):
        return not self.incoming
    
    @property    
    def final(self):
        return not self.outgoing
    
    @property
    def dangling(self):
        return self.initial and self.final

    @property
    def hadronization(self):
        """
        Any vertex which has a colored particle incoming and a non-colored 
        particle outgoing is a hadronization vertex
        """
        return (self.incoming and all(v.colored for v in self.incoming) and 
                all(not v.colored for v in self.outgoing))
                
    @property
    def connecting(self):
        """
        A connecting vertex is one which connects the two initial states 
        together.
        """        
        return (any(p.descends_one  for p in self.incoming) and 
                all(p.descends_both for p in self.outgoing))
    
    @property
    def reference(self):
        # replace - for negative vertex numbers
        return ("V%i" % self.order_number).replace("-","N")
    
    @property
    def through(self):
        """
        All particles which travel through this vertex
        """
        return self.incoming | self.outgoing

class ViewVertexSingle(ViewVertex):
    def __init__(self, graph, vertex_number):
        super(ViewVertex, self).__init__(graph)
        self.vertex_number = vertex_number
        self.graph.v_map[vertex_number] = self
        
    def __repr__(self):
        args = self.reference, len(self.incoming), len(self.outgoing)
        return '<ViewVertexSingle ref="%s" n_in="%i" n_out="%i">' % args
        
    @property
    def incoming(self):
        return self.graph.vertex_incoming_particles(self.vertex_number)
    
    @property
    def outgoing(self):
        return self.graph.vertex_outgoing_particles(self.vertex_number)

    @property
    def order_number(self):
        # replace - for negative vertex numbers
        return self.vertex_number

    @property
    def represented_numbers(self):
        return [self.vertex_number]

class ViewVertexSummary(ViewVertex, Summary):
    def __init__(self, graph, vertex_numbers):
        super(ViewVertexSummary, self).__init__(graph)
        
        self.vertex_numbers = vertex_numbers
        self._incoming = []
        self._outgoing = [] 
        self.orig_v_map, self.orig_p_map = {}, {}
        
        summarized_particle_nrs = set()
        
        for v_nr in self.vertex_numbers:
            self.orig_v_map[v_nr] = self.graph.v_map[v_nr]
            self.graph.v_map[v_nr] = self
            
            for p_nr in self.graph._incoming[v_nr]:
                if self.graph._start_vertex[p_nr] in self.vertex_numbers:
                    summarized_particle_nrs.add(p_nr)
                else:
                    self._incoming.append(p_nr)
                    
            for p_nr in self.graph._outgoing[v_nr]:
                if self.graph._end_vertex[p_nr] in self.vertex_numbers:
                    summarized_particle_nrs.add(p_nr)
                else:
                    self._outgoing.append(p_nr)
            
        for p_nr in summarized_particle_nrs:
            self.orig_p_map[p_nr] = self.graph.p_map[p_nr]
            self.graph.p_map[p_nr] = None
            
            
        self.tags.add("summary")

    def __repr__(self):
        args = (self.reference, len(self.vertex_numbers), len(self.incoming), 
                len(self.outgoing))
        return '<ViewVertexSummary ref="%s" n=%i in=%i, out=%i>' % args

    @property
    def incoming(self):
        return self.graph.numbers_to_particles(self._incoming)

    @property
    def outgoing(self):
        return self.graph.numbers_to_particles(self._outgoing)

    @property
    def order_number(self):
        #ref = "V" + "_".join("%i" % vno for vno in self.vertex_numbers)
        #return ref.replace("-","N") # replace for negative vno
        return min(self.vertex_numbers)

    @property
    def represented_numbers(self):
        return self.vertex_numbers

