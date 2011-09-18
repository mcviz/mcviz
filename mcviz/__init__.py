import sys

if not sys.version_info >= (2, 6):
    raise ImportError("mcviz is only compatible with python >= 2.6")
    
from mcviz.exception import FatalError, init_mcviz_exception_hook
init_mcviz_exception_hook()

from .logger import log

from graph import EventGraph, EventParseError
from tools import Tool
from workspace import GraphWorkspace
from options import parse_options
from main import main

