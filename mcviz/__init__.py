from event_graph import EventGraph
from options import parse_options

try:
    from IPython.Shell import IPShellEmbed
    ipshell = IPShellEmbed(["-pdb"],  rc_override=dict(quiet=True))
except ImportError:
    ipshell = lambda: None
