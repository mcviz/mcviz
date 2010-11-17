from collections import namedtuple
import re

from logging import getLogger; log = getLogger("mcviz.loaders.hepmc")

from mcviz import MCVizParseError
from ..particle import Particle
from ..vertex import Vertex


LHE_TEXT = re.compile("""
<LesHouchesEvents version="(?P<version>.*?)">
\s*<init>\s*
(?P<init>.*?)
\s*</init>\s*
(?P<events>.*)
</LesHouchesEvents>
""", re.M | re.DOTALL)

# INTEGER NUP,IDPRUP,IDUP,ISTUP,MOTHUP,ICOLUP
# DOUBLE PRECISION XWGTUP,SCALUP,AQEDUP,AQCDUP,PUP,VTIMUP,&SPINUP
# COMMON/HEPEUP/NUP,IDPRUP,XWGTUP,SCALUP,AQEDUP,AQCDUP,
# &IDUP(MAXNUP),ISTUP(MAXNUP),MOTHUP(2,MAXNUP),
# &ICOLUP(2,MAXNUP),PUP(5,MAXNUP),VTIMUP(MAXNUP),
# &SPINUP(MAXNUP

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

LHEvent = namedtuple("LHEvent", 
    "id interaction_count ev_scale alpha_qcd alpha_qed signal_proc_id "
    "signal_proc_vertex_barcode num_vertices beam_p1_barcode beam_p2_barcode "
    "random_states weights")
LHVertex = namedtuple("LHVertex", 
    "barcode id x y z ctau num_orphan_incoming num_outgoing weights")
LHParticle = namedtuple("LHParticle",
    "barcode pdgid px py pz energy mass status pol_theta pol_phi "
    "vertex_out_barcode flow") 
    
def load_first_event(filename):
    """
    Load one event from a HepMC file
    """
    with open(filename) as fd:
        match = HEPMC_TEXT.search(fd.read())
