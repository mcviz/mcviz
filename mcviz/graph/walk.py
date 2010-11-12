from itertools import takewhile

from mcviz.utils import OrderedSet


def walk(node,
         walk_action=lambda p, d: None, loop_action=lambda p, d: None, 
         completed_walks=None, uncompleted_walks=None, depth=0):
    """
    Walk the particle graph.
    
    Shamelessly stolen algorithm from:
    http://www.electricmonk.nl/log/2008/08/07/dependency-resolving-algorithm
    
    Enhanced for our purposes to provide loop marking.
    """
    if completed_walks is None: completed_walks = OrderedSet()
    if uncompleted_walks is None: uncompleted_walks = OrderedSet()
    
    next_nodes = walk_action(node, depth)

    uncompleted_walks.add(node)
    
    for next_node in next_nodes:
        if next_node not in completed_walks:
            # we haven't yet seen this particle, walk it.
            if next_node in uncompleted_walks:
                # We have a loop, because we have seen it but not walked it.
                # All particles from the end up to this daughter are 
                # participating in the loop
                if not loop_action:
                    continue
                 
                lps = takewhile(lambda x: x != next_node, 
                                reversed(uncompleted_walks))
                                 
                looping_nodes = list(lps) + [next_node]
                
                # -1 because a single particle loop should be at the same
                # depth as the self.walk() call.
                n_lp = len(looping_nodes) - 1
                for i, looping_node in enumerate(looping_nodes):
                    loop_action(looping_node, depth - n_lp + i + 1)
                     
            else:
                # Not circular, so walk it.
                walk(next_node, walk_action, loop_action,
                          completed_walks, uncompleted_walks, depth+1)
    
    completed_walks.add(node)
    uncompleted_walks.discard(node)
    return completed_walks

