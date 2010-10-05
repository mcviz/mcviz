from dual import DualLayout
from feynman import FeynmanLayout
from phi import PhiLayout

layouts = {}
layouts["dual"] = DualLayout
layouts["feynman"] = FeynmanLayout
layouts["phi"] = PhiLayout
default = "feynman"

def list_layouts():
    return sorted(layouts.keys())

def get_layout(name):
    if name is None:
        return layouts[default]
    return layouts[name]
