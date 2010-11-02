from new import classobj

from dual import DualLayout, DualDecongestedHad
from feynman import FeynmanLayout, InlineLabelsLayout
from extra import FixedHadronsLayout, FixedInitialLayout, HardProcessSubgraph
from phi import PhiLayout


layouts = {}
layouts["Dual"] = DualLayout
layouts["DualDecongestedHad"] = DualDecongestedHad
layouts["Feynman"] = FeynmanLayout
layouts["Phi"] = PhiLayout
layouts["FixHad"] = FixedHadronsLayout
layouts["FixIni"] = FixedInitialLayout
layouts["InlineLabels"] = InlineLabelsLayout
layouts["HardProcessSubgraph"] = HardProcessSubgraph

default = "InlineLabels"

# If the constructed layout doesn't inherit from one of these, we have a problem
fundamental_layouts = DualLayout, FeynmanLayout

class LayoutCombinationError(RuntimeError): pass
LAYOUT_ERRORMSG = ("You tried to construct a layout without including one of "
                   "the base layouts. Please specify a layout which includes "
                   "the bases (Feynman or Dual)")

def list_layouts():
    return sorted(layouts.keys())

def get_layout(names):
    """
    Compose a new layout from other layouts. This is tricky because we 
    dynamically create a new layout class out of objects passed on the 
    commandline. This means that the commandline must follow Python's 
    inheritance rules. Not ideal, but convenient for the moment.
    """
    if not names:
        layout_class = layouts[default]
    elif len(names) == 1:
        layout_class = layouts[names[0]]
    else:
        bases = tuple(reversed([layouts[x] for x in names]))
        layout_class = classobj("Layout_specific", bases, {})
        
    if not issubclass(layout_class, fundamental_layouts):
        # We didn't include a fundamental layout!
        raise LayoutCombinationError(LAYOUT_ERRORMSG)
        
    return layout_class
