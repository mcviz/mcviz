from dual import DualLayout
from feynman import FeynmanLayout, PrunedHadronsLayout, CombinedLayout
from phi import PhiLayout
from new import classobj

layouts = {}
layouts["dual"] = DualLayout
layouts["feynman"] = FeynmanLayout
layouts["phi"] = PhiLayout
layouts["jetless"] = PrunedHadronsLayout
layouts["combined"] = CombinedLayout
default = "feynman"

def list_layouts():
    return sorted(layouts.keys())

def get_layout(names):
    if not names:
        layout_class = layouts[default]
    elif len(names) == 1:
        layout_class = layouts[names[0]]
    else:
        bases = tuple(layouts[x] for x in names)
        layout_class = classobj("Layout_specific", bases, {})
    return layout_class
