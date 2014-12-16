"""Intermediate graph representation
This is manipulated by tools and holds styling information"""

from mcviz.utils import OrderedSet

from .view_object import ViewObject
from .view_particle import ViewParticle, ViewParticleSingle, ViewParticleSummary
from .view_vertex import ViewVertex, ViewVertexSingle, ViewVertexSummary
from .walk import walk

class GraphView(object):
    """Intermediate graph representation"""
    def __init__(self, event_graph):
        self.event = event_graph
        self.units = event_graph.units

        # create central maps (define structure)
        self.v_map, self.p_map = {}, {}
        for vertex in event_graph.vertices.keys():
            ViewVertexSingle(self, vertex)
        for particle in event_graph.particles.keys():
            ViewParticleSingle(self, particle)

        self.init_cache()

    def __str__(self):
        args = (sum(isinstance(p, ViewParticleSingle)
                    for p in self.p_map.values()),
                sum(isinstance(v, ViewVertexSingle)
                    for v in self.v_map.values()),
                sum(isinstance(p, ViewParticleSummary)
                    for p in self.p_map.values()),
                sum(isinstance(v, ViewVertexSummary)
                    for v in self.v_map.values()))
        return "GraphView contains: {0:i} particles, {1:i} vertices " \
               "({2:i}, {3:i} summarized)".format(*args)

    def init_cache(self):
        """ cache input graph topology """
        self._start_vertex, self._end_vertex = {}, {}
        self._incoming, self._outgoing = {}, {}
        self._initial_particles = []
        self._particles = sorted(self.p_map.keys())
        self._vertices = sorted(self.v_map.keys())
        for nr in self._particles:
            p = self.event.particles[nr]
            if p.vertex_in:
                self._start_vertex[nr] = p.vertex_in.vno if p.vertex_in else None
            if p.vertex_out:
                self._end_vertex[nr] = p.vertex_out.vno if p.vertex_out else None

        for nr in self._vertices:
            v = self.event.vertices[nr]
            self._incoming[nr] = sorted([p.no for p in self.event.vertices[nr].incoming])
            self._outgoing[nr] = sorted([p.no for p in self.event.vertices[nr].outgoing])
            if not self._incoming[nr]:
                self._initial_particles.extend(self._outgoing[nr])

    def numbers_to_particles(self, numbers):
        return OrderedSet(p for p in (self.p_map[nr] for nr in numbers) if p)

    def numbers_to_vertices(self, numbers):
        return OrderedSet(v for v in (self.v_map[nr] for nr in numbers) if v)

    def particle_start_vertex(self, particle_number):
        start_vertex = self._start_vertex[particle_number]
        return None if start_vertex is None else self.v_map[start_vertex]

    def particle_end_vertex(self, particle_number):
        end_vertex = self._end_vertex[particle_number]
        return None if end_vertex is None else self.v_map[end_vertex]

    def vertex_incoming_particles(self, vertex_number):
        return self.numbers_to_particles(self._incoming[vertex_number])

    def vertex_outgoing_particles(self, vertex_number):
        return self.numbers_to_particles(self._outgoing[vertex_number])

    @property
    def vertices(self):
        return self.numbers_to_vertices(self._vertices)

    @property
    def particles(self):
        return self.numbers_to_particles(self._particles)

    @property
    def initial_particles(self):
        return self.numbers_to_particles(self._initial_particles)

    def summarize_particles(self, particles):
        """Replace list of Particles with a ParticleSummary"""
        elementary_particles = []
        for particle in particles:
            if isinstance(particle, ViewParticleSummary):
                elementary_particles.extend(particle.particle_numbers)
            else:
                elementary_particles.append(particle.particle_number)
        return ViewParticleSummary(self, elementary_particles)

    def summarize_vertices(self, vertices):
        """Replace list of Vertices with a VertexSummary"""
        elementary_vertices = []
        for vertex in vertices:
            if isinstance(vertex, ViewVertexSummary):
                elementary_vertices.extend(vertex.vertex_numbers)
            else:
                elementary_vertices.append(vertex.vertex_number)
        return ViewVertexSummary(self, elementary_vertices)

    def drop(self, obj):
        """
        Remove a view{particle,vertex} from the graph.
        If calling this repeatedly, it is acceptable to continue looping even
        if this means also calling this function on implicitly removed objects.
        """
        if isinstance(obj, ViewParticle):
            for pn in obj.represented_numbers:
                self.p_map[pn] = None

            if obj.start_vertex and obj.start_vertex.dangling:
                self.drop(obj.start_vertex)
            if obj.end_vertex and obj.end_vertex.dangling:
                self.drop(obj.end_vertex)

        elif isinstance(obj, ViewVertex):
            for vn in obj.represented_numbers:
                self.v_map[vn] = None

            for particle in obj.through:
                self.drop(particle)

    def walk(self, obj,
             particle_action=lambda p, d: None,
             vertex_action=lambda p, d: None,
             loop_action=lambda p, d: None, ascend=False):
        """Visit all particles and vertices in the graph"""
        def walk_action(obj, depth):
            if isinstance(obj, ViewParticle):
                next_vertices = particle_action(obj, depth) \
                                if particle_action else None
                if next_vertices is None:
                    next_vertices = (obj.start_vertex,) \
                                    if ascend else (obj.end_vertex,)
                return next_vertices
            elif isinstance(obj, ViewVertex):
                next_particles = vertex_action(obj, depth) \
                                 if vertex_action else None
                if next_particles is None:
                    next_particles = obj.incoming if ascend else obj.outgoing
                return next_particles
            else:
                raise NotImplementedError("Unknown object in graph: {0:s}" \
                                          .format(obj.__class__.__name__))
        return walk(obj, walk_action, loop_action)

    def tag(self, obj, tag, particles=False, vertices=False, ascend=False):
        particle_action = ViewObject.tagger(tag) if particles else None
        vertex_action = ViewObject.tagger(tag) if vertices else None
        return self.walk(obj, particle_action, vertex_action, ascend=ascend)

    def set(self, obj, key, f, particles=False, vertices=False, ascend=False):
        particle_action = ViewObject.attr_setter(key, f) if particles else None
        vertex_action = ViewObject.attr_setter(key, f) if vertices else None
        return self.walk(obj, particle_action, vertex_action, ascend=ascend)
