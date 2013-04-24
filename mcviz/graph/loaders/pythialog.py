"""
This whole module is begging for a refactor, but by some miracle it works.
"""

from ... import log; log = log.getChild(__name__)

from mcviz.utils import Units
from mcviz.utils.trydecompress import try_decompress
from .. import EventParseError, Particle, Vertex

# Pythia status codes:
# (taken from http://hep.ps.uci.edu/~arajaram/worksheet.pdf)
# 11 - 19 beam particles
# 21 - 29 particles of the hardest subprocess
# 31 - 39 particles of subsequent subprocesses in multiple interactions
# 41 - 49 particles produced by initial-state-showers
# 51 - 59 particles produced by final-state-showers
# 61 - 69 particles produced by beam-remnant treatment
# 71 - 79 partons in preparation of hadronization process
# 81 - 89 primary hadrons produced by hadronization process
# 91 - 99 particles produced in decay process, or by Bose-Einstein effects


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

    # Convert mothers/daughters to objects
    for particle in particles:
        particle.daughters = set(particles[d] for d in particle.daughters if particles[d].no != 0)
        particle.mothers = set(particles[m] for m in particle.mothers if particles[m].no != 0)

    particles = [p for p in particles if p.no != 0]
    particle_dict = dict((p.no, p) for p in particles)

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
                log.error("particle %s has no mothers: %s", particle.no, particle)
        else: # initial state vertex
            vno += 1
            vertex_dict[particle] = Vertex(vno, [], [particle])

    initial_particles = []
    for particle in particles:
        if particle.final_state:
            vno += 1
            vertex_dict[particle] = Vertex(vno, [particle], [])
            if particle.color or particle.anticolor:
                log.warning("found coloured final state particle"\
                    ", this may indicate an incomplete input file")
                log.debug("final state particle: {0:s} color: {1:d} anticolor {2:d}"\
                    .format(repr(particle), particle.color, particle.anticolor))
        if particle.initial_state:
            initial_particles.append(particle)
    if len(initial_particles) != 2:
        log.warning("found {0:d} incoming particles, this may indicate an incomplete input file"\
            .format(len(initial_particles)))
        log.debug("initial particles:")
        for p in initial_particles: log.debug(repr(p))

    # Connect particles to their vertices
    for vertex in vertex_dict.itervalues():
        for particle in vertex.incoming:
            particle.vertex_out = vertex
            
        for particle in vertex.outgoing:
            particle.vertex_in = vertex

    vertex_dict = dict((v.vno,v) for v in vertex_dict.values())
    
    return vertex_dict, particle_dict, Units()

def load_event(args):
    """
    Parse a pythia event record from a log file.
    Numbers are converted to floats where possible.
    """

    filename, _, event_number = args.filename.partition(":")
    if event_number:
        try:
            event_number = int(event_number)
        except ValueError:
            log.fatal("Failed to convert filename part to an integer. Filename "
                      "should have the form 'string[:int(event number)]'")
            raise FatalError()
    else:
        event_number = 0

    with open(filename) as fd:
        lines = try_decompress(fd.read()).split("\n")
        lines = [line for line in (line.strip() for line in lines) if line]

    header = None
    if START_COMPLETE in lines:
        header = START_COMPLETE
    elif START_COMBINED in lines:
        header = START_COMBINED
    elif START_HARD in lines:
        header = START_HARD
    else:
        raise EventParseError("Failed to read pythia log file: "
                               "no complete event listing found")

    first = 0
    for i in range(event_number+1):
        first = lines.index(header, first) + 2
    last = first + lines[first:].index(END_LIST) - 1

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
