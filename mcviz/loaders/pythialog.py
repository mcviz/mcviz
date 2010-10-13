from logging import getLogger; log = getLogger("pythialog_parser")

from mcviz import MCVizParseError
from ..particle import Particle
from ..vertex import Vertex

START_COMPLETE = ("--------  "
    "PYTHIA Event Listing  (complete event)  ---------"
    "------------------------------------------------------------------------")
START_COMBINED = ("--------  "
    "PYTHIA Event Listing  (combination of several events)"
    "  ------------------------------------------------------------------")
START_HARD = ("--------  PYTHIA Event Listing  (hard process)  -------------"
    "----------------------------------------------------------------------")
END_LIST = ("--------  End PYTHIA Event Listing  -----------------------------"
    "------------------------------------------------------------------")
    
def make_pythia_graph(records):
    # Make particle objects and {no:Particle} dictionary
    particles = [Particle.from_pythia(p) for p in records]
    particle_dict = dict((p.no, p) for p in particles)
    
    # Convert mothers/daughters to objects
    for particle in particles:
        particle.daughters = set(particles[d] for d in particle.daughters)
        particle.mothers = set(particles[m] for m in particle.mothers)

    # Populate mothers and daughters for particles
    for particle in particles:
        for mother in particle.mothers:
            mother.daughters.add(particle)
        for daughter in particle.daughters:
            daughter.mothers.add(particle)

    # Remove self-connections
    for particle in particles:
        particle.mothers.discard(particle)
        particle.daughters.discard(particle)

    # TODO: Johannes: Please explain!
    vertex_dict = dict()
    vno = 0
    for particle in particles:
        found_v = None
        if frozenset(particle.mothers) in vertex_dict:
            found_v = vertex_dict[frozenset(particle.mothers)]
        else:
            for v in vertex_dict.itervalues():
                for m in particle.mothers:
                    if m in v.incoming:
                        found_v = v
                        #print >> stderr, map(lambda x: x.no, v.incoming), map(lambda x: x.no, particle.mothers)
                        break
                if found_v:
                    break

        if found_v:
            found_v.outgoing.add(particle)
            for new_mother in found_v.incoming:
                particle.mothers.add(new_mother)
                new_mother.daughters.add(particle)
        elif particle.mothers:
            vno += 1
            vertex_dict[frozenset(particle.mothers)] = Vertex(vno, particle.mothers, [particle])
            if len(particle.mothers) == 0:
                # this is the system vertex
                log.error("No mothers: %s, %s", particle.no, particle)
        else: # initial state vertex
            vno += 1
            vertex_dict[particle] = Vertex(vno, [], [particle])
            
    for particle in particles:
        if particle.final_state:
            vno += 1
            vertex_dict[particle] = Vertex(vno, [particle], [])
        if particle.initial_state:
            log.debug("INITIAL PARTICLE: %s, %s", particle.no, particle.name)
            
    # Connect particles to their vertices
    for vertex in vertex_dict.itervalues():
        for particle in vertex.incoming:
            particle.vertex_out = vertex
            
        for particle in vertex.outgoing:
            particle.vertex_in = vertex

    vertex_dict = dict((v.vno,v) for v in vertex_dict.values())
    
    # Remove system vertex
    del particle_dict[0]
    
    return vertex_dict, particle_dict
        
def load_event(filename):
    """
    Parse a pythia event record from a log file.
    Numbers are converted to floats where possible.
    """

    with open(filename) as fd:
        lines = [line for line in (line.strip() for line in fd) if line]

    if START_COMPLETE in lines:
        first = lines.index(START_COMPLETE) + 2
        last = first + lines[first:].index(END_LIST) - 1
    elif START_COMBINED in lines:
        first = lines.index(START_COMBINED) + 2
        last = first + lines[first:].index(END_LIST) - 1
    elif START_HARD in lines:
        first = lines.index(START_HARD) + 2
        last = first + lines[first:].index(END_LIST) - 1
    else:
        raise MCVizParseError("Failed to read pythia log file: "
                               "no complete event listing found")

    def maybe_num(s):
        try: return float(s)
        except ValueError:
            return s

    records = [map(maybe_num, line.split()) for line in lines[first:last]]
    # insert blank name if name is not specified
    for particle in records:
        if len(particle) == 14: 
            particle.insert(2,"")
            
    return make_pythia_graph(records)
