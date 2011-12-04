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
        return not self.incoming and len(self.outgoing) == 1
    
    @property    
    def final(self):
        return not self.outgoing and len(self.incoming) == 1

    @property    
    def vacuum(self):
        return (not self.incoming and not self.initial) or (not self.outgoing and not self.final)
    
    @property
    def dangling(self):
        return self.initial and self.final

    @property
    def hadronization(self):
        """
        Hadronization is defined as a vertex which has at least one colored and
        one anti-colored object coming in, and no colored outgoing particles.
        """
                # We must have ay least one incoming
                # colored and anticolored particle
        return (any(p.color and not p.anticolor for p in self.incoming) and
                any(p.anticolor and not p.color for p in self.incoming) and
                # Everything outgoing must be uncoloured
                all(not p.color and not p.anticolor for p in self.outgoing) and
                # No bosons
                not any(p.boson for p in self.outgoing))
                
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
    def event_vertex(self):
        return self.graph.event.vertices[self.vertex_number]
        
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

    @property
    def n_vertices(self):
        return len(self.vertex_numbers)

    @property
    def n_represented(self):
        return self.n_vertices
