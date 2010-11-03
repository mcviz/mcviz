from logging import getLogger; log = getLogger("mcviz.transforms")

from ..utils import timer
from transforms import (contract_clusters, remove_kinks, gluballs, chainmail, 
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
transforms["Shallow"] = shallow

def list_transforms():
    return sorted(transforms.keys())

def apply_transform(name, graph_view):
    transforms[name](graph_view)
    
def apply_transforms(options, graph_view):
    log.debug("Graph state (before transforms): %s", graph_view)
    
    with timer("apply all transforms", log.VERBOSE):
        for transform in options.transform:
            log.verbose('applying transform: %s' % transform)
            with timer('apply %s' % transform):
                apply_transform(transform, graph_view)

        # Apply all Taggers on the graph
        log.debug('tagging graph')
        with timer('tag the graph'):
            tag(graph_view)
    
    log.debug("Graph state (after transforms): %s", graph_view)
