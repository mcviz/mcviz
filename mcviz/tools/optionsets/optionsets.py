from .. import log; log = log.getChild(__name__)

from mcviz.tools import OptionSet, Arg
from mcviz.tools.tools import ToolSetting, tool_classes, tool_types

def setdefault(tools, tool_type, default, *args, **kwargs):
    """
    If `tool_type` is not specified on the command-line, use `default`.
    """
    if len(tools[tool_type]) == 0:
        tools[tool_type].append(ToolSetting(default, *args, **kwargs))

class CommandLineOptionSet(OptionSet):
    _name = "cl"

    def __call__(self, tools):
        for tool_type in sorted(tool_types.keys()):
            tools.setdefault(tool_type, [])
        setdefault(tools, "painter", "navisvg")
        setdefault(tools, "layout-engine", "dot")
        setdefault(tools, "layout", "Feynman")
        defstyle = "Default"
        if not defstyle in [s.name for s in tools["style"]]:
            tools["style"].insert(0, ToolSetting(defstyle))
            
class DemoOptionSet(CommandLineOptionSet):
    _name = "demo"
    _args = [Arg("layout", str, "choose a layout to demo: Feynman, Dual or InlineLabels", 
                 choices=("Feynman", "Dual", "InlineLabels"), default="Dual")]
    def __call__(self, tools):
        for tool_type in sorted(tool_types.keys()):
            tools[tool_type] = []
        setdefault(tools, "painter", "navisvg")
        setdefault(tools, "layout", self.options["layout"])
        setdefault(tools, "layout", "FixIni")
        tools["style"].append(ToolSetting("Default"))
        tools["style"].append(ToolSetting("SimpleColors"))
        tools["style"].append(ToolSetting("FancyLines"))
        tools["transform"].append(ToolSetting("NoKinks"))
        tools["transform"].append(ToolSetting("Gluballs"))
        tools["transform"].append(ToolSetting("Chainmail"))
        log.info("--demo is equivalent to '-pnavisvg:mcviz.svg -sSimpleColors -sFancyLines -tNoKinks -tGluballs -tChainmail -l%s -lFixIni'" % self.options["layout"])
        return super(DemoOptionSet, self).__call__(tools)

# If we add more optionsets, please update "OptionSets" in the wiki (grep for it!), or send an email.
