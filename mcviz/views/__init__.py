from views import GraphView
from tools import contract, remove_kinks
from tagging import tag

view_tools = {}
view_tools["kinks"] = remove_kinks

def list_view_tools():
    return sorted(view_tools.keys())

def apply_view_tool(name, graph_view):
    view_tools[name](graph_view)
