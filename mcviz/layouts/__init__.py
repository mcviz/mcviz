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
    return layout_class
