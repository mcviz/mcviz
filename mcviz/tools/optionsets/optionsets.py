from mcviz.tools import OptionSet 
from mcviz.tools.tools import tool_classes

def setdefault(tools, tool_type, default, args):
    if len(tools[tool_type]) == 0:
        tools[tool_type].append((tool_classes[tool_type][default], args))

class CommandLineOptionSet(OptionSet):
    _name = "cl"

    def __call__(self, tools):
        setdefault(tools, "painter", "svg", ())
        setdefault(tools, "layout-engine", "dot", ())
        setdefault(tools, "layout", "Feynman", ())
        defstyle = tool_classes["style"]["Default"]
        if not defstyle in dict(tools["style"]):
            tools["style"].insert(0, (defstyle, ()))
