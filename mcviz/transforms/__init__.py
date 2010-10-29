from tools import (contract_clusters, remove_kinks, gluballs, chainmail, 
                   contract_loops, pluck, unsummarize, shallow)
from tagging import tag


transforms = {}
transforms["Clusters"] = contract_clusters
transforms["Gluballs"] = gluballs
transforms["NoKinks"] = remove_kinks
transforms["NoLoops"] = contract_loops
transforms["NoSiblings"] = chainmail
transforms["Pluck"] = pluck
transforms["Unsummarize"] = unsummarize
tools["Shallow"] = shallow

def list_transforms():
    return sorted(transforms.keys())

def apply_transform(name, graph_view):
    transforms[name](graph_view)
