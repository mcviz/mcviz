from ... import log; log = log.getChild(__name__)


from collections import namedtuple
from itertools import izip
import re

from mcviz import FatalError
from mcviz.utils import Units
from mcviz.utils.trydecompress import try_decompress
from .. import EventParseError, Particle, Vertex


HEPMC_TEXT = re.compile("""(?:
HepMC::Version (?P<version>.*?))?\s*
HepMC::IO_(?:GenEvent|Ascii)-START_EVENT_LISTING
(?P<events>.*)
HepMC::IO_(?:GenEvent|Ascii)-END_EVENT_LISTING
""", re.M | re.DOTALL)

def event_generator(lines):
    """
    Yield one event at a time from a HepMC file
    """
    event = []
    for line in (l.split() for l in lines):
        if line[0] == "E" and event:
            yield event
            event = []
        event.append(line)
    yield event

HEvent = namedtuple("HEvent", 
    "id interaction_count ev_scale alpha_qcd alpha_qed signal_proc_id "
    "signal_proc_vertex_barcode num_vertices beam_p1_barcode beam_p2_barcode "
    "random_states weights")
HPDF = namedtuple("HPDF",
    "id1 id2 x1 x2 scalePDF pdf1 pdf2 pdf_id1 pdf_id2")
HVertex = namedtuple("HVertex",
    "barcode id x y z ctau num_orphan_incoming num_outgoing weights")
HParticle = namedtuple("HParticle",
    "barcode pdgid px py pz energy mass status pol_theta pol_phi "
    "vertex_out_barcode flow")

def items(length, record):
    """
    Parse a `record` with a given `length`. Returns what was parsed and what
    remains to be parsed
    """
    return record[:length], record[length:]

def variable_item(record):
    """
    Parses a variable-length `record` where the first item
    """
    if not record: return [], []
    # Ugh, some hepmc writers give us floats for this field!?
    n, record = int(float(record[0])), record[1:]
    return items(n, record)

def make_record(record):
    """
    Given a HepMC record, return a named tuple containing the same information
    """
    orig_record = record[:]
    type_, record = record[0], record[1:]
    
    if type_ == "E":
        varparts_idx = HEvent._fields.index("random_states")
        first_part,    record = items(varparts_idx, record)
        random_states, record = variable_item(record)
        if record:
            weights,   record = variable_item(record)
        else:
            weights = None
        assert not record, "Unexpected additional data on event"
        
        return HEvent._make(first_part + [random_states, weights])
        
    elif type_ == "V":
        varparts_idx = HVertex._fields.index("weights")
        first_part, record = items(varparts_idx, record)
        weights,    record = variable_item(record)
        assert not record, "Unexpected additional data on vertex"
        
        return HVertex._make(first_part + [weights])
    
    elif type_ == "P":
        if len(record) in [11,13,15]:
            # Strange dialect which misses the "mass" column? Insert 0 mass.
            midx = HParticle._fields.index("mass")
            record = record[:midx] + [0] + record[midx:]
        varparts_idx = HParticle._fields.index("flow")
        first_part, record = items(varparts_idx, record)
        flow = {}
        if record:
            # try parsing flow information
            (n_flow,), record = items(1, record)
            flow,      record = items(int(n_flow)*2, record)
            flow = map(int, flow)
            flow = dict(zip(flow[::2], flow[1::2]))
        assert not record, "Unexpected additional data on vertex"

        if not first_part[1] == '0':
            return HParticle._make(first_part + [flow])
        
    elif type_ == "U":
        log.verbose("event reports units are {0} and {1}".format(*record[:2]))
        u = Units(record[0] + " " + record[1])
        return u

    elif type_ == "F":
        return HPDF._make(record)

def load_single_event(ev, args):
    """
    Given one event in HepMC's text format, return a list of mcviz's `Particle`s
    and `Vertex`es.
    """
    current_vertex = event = None
    outgoing_particles = []
    
    vertices, particles = {}, {}
    vertex_incoming = {} # { vertex_barcode : set(particles) }
    
    initial_particles = []

    if args.units:
        units = Units(args.units)
    else:
        units = None
    
    orphans = 0

    pdfinfo = None

    # Loop over event records.
    # Read a vertex, then read N particles. When we get to the next vertex, 
    # associate the N particles with the previous vertexEventParseError
    for record in map(make_record, ev):
        if isinstance(record, Units):
            if units is None:
                units = record
            else:
                log.verbose("previous units declaration overriding input's unit record")
        elif isinstance(record, HEvent):
            assert event is None, "Duplicate event records in event"
            event = record
            log.debug("Event record: {0} ".format(event))
        
        elif event is None:
            raise RuntimeError("Event record should come first. Corrupted "
                                  "input hepmc?")
        
        elif isinstance(record, HVertex):
            if current_vertex:
                # If there is a vertex outstanding, make it and record
                # the particles outgoing from it.
                vertex = Vertex.from_hepmc(current_vertex, outgoing_particles)
                vertices[vertex.vno] = vertex
                outgoing_particles = []
            current_vertex = record
            orphans = int(current_vertex.num_orphan_incoming)
            
        elif isinstance(record, HParticle):
            particle = Particle.from_hepmc(record)
            particles[particle.no] = particle
            
            if not orphans:
                outgoing_particles.append(particle)
            else:
                orphans -= 1
                initial_particles.append(particle)
            
            vertex_incoming.setdefault(int(record.vertex_out_barcode), set()).add(particle)

        elif isinstance(record, HPDF):
            pdfinfo = record

    # Use default units if they are not specified
    if units is None:
        units = Units()
        
    vertex = Vertex.from_hepmc(current_vertex, outgoing_particles)
    vertices[vertex.vno] = vertex

    vno = min(vertices.keys()) - 1
        
    for vertex_barcode in sorted(vertex_incoming.keys()):
        incoming_particles = vertex_incoming[vertex_barcode]
        if not vertex_barcode:
            # Final state particle
            # Horrendous HACK, but I want it to work _now_
            for p in sorted(incoming_particles):
                vertices[vno] = Vertex(vno, [p])
                vno -= 1 
        else:
            v = vertices[vertex_barcode]
            v.incoming = incoming_particles

    # Check theres only 2 incoming vertices
    if len(initial_particles) != 2:
        log.warning("found {0:d} incoming particles, this may indicate an incomplete input file"\
            .format(len(initial_particles)))
        log.debug("initial particles:")
        for p in initial_particles: log.debug(repr(p))

    # Construct "initial" vertices
    for initial_particle in initial_particles:
        if str(initial_particle.no) in (event.beam_p1_barcode, event.beam_p2_barcode):
            pass
        units.initial_check(initial_particle)
        vertices[vno] = Vertex(vno, outgoing=[initial_particle])
        vno -= 1
    
    for vno, vertex in vertices.iteritems():
        # set mothers and daughters
        for p_in in vertex.incoming:
            p_in.vertex_out = vertex
            p_in.daughters = vertex.outgoing
        for p_out in vertex.outgoing:
            p_out.vertex_in = vertex
            p_out.mothers = vertex.incoming
            
    for i in particles:
        particle = particles[i]
        if particle.final_state and not particle.daughters:
            if particle.color or particle.anticolor:
                log.warning("found coloured final state particle"\
                    ", this may indicate an incomplete input file")
                log.debug("final state particle: {0:s} color: {1:d} anticolor {2:d}"\
                    .format(repr(particle), particle.color, particle.anticolor))

    # Probably not the greatest way to do this, but oh well...
    vertices = dict((vno, vertex) for vno, vertex in vertices.iteritems()
                                  if vertex.outgoing or vertex.incoming)

    return vertices, particles, units, pdfinfo

def load_event(args):
    """
    Load one event from a HepMC file
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
        match = HEPMC_TEXT.search(data)

    if not match:
        raise EventParseError("Not obviously hepmc data.")
        
    result = match.groupdict()
    #version = tuple(map(int, result.get("version", "0").split(".")))
    #if version != (2, 06, 01):
        #log.warning("Warning: Only tested with hepmc 2.06.01")
    lines = result["events"].split("\n")
    
    for i, event in izip(xrange(event_number+1), event_generator(lines)):
        # Load only one event
        pass
    return load_single_event(event, args)

if __name__ == "__main__":
    from IPython.Shell import IPShellEmbed; ip = IPShellEmbed(["-pdb"])
    from sys import argv
    test(argv[1])
