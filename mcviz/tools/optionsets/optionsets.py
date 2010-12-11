from mcviz.tools import OptionSet 
from mcviz.tools.tools import ToolSetting, tool_classes

def setdefault(tools, tool_type, default, args=None, kwargs=None):
    if len(tools[tool_type]) == 0:
        tools[tool_type].append(ToolSetting(default, args, kwargs))

class CommandLineOptionSet(OptionSet):
    _name = "cl"

    def __call__(self, tools):
        setdefault(tools, "painter", "svg")
        setdefault(tools, "layout-engine", "dot")
        setdefault(tools, "layout", "Feynman")
        defstyle = "Default"
        if not defstyle in [s.name for s in tools["style"]]:
            tools["style"].insert(0, ToolSetting(defstyle))
