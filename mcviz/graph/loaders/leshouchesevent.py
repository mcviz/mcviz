from collections import namedtuple
from itertools import izip
import re

from ... import log; log = log.getChild(__name__)

from mcviz import FatalError
from mcviz.utils import Units
from mcviz.utils.trydecompress import try_decompress
from .. import EventParseError, Particle, Vertex


LHE_TEXT = re.compile("""
*<LesHouchesEvents version="(?P<version>.*?)">
.*\s*<init>\s*
(?P<init>.*?)
\s*</init>\s*
(?P<events>.*)
</LesHouchesEvents>
*""", re.M | re.DOTALL)

LHE_EVENT = re.compile("""
*\s*<event>\s*
(?P<event>.*?)
\s*</event>\s*
*""", re.M | re.DOTALL)

# See the following for info on the LHE format:
# http://arxiv.org/abs/hep-ph/0609017
# http://arxiv.org/abs/hep-ph/0109068

def event_generator(lines):
    """
    Yield one event at a time from a LHE file
    """
    eventiter = LHE_EVENT.finditer(lines)
    
    for match in eventiter:
      result = match.groupdict()
      yield result['event']

def make_lhe_graph(lines, init, args):
    """
    Return the particles and vertices in the event
    """
    # First is an event details line with the number of particle as NUP
    LEVENT = namedtuple('LEVENT', 'NUP, IDPRUP, XWGTUP, SCALUP, AQEDUP, AQCDUP')
    line = lines.pop(0).split()
    line = [int(i) for i in line[:2] ] + [float(i) for i in line[2:6] ]
    event = LEVENT._make(line)

    # Now add the initial beam particles to this event
    lines.insert(0, "%s -1 0 0 0 0 0 0 %s %s 0 0 9" %(init.IDBMUP1, init.EBMUP1, init.EBMUP1) )
    lines.insert(1, "%s -1 0 0 0 0 0 0 %s %s 0 0 9" %(init.IDBMUP2, init.EBMUP2, init.EBMUP2) )

    # Particles have the format:
    LPARTICLE = namedtuple('LPARTICLE', 'IDUP, ISTUP, MOTHUP1, MOTHUP2, ICOLUP1, ICOLUP2, PUP1, PUP2, PUP3, PUP4, PUP5, VTIMUP, SPINUP')
    particles = []
    for I, line in izip(range(1, event.NUP+3), lines):
      line = line.split()
      if len(line[3]) > 1 and line[3][0] == '0':
          line = [int(i) for i in line[:3] ] + [0] + [line[3][1:] ] +[int(i) for i in line[4:5] ] + [float(i) for i in line[5:12] ]
      else:
          line = [int(i) for i in line[:6] ] + [float(i) for i in line[6:13] ]

      # Correct indices for the initial beam particles
      if line[2]: line[2] += 2
      if line[3]: line[3] += 2
      # Connect the first daughters to the inital particles
      if I == 3: line[2] = 1
      elif I == 4: line[2] = 2

      part = LPARTICLE._make(line)
      particles.append(Particle.from_lhe(I, part) )

    # Convert mothers/daughters to objects
    for particle in particles:
        particle.daughters = set(particles[d-1] for d in particle.daughters
            if d != 0 and d <= len(particles) )
        particle.mothers = set(particles[m-1] for m in particle.mothers
            if m != 0 and m <= len(particles) )

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

    for particle in particles:
        if particle.final_state and particle.initial_state: #len(particle.mothers) == 0:
            if particle.vertex_in: del vertex_dict[particle.vertex_in.vno]
            del vertex_dict[particle.vertex_out.vno]
            del particle_dict[particle.no]
#particles.remove(particle)
            continue

    units = Units(args.units)

    return vertex_dict, particle_dict, units
    
def load_event(args):
    """
    Load one event from a LHE file
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
        data = try_decompress(fd.read())
        match = LHE_TEXT.search(data)
    
    if not match:
        raise EventParseError("Failed to parse LHE data")

    result = match.groupdict()
    
    # Init block has the following format:
    LINIT = namedtuple('LINIT', 'IDBMUP1, IDBMUP2, EBMUP1, EBMUP2, PDFGUP1, PDFGUP2, PDFSUP1, PDFSUP2, IDWTUP, NPRUP')
    init = result['init'].splitlines()[0].split()
    init = [int(i) for i in init[:2] ] + [float(i) for i in init[2:4] ] + [int(i) for i in init[4:10] ] 
    init = LINIT._make(init)
    # Followed by NPRUP lines of processes
    log.verbose("LHE init block:")
    for line in result['init'].splitlines():
        log.verbose(line.strip())

    for i, event in izip(xrange(event_number+1), event_generator(result['events']) ):
        # Load only one event
        pass

    return make_lhe_graph(event.splitlines(), init, args)
    
if __name__ == "__main__":
    from IPython.Shell import IPShellEmbed; ip = IPShellEmbed(["-pdb"])
    from sys import argv
    test(argv[1])
