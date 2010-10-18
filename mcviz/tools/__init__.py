from tools import contract_jets, remove_kinks, gluballs, chainmail, contract_loops, pluck, unsummarize
from tagging import tag

tools = {}
tools["kinks"] = remove_kinks
tools["gluballs"] = gluballs
tools["chainmail"] = chainmail
tools["jets"] = contract_jets
tools["loops"] = contract_loops
tools["pluck"] = pluck
tools["unsummarize"] = unsummarize

def list_tools():
    return sorted(tools.keys())

def apply_tool(name, graph_view):
    tools[name](graph_view)
