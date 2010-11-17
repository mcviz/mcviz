from mcviz.tools import OptionSet 
from mcviz.tools.tools import tool_classes

class CommandLineOptionSet(OptionSet):
    _name = "cl"

    def __call__(self, tools):
        if len(tools["painter"]) == 0:
            tools["painter"].append((tool_classes["painter"]["svg"], ()))
        if len(tools["layout-engine"]) == 0:
            tools["layout-engine"].append((tool_classes["layout-engine"]["dot"], ()))
