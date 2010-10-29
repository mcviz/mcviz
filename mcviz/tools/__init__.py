from tools import contract_clusters, remove_kinks, gluballs, chainmail, contract_loops, pluck, unsummarize
from tagging import tag

tools = {}
tools["Clusters"] = contract_clusters
tools["Gluballs"] = gluballs
tools["NoKinks"] = remove_kinks
tools["NoLoops"] = contract_loops
tools["NoSiblings"] = chainmail
tools["Pluck"] = pluck
tools["Unsummarize"] = unsummarize

def list_tools():
    return sorted(tools.keys())

def apply_tool(name, graph_view):
    tools[name](graph_view)
