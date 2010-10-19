from dual import DualLayout
from feynman import FeynmanLayout, FixedHadronsLayout, CombinedLayout
from phi import PhiLayout
from new import classobj

layouts = {}
layouts["dual"] = DualLayout
layouts["feynman"] = FeynmanLayout
layouts["phi"] = PhiLayout
layouts["fixhad"] = FixedHadronsLayout
layouts["combined"] = CombinedLayout
default = "feynman"

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
        bases = tuple(layouts[x] for x in names)
        layout_class = classobj("Layout_specific", bases, {})
    return layout_class
